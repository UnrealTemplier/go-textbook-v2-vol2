package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/UnrealTemplier/go-textbook-v2-vol2/project/final"
	"github.com/UnrealTemplier/go-textbook-v2-vol2/project/final/ledgerdriver"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	inst := ledgerdriver.NewInstance()
	db := inst.OpenDB()
	defer db.Close()

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(10)
	db.SetConnMaxLifetime(30 * time.Minute)
	db.SetConnMaxIdleTime(5 * time.Minute)

	svc := final.NewLedgerService(db)
	api := final.NewServer(db, svc)

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           api,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      15 * time.Second,
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	go func() {
		logger.Info("ledgerpulse listening", "addr", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("server failed", "err", err)
			os.Exit(1)
		}
	}()

	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
	logger.Info("ledgerpulse stopped")
}
