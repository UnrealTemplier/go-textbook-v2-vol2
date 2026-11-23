// Package final собирает сквозной сервис LedgerPulse: Repository + Unit of Work поверх *sql.DB,
// идемпотентность + Outbox, кэш Singleflight, OLAP-витрину и HTTP API с Graceful Shutdown.
package final

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"
)

var (
	ErrNotFound = errors.New("record not found")
)

type Account struct {
	ID         int64  `json:"id"`
	ExternalID string `json:"external_id"`
	OwnerName  string `json:"owner_name"`
	Currency   string `json:"currency"`
	Balance    int64  `json:"balance"`
	Status     string `json:"status"`
}

type LedgerEntry struct {
	ID            int64     `json:"id"`
	TransactionID int64     `json:"transaction_id"`
	AccountID     int64     `json:"account_id"`
	Amount        int64     `json:"amount"`
	Currency      string    `json:"currency"`
	CreatedAt     time.Time `json:"created_at"`
}

type OutboxEvent struct {
	ID            int64  `json:"id"`
	AggregateType string `json:"aggregate_type"`
	AggregateID   string `json:"aggregate_id"`
	EventType     string `json:"event_type"`
	Payload       string `json:"payload"`
}

type IdempotencyRecord struct {
	TransactionID int64
	ResponseCode  int
	ResponseBody  string
}

// DBTX задаёт общий контракт для *sql.DB и *sql.Tx (Consumer-driven interface).
type DBTX interface {
	ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error)
	QueryContext(ctx context.Context, query string, args ...any) (*sql.Rows, error)
	QueryRowContext(ctx context.Context, query string, args ...any) *sql.Row
}

// Repository определяет операции хранилища LedgerPulse без утечки деталей СУБД в сервис.
type Repository interface {
	CreateAccount(ctx context.Context, externalID, ownerName, currency string, balance int64) (Account, error)
	GetAccount(ctx context.Context, id int64) (Account, error)
	ListEntriesKeyset(ctx context.Context, accountID, cursorID int64, limit int) ([]LedgerEntry, error)
	ListUnpublishedOutbox(ctx context.Context, limit int) ([]OutboxEvent, error)
	MarkOutboxPublished(ctx context.Context, id int64, publishedAt time.Time) error
}

// TxRepository расширяет Repository методами, выполняемыми внутри Unit of Work.
type TxRepository interface {
	Repository
	GetIdempotency(ctx context.Context, key string) (IdempotencyRecord, bool, error)
	InsertTransaction(ctx context.Context, refID, kind, status, desc string) (int64, error)
	UpdateAccountBalance(ctx context.Context, accountID, delta int64) (int64, error)
	InsertEntry(ctx context.Context, txID, accountID, amount int64, currency string) (int64, error)
	InsertOutbox(ctx context.Context, aggType, aggID, evType, payload string) (int64, error)
	InsertIdempotency(ctx context.Context, key, reqHash string, txID int64, code int, body string) error
}

// TxManager управляет границами транзакции через замыкание с гарантированным Rollback при ошибке/панике.
type TxManager struct {
	db *sql.DB
}

func NewTxManager(db *sql.DB) *TxManager {
	return &TxManager{db: db}
}

func (m *TxManager) WithinTx(ctx context.Context, opts *sql.TxOptions, fn func(txRepo TxRepository) error) error {
	tx, err := m.db.BeginTx(ctx, opts)
	if err != nil {
		return fmt.Errorf("begin tx: %w", err)
	}
	defer func() {
		_ = tx.Rollback()
	}()

	if err := fn(&sqlRepo{q: tx}); err != nil {
		return err
	}
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("commit tx: %w", err)
	}
	return nil
}

type sqlRepo struct {
	q DBTX
}

func NewSQLRepository(db *sql.DB) Repository {
	return &sqlRepo{q: db}
}

func (r *sqlRepo) CreateAccount(ctx context.Context, externalID, ownerName, currency string, balance int64) (Account, error) {
	var id int64
	err := r.q.QueryRowContext(ctx,
		`INSERT INTO accounts (external_id, owner_name, currency, balance) VALUES ($1, $2, $3, $4) RETURNING id`,
		externalID, ownerName, currency, balance,
	).Scan(&id)
	if err != nil {
		return Account{}, err
	}
	return Account{
		ID:         id,
		ExternalID: externalID,
		OwnerName:  ownerName,
		Currency:   currency,
		Balance:    balance,
		Status:     "active",
	}, nil
}

