// Package step01 моделирует домен и реляционные ограничения схемы LedgerPulse:
// хранение денег в неделимых целых единицах, двойную запись и проверки NOT NULL, UNIQUE, CHECK, FK.
package step01

import (
	"errors"
	"fmt"
	"strings"
)

var (
	ErrNotNullViolation    = errors.New("not null violation")
	ErrUniqueViolation     = errors.New("unique constraint violation")
	ErrCheckViolation      = errors.New("check constraint violation")
	ErrForeignKeyViolation = errors.New("foreign key violation")
	ErrUnbalancedLedger    = errors.New("double-entry sum must equal zero")
)

// Money хранит сумму в минимальных неделимых единицах (копейках, центах) и 3-буквенную валюту ISO 4217.
type Money struct {
	Minor    int64
	Currency string
}

func NewMoney(minor int64, currency string) (Money, error) {
	c := strings.ToUpper(strings.TrimSpace(currency))
	if len(c) != 3 {
		return Money{}, fmt.Errorf("%w: currency %q must be 3 letters", ErrCheckViolation, currency)
	}
	for i := range len(c) {
		if c[i] < 'A' || c[i] > 'Z' {
			return Money{}, fmt.Errorf("%w: invalid currency %q", ErrCheckViolation, currency)
		}
	}
	return Money{Minor: minor, Currency: c}, nil
}

type Account struct {
	ID         int64
	ExternalID string
	OwnerName  string
	Currency   string
	Balance    int64
	Status     string
}

type Entry struct {
	AccountID int64
	Amount    int64 // >0 пополнение (дебет), <0 списание (кредит)
	Currency  string
}

// LedgerSchema имитирует реляционную таблицу с проверкой ограничений целостности до записи.
type LedgerSchema struct {
	nextAccountID int64
	accounts      map[int64]Account
	byExternalID  map[string]int64
	entries       []Entry
}

func NewLedgerSchema() *LedgerSchema {
	return &LedgerSchema{
		nextAccountID: 1,
		accounts:      make(map[int64]Account),
		byExternalID:  make(map[string]int64),
	}
}

func (s *LedgerSchema) CreateAccount(externalID, ownerName, currency string, initialBalance int64) (Account, error) {
	if strings.TrimSpace(externalID) == "" || strings.TrimSpace(ownerName) == "" {
		return Account{}, fmt.Errorf("%w: external_id and owner_name required", ErrNotNullViolation)
	}
	if _, exists := s.byExternalID[externalID]; exists {
		return Account{}, fmt.Errorf("%w: external_id=%q", ErrUniqueViolation, externalID)
	}
	m, err := NewMoney(initialBalance, currency)
	if err != nil {
		return Account{}, err
	}
	if m.Minor < 0 {
		return Account{}, fmt.Errorf("%w: balance must be >= 0", ErrCheckViolation)
	}

	acc := Account{
		ID:         s.nextAccountID,
		ExternalID: externalID,
		OwnerName:  ownerName,
		Currency:   m.Currency,
		Balance:    m.Minor,
		Status:     "active",
	}
	s.nextAccountID++
	s.accounts[acc.ID] = acc
	s.byExternalID[externalID] = acc.ID
	return acc, nil
}

// PostEntries проверяет внешний ключ, валюту, неотрицательность баланса и инвариант двойной записи (сумма == 0).
func (s *LedgerSchema) PostEntries(entries []Entry) error {
	if len(entries) < 2 {
		return fmt.Errorf("%w: at least 2 entries required", ErrCheckViolation)
	}

	var sum int64
	deltas := make(map[int64]int64)
	currency := entries[0].Currency

	for _, e := range entries {
		if e.Amount == 0 {
			return fmt.Errorf("%w: entry amount cannot be 0", ErrCheckViolation)
		}
		acc, ok := s.accounts[e.AccountID]
		if !ok {
			return fmt.Errorf("%w: account_id=%d not found", ErrForeignKeyViolation, e.AccountID)
		}
		if acc.Currency != e.Currency || e.Currency != currency {
			return fmt.Errorf("%w: currency mismatch (%s vs %s)", ErrCheckViolation, acc.Currency, e.Currency)
		}
		sum += e.Amount
		deltas[e.AccountID] += e.Amount
	}

	if sum != 0 {
		return fmt.Errorf("%w: got %d", ErrUnbalancedLedger, sum)
	}

	for id, delta := range deltas {
		if s.accounts[id].Balance+delta < 0 {
			return fmt.Errorf("%w: account %d balance would become negative", ErrCheckViolation, id)
		}
	}

	for id, delta := range deltas {
		acc := s.accounts[id]
		acc.Balance += delta
		s.accounts[id] = acc
	}
	s.entries = append(s.entries, entries...)
	return nil
}

func (s *LedgerSchema) Account(id int64) (Account, bool) {
	acc, ok := s.accounts[id]
	return acc, ok
}
