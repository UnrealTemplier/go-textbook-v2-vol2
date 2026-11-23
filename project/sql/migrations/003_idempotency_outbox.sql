-- 003_idempotency_outbox.sql: Идемпотентность, Transactional Outbox и Row-Level Security

CREATE TABLE IF NOT EXISTS idempotency_keys (
    idempotency_key TEXT        PRIMARY KEY,
    request_hash    TEXT        NOT NULL,
    transaction_id  BIGINT      REFERENCES transactions(id) ON DELETE SET NULL,
    response_code   INT         NOT NULL,
    response_body   JSONB       NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_idempotency_expires_at
    ON idempotency_keys (expires_at);

CREATE TABLE IF NOT EXISTS outbox_events (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    aggregate_type TEXT        NOT NULL,
    aggregate_id   TEXT        NOT NULL,
    event_type     TEXT        NOT NULL,
    payload        JSONB       NOT NULL,
    published_at   TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Частичный индекс для фонового ретранслятора Outbox
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON outbox_events (created_at, id)
    WHERE published_at IS NULL;

-- Пример Row-Level Security (RLS) для изоляции тенантов в таблице счетов
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY accounts_tenant_isolation ON accounts
    USING (metadata ->> 'tenant_id' = current_setting('app.tenant_id', true));
