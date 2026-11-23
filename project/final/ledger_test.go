package final

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/UnrealTemplier/go-textbook-v2-vol2/project/final/ledgerdriver"
)

func TestLedgerPulseEndToEndAndConcurrency(t *testing.T) {
	inst := ledgerdriver.NewInstance()
	db := inst.OpenDB()
	defer db.Close()

	db.SetMaxOpenConns(16)
	db.SetMaxIdleConns(4)
	db.SetConnMaxLifetime(5 * time.Minute)

	svc := NewLedgerService(db)
	srv := NewServer(db, svc)

	ctx := context.Background()
	accA, err := svc.CreateAccount(ctx, "ext-a", "Alice", "RUB", 10_000)
	if err != nil {
		t.Fatalf("create account A: %v", err)
	}
	accB, err := svc.CreateAccount(ctx, "ext-b", "Bob", "RUB", 5_000)
	if err != nil {
		t.Fatalf("create account B: %v", err)
	}

	// Идемпотентный перевод через HTTP API
	reqBody, _ := json.Marshal(TransferRequest{
		IdempotencyKey: "idem-001",
		FromAccountID:  accA.ID,
		ToAccountID:    accB.ID,
		Amount:         2_500,
		Currency:       "RUB",
		Description:    "payment #1",
	})
	rec1 := httptest.NewRecorder()
	srv.ServeHTTP(rec1, httptest.NewRequest(http.MethodPost, "/api/v1/transfers", bytes.NewReader(reqBody)))
	if rec1.Code != http.StatusOK {
		t.Fatalf("transfer 1 status=%d body=%s", rec1.Code, rec1.Body.String())
	}

	// Повтор с тем же ключом идемпотентности не должен списывать деньги повторно
	rec2 := httptest.NewRecorder()
	srv.ServeHTTP(rec2, httptest.NewRequest(http.MethodPost, "/api/v1/transfers", bytes.NewReader(reqBody)))
	if rec2.Code != http.StatusOK {
		t.Fatalf("transfer replay status=%d body=%s", rec2.Code, rec2.Body.String())
	}
	var res2 TransferResult
	if err := json.NewDecoder(rec2.Body).Decode(&res2); err != nil || !res2.Replayed {
		t.Fatalf("expected Replayed=true, got %+v err=%v", res2, err)
	}

	gotA, _ := svc.GetAccount(ctx, accA.ID)
	gotB, _ := svc.GetAccount(ctx, accB.ID)
	if gotA.Balance != 7_500 || gotB.Balance != 7_500 {
		t.Fatalf("unexpected balances after idempotent transfer: A=%d B=%d", gotA.Balance, gotB.Balance)
	}

	// Outbox должен содержать ровно 1 событие
	relayed, err := svc.RelayOutbox(ctx, 10)
	if err != nil || relayed != 1 {
		t.Fatalf("expected 1 outbox event relayed, got %d err=%v", relayed, err)
	}

	// Перевод сверх остатка должен откатить всю транзакцию (включая Outbox)
	overBody, _ := json.Marshal(TransferRequest{
		IdempotencyKey: "idem-overdraft",
		FromAccountID:  accA.ID,
		ToAccountID:    accB.ID,
		Amount:         999_999,
		Currency:       "RUB",
	})
	recOver := httptest.NewRecorder()
	srv.ServeHTTP(recOver, httptest.NewRequest(http.MethodPost, "/api/v1/transfers", bytes.NewReader(overBody)))
	if recOver.Code != http.StatusUnprocessableEntity {
		t.Fatalf("expected 422 for overdraft, got %d", recOver.Code)
	}
	if relayed2, _ := svc.RelayOutbox(ctx, 10); relayed2 != 0 {
		t.Fatalf("expected 0 outbox events after rollback, got %d", relayed2)
	}

	// Встречные конкурентные переводы (A -> B и B -> A) без deadlock и с сохранением суммарного баланса
	var wg sync.WaitGroup
	for i := range 20 {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			from, to := accA.ID, accB.ID
			if idx%2 == 1 {
				from, to = accB.ID, accA.ID
			}
			_, err := svc.Transfer(ctx, TransferRequest{
				IdempotencyKey: time.Now().Format("150405.000000000") + "-" + string(rune('a'+idx)),
				FromAccountID:  from,
				ToAccountID:    to,
				Amount:         100,
				Currency:       "RUB",
			})
			if err != nil {
				t.Errorf("concurrent transfer %d failed: %v", idx, err)
			}
		}(i)
	}
	wg.Wait()

	finalA, _ := svc.GetAccount(ctx, accA.ID)
	finalB, _ := svc.GetAccount(ctx, accB.ID)
	if finalA.Balance+finalB.Balance != 15_000 {
		t.Fatalf("conservation of money violated: A=%d B=%d", finalA.Balance, finalB.Balance)
	}

	// Метрики пула database/sql и healthz
	recHealth := httptest.NewRecorder()
	srv.ServeHTTP(recHealth, httptest.NewRequest(http.MethodGet, "/healthz", nil))
	if recHealth.Code != http.StatusOK {
		t.Fatalf("healthz failed: %d", recHealth.Code)
	}
	recStats := httptest.NewRecorder()
	srv.ServeHTTP(recStats, httptest.NewRequest(http.MethodGet, "/metrics/db", nil))
	if recStats.Code != http.StatusOK || !strings.Contains(recStats.Body.String(), "max_open_connections") {
		t.Fatalf("metrics/db unexpected: %d %s", recStats.Code, recStats.Body.String())
	}

	// Проверка ErrBadConn retry со стороны database/sql при выполнении запроса (в отличие от PingContext, который не оборачивает pingDC в db.retry)
	inst.FailNextWithBadConn()
	if _, err := svc.repo.GetAccount(ctx, accA.ID); err != nil {
		t.Fatalf("expected database/sql to recover query from driver.ErrBadConn, got %v", err)
	}
}

func TestSQLArtifactsExistAndValid(t *testing.T) {
	required := []string{
		filepath.Join("..", "sql", "migrations", "001_init_ledger.sql"),
		filepath.Join("..", "sql", "migrations", "002_indexes.sql"),
		filepath.Join("..", "sql", "migrations", "003_idempotency_outbox.sql"),
		filepath.Join("..", "sql", "clickhouse", "001_ledger_events.sql"),
		filepath.Join("..", "docker-compose.yml"),
	}
	for _, p := range required {
		b, err := os.ReadFile(p)
		if err != nil || len(b) < 50 {
			t.Fatalf("missing or empty SQL/compose artifact %s: %v", p, err)
		}
	}
}
