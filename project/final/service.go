package final

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
	"time"

	"github.com/UnrealTemplier/go-textbook-v2-vol2/project/step07"
)

var (
	ErrInvalidTransfer = errors.New("invalid transfer request")
	ErrCurrencyMismatch = errors.New("account currencies do not match")
)

type TransferRequest struct {
	IdempotencyKey string `json:"idempotency_key"`
	FromAccountID  int64  `json:"from_account_id"`
	ToAccountID    int64  `json:"to_account_id"`
	Amount         int64  `json:"amount"`
	Currency       string `json:"currency"`
	Description    string `json:"description"`
}

type TransferResult struct {
	TransactionID int64 `json:"transaction_id"`
	FromBalance   int64 `json:"from_balance"`
	ToBalance     int64 `json:"to_balance"`
	Replayed      bool  `json:"replayed"`
}

type LedgerService struct {
	repo  Repository
	txMgr *TxManager
	cache *step07.SingleflightCache[Account]
	olap  *step07.MergeTreeSimulator
}

func NewLedgerService(db *sql.DB) *LedgerService {
	return &LedgerService{
		repo:  NewSQLRepository(db),
		txMgr: NewTxManager(db),
		cache: step07.NewSingleflightCache[Account](),
		olap:  step07.NewMergeTreeSimulator(),
	}
}

func (s *LedgerService) CreateAccount(ctx context.Context, externalID, ownerName, currency string, balance int64) (Account, error) {
	return s.repo.CreateAccount(ctx, externalID, ownerName, currency, balance)
}

func (s *LedgerService) GetAccount(ctx context.Context, id int64) (Account, error) {
	key := fmt.Sprintf("acc:%d", id)
	return s.cache.GetOrLoad(ctx, key, 15*time.Second, func(ctx context.Context) (Account, error) {
		return s.repo.GetAccount(ctx, id)
	})
}

func (s *LedgerService) ListEntries(ctx context.Context, accountID, cursorID int64, limit int) ([]LedgerEntry, error) {
	return s.repo.ListEntriesKeyset(ctx, accountID, cursorID, limit)
}

// Transfer выполняет двойную запись, обновление балансов (в порядке ID против deadlock),
// запись в Outbox и фиксацию ключа идемпотентности в одной ACID-транзакции.
func (s *LedgerService) Transfer(ctx context.Context, req TransferRequest) (TransferResult, error) {
	if req.IdempotencyKey == "" || req.FromAccountID <= 0 || req.ToAccountID <= 0 ||
		req.FromAccountID == req.ToAccountID || req.Amount <= 0 || len(req.Currency) != 3 {
		return TransferResult{}, ErrInvalidTransfer
	}

	var result TransferResult
	err := s.txMgr.WithinTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted}, func(txRepo TxRepository) error {
		if existing, found, err := txRepo.GetIdempotency(ctx, req.IdempotencyKey); err != nil {
			return err
		} else if found {
			if err := json.Unmarshal([]byte(existing.ResponseBody), &result); err != nil {
				return err
			}
			result.Replayed = true
			return nil
		}

		fromAcc, err := txRepo.GetAccount(ctx, req.FromAccountID)
		if err != nil {
			return err
		}
		toAcc, err := txRepo.GetAccount(ctx, req.ToAccountID)
		if err != nil {
			return err
		}
		if fromAcc.Currency != req.Currency || toAcc.Currency != req.Currency {
			return ErrCurrencyMismatch
		}

		txID, err := txRepo.InsertTransaction(ctx, req.IdempotencyKey, "transfer", "posted", req.Description)
		if err != nil {
			return err
		}

		// Обновляем счета в детерминированном порядке ID для предотвращения взаимоблокировок (Deadlock)
		var fromBal, toBal int64
		if req.FromAccountID < req.ToAccountID {
			if fromBal, err = txRepo.UpdateAccountBalance(ctx, req.FromAccountID, -req.Amount); err != nil {
				return err
			}
			if toBal, err = txRepo.UpdateAccountBalance(ctx, req.ToAccountID, req.Amount); err != nil {
				return err
			}
		} else {
			if toBal, err = txRepo.UpdateAccountBalance(ctx, req.ToAccountID, req.Amount); err != nil {
				return err
			}
			if fromBal, err = txRepo.UpdateAccountBalance(ctx, req.FromAccountID, -req.Amount); err != nil {
				return err
			}
		}

		if _, err := txRepo.InsertEntry(ctx, txID, req.FromAccountID, -req.Amount, req.Currency); err != nil {
			return err
		}
		if _, err := txRepo.InsertEntry(ctx, txID, req.ToAccountID, req.Amount, req.Currency); err != nil {
			return err
		}

		res := TransferResult{
			TransactionID: txID,
			FromBalance:   fromBal,
			ToBalance:     toBal,
		}
		rawBody, err := json.Marshal(res)
		if err != nil {
			return err
		}

		if _, err := txRepo.InsertOutbox(ctx, "transaction", strconv.FormatInt(txID, 10), "TransferPosted", string(rawBody)); err != nil {
			return err
		}
		hash := sha256.Sum256([]byte(fmt.Sprintf("%d:%d:%d:%s", req.FromAccountID, req.ToAccountID, req.Amount, req.Currency)))
		if err := txRepo.InsertIdempotency(ctx, req.IdempotencyKey, hex.EncodeToString(hash[:]), txID, 200, string(rawBody)); err != nil {
			return err
		}

		result = res
		return nil
	})
	if err != nil {
		return TransferResult{}, err
	}

	if !result.Replayed {
		s.cache.Invalidate(fmt.Sprintf("acc:%d", req.FromAccountID))
		s.cache.Invalidate(fmt.Sprintf("acc:%d", req.ToAccountID))
		today := time.Now().UTC().Format("2006-01-02")
		s.olap.InsertBatch([]step07.OLAPEvent{
			{Day: today, Currency: req.Currency, AccountID: uint64(req.FromAccountID), Amount: -req.Amount},
			{Day: today, Currency: req.Currency, AccountID: uint64(req.ToAccountID), Amount: req.Amount},
		})
	}
	return result, nil
}

// RelayOutbox доставляет накопившиеся события и помечает их опубликованными.
func (s *LedgerService) RelayOutbox(ctx context.Context, batchSize int) (int, error) {
	events, err := s.repo.ListUnpublishedOutbox(ctx, batchSize)
	if err != nil {
		return 0, err
	}
	now := time.Now().UTC()
	for _, ev := range events {
		if err := s.repo.MarkOutboxPublished(ctx, ev.ID, now); err != nil {
			return 0, err
		}
	}
	return len(events), nil
}

func (s *LedgerService) OLAPTurnover(currency string) int64 {
	return s.olap.SumByCurrency(currency)
}
