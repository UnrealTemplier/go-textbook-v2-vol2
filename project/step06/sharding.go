// Package step06 моделирует консистентное хеширование (Consistent Hashing с виртуальными узлами),
// маршрутизацию чтения с гарантией Read-Your-Writes и проверку fencing tokens для распределённых блокировок.
package step06

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"fmt"
	"slices"
	"sync"
	"time"
)

var ErrStaleFencingToken = errors.New("stale fencing token rejected")

type vnode struct {
	hash  uint64
	shard string
}

// ShardRouter распределяет account_id по физическим шардам через кольцо консистентного хеширования.
type ShardRouter struct {
	vnodesPerShard int
	ring           []vnode
}

func NewShardRouter(shards []string, vnodesPerShard int) *ShardRouter {
	if vnodesPerShard <= 0 {
		vnodesPerShard = 64
	}
	r := &ShardRouter{vnodesPerShard: vnodesPerShard}
	for _, s := range shards {
		for i := range vnodesPerShard {
			h := hashKey(fmt.Sprintf("%s#%d", s, i))
			r.ring = append(r.ring, vnode{hash: h, shard: s})
		}
	}
	slices.SortFunc(r.ring, func(a, b vnode) int {
		if a.hash < b.hash {
			return -1
		}
		if a.hash > b.hash {
			return 1
		}
		return 0
	})
	return r
}

func hashKey(k string) uint64 {
	sum := sha256.Sum256([]byte(k))
	return binary.BigEndian.Uint64(sum[:8])
}

func (r *ShardRouter) ShardFor(key string) string {
	if len(r.ring) == 0 {
		return ""
	}
	h := hashKey(key)
	idx, _ := slices.BinarySearchFunc(r.ring, h, func(v vnode, target uint64) int {
		if v.hash < target {
			return -1
		}
		if v.hash > target {
			return 1
		}
		return 0
	})
	if idx == len(r.ring) {
		idx = 0
	}
	return r.ring[idx].shard
}

// ReadYourWritesRouter направляет чтение на Leader, если клиент недавно писал в этот аккаунт,
// иначе разгружает чтение на Follower-реплики.
type ReadYourWritesRouter struct {
	mu        sync.RWMutex
	window    time.Duration
	lastWrite map[string]time.Time
}

func NewReadYourWritesRouter(window time.Duration) *ReadYourWritesRouter {
	return &ReadYourWritesRouter{
		window:    window,
		lastWrite: make(map[string]time.Time),
	}
}

func (r *ReadYourWritesRouter) RecordWrite(accountKey string, now time.Time) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.lastWrite[accountKey] = now
}

func (r *ReadYourWritesRouter) TargetNode(accountKey string, now time.Time) string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	t, ok := r.lastWrite[accountKey]
	if ok && now.Sub(t) <= r.window {
		return "leader"
	}
	return "follower"
}

// FencedStorage защищает хранилище от устаревшего держателя блокировки после GC-паузы.
type FencedStorage struct {
	mu           sync.Mutex
	highestToken uint64
	data         map[string]int64
}

func NewFencedStorage() *FencedStorage {
	return &FencedStorage{data: make(map[string]int64)}
}

func (s *FencedStorage) WriteWithToken(token uint64, key string, val int64) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if token < s.highestToken {
		return fmt.Errorf("%w: got %d, highest %d", ErrStaleFencingToken, token, s.highestToken)
	}
	s.highestToken = token
	s.data[key] = val
	return nil
}
