// Package step05 моделирует WAL (Write-Ahead Log) с CRC32 и восстановлением после сбоя,
// MVCC-версии кортежей (xmin/xmax), Snapshot Isolation с write-conflict и графовый детектор Deadlock.
package step05

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"hash/crc32"
	"os"
	"sync"
)

var (
	ErrWriteConflict = errors.New("could not serialize access due to concurrent update")
	ErrCorruptedWAL  = errors.New("wal checksum mismatch")
)

type walRecord struct {
	LSN   uint64 `json:"lsn"`
	TxID  uint64 `json:"tx"`
	Op    string `json:"op"` // "PUT", "COMMIT", "ABORT"
	Key   string `json:"key,omitempty"`
	Value int64  `json:"val,omitempty"`
	CRC   uint32 `json:"crc"`
}

func (r walRecord) checksum() uint32 {
	payload := fmt.Sprintf("%d|%d|%s|%s|%d", r.LSN, r.TxID, r.Op, r.Key, r.Value)
	return crc32.ChecksumIEEE([]byte(payload))
}

// WALStore записывает изменения сначала в append-only журнал с Sync(), и лишь затем меняет состояние.
type WALStore struct {
	mu      sync.Mutex
	walPath string
	nextLSN uint64
	state   map[string]int64
}

func OpenWALStore(walPath string) (*WALStore, error) {
	s := &WALStore{
		walPath: walPath,
		state:   make(map[string]int64),
	}
	if err := s.recover(); err != nil {
		return nil, err
	}
	return s, nil
}

func (s *WALStore) recover() error {
	f, err := os.Open(s.walPath)
	if errors.Is(err, os.ErrNotExist) {
		return nil
	}
	if err != nil {
		return err
	}
	defer f.Close()

	pending := make(map[uint64][]walRecord)
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := sc.Bytes()
		if len(line) == 0 {
			continue
		}
		var rec walRecord
		if err := json.Unmarshal(line, &rec); err != nil {
			// Оборванный хвост после сбоя питания отбрасываем при восстановлении
			break
		}
		if rec.CRC != rec.checksum() {
			return fmt.Errorf("%w at lsn=%d", ErrCorruptedWAL, rec.LSN)
		}
		s.nextLSN = max(s.nextLSN, rec.LSN)
		switch rec.Op {
		case "PUT":
			pending[rec.TxID] = append(pending[rec.TxID], rec)
		case "COMMIT":
			for _, w := range pending[rec.TxID] {
				s.state[w.Key] = w.Value
			}
			delete(pending, rec.TxID)
		case "ABORT":
			delete(pending, rec.TxID)
		}
	}
	return sc.Err()
}

func (s *WALStore) appendAndSync(recs ...walRecord) error {
	f, err := os.OpenFile(s.walPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o600)
	if err != nil {
		return err
	}
	defer f.Close()

	for i := range recs {
		s.nextLSN++
		recs[i].LSN = s.nextLSN
		recs[i].CRC = recs[i].checksum()
		line, err := json.Marshal(recs[i])
		if err != nil {
			return err
		}
		if _, err := f.Write(append(line, '\n')); err != nil {
			return err
		}
	}
	return f.Sync()
}

func (s *WALStore) ApplyCommitted(txID uint64, writes map[string]int64) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	var recs []walRecord
	for k, v := range writes {
		recs = append(recs, walRecord{TxID: txID, Op: "PUT", Key: k, Value: v})
	}
	recs = append(recs, walRecord{TxID: txID, Op: "COMMIT"})
	if err := s.appendAndSync(recs...); err != nil {
		return err
	}
	for k, v := range writes {
		s.state[k] = v
	}
	return nil
}

func (s *WALStore) WriteUncommitted(txID uint64, key string, val int64) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.appendAndSync(walRecord{TxID: txID, Op: "PUT", Key: key, Value: val})
}

func (s *WALStore) Get(key string) (int64, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	v, ok := s.state[key]
	return v, ok
}

