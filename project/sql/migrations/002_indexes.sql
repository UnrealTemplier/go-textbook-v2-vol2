-- 002_indexes.sql: Индексы под ключевые запросы LedgerPulse и планы EXPLAIN ANALYZE

-- Составной покрывающий индекс для keyset-пагинации ленты проводок по счёту без обращения к Heap
CREATE INDEX IF NOT EXISTS idx_ledger_entries_account_created
    ON ledger_entries (account_id, created_at DESC, id DESC)
    INCLUDE (amount, currency, transaction_id);

-- Частичный индекс: быстрый поиск только незавершённых транзакций (экономит память и кэш)
CREATE INDEX IF NOT EXISTS idx_transactions_pending
    ON transactions (created_at)
    WHERE status = 'pending';

-- Составной индекс для поиска счетов клиента в разрезе валюты
CREATE INDEX IF NOT EXISTS idx_accounts_status_currency
    ON accounts (status, currency)
    WHERE status = 'active';

-- GIN-индекс для фильтрации по JSONB-метаданным счетов (например, тариф или регион)
CREATE INDEX IF NOT EXISTS idx_accounts_metadata_gin
    ON accounts USING GIN (metadata jsonb_path_ops);
