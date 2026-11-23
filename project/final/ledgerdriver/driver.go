// Package ledgerdriver реализует чистый Go database/sql/driver для автономной работы
// и тестирования LedgerPulse поверх настоящего пула *sql.DB, транзакций и Prepared Statements.
package ledgerdriver

import (
	"context"
	"database/sql"
	"database/sql/driver"
	"errors"
	"fmt"
	"io"
	"slices"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

var (
	ErrDuplicateKey      = errors.New("unique_violation: duplicate key value")
	ErrInsufficientFunds = errors.New("check_violation: insufficient balance")
	ErrAccountNotFound   = errors.New("not_found: account does not exist")
)

type accountRow struct {
	id         int64
	externalID string
	ownerName  string
	currency   string
	balance    int64
	status     string
}

type txRow struct {
	id          int64
	referenceID string
	kind        string
	status      string
	description string
}

type entryRow struct {
	id            int64
	transactionID int64
	accountID     int64
	amount        int64
	currency      string
	createdAt     time.Time
}

type idempotencyRow struct {
	key          string
	requestHash  string
	txID         int64
	responseCode int64
	responseBody string
}

type outboxRow struct {
	id            int64
	aggregateType string
	aggregateID   string
	eventType     string
	payload       string
	publishedAt   *time.Time
}

type dbState struct {
	nextAccID   int64
	nextTxID    int64
	nextEntryID int64
	nextOutID   int64
	accounts    map[int64]accountRow
	accByExt    map[string]int64
	txs         map[int64]txRow
	txByRef     map[string]int64
	entries     []entryRow
	idempotency map[string]idempotencyRow
	outbox      []outboxRow
}

func newDBState() *dbState {
	return &dbState{
		nextAccID:   1,
		nextTxID:    1,
		nextEntryID: 1,
		nextOutID:   1,
		accounts:    make(map[int64]accountRow),
		accByExt:    make(map[string]int64),
		txs:         make(map[int64]txRow),
		txByRef:     make(map[string]int64),
		idempotency: make(map[string]idempotencyRow),
	}
}

func (s *dbState) clone() *dbState {
	c := &dbState{
		nextAccID:   s.nextAccID,
		nextTxID:    s.nextTxID,
		nextEntryID: s.nextEntryID,
		nextOutID:   s.nextOutID,
		accounts:    make(map[int64]accountRow, len(s.accounts)),
		accByExt:    make(map[string]int64, len(s.accByExt)),
		txs:         make(map[int64]txRow, len(s.txs)),
		txByRef:     make(map[string]int64, len(s.txByRef)),
		entries:     slices.Clone(s.entries),
		idempotency: make(map[string]idempotencyRow, len(s.idempotency)),
		outbox:      slices.Clone(s.outbox),
	}
	for k, v := range s.accounts {
		c.accounts[k] = v
	}
	for k, v := range s.accByExt {
		c.accByExt[k] = v
	}
	for k, v := range s.txs {
		c.txs[k] = v
	}
	for k, v := range s.txByRef {
		c.txByRef[k] = v
	}
	for k, v := range s.idempotency {
		c.idempotency[k] = v
	}
	return c
}

// Instance хранит изолированное состояние одной виртуальной БД (удобно для параллельных тестов).
type Instance struct {
	mu          sync.Mutex
	state       *dbState
	failNextBad atomic.Bool
	slowHook    func(query string, dur time.Duration)
}

func NewInstance() *Instance {
	return &Instance{state: newDBState()}
}

func (i *Instance) FailNextWithBadConn() {
	i.failNextBad.Store(true)
}

func (i *Instance) SetSlowQueryHook(fn func(query string, dur time.Duration)) {
	i.mu.Lock()
	defer i.mu.Unlock()
	i.slowHook = fn
}

// OpenDB открывает готовый *sql.DB, привязанный к данному Instance.
func (i *Instance) OpenDB() *sql.DB {
	return sql.OpenDB(&connector{inst: i})
}

type connector struct {
	inst *Instance
}

func (c *connector) Connect(_ context.Context) (driver.Conn, error) {
	return &conn{inst: c.inst}, nil
}

func (c *connector) Driver() driver.Driver {
	return Driver{}
}

// Driver реализует интерфейс database/sql/driver.Driver для регистрации через sql.Register.
type Driver struct{}

var (
	registryMu sync.RWMutex
	instances  = make(map[string]*Instance)
)

func init() {
	sql.Register("ledgerpulse", Driver{})
}

func RegisterInstance(dsn string, inst *Instance) {
	registryMu.Lock()
	defer registryMu.Unlock()
	instances[dsn] = inst
}

func (d Driver) Open(dsn string) (driver.Conn, error) {
	registryMu.RLock()
	inst, ok := instances[dsn]
	registryMu.RUnlock()
	if !ok {
		inst = NewInstance()
		RegisterInstance(dsn, inst)
	}
	return &conn{inst: inst}, nil
}

type conn struct {
	inst  *Instance
	tx    *dbState // не nil, если открыта транзакция
	txMu  sync.Mutex
	closed bool
}

func (c *conn) Prepare(query string) (driver.Stmt, error) {
	return c.PrepareContext(context.Background(), query)
}

func (c *conn) PrepareContext(_ context.Context, query string) (driver.Stmt, error) {
	if c.closed {
		return nil, driver.ErrBadConn
	}
	return &stmt{c: c, query: query}, nil
}

func (c *conn) Close() error {
	c.closed = true
	c.tx = nil
	return nil
}

func (c *conn) Begin() (driver.Tx, error) {
	return c.BeginTx(context.Background(), driver.TxOptions{})
}

func (c *conn) BeginTx(_ context.Context, _ driver.TxOptions) (driver.Tx, error) {
	if c.closed {
		return nil, driver.ErrBadConn
	}
	c.inst.mu.Lock()
	snap := c.inst.state.clone()
	c.inst.mu.Unlock()
	c.tx = snap
	return &txHandle{c: c}, nil
}

func (c *conn) Ping(ctx context.Context) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	if c.inst.failNextBad.Swap(false) {
		return driver.ErrBadConn
	}
	return nil
}

