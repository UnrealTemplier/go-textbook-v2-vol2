package step02

import (
	"errors"
	"strings"
	"testing"
	"time"
)

func TestBuildEntriesQueryAndKeyset(t *testing.T) {
	minAmt := int64(100)
	curT := time.Date(2026, 5, 1, 12, 0, 0, 0, time.UTC)
	curID := int64(42)

	q, err := BuildEntriesQuery(EntryFilter{
		AccountID:  7,
		Currency:   "rub",
		MinAmount:  &minAmt,
		CursorTime: &curT,
		CursorID:   &curID,
		Limit:      25,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(q.SQL, "(created_at, id) < ($4, $5)") || !strings.Contains(q.SQL, "LIMIT $6") {
		t.Fatalf("unexpected SQL:\n%s", q.SQL)
	}
	if len(q.Args) != 6 || q.Args[1] != "RUB" || q.Args[5] != 25 {
		t.Fatalf("unexpected args: %#v", q.Args)
	}

	// Защита от SQL-инъекции через ORDER BY
	_, err = BuildEntriesQuery(EntryFilter{
		AccountID: 7,
		OrderBy:   "id; DROP TABLE accounts;--",
	})
	if !errors.Is(err, ErrInvalidSortColumn) {
		t.Fatalf("expected ErrInvalidSortColumn, got %v", err)
	}

	// Keyset-пагинация при одинаковых timestamp (разрешение через id)
	base := time.Date(2026, 5, 1, 10, 0, 0, 0, time.UTC)
	rows := []EntryRow{
		{ID: 1, AccountID: 7, Amount: 100, CreatedAt: base},
		{ID: 2, AccountID: 7, Amount: 200, CreatedAt: base},
		{ID: 3, AccountID: 7, Amount: 300, CreatedAt: base.Add(time.Minute)},
	}
	p1 := KeysetPage(rows, 7, nil, nil, 2)
	if len(p1) != 2 || p1[0].ID != 3 || p1[1].ID != 2 {
		t.Fatalf("unexpected page 1: %+v", p1)
	}
	p2 := KeysetPage(rows, 7, &p1[1].CreatedAt, &p1[1].ID, 2)
	if len(p2) != 1 || p2[0].ID != 1 {
		t.Fatalf("unexpected page 2: %+v", p2)
	}
}
