package step06

import (
	"errors"
	"fmt"
	"testing"
	"time"
)

func TestConsistentHashingRebalanceAndFencing(t *testing.T) {
	r3 := NewShardRouter([]string{"pg-shard-1", "pg-shard-2", "pg-shard-3"}, 128)
	r4 := NewShardRouter([]string{"pg-shard-1", "pg-shard-2", "pg-shard-3", "pg-shard-4"}, 128)

	counts := make(map[string]int)
	moved := 0
	const totalKeys = 1000
	for i := range totalKeys {
		k := fmt.Sprintf("acc:%d", i)
		s3 := r3.ShardFor(k)
		s4 := r4.ShardFor(k)
		counts[s3]++
		if s3 != s4 {
			moved++
		}
	}

	for shard, cnt := range counts {
		if cnt < 200 || cnt > 450 {
			t.Fatalf("skew too high on %s: %d/%d", shard, cnt, totalKeys)
		}
	}
	// При добавлении 4-го шарда на консистентном кольце мигрирует около ~25% ключей (в идеале < 35%)
	if moved == 0 || moved > 380 {
		t.Fatalf("unexpected moved keys count: %d/%d", moved, totalKeys)
	}

	ryw := NewReadYourWritesRouter(2 * time.Second)
	t0 := time.Date(2026, 5, 1, 12, 0, 0, 0, time.UTC)
	if got := ryw.TargetNode("acc:1", t0); got != "follower" {
		t.Fatalf("expected follower before write, got %s", got)
	}
	ryw.RecordWrite("acc:1", t0)
	if got := ryw.TargetNode("acc:1", t0.Add(time.Second)); got != "leader" {
		t.Fatalf("expected leader within RYW window, got %s", got)
	}
	if got := ryw.TargetNode("acc:1", t0.Add(3*time.Second)); got != "follower" {
		t.Fatalf("expected follower after RYW window, got %s", got)
	}

	st := NewFencedStorage()
	if err := st.WriteWithToken(34, "bal", 100); err != nil {
		t.Fatalf("token 34 failed: %v", err)
	}
	if err := st.WriteWithToken(33, "bal", 999); !errors.Is(err, ErrStaleFencingToken) {
		t.Fatalf("expected ErrStaleFencingToken for token 33, got %v", err)
	}
}