func (c *conn) ExecContext(ctx context.Context, query string, args []driver.NamedValue) (driver.Result, error) {
	cols, rows, err := c.runQuery(ctx, query, args)
	_ = cols
	if err != nil {
		return nil, err
	}
	return driver.RowsAffected(len(rows)), nil
}

func (c *conn) QueryContext(ctx context.Context, query string, args []driver.NamedValue) (driver.Rows, error) {
	cols, rows, err := c.runQuery(ctx, query, args)
	if err != nil {
		return nil, err
	}
	return &memRows{cols: cols, rows: rows}, nil
}

func (c *conn) runQuery(ctx context.Context, query string, args []driver.NamedValue) ([]string, [][]driver.Value, error) {
	if err := ctx.Err(); err != nil {
		return nil, nil, err
	}
	if c.closed || c.inst.failNextBad.Swap(false) {
		return nil, nil, driver.ErrBadConn
	}

	start := time.Now()
	defer func() {
		c.inst.mu.Lock()
		hook := c.inst.slowHook
		c.inst.mu.Unlock()
		if hook != nil {
			hook(query, time.Since(start))
		}
	}()

	norm := strings.Join(strings.Fields(query), " ")

	var st *dbState
	if c.tx != nil {
		st = c.tx
	} else {
		c.inst.mu.Lock()
		defer c.inst.mu.Unlock()
		st = c.inst.state
	}

	switch {
	case strings.HasPrefix(norm, "INSERT INTO accounts"):
		extID := asString(args[0].Value)
		owner := asString(args[1].Value)
		curr := asString(args[2].Value)
		bal := asInt64(args[3].Value)
		if _, exists := st.accByExt[extID]; exists {
			return nil, nil, ErrDuplicateKey
		}
		if bal < 0 {
			return nil, nil, ErrInsufficientFunds
		}
		id := st.nextAccID
		st.nextAccID++
		st.accounts[id] = accountRow{
			id:         id,
			externalID: extID,
			ownerName:  owner,
			currency:   curr,
			balance:    bal,
			status:     "active",
		}
		st.accByExt[extID] = id
		return []string{"id"}, [][]driver.Value{{id}}, nil

	case strings.HasPrefix(norm, "SELECT id, external_id, owner_name, currency, balance, status FROM accounts WHERE id ="):
		id := asInt64(args[0].Value)
		acc, ok := st.accounts[id]
		if !ok {
			return []string{"id", "external_id", "owner_name", "currency", "balance", "status"}, nil, nil
		}
		return []string{"id", "external_id", "owner_name", "currency", "balance", "status"},
			[][]driver.Value{{acc.id, acc.externalID, acc.ownerName, acc.currency, acc.balance, acc.status}}, nil

	case strings.HasPrefix(norm, "SELECT transaction_id, response_code, response_body FROM idempotency_keys WHERE idempotency_key ="):
		key := asString(args[0].Value)
		row, ok := st.idempotency[key]
		if !ok {
			return []string{"transaction_id", "response_code", "response_body"}, nil, nil
		}
		return []string{"transaction_id", "response_code", "response_body"},
			[][]driver.Value{{row.txID, row.responseCode, row.responseBody}}, nil

	case strings.HasPrefix(norm, "INSERT INTO transactions"):
		refID := asString(args[0].Value)
		kind := asString(args[1].Value)
		status := asString(args[2].Value)
		desc := asString(args[3].Value)
		if _, exists := st.txByRef[refID]; exists {
			return nil, nil, ErrDuplicateKey
		}
		id := st.nextTxID
		st.nextTxID++
		st.txs[id] = txRow{id: id, referenceID: refID, kind: kind, status: status, description: desc}
		st.txByRef[refID] = id
		return []string{"id"}, [][]driver.Value{{id}}, nil

	case strings.HasPrefix(norm, "UPDATE accounts SET balance = balance +"):
		delta := asInt64(args[0].Value)
		id := asInt64(args[1].Value)
		acc, ok := st.accounts[id]
		if !ok {
			return nil, nil, ErrAccountNotFound
		}
		if acc.balance+delta < 0 {
			return nil, nil, ErrInsufficientFunds
		}
		acc.balance += delta
		st.accounts[id] = acc
		return []string{"balance"}, [][]driver.Value{{acc.balance}}, nil

	case strings.HasPrefix(norm, "INSERT INTO ledger_entries"):
		txID := asInt64(args[0].Value)
		accID := asInt64(args[1].Value)
		amt := asInt64(args[2].Value)
		curr := asString(args[3].Value)
		id := st.nextEntryID
		st.nextEntryID++
		st.entries = append(st.entries, entryRow{
			id:            id,
			transactionID: txID,
			accountID:     accID,
			amount:        amt,
			currency:      curr,
			createdAt:     time.Now().UTC(),
		})
		return []string{"id"}, [][]driver.Value{{id}}, nil

	case strings.HasPrefix(norm, "INSERT INTO outbox_events"):
		aggType := asString(args[0].Value)
		aggID := asString(args[1].Value)
		evType := asString(args[2].Value)
		payload := asString(args[3].Value)
		id := st.nextOutID
		st.nextOutID++
		st.outbox = append(st.outbox, outboxRow{
			id:            id,
			aggregateType: aggType,
			aggregateID:   aggID,
			eventType:     evType,
			payload:       payload,
		})
		return []string{"id"}, [][]driver.Value{{id}}, nil

	case strings.HasPrefix(norm, "INSERT INTO idempotency_keys"):
		key := asString(args[0].Value)
		reqHash := asString(args[1].Value)
		txID := asInt64(args[2].Value)
		code := asInt64(args[3].Value)
		body := asString(args[4].Value)
		if _, exists := st.idempotency[key]; exists {
			return nil, nil, ErrDuplicateKey
		}
		st.idempotency[key] = idempotencyRow{
			key:          key,
			requestHash:  reqHash,
			txID:         txID,
			responseCode: code,
			responseBody: body,
		}
		return nil, [][]driver.Value{{int64(1)}}, nil

	case strings.HasPrefix(norm, "SELECT id, transaction_id, account_id, amount, currency, created_at FROM ledger_entries"):
		accID := asInt64(args[0].Value)
		cursorID := asInt64(args[1].Value)
		limit := int(asInt64(args[2].Value))
		var out [][]driver.Value
		for idx := len(st.entries) - 1; idx >= 0; idx-- {
			e := st.entries[idx]
			if e.accountID != accID {
				continue
			}
			if cursorID > 0 && e.id >= cursorID {
				continue
			}
			out = append(out, []driver.Value{e.id, e.transactionID, e.accountID, e.amount, e.currency, e.createdAt})
			if len(out) >= limit {
				break
			}
		}
		return []string{"id", "transaction_id", "account_id", "amount", "currency", "created_at"}, out, nil

	case strings.HasPrefix(norm, "SELECT id, aggregate_type, aggregate_id, event_type, payload FROM outbox_events WHERE published_at IS NULL"):
		limit := int(asInt64(args[0].Value))
		var out [][]driver.Value
		for _, ev := range st.outbox {
			if ev.publishedAt != nil {
				continue
			}
			out = append(out, []driver.Value{ev.id, ev.aggregateType, ev.aggregateID, ev.eventType, ev.payload})
			if len(out) >= limit {
				break
			}
		}
		return []string{"id", "aggregate_type", "aggregate_id", "event_type", "payload"}, out, nil

	case strings.HasPrefix(norm, "UPDATE outbox_events SET published_at ="):
		pub := args[0].Value.(time.Time)
		id := asInt64(args[1].Value)
		for idx := range st.outbox {
			if st.outbox[idx].id == id {
				st.outbox[idx].publishedAt = &pub
				return nil, [][]driver.Value{{int64(1)}}, nil
			}
		}
		return nil, nil, nil

	default:
		return nil, nil, fmt.Errorf("ledgerdriver: unsupported SQL %q", norm)
	}
}

