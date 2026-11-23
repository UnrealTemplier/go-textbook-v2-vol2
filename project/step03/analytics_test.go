package step03

import (
	"strings"
	"testing"
	"time"
)

func TestComputeAccountWindow(t *testing.T) {
	t0 := time.Date(2026, 5, 1, 9, 0, 0, 0, time.UTC)
	entries := []Entry{
		{ID: 1, AccountID: 10, Amount: 500, CreatedAt: t0},
		{ID: 2, AccountID: 10, Amount: 500, CreatedAt: t0.Add(time.Hour)},
		{ID: 3, AccountID: 10, Amount: 200, CreatedAt: t0.Add(2 * time.Hour)},
		{ID: 4, AccountID: 10, Amount: 800, CreatedAt: t0.Add(3 * time.Hour)},
	}

	res := ComputeAccountWindow(entries)
	if len(res) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(res))
	}
	// Проверяем нарастающий итог и скользящее среднее 3 последних строк
	if res[3].RowNumber != 4 || res[3].RunningSum != 2000 {
		t.Fatalf("unexpected row 4 stats: %+v", res[3])
	}
	if res[3].MovingAvg3 != 500 {
		t.Fatalf("expected moving avg (500+200+800)/3 = 500, got %v", res[3].MovingAvg3)
	}
	if res[0].PrevAmount != nil || *res[1].PrevAmount != 500 {
		t.Fatalf("unexpected LAG values")
	}
	// По сумме: 800 (rank 1, dense 1), 500 (rank 2, dense 2), 500 (rank 2, dense 2), 200 (rank 4, dense 3)
	if res[2].Rank != 4 || res[2].DenseRank != 3 {
		t.Fatalf("expected rank=4, dense_rank=3 for 200; got rank=%d dense=%d", res[2].Rank, res[2].DenseRank)
	}
	if !strings.Contains(DailySummarySQL, "OVER (PARTITION BY account_id ORDER BY day)") {
		t.Fatalf("missing window clause in DailySummarySQL")
	}
}