func (r *sqlRepo) GetAccount(ctx context.Context, id int64) (Account, error) {
	var acc Account
	err := r.q.QueryRowContext(ctx,
		`SELECT id, external_id, owner_name, currency, balance, status FROM accounts WHERE id = $1`,
		id,
	).Scan(&acc.ID, &acc.ExternalID, &acc.OwnerName, &acc.Currency, &acc.Balance, &acc.Status)
	if errors.Is(err, sql.ErrNoRows) {
		return Account{}, ErrNotFound
	}
	return acc, err
}

func (r *sqlRepo) GetIdempotency(ctx context.Context, key string) (IdempotencyRecord, bool, error) {
	var rec IdempotencyRecord
	err := r.q.QueryRowContext(ctx,
		`SELECT transaction_id, response_code, response_body FROM idempotency_keys WHERE idempotency_key = $1`,
		key,
	).Scan(&rec.TransactionID, &rec.ResponseCode, &rec.ResponseBody)
	if errors.Is(err, sql.ErrNoRows) {
		return IdempotencyRecord{}, false, nil
	}
	if err != nil {
		return IdempotencyRecord{}, false, err
	}
	return rec, true, nil
}

func (r *sqlRepo) InsertTransaction(ctx context.Context, refID, kind, status, desc string) (int64, error) {
	var id int64
	err := r.q.QueryRowContext(ctx,
		`INSERT INTO transactions (reference_id, kind, status, description) VALUES ($1, $2, $3, $4) RETURNING id`,
		refID, kind, status, desc,
	).Scan(&id)
	return id, err
}

func (r *sqlRepo) UpdateAccountBalance(ctx context.Context, accountID, delta int64) (int64, error) {
	var newBal int64
	err := r.q.QueryRowContext(ctx,
		`UPDATE accounts SET balance = balance + $1 WHERE id = $2 AND balance + $1 >= 0 RETURNING balance`,
		delta, accountID,
	).Scan(&newBal)
	return newBal, err
}

func (r *sqlRepo) InsertEntry(ctx context.Context, txID, accountID, amount int64, currency string) (int64, error) {
	var id int64
	err := r.q.QueryRowContext(ctx,
		`INSERT INTO ledger_entries (transaction_id, account_id, amount, currency) VALUES ($1, $2, $3, $4) RETURNING id`,
		txID, accountID, amount, currency,
	).Scan(&id)
	return id, err
}

func (r *sqlRepo) InsertOutbox(ctx context.Context, aggType, aggID, evType, payload string) (int64, error) {
	var id int64
	err := r.q.QueryRowContext(ctx,
		`INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES ($1, $2, $3, $4) RETURNING id`,
		aggType, aggID, evType, payload,
	).Scan(&id)
	return id, err
}

func (r *sqlRepo) InsertIdempotency(ctx context.Context, key, reqHash string, txID int64, code int, body string) error {
	_, err := r.q.ExecContext(ctx,
		`INSERT INTO idempotency_keys (idempotency_key, request_hash, transaction_id, response_code, response_body) VALUES ($1, $2, $3, $4, $5)`,
		key, reqHash, txID, code, body,
	)
	return err
}

func (r *sqlRepo) ListEntriesKeyset(ctx context.Context, accountID, cursorID int64, limit int) ([]LedgerEntry, error) {
	if limit <= 0 || limit > 200 {
		limit = 50
	}
	rows, err := r.q.QueryContext(ctx,
		`SELECT id, transaction_id, account_id, amount, currency, created_at FROM ledger_entries WHERE account_id = $1 AND id < $2 ORDER BY id DESC LIMIT $3`,
		accountID, cursorID, limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []LedgerEntry
	for rows.Next() {
		var e LedgerEntry
		if err := rows.Scan(&e.ID, &e.TransactionID, &e.AccountID, &e.Amount, &e.Currency, &e.CreatedAt); err != nil {
			return nil, err
		}
		out = append(out, e)
	}
	return out, rows.Err()
}

func (r *sqlRepo) ListUnpublishedOutbox(ctx context.Context, limit int) ([]OutboxEvent, error) {
	rows, err := r.q.QueryContext(ctx,
		`SELECT id, aggregate_type, aggregate_id, event_type, payload FROM outbox_events WHERE published_at IS NULL ORDER BY id ASC LIMIT $1`,
		limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []OutboxEvent
	for rows.Next() {
		var ev OutboxEvent
		if err := rows.Scan(&ev.ID, &ev.AggregateType, &ev.AggregateID, &ev.EventType, &ev.Payload); err != nil {
			return nil, err
		}
		out = append(out, ev)
	}
	return out, rows.Err()
}

func (r *sqlRepo) MarkOutboxPublished(ctx context.Context, id int64, publishedAt time.Time) error {
	_, err := r.q.ExecContext(ctx,
		`UPDATE outbox_events SET published_at = $1 WHERE id = $2`,
		publishedAt, id,
	)
	return err
}