// TupleVersion описывает одну физическую версию строки в MVCC.
type TupleVersion struct {
	Xmin  uint64
	Xmax  uint64 // 0 означает актуальную версию
	Value int64
}

// MVCCEngine реализует снимки (Snapshot Isolation) и First-Committer-Wins.
type MVCCEngine struct {
	mu        sync.Mutex
	nextXID   uint64
	committed map[uint64]bool
	versions  map[string][]TupleVersion
}

type SnapshotTx struct {
	XID       uint64
	Snapshot  map[uint64]bool // закоммиченные на момент старта транзакции
	writeset  map[string]int64
	readXmax  map[string]uint64
	engine    *MVCCEngine
	finished  bool
}

func NewMVCCEngine() *MVCCEngine {
	return &MVCCEngine{
		nextXID:   1,
		committed: make(map[uint64]bool),
		versions:  make(map[string][]TupleVersion),
	}
}

func (e *MVCCEngine) Begin() *SnapshotTx {
	e.mu.Lock()
	defer e.mu.Unlock()

	xid := e.nextXID
	e.nextXID++
	snap := make(map[uint64]bool, len(e.committed))
	for k, v := range e.committed {
		snap[k] = v
	}
	return &SnapshotTx{
		XID:      xid,
		Snapshot: snap,
		writeset: make(map[string]int64),
		readXmax: make(map[string]uint64),
		engine:   e,
	}
}

func (tx *SnapshotTx) Get(key string) (int64, bool) {
	if v, ok := tx.writeset[key]; ok {
		return v, true
	}
	tx.engine.mu.Lock()
	defer tx.engine.mu.Unlock()

	vers := tx.engine.versions[key]
	for i := len(vers) - 1; i >= 0; i-- {
		v := vers[i]
		if !tx.Snapshot[v.Xmin] {
			continue
		}
		if v.Xmax != 0 && tx.Snapshot[v.Xmax] {
			continue
		}
		return v.Value, true
	}
	return 0, false
}

func (tx *SnapshotTx) Set(key string, val int64) {
	tx.writeset[key] = val
}

func (tx *SnapshotTx) Commit() error {
	if tx.finished {
		return errors.New("tx already finished")
	}
	tx.engine.mu.Lock()
	defer tx.engine.mu.Unlock()
	tx.finished = true

	// Проверка First-Committer-Wins: никто вне нашего снимка не успел обновить те же ключи
	for k := range tx.writeset {
		vers := tx.engine.versions[k]
		for _, v := range vers {
			if tx.engine.committed[v.Xmin] && !tx.Snapshot[v.Xmin] && v.Xmin != tx.XID {
				return ErrWriteConflict
			}
		}
	}

	for k, val := range tx.writeset {
		vers := tx.engine.versions[k]
		for i := len(vers) - 1; i >= 0; i-- {
			if tx.Snapshot[vers[i].Xmin] && vers[i].Xmax == 0 {
				vers[i].Xmax = tx.XID
				break
			}
		}
		vers = append(vers, TupleVersion{Xmin: tx.XID, Value: val})
		tx.engine.versions[k] = vers
	}
	tx.engine.committed[tx.XID] = true
	return nil
}

// HasDeadlockCycle проверяет граф ожиданий (wait-for graph) на цикл через DFS.
func HasDeadlockCycle(waits map[uint64][]uint64) bool {
	const (
		unvisited = 0
		visiting  = 1
		visited   = 2
	)
	state := make(map[uint64]int)
	var dfs func(u uint64) bool
	dfs = func(u uint64) bool {
		state[u] = visiting
		for _, v := range waits[u] {
			if state[v] == visiting {
				return true
			}
			if state[v] == unvisited && dfs(v) {
				return true
			}
		}
		state[u] = visited
		return false
	}
	for u := range waits {
		if state[u] == unvisited && dfs(u) {
			return true
		}
	}
	return false
}
