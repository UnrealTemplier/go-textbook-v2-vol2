-- 001_ledger_events.sql: Аналитическая витрина LedgerPulse в ClickHouse (OLAP)

CREATE DATABASE IF NOT EXISTS ledgerpulse;

CREATE TABLE IF NOT EXISTS ledgerpulse.ledger_events
(
    event_date     Date,
    created_at     DateTime64(3, 'UTC'),
    transaction_id UInt64,
    account_id     UInt64,
    currency       LowCardinality(FixedString(3)),
    kind           LowCardinality(String),
    amount_minor   Int64,
    is_credit      UInt8
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (currency, account_id, created_at, transaction_id)
SETTINGS index_granularity = 8192;

-- Дневная агрегированная витрина оборотов (SummingMergeTree + Materialized View)
CREATE TABLE IF NOT EXISTS ledgerpulse.daily_turnover
(
    event_date   Date,
    currency     LowCardinality(FixedString(3)),
    account_id   UInt64,
    total_volume UInt64,
    net_delta    Int64,
    tx_count     UInt64
)
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, currency, account_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS ledgerpulse.mv_daily_turnover
TO ledgerpulse.daily_turnover
AS
SELECT
    event_date,
    currency,
    account_id,
    sum(abs(amount_minor)) AS total_volume,
    sum(amount_minor)      AS net_delta,
    count()                AS tx_count
FROM ledgerpulse.ledger_events
GROUP BY event_date, currency, account_id;