func asInt64(v any) int64 {
	switch x := v.(type) {
	case int64:
		return x
	case int:
		return int64(x)
	default:
		return 0
	}
}

func asString(v any) string {
	switch x := v.(type) {
	case string:
		return x
	case []byte:
		return string(x)
	default:
		return fmt.Sprint(v)
	}
}

type txHandle struct {
	c *conn
}

func (t *txHandle) Commit() error {
	if t.c.tx == nil {
		return errors.New("tx already closed")
	}
	t.c.inst.mu.Lock()
	t.c.inst.state = t.c.tx
	t.c.inst.mu.Unlock()
	t.c.tx = nil
	return nil
}

func (t *txHandle) Rollback() error {
	t.c.tx = nil
	return nil
}

type stmt struct {
	c     *conn
	query string
}

func (s *stmt) Close() error  { return nil }
func (s *stmt) NumInput() int { return -1 }

func (s *stmt) Exec(args []driver.Value) (driver.Result, error) {
	return s.ExecContext(context.Background(), toNamed(args))
}

func (s *stmt) ExecContext(ctx context.Context, args []driver.NamedValue) (driver.Result, error) {
	return s.c.ExecContext(ctx, s.query, args)
}

func (s *stmt) Query(args []driver.Value) (driver.Rows, error) {
	return s.QueryContext(context.Background(), toNamed(args))
}

func (s *stmt) QueryContext(ctx context.Context, args []driver.NamedValue) (driver.Rows, error) {
	return s.c.QueryContext(ctx, s.query, args)
}

func toNamed(args []driver.Value) []driver.NamedValue {
	out := make([]driver.NamedValue, len(args))
	for i, a := range args {
		out[i] = driver.NamedValue{Ordinal: i + 1, Value: a}
	}
	return out
}

type memRows struct {
	cols []string
	rows [][]driver.Value
	pos  int
}

func (r *memRows) Columns() []string { return r.cols }
func (r *memRows) Close() error      { return nil }
func (r *memRows) Next(dest []driver.Value) error {
	if r.pos >= len(r.rows) {
		return io.EOF
	}
	copy(dest, r.rows[r.pos])
	r.pos++
	return nil
}
