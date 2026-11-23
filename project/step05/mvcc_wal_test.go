package step05

import (
	"errors"
	"path/filepath"
	"sync"
	"testing"
)

func TestWALRecoveryAndMVCC(t *testing.T) {
	walPath := filepath.Join(t.TempDir(), "ledger.wal")
	store, err := OpenWALStore(walPath)
	if err != nil {
		t.Fatalf("open wal: %v", err)
	}
	if err := store.ApplyCommitted(1, map[string]int64{"acc:1": 1000}); err != nil {
		t.Fatalf("commit tx 1: %v", err)
	}
	// Незавершённая транзакция 2 не должна восстановиться после рестарта
	if err := store.WriteUncommitted(2, "acc:1", 9999); err != nil {
		t.Fatalf("uncommitted write: %v", err)
	}

	reopened, err := OpenWALStore(walPath)
	if err != nil {
		t.Fatalf("reopen wal: %v", err)
	}
	if v, ok := reopened.Get("acc:1"); !ok || v != 1000 {
		t.Fatalf("expected acc:1=1000 after WAL recovery, got %d (ok=%v)", v, ok)
	}

	// MVCC Snapshot Isolation + First-Committer-Wins
	eng := NewMVCCEngine()
	seed := eng.Begin()
	seed.Set("balance", 500)
	seed.Set("audit_tag", 1)
	if err := seed.Commit(); err != nil {
		t.Fatalf("seed commit: %v", err)
	}

	tx1 := eng.Begin()
	tx2 := eng.Begin()
	tx1.Set("balance", 600)
	tx1.Set("audit_tag", 2)
	tx2.Set("balance", 700)

	if err := tx1.Commit(); err != nil {
		t.Fatalf("tx1 commit: %v", err)
	}
	// tx2 всё ещё видит снимок с audit_tag=1 (Snapshot Isolation)
	if tag, ok := tx2.Get("audit_tag"); !ok || tag != 1 {
		t.Fatalf("expected tx2 snapshot to see audit_tag=1, got %d (ok=%v)", tag, ok)
	}
	if err := tx2.Commit(); !errors.Is(err, ErrWriteConflict) {
		t.Fatalf("expected ErrWriteConflict, got %v", err)
	}

	// Параллельное чтение из MVCC под -race
	var wg sync.WaitGroup
	for range 8 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			r := eng.Begin()
			if v, ok := r.Get("balance"); !ok || v != 600 {
				t.Errorf("expected 600, got %d", v)
			}
		}()
	}
	wg.Wait()

	// Детектор Deadlock
	if !HasDeadlockCycle(map[uint64][]uint64{1: {2}, 2: {3}, 3: {1}}) {
		t.Fatalf("expected deadlock cycle")
	}
	if HasDeadlockCycle(map[uint64][]uint64{1: {2}, 2: {3}}) {
		t.Fatalf("unexpected deadlock cycle")
	}
}
