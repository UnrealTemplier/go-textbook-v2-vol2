// Package step02 реализует параметризованный конструктор SQL-запросов ($1, $2),
// keyset-пагинацию против OFFSET и белый список столбцов сортировки для защиты от SQL-инъекций.
package step02

import (
	"errors"
	"fmt"
	"slices"
	"strings"
	"time"
)

var ErrInvalidSortColumn = errors.New("sort column is not in allowlist")

// EntryFilter описывает фильтрацию проводок LedgerPulse и keyset-курсор.
type EntryFilter struct {
	AccountID  int64
	Currency   string
	MinAmount  *int64
	CursorTime *time.Time
	CursorID   *int64
	Limit      int
	OrderBy    string
}

type BuiltQuery struct {
	SQL  string
	Args []any
}

var allowedOrderColumns = []string{"created_at", "id", "amount"}

// BuildEntriesQuery строит безопасный параметризованный запрос с keyset-пагинацией (created_at, id) < ($k, $k+1).
func BuildEntriesQuery(f EntryFilter) (BuiltQuery, error) {
	if f.AccountID <= 0 {
		return BuiltQuery{}, errors.New("account_id must be positive")
	}
	limit := f.Limit
	if limit <= 0 || limit > 200 {
		limit = 50
	}
	orderCol := "created_at"
	if f.OrderBy != "" {
		if !slices.Contains(allowedOrderColumns, f.OrderBy) {
			return BuiltQuery{}, fmt.Errorf("%w: %q", ErrInvalidSortColumn, f.OrderBy)
		}
		orderCol = f.OrderBy
	}

	var where []string
	var args []any
	addArg := func(v any) string {
		args = append(args, v)
		return fmt.Sprintf("$%d", len(args))
	}

	where = append(where, "account_id = "+addArg(f.AccountID))
	if f.Currency != "" {
		where = append(where, "currency = "+addArg(strings.ToUpper(f.Currency)))
	}
	if f.MinAmount != nil {
		where = append(where, "amount >= "+addArg(*f.MinAmount))
	}
	if f.CursorTime != nil && f.CursorID != nil {
		pTime := addArg(*f.CursorTime)
		pID := addArg(*f.CursorID)
		where = append(where, fmt.Sprintf("(created_at, id) < (%s, %s)", pTime, pID))
	}

	pLimit := addArg(limit)
	query := fmt.Sprintf(
		"SELECT id, transaction_id, account_id, amount, currency, created_at\n"+
			"FROM ledger_entries\n"+
			"WHERE %s\n"+
			"ORDER BY %s DESC, id DESC\n"+
			"LIMIT %s",
		strings.Join(where, " AND "),
		orderCol,
		pLimit,
	)

	return BuiltQuery{SQL: query, Args: args}, nil
}

// EntryRow представляет строку для локальной демонстрации keyset-пагинации без OFFSET.
type EntryRow struct {
	ID        int64
	AccountID int64
	Amount    int64
	CreatedAt time.Time
}

// KeysetPage возвращает срез строк после курсора (created_at, id) без деградации при глубокой пагинации.
func KeysetPage(rows []EntryRow, accountID int64, cursorTime *time.Time, cursorID *int64, limit int) []EntryRow {
	var filtered []EntryRow
	for _, r := range rows {
		if r.AccountID != accountID {
			continue
		}
		if cursorTime != nil && cursorID != nil {
			if r.CreatedAt.After(*cursorTime) {
				continue
			}
			if r.CreatedAt.Equal(*cursorTime) && r.ID >= *cursorID {
				continue
			}
		}
		filtered = append(filtered, r)
	}
	slices.SortFunc(filtered, func(a, b EntryRow) int {
		if a.CreatedAt.After(b.CreatedAt) {
			return -1
		}
		if a.CreatedAt.Before(b.CreatedAt) {
			return 1
		}
		return int(b.ID - a.ID)
	})
	if limit > 0 && len(filtered) > limit {
		return filtered[:limit]
	}
	return filtered
}
