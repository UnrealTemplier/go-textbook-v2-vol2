// Package step07 моделирует Cache-Aside с TTL+jitter, Singleflight против Cache Stampede
// и батчевую колоночную запись с компактификацией частей (аналог ClickHouse MergeTree).
package step07

import (
	"context"
	"math/rand/v2"
	"slices"
	"sync"
	"time"
)

type cacheEntry[V any] struct {
	val       V
	expiresAt time.Time
}

type call[V any] struct {
	wg  sync.WaitGroup
	val V
	err error
}

// SingleflightCache объединяет in-memory кэш (Redis/Valkey модель) и защиту от Cache Stampede.
type SingleflightCache[V any] struct {
	mu      sync.Mutex
	items   map[string]cacheEntry[V]
	inflight map[string]*call[V]
	now     func() time.Time
}

func NewSingleflightCache[V any]() *SingleflightCache[V] {
	return &SingleflightCache[V]{
		items:    make(map[string]cacheEntry[V]),
		inflight: make(map[string]*call[V]),
		now:      time.Now,
	}
}

func (c *SingleflightCache[V]) GetOrLoad(ctx context.Context, key string, baseTTL time.Duration, loader func(context.Context) (V, error)) (V, error) {
	c.mu.Lock()
	if ent, ok := c.items[key]; ok && c.now().Before(ent.expiresAt) {
		c.mu.Unlock()
		return ent.val, nil
	}
	if existing, ok := c.inflight[key]; ok {
		c.mu.Unlock()
		existing.wg.Wait()
		return existing.val, existing.err
	}

	cl := &call[V]{}
	cl.wg.Add(1)
	c.inflight[key] = cl
	c.mu.Unlock()

	val, err := loader(ctx)
	cl.val = val
	cl.err = err

	c.mu.Lock()
	delete(c.inflight, key)
	if err == nil && baseTTL > 0 {
		// Добавляем джиттер ±15%, чтобы избежать лавинообразного истечения ключей
		jitter := time.Duration(float64(baseTTL) * (0.85 + rand.Float64()*0.30))
		c.items[key] = cacheEntry[V]{val: val, expiresAt: c.now().Add(jitter)}
	}
	c.mu.Unlock()

	cl.wg.Done()
	return val, err
}

func (c *SingleflightCache[V]) Invalidate(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.items, key)
}

// OLAPEvent — строка аналитической витрины, хранимая в памяти в колоночном формате (Structure of Arrays).
type OLAPEvent struct {
	Day       string
	Currency  string
	AccountID uint64
	Amount    int64
}

type ColumnPart struct {
	Days       []string
	Currencies []string
	AccountIDs []uint64
	Amounts    []int64
}

// MergeTreeSimulator накапливает иммутабельные колоночные части и периодически сливает их в одну.
type MergeTreeSimulator struct {
	mu    sync.Mutex
	parts []ColumnPart
}

func NewMergeTreeSimulator() *MergeTreeSimulator {
	return &MergeTreeSimulator{}
}

// InsertBatch записывает пачку событий одной неизменяемой колоночной частью (сортировка по Currency, AccountID).
func (m *MergeTreeSimulator) InsertBatch(events []OLAPEvent) {
	if len(events) == 0 {
		return
	}
	sorted := slices.Clone(events)
	slices.SortFunc(sorted, func(a, b OLAPEvent) int {
		if a.Currency < b.Currency {
			return -1
		}
		if a.Currency > b.Currency {
			return 1
		}
		if a.AccountID < b.AccountID {
			return -1
		}
		if a.AccountID > b.AccountID {
			return 1
		}
		return 0
	})

	part := ColumnPart{
		Days:       make([]string, len(sorted)),
		Currencies: make([]string, len(sorted)),
		AccountIDs: make([]uint64, len(sorted)),
		Amounts:    make([]int64, len(sorted)),
	}
	for i, ev := range sorted {
		part.Days[i] = ev.Day
		part.Currencies[i] = ev.Currency
		part.AccountIDs[i] = ev.AccountID
		part.Amounts[i] = ev.Amount
	}

	m.mu.Lock()
	m.parts = append(m.parts, part)
	m.mu.Unlock()
}

// CompactParts имитирует фоновое слияние частей в MergeTree.
func (m *MergeTreeSimulator) CompactParts() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	if len(m.parts) <= 1 {
		return len(m.parts)
	}
	var all []OLAPEvent
	for _, p := range m.parts {
		for i := range p.Amounts {
			all = append(all, OLAPEvent{
				Day:       p.Days[i],
				Currency:  p.Currencies[i],
				AccountID: p.AccountIDs[i],
				Amount:    p.Amounts[i],
			})
		}
	}
	part := buildColumnPart(all)
	m.parts = []ColumnPart{part}
	return len(m.parts)
}

func buildColumnPart(events []OLAPEvent) ColumnPart {
	sorted := slices.Clone(events)
	slices.SortFunc(sorted, func(a, b OLAPEvent) int {
		if a.Currency < b.Currency {
			return -1
		}
		if a.Currency > b.Currency {
			return 1
		}
		if a.AccountID < b.AccountID {
			return -1
		}
		if a.AccountID > b.AccountID {
			return 1
		}
		return 0
	})
	part := ColumnPart{
		Days:       make([]string, len(sorted)),
		Currencies: make([]string, len(sorted)),
		AccountIDs: make([]uint64, len(sorted)),
		Amounts:    make([]int64, len(sorted)),
	}
	for i, ev := range sorted {
		part.Days[i] = ev.Day
		part.Currencies[i] = ev.Currency
		part.AccountIDs[i] = ev.AccountID
		part.Amounts[i] = ev.Amount
	}
	return part
}

// SumByCurrency читает только две колонки (Currencies и Amounts) без распаковки остальных полей.
func (m *MergeTreeSimulator) SumByCurrency(currency string) int64 {
	m.mu.Lock()
	defer m.mu.Unlock()
	var sum int64
	for _, p := range m.parts {
		for i, c := range p.Currencies {
			if c == currency {
				sum += p.Amounts[i]
			}
		}
	}
	return sum
}
