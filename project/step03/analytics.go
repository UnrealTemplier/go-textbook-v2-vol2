// Package step03 моделирует оконные функции SQL (ROW_NUMBER, RANK, DENSE_RANK, LAG,
// нарастающий итог, скользящее окно) и SQL-представление дневной аналитики LedgerPulse.
package step03

import (
	"slices"
	"time"
)

type Entry struct {
	ID        int64
	AccountID int64
	Amount    int64
	CreatedAt time.Time
}

type WindowedEntry struct {
	Entry
	RowNumber  int
	Rank       int
	DenseRank  int
	PrevAmount *int64
	RunningSum int64
	MovingAvg3 float64
}

// ComputeAccountWindow воспроизводит поведение OVER (PARTITION BY account_id ORDER BY created_at, id)
// и ранжирование по величине |amount| внутри каждого счёта.
func ComputeAccountWindow(entries []Entry) []WindowedEntry {
	byAcc := make(map[int64][]Entry)
	for _, e := range entries {
		byAcc[e.AccountID] = append(byAcc[e.AccountID], e)
	}

	var accIDs []int64
	for id := range byAcc {
		accIDs = append(accIDs, id)
	}
	slices.Sort(accIDs)

	var out []WindowedEntry
	for _, accID := range accIDs {
		list := slices.Clone(byAcc[accID])
		slices.SortFunc(list, func(a, b Entry) int {
			if a.CreatedAt.Before(b.CreatedAt) {
				return -1
			}
			if a.CreatedAt.After(b.CreatedAt) {
				return 1
			}
			return int(a.ID - b.ID)
		})

		// Предвычислим RANK и DENSE_RANK по amount DESC внутри партиции
		byAmount := slices.Clone(list)
		slices.SortFunc(byAmount, func(a, b Entry) int {
			if a.Amount > b.Amount {
				return -1
			}
			if a.Amount < b.Amount {
				return 1
			}
			return int(a.ID - b.ID)
		})
		rankByID := make(map[int64]int)
		denseByID := make(map[int64]int)
		curDense := 0
		for i, e := range byAmount {
			if i == 0 || e.Amount != byAmount[i-1].Amount {
				rankByID[e.ID] = i + 1
				curDense++
			} else {
				rankByID[e.ID] = rankByID[byAmount[i-1].ID]
			}
			denseByID[e.ID] = curDense
		}

		var running int64
		for i, e := range list {
			running += e.Amount
			var prev *int64
			if i > 0 {
				v := list[i-1].Amount
				prev = &v
			}
			start := max(0, i-2)
			var winSum int64
			for j := start; j <= i; j++ {
				winSum += list[j].Amount
			}
			out = append(out, WindowedEntry{
				Entry:      e,
				RowNumber:  i + 1,
				Rank:       rankByID[e.ID],
				DenseRank:  denseByID[e.ID],
				PrevAmount: prev,
				RunningSum: running,
				MovingAvg3: float64(winSum) / float64(i-start+1),
			})
		}
	}
	return out
}

// DailySummarySQL возвращает эталонный SQL с CTE и оконными функциями для PostgreSQL.
const DailySummarySQL = `WITH daily AS (
    SELECT
        account_id,
        date_trunc('day', created_at) AS day,
        SUM(amount) AS net_delta,
        COUNT(*) FILTER (WHERE amount > 0) AS incoming_cnt
    FROM ledger_entries
    GROUP BY account_id, date_trunc('day', created_at)
)
SELECT
    account_id,
    day,
    net_delta,
    SUM(net_delta) OVER (PARTITION BY account_id ORDER BY day) AS running_balance,
    LAG(net_delta) OVER (PARTITION BY account_id ORDER BY day) AS prev_day_delta
FROM daily
ORDER BY account_id, day;`
