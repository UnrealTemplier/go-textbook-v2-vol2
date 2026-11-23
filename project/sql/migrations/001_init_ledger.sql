-- 001_init_ledger.sql: Базовая реляционная схема LedgerPulse (PostgreSQL 17)
-- Все денежные суммы хранятся в минимальных неделимых единицах (копейки/центы) в BIGINT.

CREATE TABLE IF NOT EXISTS accounts (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_id TEXT        NOT NULL UNIQUE,
    owner_name  TEXT        NOT NULL,
    currency    CHAR(3)     NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    balance     BIGINT      NOT NULL DEFAULT 0 CHECK (balance >= 0),
    status      TEXT        NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'frozen', 'closed')),
    metadata    JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transactions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reference_id    TEXT        NOT NULL UNIQUE,
    kind            TEXT        NOT NULL CHECK (kind IN ('transfer', 'deposit', 'withdrawal', 'fee')),
    status          TEXT        NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'posted', 'failed', 'reversed')),
    description     TEXT        NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id BIGINT      NOT NULL REFERENCES transactions(id) ON DELETE RESTRICT,
    account_id     BIGINT      NOT NULL REFERENCES accounts(id)     ON DELETE RESTRICT,
    amount         BIGINT      NOT NULL CHECK (amount <> 0), -- >0 дебет/пополнение, <0 кредит/списание
    currency       CHAR(3)     NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
