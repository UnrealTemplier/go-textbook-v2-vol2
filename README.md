# Том 2. Базы данных: от SQL и моделирования до движков и HighLoad

> Фундаментальный учебник по базам данных для Go-разработчика: реляционная модель, SQL с нуля, индексы и EXPLAIN, транзакции и ACID, движки PostgreSQL и MySQL/InnoDB, репликация, шардирование и NoSQL.

* **Серия:** `go-textbook-v2` (Том 2 из 7)
* **Входные требования:** Пройден Том 1 (Go, базовый HTTP-сервис, вводный DSA: деревья и хеш-таблицы).
* **Целевая версия Go:** `Go 1.22–1.24`
* **Движок:** `html-textbook-engine` (100% Offline-First, сборка в `dist/` для `file:///` и GitHub Pages)

## Сквозной проект тома (`project/`)

LedgerPulse — подсистема финансового учёта и аналитическая витрина (PostgreSQL, Redis, ClickHouse)

Запуск тестов проекта:
```bash
cd project && go test ./...
```

## Сборка и проверка локально

```bash
python3 -m pip install -r requirements.txt
python3 -m engine.build --all --strict
python3 -m engine.audit --strict --no-mermaid-runtime
```

Открыть локально: `xdg-open dist/index.html`.
