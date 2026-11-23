package final

import (
	"database/sql"
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"github.com/UnrealTemplier/go-textbook-v2-vol2/project/final/ledgerdriver"
)

type Server struct {
	svc *LedgerService
	db  *sql.DB
	mux *http.ServeMux
}

func NewServer(db *sql.DB, svc *LedgerService) *Server {
	s := &Server{
		svc: svc,
		db:  db,
		mux: http.NewServeMux(),
	}
	s.mux.HandleFunc("GET /healthz", s.handleHealth)
	s.mux.HandleFunc("GET /metrics/db", s.handleDBStats)
	s.mux.HandleFunc("POST /api/v1/accounts", s.handleCreateAccount)
	s.mux.HandleFunc("GET /api/v1/accounts/{id}", s.handleGetAccount)
	s.mux.HandleFunc("GET /api/v1/accounts/{id}/entries", s.handleListEntries)
	s.mux.HandleFunc("POST /api/v1/transfers", s.handleTransfer)
	return s
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.mux.ServeHTTP(w, r)
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	if err := s.db.PingContext(r.Context()); err != nil {
		writeJSONError(w, http.StatusServiceUnavailable, err.Error())
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func (s *Server) handleDBStats(w http.ResponseWriter, _ *http.Request) {
	st := s.db.Stats()
	writeJSON(w, http.StatusOK, map[string]any{
		"max_open_connections": st.MaxOpenConnections,
		"open_connections":     st.OpenConnections,
		"in_use":               st.InUse,
		"idle":                 st.Idle,
		"wait_count":           st.WaitCount,
	})
}

func (s *Server) handleCreateAccount(w http.ResponseWriter, r *http.Request) {
	var in struct {
		ExternalID string `json:"external_id"`
		OwnerName  string `json:"owner_name"`
		Currency   string `json:"currency"`
		Balance    int64  `json:"balance"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&in); err != nil {
		writeJSONError(w, http.StatusBadRequest, "invalid json")
		return
	}
	acc, err := s.svc.CreateAccount(r.Context(), in.ExternalID, in.OwnerName, in.Currency, in.Balance)
	if err != nil {
		writeDomainError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, acc)
}

func (s *Server) handleGetAccount(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil || id <= 0 {
		writeJSONError(w, http.StatusBadRequest, "invalid account id")
		return
	}
	acc, err := s.svc.GetAccount(r.Context(), id)
	if err != nil {
		writeDomainError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, acc)
}

func (s *Server) handleListEntries(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil || id <= 0 {
		writeJSONError(w, http.StatusBadRequest, "invalid account id")
		return
	}
	var cursorID int64
	if raw := r.URL.Query().Get("cursor_id"); raw != "" {
		cursorID, _ = strconv.ParseInt(raw, 10, 64)
	}
	limit := 50
	if raw := r.URL.Query().Get("limit"); raw != "" {
		if n, err := strconv.Atoi(raw); err == nil && n > 0 {
			limit = n
		}
	}
	entries, err := s.svc.ListEntries(r.Context(), id, cursorID, limit)
	if err != nil {
		writeDomainError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"items": entries})
}

func (s *Server) handleTransfer(w http.ResponseWriter, r *http.Request) {
	var req TransferRequest
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&req); err != nil {
		writeJSONError(w, http.StatusBadRequest, "invalid json")
		return
	}
	res, err := s.svc.Transfer(r.Context(), req)
	if err != nil {
		writeDomainError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, res)
}

func writeDomainError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, ErrNotFound), errors.Is(err, ledgerdriver.ErrAccountNotFound):
		writeJSONError(w, http.StatusNotFound, err.Error())
	case errors.Is(err, ErrInvalidTransfer), errors.Is(err, ErrCurrencyMismatch), errors.Is(err, ledgerdriver.ErrInsufficientFunds):
		writeJSONError(w, http.StatusUnprocessableEntity, err.Error())
	case errors.Is(err, ledgerdriver.ErrDuplicateKey):
		writeJSONError(w, http.StatusConflict, err.Error())
	default:
		writeJSONError(w, http.StatusInternalServerError, err.Error())
	}
}

func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func writeJSONError(w http.ResponseWriter, code int, msg string) {
	writeJSON(w, code, map[string]string{"error": msg})
}
