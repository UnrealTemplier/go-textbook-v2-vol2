# Сквозной проект · Том 2 · `LedgerPulse`

**Проект:** `LedgerPulse` — подсистема финансового учёта с двойной записью, транзакционной идемпотентностью, Outbox, кэшированием и аналитической витриной (PostgreSQL, Valkey/Redis, ClickHouse).  
**Целевая версия Go:** `Go 1.24` *(0 внешних зависимостей — автономные тесты работают под `go test -race ./...` без запущенного Docker; рядом лежат реальные SQL-миграции PostgreSQL, ClickHouse DDL и `docker-compose.yml`)*.

## Карта шагов

| Каталог / файл | Модуль Тома 2 | Что добавляется на этом шаге |
|---|---|---|
| `sql/migrations/` | Модули 1, 4, 10 | Реальные PostgreSQL DDL: таблицы (`001`), составные/покрывающие/частичные/GIN индексы (`002`), идемпотентность, Outbox и RLS (`003`) |
| `sql/clickhouse/` | Модуль 9 | Схема OLAP-витрины ClickHouse (`MergeTree`, `SummingMergeTree`, `Materialized View`) |
| `docker-compose.yml` | Модули 6, 9, 10 | Локальный стенд: PostgreSQL 17, Valkey 8 и ClickHouse 24 |
| `step01/` | Модуль 1 | Домен `Money`, двойная запись (инвариант суммы = 0), проверка `NOT NULL`, `UNIQUE`, `CHECK`, `FK` |
| `step02/` | Модуль 2 | Параметризованный SQL-конструктор (`$1, $2`), keyset-пагинация против `OFFSET`, allowlist сортировки |
| `step03/` | Модуль 3 | Оконные функции (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, нарастающий итог, скользящее среднее) |
| `step04/` | Модуль 4 | Учебный `BPlusTree` с `page split` и диапазонным сканом по листьям + симулятор стоимостного планировщика (`EXPLAIN`) |
| `step05/` | Модуль 5 | Append-only WAL с CRC32 и `Crash Recovery`, MVCC (`xmin`/`xmax`) с `Snapshot Isolation` и детектор `Deadlock` |
| `step06/` | Модуль 8 | Кольцо консистентного хеширования (`ShardRouter`), маршрутизация `Read-Your-Writes` и `FencedStorage` |
| `step07/` | Модуль 9 | Cache-Aside с TTL+jitter и `Singleflight` против Cache Stampede + колоночная модель `MergeTree` |
| `final/` | Модуль 10 | Полноценный сервис поверх `database/sql` + собственный `ledgerdriver`, `TxManager`, идемпотентность, Outbox, `/metrics/db` |

## Проверка и запуск

Запуск всех тестов под детектором гонок:
```bash
go test -race ./...
```

Поднятие инфраструктуры PostgreSQL 17 + Valkey 8 + ClickHouse 24:
```bash
docker compose up -d
```

Запуск локального HTTP-сервиса:
```bash
go run ./final/cmd/ledgerpulse
```
