package step07

import (
	"context"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestSingleflightCacheAndMergeTree(t *testing.T) {
	cache := NewSingleflightCache[int64]()
	var dbHits atomic.Int64

	var wg sync.WaitGroup
	for range 32 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			v, err := cache.GetOrLoad(context.Background(), "acc:42", time.Minute, func(ctx context.Context) (int64, error) {
				time.Sleep(15 * time.Millisecond)
				dbHits.Add(1)
				return 125_00, nil
			})
			if err != nil || v != 125_00 {
				t.Errorf("unexpected result: v=%d err=%v", v, err)
			}
		}()
	}
	wg.Wait()

	if hits := dbHits.Load(); hits != 1 {
		t.Fatalf("expected Singleflight to coalesce 32 callers into 1 DB hit, got %d", hits)
	}

	// Повторное чтение идёт из кэша
	v, err := cache.GetOrLoad(context.Background(), "acc:42", time.Minute, func(ctx context.Context) (int64, error) {
		dbHits.Add(1)
		return 0, nil
	})
	if err != nil || v != 125_00 || dbHits.Load() != 1 {
		t.Fatalf("expected cache hit without DB call")
	}

	// MergeTree OLAP
	olap := NewMergeTreeSimulator()
	olap.InsertBatch([]OLAPEvent{
		{Day: "2026-05-01", Currency: "RUB", AccountID: 2, Amount: 400},
		{Day: "2026-05-01", Currency: "USD", AccountID: 1, Amount: 100},
	})
	olap.InsertBatch([]OLAPEvent{
		{Day: "2026-05-01", Currency: "RUB", AccountID: 1, Amount: 600},
	})
	if got := olap.CompactParts(); got != 1 {
		t.Fatalf("expected 1 compacted part, got %d", got)
	}
	if sum := olap.SumByCurrency("RUB"); sum != 1000 {
		t.Fatalf("expected RUB sum 1000, got %d", sum)
	}
}
