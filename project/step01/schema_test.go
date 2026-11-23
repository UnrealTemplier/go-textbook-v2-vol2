package step01

import (
	"errors"
	"testing"
)

func TestLedgerSchemaConstraints(t *testing.T) {
	s := NewLedgerSchema()

	alice, err := s.CreateAccount("ext-alice", "Alice", "RUB", 100_00)
	if err != nil {
		t.Fatalf("create alice: %v", err)
	}
	bob, err := s.CreateAccount("ext-bob", "Bob", "RUB", 50_00)
	if err != nil {
		t.Fatalf("create bob: %v", err)
	}

	if _, err := s.CreateAccount("ext-alice", "Clone", "RUB", 0); !errors.Is(err, ErrUniqueViolation) {
		t.Fatalf("expected ErrUniqueViolation, got %v", err)
	}
	if _, err := s.CreateAccount("", "NoExt", "RUB", 0); !errors.Is(err, ErrNotNullViolation) {
		t.Fatalf("expected ErrNotNullViolation, got %v", err)
	}
	if _, err := s.CreateAccount("ext-bad", "Bad", "RUB", -1); !errors.Is(err, ErrCheckViolation) {
		t.Fatalf("expected ErrCheckViolation for negative balance, got %v", err)
	}

	err = s.PostEntries([]Entry{
		{AccountID: alice.ID, Amount: -30_00, Currency: "RUB"},
		{AccountID: bob.ID, Amount: 30_00, Currency: "RUB"},
	})
	if err != nil {
		t.Fatalf("valid transfer failed: %v", err)
	}

	aGot, _ := s.Account(alice.ID)
	bGot, _ := s.Account(bob.ID)
	if aGot.Balance != 70_00 || bGot.Balance != 80_00 {
		t.Fatalf("unexpected balances: alice=%d bob=%d", aGot.Balance, bGot.Balance)
	}

	// Нарушение FK
	err = s.PostEntries([]Entry{
		{AccountID: alice.ID, Amount: -10_00, Currency: "RUB"},
		{AccountID: 9999, Amount: 10_00, Currency: "RUB"},
	})
	if !errors.Is(err, ErrForeignKeyViolation) {
		t.Fatalf("expected ErrForeignKeyViolation, got %v", err)
	}

	// Нарушение двойной записи
	err = s.PostEntries([]Entry{
		{AccountID: alice.ID, Amount: -10_00, Currency: "RUB"},
		{AccountID: bob.ID, Amount: 5_00, Currency: "RUB"},
	})
	if !errors.Is(err, ErrUnbalancedLedger) {
		t.Fatalf("expected ErrUnbalancedLedger, got %v", err)
	}
}
