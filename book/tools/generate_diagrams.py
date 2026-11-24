#!/usr/bin/env python3
"""
book/tools/generate_diagrams.py
Генерация 35 точных технических SVG-схем Тома 2 в едином стиле инженерного чертежа
(светлый фон #fcfaf5, тёмный контур #1e293b, акценты #0369a1 и #c2410c, invert_dark = true,
license = "own") и обновление соответствующих media/credits.toml.
"""

import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from book.tools.commons_fetch import credits_block, write_credits  # noqa: E402
from engine.media import image_size, load_credits  # noqa: E402


def wrap_svg(w: int, h: int, title: str, subtitle: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#e2e8f0" stroke-width="0.7"/>
    </pattern>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1e293b"/>
    </marker>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0369a1"/>
    </marker>
    <marker id="arrowOrange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c2410c"/>
    </marker>
  </defs>
  <style>
    .bg {{ fill: #fcfaf5; }}
    .frame {{ fill: none; stroke: #1e293b; stroke-width: 2; }}
    .box {{ fill: #ffffff; stroke: #1e293b; stroke-width: 1.8; }}
    .box-accent {{ fill: #f0f9ff; stroke: #0369a1; stroke-width: 2; }}
    .box-warm {{ fill: #fff7ed; stroke: #c2410c; stroke-width: 2; }}
    .box-dark {{ fill: #f1f5f9; stroke: #334155; stroke-width: 1.8; }}
    .line {{ fill: none; stroke: #1e293b; stroke-width: 2; }}
    .line-blue {{ fill: none; stroke: #0369a1; stroke-width: 2.2; }}
    .line-orange {{ fill: none; stroke: #c2410c; stroke-width: 2.2; }}
    .line-dash {{ fill: none; stroke: #64748b; stroke-width: 1.6; stroke-dasharray: 6 4; }}
    .h1 {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 19px; font-weight: 700; fill: #0f172a; }}
    .sub {{ font-family: "Inter", "IBM Plex Sans", sans-serif; font-size: 13.5px; fill: #334155; }}
    .mono {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 13px; fill: #0f172a; }}
    .mono-sm {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 11.5px; fill: #334155; }}
    .mono-bold {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 13.5px; font-weight: 700; fill: #0f172a; }}
    .mono-blue {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 13.5px; font-weight: 700; fill: #0369a1; }}
    .mono-orange {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 13.5px; font-weight: 700; fill: #c2410c; }}
    .label {{ font-family: "Inter", "IBM Plex Sans", sans-serif; font-size: 12.5px; fill: #475569; }}
  </style>
  <rect width="{w}" height="{h}" class="bg"/>
  <rect x="16" y="16" width="{w - 32}" height="{h - 32}" fill="url(#grid)"/>
  <rect x="16" y="16" width="{w - 32}" height="{h - 32}" class="frame"/>
  <rect x="16" y="16" width="{w - 32}" height="58" fill="#f8fafc" stroke="#1e293b" stroke-width="1.6"/>
  <rect x="16" y="16" width="8" height="58" fill="#0369a1"/>
  <text x="38" y="42" class="h1">{title}</text>
  <text x="38" y="63" class="sub">{subtitle}</text>
{body}
</svg>
'''


DIAGRAMS = [
    # --- МОДУЛЬ 1 (3 схемы) ---
    {
        "dir": "sources/1. Фундамент баз данных и моделирование",
        "filename": "object-graph-vs-relational-sets.svg",
        "w": 1040, "h": 460,
        "title": "ОБЪЕКТНЫЙ ГРАФ В ПАМЯТИ ПРОТИВ РЕЛЯЦИОННЫХ МНОЖЕСТВ НА ДИСКЕ",
        "subtitle": "Почему навигация по указателям в ORM порождает N+1, а реляционная алгебра работает с множествами за 1 проход",
        "caption": "Сравнение объектного графа (навигация по ссылкам) и реляционных таблиц (множества кортежей в 8-КБ страницах)",
        "alt": "Сравнение объектного графа в памяти приложения и реляционных таблиц с внешними ключами в СУБД",
        "body": '''
  <rect x="38" y="92" width="465" height="334" rx="6" class="box"/>
  <text x="270" y="118" text-anchor="middle" class="mono-orange">ООП-ГРАФ В ПАМЯТИ (IMPEDANCE MISMATCH)</text>
  <rect x="70" y="142" width="175" height="64" class="box-warm"/>
  <text x="157" y="167" text-anchor="middle" class="mono-bold">User { ID: 7 }</text>
  <text x="157" y="188" text-anchor="middle" class="label">Orders: []*Order</text>
  <line x1="245" y1="165" x2="310" y2="148" class="line-orange" marker-end="url(#arrowOrange)"/>
  <line x1="245" y1="185" x2="310" y2="218" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="313" y="128" width="160" height="50" class="box-dark"/>
  <text x="393" y="158" text-anchor="middle" class="mono">Order #101</text>
  <rect x="313" y="196" width="160" height="50" class="box-dark"/>
  <text x="393" y="226" text-anchor="middle" class="mono">Order #102</text>
  <rect x="70" y="274" width="403" height="128" class="box-warm"/>
  <text x="90" y="302" class="mono-orange">Цена наивного ORM-подхода:</text>
  <text x="90" y="326" class="label">1. Цикл по указателям превращается в N+1 SQL-запросов по сети</text>
  <text x="90" y="348" class="label">2. Чтение целых объектов тянет лишние столбцы (SELECT *)</text>
  <text x="90" y="370" class="label">3. Размывается граница транзакций и блокировок в БД</text>

  <rect x="535" y="92" width="467" height="334" rx="6" class="box-accent"/>
  <text x="768" y="118" text-anchor="middle" class="mono-blue">РЕЛЯЦИОННЫЕ МНОЖЕСТВА (8 КБ СТРАНИЦЫ)</text>
  <rect x="560" y="142" width="195" height="104" class="box"/>
  <text x="657" y="166" text-anchor="middle" class="mono-blue">Relation: accounts</text>
  <text x="575" y="192" class="mono-sm">id=7 | Alice | RUB</text>
  <text x="575" y="214" class="mono-sm">id=8 | Bob   | RUB</text>
  <rect x="780" y="142" width="198" height="104" class="box"/>
  <text x="879" y="166" text-anchor="middle" class="mono-blue">Relation: entries</text>
  <text x="795" y="192" class="mono-sm">acc=7 | -3000</text>
  <text x="795" y="214" class="mono-sm">acc=8 | +3000</text>
  <line x1="755" y1="194" x2="778" y2="194" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="560" y="274" width="418" height="128" class="box"/>
  <text x="580" y="302" class="mono-blue">Преимущество работы с множествами:</text>
  <text x="580" y="326" class="label">1. Декларативный JOIN + агрегация за 1 сетевой вызов</text>
  <text x="580" y="348" class="label">2. Buffer Pool держит горячие 8-КБ страницы в RAM (~100 нс)</text>
  <text x="580" y="370" class="label">3. Замкнутость алгебры: результат запроса — новая таблица</text>
'''
    },
    {
        "dir": "sources/1. Фундамент баз данных и моделирование",
        "filename": "normalization-1nf-2nf-3nf.svg",
        "w": 1040, "h": 460,
        "title": "СТУПЕНИ НОРМАЛИЗАЦИИ: ОТ ХАОСА 0NF К ЧИСТОЙ 3NF",
        "subtitle": "Последовательное устранение списков в полях, частичных зависимостей от составного ключа и транзитивных связей",
        "caption": "Эволюция таблицы от 0NF/1NF к 2NF и 3NF с устранением аномалий вставки, обновления и удаления",
        "alt": "Схема перехода таблицы через первую, вторую и третью нормальные формы",
        "body": '''
  <rect x="38" y="96" width="225" height="320" rx="6" class="box-warm"/>
  <text x="150" y="124" text-anchor="middle" class="mono-orange">0NF (Аномалии)</text>
  <text x="55" y="156" class="mono-sm">order_id = 10</text>
  <text x="55" y="178" class="mono-sm">items = "A, B, C"</text>
  <text x="55" y="200" class="mono-sm">city = "Москва"</text>
  <text x="55" y="222" class="mono-sm">zip = "101000"</text>
  <line x1="55" y1="248" x2="245" y2="248" stroke="#cbd5e1"/>
  <text x="55" y="276" class="label">Нельзя индексировать</text>
  <text x="55" y="296" class="label">элемент списка; правка</text>
  <text x="55" y="316" class="label">города бьёт десятки строк</text>

  <line x1="263" y1="256" x2="293" y2="256" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="296" y="96" width="225" height="320" rx="6" class="box-dark"/>
  <text x="408" y="124" text-anchor="middle" class="mono-bold">1NF (Атомарность)</text>
  <text x="312" y="156" class="mono-sm">PK: (order_id, item_id)</text>
  <text x="312" y="182" class="mono-sm">order_date (зависит</text>
  <text x="312" y="202" class="mono-sm">  только от order_id!)</text>
  <text x="312" y="228" class="mono-sm">city → zip</text>
  <line x1="312" y1="248" x2="505" y2="248" stroke="#cbd5e1"/>
  <text x="312" y="276" class="label">Убрали списки в ячейке,</text>
  <text x="312" y="296" class="label">но order_date дублируется</text>
  <text x="312" y="316" class="label">в каждой позиции заказа</text>

  <line x1="521" y1="256" x2="551" y2="256" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="554" y="96" width="225" height="320" rx="6" class="box"/>
  <text x="666" y="124" text-anchor="middle" class="mono-blue">2NF (Полный ключ)</text>
  <text x="570" y="156" class="mono-sm">orders(id, date, city, zip)</text>
  <text x="570" y="182" class="mono-sm">order_items(order_id,</text>
  <text x="570" y="202" class="mono-sm">  item_id, qty)</text>
  <line x1="570" y1="248" x2="762" y2="248" stroke="#cbd5e1"/>
  <text x="570" y="276" class="label">Частичные зависимости</text>
  <text x="570" y="296" class="label">вынесены; осталась связь</text>
  <text x="570" y="316" class="label">city → zip не через ключ</text>

  <line x1="779" y1="256" x2="809" y2="256" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="812" y="96" width="190" height="320" rx="6" class="box-accent"/>
  <text x="907" y="124" text-anchor="middle" class="mono-blue">3NF (Только ключ)</text>
  <text x="826" y="156" class="mono-sm">orders(id, date, zip)</text>
  <text x="826" y="184" class="mono-sm">order_items(...)</text>
  <text x="826" y="212" class="mono-sm">cities(zip PK, city)</text>
  <line x1="826" y1="248" x2="988" y2="248" stroke="#cbd5e1"/>
  <text x="826" y="276" class="label">Каждый неключевой</text>
  <text x="826" y="296" class="label">атрибут зависит</text>
  <text x="826" y="316" class="label">только от ключа</text>
'''
    },
    {
        "dir": "sources/1. Фундамент баз данных и моделирование",
        "filename": "ledgerpulse-er-schema.svg",
        "w": 1040, "h": 460,
        "title": "ФИЗИЧЕСКАЯ ER-СХЕМА LEDGERPULSE (001_INIT_LEDGER.SQL)",
        "subtitle": "Двойная запись в целых единицах BIGINT: связь accounts, transactions и ledger_entries с ограничениями",
        "caption": "ER-диаграмма финансового ядра LedgerPulse: таблицы accounts, transactions и ledger_entries с кардинальностями 1:N",
        "alt": "ER-схема таблиц accounts, transactions и ledger_entries проекта LedgerPulse",
        "body": '''
  <rect x="42" y="110" width="290" height="295" rx="6" class="box-accent"/>
  <text x="187" y="138" text-anchor="middle" class="mono-blue">accounts</text>
  <line x1="42" y1="150" x2="332" y2="150" stroke="#0369a1" stroke-width="1.5"/>
  <text x="58" y="176" class="mono-bold">PK id BIGINT IDENTITY</text>
  <text x="58" y="200" class="mono">external_id TEXT UNIQUE</text>
  <text x="58" y="224" class="mono">owner_name TEXT NOT NULL</text>
  <text x="58" y="248" class="mono">currency CHAR(3) CHECK</text>
  <text x="58" y="272" class="mono-orange">balance BIGINT CHECK &gt;= 0</text>
  <text x="58" y="296" class="mono">status TEXT (active/frozen)</text>
  <text x="58" y="320" class="mono">metadata JSONB</text>
  <text x="58" y="344" class="mono-sm">created_at / updated_at</text>

  <rect x="382" y="110" width="295" height="295" rx="6" class="box-warm"/>
  <text x="529" y="138" text-anchor="middle" class="mono-orange">ledger_entries</text>
  <line x1="382" y1="150" x2="677" y2="150" stroke="#c2410c" stroke-width="1.5"/>
  <text x="398" y="176" class="mono-bold">PK id BIGINT IDENTITY</text>
  <text x="398" y="200" class="mono-blue">FK transaction_id BIGINT</text>
  <text x="398" y="224" class="mono-blue">FK account_id BIGINT</text>
  <text x="398" y="248" class="mono-orange">amount BIGINT CHECK &lt;&gt; 0</text>
  <text x="398" y="272" class="mono">currency CHAR(3)</text>
  <text x="398" y="296" class="mono-sm">created_at TIMESTAMPTZ</text>
  <rect x="398" y="322" width="262" height="64" class="box"/>
  <text x="529" y="348" text-anchor="middle" class="mono-bold">Инвариант двойной записи</text>
  <text x="529" y="369" text-anchor="middle" class="label">SUM(amount) по tx_id == 0</text>

  <rect x="726" y="110" width="275" height="295" rx="6" class="box"/>
  <text x="863" y="138" text-anchor="middle" class="mono-bold">transactions</text>
  <line x1="726" y1="150" x2="1001" y2="150" stroke="#1e293b" stroke-width="1.5"/>
  <text x="742" y="176" class="mono-bold">PK id BIGINT IDENTITY</text>
  <text x="742" y="200" class="mono">reference_id TEXT UNIQUE</text>
  <text x="742" y="224" class="mono">kind TEXT CHECK</text>
  <text x="742" y="248" class="mono">status TEXT CHECK</text>
  <text x="742" y="272" class="mono">description TEXT</text>
  <text x="742" y="296" class="mono-sm">created_at TIMESTAMPTZ</text>
  <text x="742" y="346" class="label">ON DELETE RESTRICT</text>
  <text x="742" y="366" class="label">защищает журнал от потери</text>

  <line x1="332" y1="220" x2="382" y2="220" class="line-blue" marker-end="url(#arrowBlue)"/>
  <text x="357" y="210" text-anchor="middle" class="mono-sm">1:N</text>
  <line x1="726" y1="196" x2="677" y2="196" class="line-blue" marker-end="url(#arrowBlue)"/>
  <text x="701" y="186" text-anchor="middle" class="mono-sm">1:N</text>
'''
    },

    # --- МОДУЛЬ 2 (3 схемы) ---
    {
        "dir": "sources/2. Базовый SQL с нуля",
        "filename": "sql-logical-execution-order.svg",
        "w": 1040, "h": 440,
        "title": "ЛОГИЧЕСКИЙ КОНВЕЙЕР ВЫПОЛНЕНИЯ SQL-ЗАПРОСА",
        "subtitle": "Почему синтаксически SELECT стоит первым, но логически выполняется пятым — после FROM, WHERE, GROUP BY и HAVING",
        "caption": "Схема семи логических фаз выполнения SQL-запроса и области видимости вычисляемых алиасов",
        "alt": "Логический порядок выполнения клауз SQL: FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT",
        "body": '''
  <rect x="42" y="102" width="956" height="190" rx="6" class="box"/>
  <text x="64" y="132" class="mono-blue">СИНТАКСИС: SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT</text>
  <g transform="translate(64, 152)">
    <rect x="0" y="0" width="110" height="72" class="box-accent"/><text x="55" y="26" text-anchor="middle" class="mono-blue">1. FROM</text><text x="55" y="48" text-anchor="middle" class="label">Декартово +</text><text x="55" y="63" text-anchor="middle" class="label">ON / JOIN</text>
    <line x1="110" y1="36" x2="128" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="130" y="0" width="110" height="72" class="box-dark"/><text x="185" y="26" text-anchor="middle" class="mono-bold">2. WHERE</text><text x="185" y="48" text-anchor="middle" class="label">Отсев строк</text><text x="185" y="63" text-anchor="middle" class="label">до групп</text>
    <line x1="240" y1="36" x2="258" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="260" y="0" width="115" height="72" class="box-dark"/><text x="317" y="26" text-anchor="middle" class="mono-bold">3. GROUP BY</text><text x="317" y="48" text-anchor="middle" class="label">Разбиение</text><text x="317" y="63" text-anchor="middle" class="label">на корзины</text>
    <line x1="375" y1="36" x2="393" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="395" y="0" width="110" height="72" class="box-dark"/><text x="450" y="26" text-anchor="middle" class="mono-bold">4. HAVING</text><text x="450" y="48" text-anchor="middle" class="label">Отсев</text><text x="450" y="63" text-anchor="middle" class="label">корзин</text>
    <line x1="505" y1="36" x2="523" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="525" y="0" width="120" height="72" class="box-accent"/><text x="585" y="26" text-anchor="middle" class="mono-blue">5. SELECT</text><text x="585" y="48" text-anchor="middle" class="label">Алиасы AS</text><text x="585" y="63" text-anchor="middle" class="label">+ DISTINCT</text>
    <line x1="645" y1="36" x2="663" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="665" y="0" width="118" height="72" class="box-warm"/><text x="724" y="26" text-anchor="middle" class="mono-orange">6. ORDER BY</text><text x="724" y="48" text-anchor="middle" class="label">Сортировка</text><text x="724" y="63" text-anchor="middle" class="label">алиасов</text>
    <line x1="783" y1="36" x2="801" y2="36" class="line" marker-end="url(#arrow)"/>
    <rect x="803" y="0" width="108" height="72" class="box-warm"/><text x="857" y="26" text-anchor="middle" class="mono-orange">7. LIMIT</text><text x="857" y="48" text-anchor="middle" class="label">Top-N срез</text><text x="857" y="63" text-anchor="middle" class="label">строк</text>
  </g>
  <text x="64" y="266" class="label">На этапе 5 рождаются алиасы SELECT — поэтому на этапах 2 и 4 они ещё не существуют, а на этапе 6 (ORDER BY) уже доступны.</text>

  <rect x="42" y="315" width="465" height="92" rx="6" class="box-warm"/>
  <text x="64" y="344" class="mono-orange">Ошибка: WHERE total_cents &gt; 1000</text>
  <text x="64" y="368" class="label">Если total_cents вычислен в SELECT как alias, шаг WHERE падает:</text>
  <text x="64" y="388" class="mono-sm">ERROR: column "total_cents" does not exist</text>

  <rect x="533" y="315" width="465" height="92" rx="6" class="box-accent"/>
  <text x="555" y="344" class="mono-blue">Заметка о физическом оптимизаторе</text>
  <text x="555" y="368" class="label">CBO имеет право пробросить фильтр раньше JOIN (Predicate Pushdown),</text>
  <text x="555" y="388" class="label">но обязан сохранить ровно тот же результат, что и логический порядок.</text>
'''
    },
    {
        "dir": "sources/2. Базовый SQL с нуля",
        "filename": "sql-joins-row-matrix.svg",
        "w": 1040, "h": 460,
        "title": "ОБЪЕДИНЕНИЯ JOIN НА РЕАЛЬНЫХ СТРОКАХ (БЕЗ КРУГОВ ВЕННА)",
        "subtitle": "Почему круги Венна вводят в заблуждение, а результат JOIN определяется сопоставлением ключей и NULL-дополнением",
        "caption": "Сравнение INNER, LEFT, RIGHT и FULL JOIN на таблицах accounts и ledger_entries с показом дублирования 1:N и NULL-строк",
        "alt": "Матрица сопоставления строк при INNER JOIN, LEFT JOIN, RIGHT JOIN и FULL JOIN",
        "body": '''
  <rect x="38" y="94" width="230" height="150" rx="6" class="box-accent"/>
  <text x="153" y="118" text-anchor="middle" class="mono-blue">Левая: accounts</text>
  <text x="58" y="148" class="mono">id=1 | Alice</text>
  <text x="58" y="174" class="mono">id=2 | Bob</text>
  <text x="58" y="200" class="mono-orange">id=3 | Eve (нет записей)</text>

  <rect x="38" y="266" width="230" height="155" rx="6" class="box-dark"/>
  <text x="153" y="290" text-anchor="middle" class="mono-bold">Правая: entries</text>
  <text x="58" y="320" class="mono">e1 | acc=1 | +500</text>
  <text x="58" y="346" class="mono">e2 | acc=1 | -200</text>
  <text x="58" y="372" class="mono">e3 | acc=2 | +100</text>
  <text x="58" y="398" class="mono-orange">e4 | acc=99 (сирота)</text>

  <rect x="295" y="94" width="335" height="150" rx="6" class="box"/>
  <text x="462" y="118" text-anchor="middle" class="mono-bold">INNER JOIN (только пары)</text>
  <text x="315" y="148" class="mono-sm">1 | Alice | e1 (+500)</text>
  <text x="315" y="172" class="mono-sm">1 | Alice | e2 (-200)  ← 1:N размножение!</text>
  <text x="315" y="196" class="mono-sm">2 | Bob   | e3 (+100)</text>
  <text x="315" y="224" class="label">Eve и e4 отброшены</text>

  <rect x="655" y="94" width="347" height="150" rx="6" class="box-accent"/>
  <text x="828" y="118" text-anchor="middle" class="mono-blue">LEFT JOIN (вся левая + NULL)</text>
  <text x="675" y="148" class="mono-sm">1 | Alice | e1, e2 (2 строки)</text>
  <text x="675" y="172" class="mono-sm">2 | Bob   | e3</text>
  <text x="675" y="196" class="mono-orange">3 | Eve   | NULL, NULL</text>
  <text x="675" y="224" class="label">Фильтр правой в WHERE убьёт строку Eve!</text>

  <rect x="295" y="266" width="335" height="155" rx="6" class="box"/>
  <text x="462" y="290" text-anchor="middle" class="mono-bold">FULL OUTER JOIN</text>
  <text x="315" y="320" class="mono-sm">1..2 | совпавшие пары</text>
  <text x="315" y="346" class="mono-orange">3 | Eve  | NULL</text>
  <text x="315" y="372" class="mono-orange">NULL     | e4 (acc=99)</text>
  <text x="315" y="400" class="label">Полезно для сверки двух реестров</text>

  <rect x="655" y="266" width="347" height="155" rx="6" class="box-warm"/>
  <text x="828" y="290" text-anchor="middle" class="mono-orange">Ловушка LEFT JOIN + WHERE</text>
  <text x="675" y="322" class="mono-sm">LEFT JOIN entries e ON ...</text>
  <text x="675" y="344" class="mono-orange">WHERE e.amount &gt; 0  -- превращает в INNER!</text>
  <line x1="675" y1="362" x2="980" y2="362" stroke="#cbd5e1"/>
  <text x="675" y="384" class="mono-blue">Верно: ON a.id = e.account_id</text>
  <text x="675" y="404" class="mono-blue">       AND e.amount &gt; 0</text>
'''
    },
    {
        "dir": "sources/2. Базовый SQL с нуля",
        "filename": "offset-vs-keyset-pagination.svg",
        "w": 1040, "h": 440,
        "title": "ПАГИНАЦИЯ: ДЕГРАДАЦИЯ OFFSET O(N) ПРОТИВ KEYSET O(log N)",
        "subtitle": "Почему OFFSET 100000 сканирует и отбрасывает тысячи строк, а курсор (created_at, id) сразу прыгает к нужной странице",
        "caption": "Сравнение механики OFFSET и Keyset-пагинации в project/step02/query.go: работа с индексом и устойчивость при вставках",
        "alt": "Сравнение линейного сканирования OFFSET и индексного перехода Keyset-пагинации",
        "body": '''
  <rect x="38" y="96" width="964" height="145" rx="6" class="box-warm"/>
  <text x="60" y="124" class="mono-orange">1. OFFSET 100000 LIMIT 3 — СКАН И СБРОС (РАСТЁТ ЛИНЕЙНО С НОМЕРОМ СТРАНИЦЫ)</text>
  <rect x="60" y="144" width="660" height="44" class="box-dark"/>
  <text x="390" y="171" text-anchor="middle" class="mono">Прочитано, отсортировано и ВЫБРОШЕНО: 100 000 кортежей</text>
  <line x1="720" y1="166" x2="760" y2="166" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="765" y="144" width="215" height="44" class="box"/>
  <text x="872" y="171" text-anchor="middle" class="mono-bold">Возвращено: 3 строки</text>
  <text x="60" y="218" class="label">При вставке новой записи в начало ленты все следующие страницы «съезжают», порождая дубли у клиента.</text>

  <rect x="38" y="262" width="964" height="145" rx="6" class="box-accent"/>
  <text x="60" y="290" class="mono-blue">2. KEYSET: WHERE (created_at, id) &lt; ($4, $5) ORDER BY created_at DESC, id DESC LIMIT 3</text>
  <rect x="60" y="310" width="240" height="44" class="box"/>
  <text x="180" y="337" text-anchor="middle" class="mono-blue">B-Tree Seek → ($4, $5)</text>
  <line x1="300" y1="332" x2="345" y2="332" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="348" y="310" width="290" height="44" class="box"/>
  <text x="493" y="337" text-anchor="middle" class="mono-bold">Читает ровно 3 соседа по листу</text>
  <line x1="638" y1="332" x2="682" y2="332" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="685" y="310" width="295" height="44" class="box-dark"/>
  <text x="832" y="337" text-anchor="middle" class="mono">Стабильно O(log N) и 0 дублей</text>
  <text x="60" y="384" class="label">Тайбрейкер id гарантирует строгий порядок даже при совпадении timestamp у двух операций (step02/query.go).</text>
'''
    },

    # --- МОДУЛЬ 3 (3 схемы) ---
    {
        "dir": "sources/3. Продвинутый SQL и аналитика",
        "filename": "window-frame-anatomy.svg",
        "w": 1040, "h": 450,
        "title": "АНАТОМИЯ ОКОННОЙ ФУНКЦИИ: PARTITION BY, ORDER BY И РАМКА ОКНА",
        "subtitle": "Почему ROWS BETWEEN 2 PRECEDING AND CURRENT ROW отличается от RANGE по умолчанию при равных ключах",
        "caption": "Схема работы WindowAgg: разделение на партиции, сортировка внутри партиции и отличие рамки ROWS от RANGE",
        "alt": "Анатомия оконной функции OVER с партициями и сравнением рамок ROWS и RANGE",
        "body": '''
  <rect x="38" y="94" width="465" height="325" rx="6" class="box"/>
  <text x="270" y="122" text-anchor="middle" class="mono-blue">ПАРТИЦИЯ account_id = 10 (WindowAgg)</text>
  <rect x="60" y="142" width="420" height="34" class="box-dark"/><text x="76" y="164" class="mono">1 | 10:00 | +500 | ROW_NUMBER=1</text>
  <rect x="60" y="182" width="420" height="34" class="box-accent"/><text x="76" y="204" class="mono">2 | 10:00 | +500 | ROWS: 1000 | RANGE: 1000</text>
  <rect x="60" y="222" width="420" height="34" class="box-warm"/><text x="76" y="244" class="mono">3 | 10:05 | +200 | MovingAvg3 = 400</text>
  <rect x="60" y="262" width="420" height="34" class="box"/><text x="76" y="284" class="mono">4 | 10:10 | +800 | RunningSum = 2000</text>
  <text x="60" y="330" class="label">Строки остаются на месте (в отличие от GROUP BY),</text>
  <text x="60" y="350" class="label">к каждой приклеивается агрегат по её скользящему окну.</text>
  <text x="60" y="378" class="mono-blue">Эталон на Go: project/step03/analytics.go</text>

  <rect x="533" y="94" width="469" height="325" rx="6" class="box"/>
  <text x="767" y="122" text-anchor="middle" class="mono-orange">ЛОВУШКА РАМКИ ПО УМОЛЧАНИЮ (RANGE vs ROWS)</text>
  <rect x="558" y="148" width="420" height="110" class="box-warm"/>
  <text x="576" y="176" class="mono-orange">OVER (ORDER BY created_at)</text>
  <text x="576" y="200" class="label">Неявно включает: RANGE BETWEEN UNBOUNDED PRECEDING</text>
  <text x="576" y="220" class="label">AND CURRENT ROW — все peer-строки с тем же временем</text>
  <text x="576" y="240" class="label">суммируются разом, ломая нарастающий итог!</text>

  <rect x="558" y="278" width="420" height="112" class="box-accent"/>
  <text x="576" y="306" class="mono-blue">Явно и безопасно: ROWS BETWEEN ... AND CURRENT ROW</text>
  <text x="576" y="330" class="label">Сдвигает рамку строго по физическим строкам,</text>
  <text x="576" y="350" class="label">а LAST_VALUE требует UNBOUNDED FOLLOWING,</text>
  <text x="576" y="370" class="label">иначе возвращает только текущую строку.</text>
'''
    },
    {
        "dir": "sources/3. Продвинутый SQL и аналитика",
        "filename": "recursive-cte-tree.svg",
        "w": 1040, "h": 440,
        "title": "РАБОТА WITH RECURSIVE: ИТЕРАТИВНАЯ ОЧЕРЕДЬ WORKTABLE И ЗАЩИТА CYCLE",
        "subtitle": "Как СУБД разворачивает иерархию счетов/категорий без рекурсии в стеке, шаг за шагом опустошая рабочую таблицу",
        "caption": "Итеративный алгоритм WITH RECURSIVE: якорь, WorkTable, рекурсивный шаг и защита от зацикливания графа",
        "alt": "Схема работы рекурсивного CTE через якорь, WorkTable и проверку циклов",
        "body": '''
  <rect x="42" y="100" width="265" height="120" rx="6" class="box-accent"/>
  <text x="174" y="128" text-anchor="middle" class="mono-blue">1. Якорь (Anchor Member)</text>
  <text x="174" y="156" text-anchor="middle" class="mono">WHERE parent_id IS NULL</text>
  <text x="174" y="182" text-anchor="middle" class="label">Выполняется 1 раз →</text>
  <text x="174" y="202" text-anchor="middle" class="label">кладёт корень в WorkTable</text>

  <line x1="307" y1="160" x2="365" y2="160" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="368" y="100" width="305" height="120" rx="6" class="box-warm"/>
  <text x="520" y="128" text-anchor="middle" class="mono-orange">2. Рабочая очередь WorkTable</text>
  <text x="520" y="156" text-anchor="middle" class="mono">depth=0 → depth=1 → depth=2</text>
  <text x="520" y="182" text-anchor="middle" class="label">Пока WorkTable не пуста,</text>
  <text x="520" y="202" text-anchor="middle" class="label">присоединяем дочерние узлы</text>

  <line x1="673" y1="160" x2="730" y2="160" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="733" y="100" width="265" height="120" rx="6" class="box-dark"/>
  <text x="865" y="128" text-anchor="middle" class="mono-bold">3. Результат (UNION ALL)</text>
  <text x="865" y="156" text-anchor="middle" class="mono">Накопленное дерево</text>
  <text x="865" y="182" text-anchor="middle" class="label">Без лишней дедупликации</text>
  <text x="865" y="202" text-anchor="middle" class="label">(UNION требует Sort/Hash)</text>

  <path d="M 520 220 L 520 258 L 368 258" class="line-orange" marker-end="url(#arrowOrange)"/>
  <text x="444" y="278" text-anchor="middle" class="mono-sm">Итерация по шагам</text>

  <rect x="42" y="298" width="956" height="110" rx="6" class="box"/>
  <text x="64" y="328" class="mono-orange">ЗАЩИТА ОТ БЕСКОНЕЧНОГО ЦИКЛА В ГРАФЕ (A → B → A):</text>
  <text x="64" y="354" class="mono">CYCLE id SET is_cycle USING path   -- PostgreSQL 14+ или NOT (id = ANY(path))</text>
  <text x="64" y="382" class="label">Плюс жёсткий ограничитель WHERE depth &lt; 50, чтобы битые данные не переполнили work_mem и диск temp_files.</text>
'''
    },
    {
        "dir": "sources/3. Продвинутый SQL и аналитика",
        "filename": "view-vs-materialized-view.svg",
        "w": 1040, "h": 440,
        "title": "VIEW (ПОДСТАНОВКА AST) ПРОТИВ MATERIALIZED VIEW (СНИМОК НА ДИСКЕ)",
        "subtitle": "Почему обычное представление не ускоряет запрос, а материализованное требует UNIQUE-индекса для CONCURRENTLY",
        "caption": "Сравнение выполнения обычного VIEW и MATERIALIZED VIEW с обновлением REFRESH MATERIALIZED VIEW CONCURRENTLY",
        "alt": "Сравнение архитектуры обычного VIEW и материализованного представления MATERIALIZED VIEW",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box"/>
  <text x="270" y="124" text-anchor="middle" class="mono-blue">ОБЫЧНОЕ VIEW (ТОЛЬКО СИНТАКСИС)</text>
  <rect x="64" y="146" width="412" height="58" class="box-dark"/>
  <text x="270" y="172" text-anchor="middle" class="mono">SELECT * FROM v_daily_turnover</text>
  <text x="270" y="192" text-anchor="middle" class="label">0 байт на диске, всегда 100% свежие данные</text>
  <line x1="270" y1="204" x2="270" y2="238" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="64" y="240" width="412" height="62" class="box-accent"/>
  <text x="270" y="266" text-anchor="middle" class="mono-bold">Rewrite Rule подставляет исходный SQL</text>
  <text x="270" y="286" text-anchor="middle" class="label">Полный пересчёт JOIN + GROUP BY на каждый вызов</text>
  <text x="64" y="340" class="label">В PostgreSQL 15+ используйте WITH (security_invoker = true),</text>
  <text x="64" y="360" class="label">чтобы проверялись права и RLS вызывающего пользователя.</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box-accent"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">MATERIALIZED VIEW (ФИЗИЧЕСКАЯ ТАБЛИЦА)</text>
  <rect x="560" y="146" width="415" height="58" class="box"/>
  <text x="767" y="172" text-anchor="middle" class="mono">SELECT * FROM mv_daily_turnover</text>
  <text x="767" y="192" text-anchor="middle" class="label">Читает готовые 8-КБ страницы + собственные индексы</text>
  <line x1="767" y1="204" x2="767" y2="238" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="560" y="240" width="415" height="62" class="box-warm"/>
  <text x="767" y="266" text-anchor="middle" class="mono-orange">REFRESH MATERIALIZED VIEW CONCURRENTLY</text>
  <text x="767" y="286" text-anchor="middle" class="label">Строит diff в фоне без блокировки SELECT (нужен UNIQUE!)</text>
  <text x="560" y="340" class="label">Без CONCURRENTLY ставится AccessExclusiveLock на всё время</text>
  <text x="560" y="360" class="label">пересчёта — читатели дашбордов замирают.</text>
'''
    },

    # --- МОДУЛЬ 4 (5 схем) ---
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "pg-btree-8kb-page.svg",
        "w": 1040, "h": 460,
        "title": "АНАТОМИЯ 8-КБ СТРАНИЦЫ B+ TREE В POSTGRESQL (SLOTTED PAGE)",
        "subtitle": "Почему ключи растут с начала страницы навстречу телам элементов и как устроен High Key по Леману–Яо",
        "caption": "Внутренняя разметка 8-килобайтной страницы B+ Tree: PageHeaderData, ItemIdData, свободное пространство, Items и BTPageOpaqueData",
        "alt": "Схема 8-КБ страницы B+ Tree в PostgreSQL с заголовком, массивом ItemId, кортежами и High Key",
        "body": '''
  <rect x="38" y="96" width="964" height="205" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">СТРАНИЦА ИНДЕКСА B+ TREE = 8 192 БАЙТА (BLCKSZ)</text>
  <g transform="translate(60, 142)">
    <rect x="0" y="0" width="135" height="105" class="box-dark"/>
    <text x="67" y="30" text-anchor="middle" class="mono-bold">PageHeader</text>
    <text x="67" y="52" text-anchor="middle" class="mono-sm">24 байта</text>
    <text x="67" y="74" text-anchor="middle" class="label">pd_lsn, lower,</text>
    <text x="67" y="92" text-anchor="middle" class="label">upper, special</text>

    <rect x="135" y="0" width="180" height="105" class="box-accent"/>
    <text x="225" y="30" text-anchor="middle" class="mono-blue">Line Pointers</text>
    <text x="225" y="52" text-anchor="middle" class="mono-sm">ItemIdData (4 Б)</text>
    <text x="225" y="74" text-anchor="middle" class="label">Смещения →</text>
    <text x="225" y="92" text-anchor="middle" class="label">Binary Search</text>

    <rect x="315" y="0" width="210" height="105" class="box"/>
    <text x="420" y="42" text-anchor="middle" class="mono-bold">Free Space</text>
    <text x="420" y="66" text-anchor="middle" class="label">lower ... upper</text>
    <text x="420" y="88" text-anchor="middle" class="label">(fillfactor 90%)</text>

    <rect x="525" y="0" width="265" height="105" class="box-warm"/>
    <text x="657" y="30" text-anchor="middle" class="mono-orange">Index Tuples (Items)</text>
    <text x="657" y="52" text-anchor="middle" class="mono-sm">← Растут справа налево</text>
    <text x="657" y="74" text-anchor="middle" class="label">[High Key] + (key, ctid)</text>
    <text x="657" y="92" text-anchor="middle" class="label">В ветках — номера страниц</text>

    <rect x="790" y="0" width="130" height="105" class="box-dark"/>
    <text x="855" y="30" text-anchor="middle" class="mono-bold">Opaque</text>
    <text x="855" y="52" text-anchor="middle" class="mono-sm">16 байт</text>
    <text x="855" y="74" text-anchor="middle" class="label">btpo_prev /</text>
    <text x="855" y="92" text-anchor="middle" class="label">btpo_next</text>
  </g>
  <text x="60" y="276" class="label">Отсортированный массив ItemIdData даёт O(log₂ M) в L1/L2 кэше без перемещения тяжёлых кортежей при вставке.</text>

  <rect x="38" y="320" width="465" height="106" rx="6" class="box-accent"/>
  <text x="60" y="348" class="mono-blue">Указатели на листья: двусвязный список</text>
  <text x="60" y="372" class="label">btpo_prev и btpo_next связывают листья на одном уровне:</text>
  <text x="60" y="394" class="label">диапазонный скан идёт вбок по листьям без возврата к корню.</text>

  <rect x="533" y="320" width="469" height="106" rx="6" class="box-warm"/>
  <text x="555" y="348" class="mono-orange">High Key и блокировки Лемана–Яо</text>
  <text x="555" y="372" class="label">Если лист расщепился во время спуска читателя, ключ &gt; High Key</text>
  <text x="555" y="394" class="label">просто направляет поиск вправо по btpo_next без глобальной блокировки.</text>
'''
    },
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "btree-page-split-steps.svg",
        "w": 1040, "h": 450,
        "title": "РАСЩЕПЛЕНИЕ СТРАНИЦЫ (PAGE SPLIT): ПОЧЕМУ UUIDV4 БЬЁТ ПО ДИСКУ",
        "subtitle": "Что происходит, когда новая запись попадает в переполненную 8-КБ страницу B+ Tree — каскадное копирование и фрагментация",
        "caption": "Пошаговая схема Page Split: переполнение листа, аллокация новой страницы, перенос половины ключей и вставка разделителя в родителя",
        "alt": "Пошаговая диаграмма расщепления переполненной страницы B+ Tree при вставке случайного ключа",
        "body": '''
  <rect x="38" y="96" width="300" height="225" rx="6" class="box-warm"/>
  <text x="188" y="124" text-anchor="middle" class="mono-orange">ШАГ 1: ПЕРЕПОЛНЕНИЕ ЛИСТА</text>
  <rect x="60" y="145" width="255" height="44" class="box"/>
  <text x="187" y="172" text-anchor="middle" class="mono">Страница #42: [10, 20, 30, 40]</text>
  <text x="187" y="216" text-anchor="middle" class="mono-orange">+ Вставка ключа 25</text>
  <text x="187" y="246" text-anchor="middle" class="label">Свободных байт &lt; размера кортежа</text>
  <text x="187" y="268" text-anchor="middle" class="label">Требуется Latch и новая страница</text>

  <line x1="338" y1="208" x2="368" y2="208" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="371" y="96" width="315" height="225" rx="6" class="box"/>
  <text x="528" y="124" text-anchor="middle" class="mono-blue">ШАГ 2: РАСЩЕПЛЕНИЕ 50 / 50</text>
  <rect x="392" y="145" width="128" height="62" class="box-accent"/>
  <text x="456" y="170" text-anchor="middle" class="mono-bold">Стр. #42</text>
  <text x="456" y="192" text-anchor="middle" class="mono">[10, 20, 25]</text>
  <line x1="520" y1="176" x2="540" y2="176" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="542" y="145" width="124" height="62" class="box-warm"/>
  <text x="604" y="170" text-anchor="middle" class="mono-orange">Стр. #98</text>
  <text x="604" y="192" text-anchor="middle" class="mono">[30, 40]</text>
  <text x="528" y="236" text-anchor="middle" class="label">Полные образы страниц пишутся</text>
  <text x="528" y="256" text-anchor="middle" class="label">в WAL (Full Page Writes) +</text>
  <text x="528" y="276" text-anchor="middle" class="label">разделитель 30 уходит наверх</text>

  <line x1="686" y1="208" x2="716" y2="208" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="719" y="96" width="283" height="225" rx="6" class="box-accent"/>
  <text x="860" y="124" text-anchor="middle" class="mono-blue">ШАГ 3: РОСТ ВВЕРХ И BLOAT</text>
  <rect x="742" y="145" width="236" height="44" class="box"/>
  <text x="860" y="172" text-anchor="middle" class="mono">Parent: [..., 30 → #98]</text>
  <text x="860" y="218" text-anchor="middle" class="label">При переполнении корня</text>
  <text x="860" y="238" text-anchor="middle" class="label">высота дерева растёт (+1).</text>
  <text x="860" y="268" text-anchor="middle" class="mono-orange">Заполнение падает до ~50%</text>

  <rect x="38" y="340" width="964" height="78" rx="6" class="box-dark"/>
  <text x="60" y="368" class="mono-bold">Вывод для LedgerPulse: последовательный BIGINT / UUIDv7 бьёт только в крайний правый лист (~90% плотности),</text>
  <text x="60" y="392" class="label">тогда как случайный UUIDv4 вызывает постоянные Page Splits по всему дереву, раздувая индекс и вымывая Buffer Pool.</text>
'''
    },
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "composite-index-left-prefix.svg",
        "w": 1040, "h": 440,
        "title": "СОСТАВНОЙ ИНДЕКС (account_id, created_at, id) И ПРАВИЛО ESR",
        "subtitle": "Лексикографическая сортировка ключей: почему фильтр без ведущего столбца не попадает в индексный поиск",
        "caption": "Раскладка составного индекса (account_id, created_at DESC) и правило порядка столбцов Equality → Sort → Range",
        "alt": "Схема сортировки составного индекса по левому префиксу и правило ESR",
        "body": '''
  <rect x="38" y="94" width="490" height="316" rx="6" class="box"/>
  <text x="283" y="122" text-anchor="middle" class="mono-blue">ЛЕКСИКОГРАФИЧЕСКИЙ ПОРЯДОК В B+ TREE</text>
  <rect x="60" y="142" width="445" height="34" class="box-accent"/><text x="76" y="164" class="mono">(acc=1, 2026-05-02, id=9)  ← непрерывный блок</text>
  <rect x="60" y="180" width="445" height="34" class="box-accent"/><text x="76" y="202" class="mono">(acc=1, 2026-05-01, id=4)  ← для acc=1</text>
  <rect x="60" y="218" width="445" height="34" class="box-dark"/><text x="76" y="240" class="mono">(acc=2, 2026-05-03, id=11)</text>
  <rect x="60" y="256" width="445" height="34" class="box-dark"/><text x="76" y="278" class="mono">(acc=2, 2026-05-01, id=2)</text>
  <rect x="60" y="294" width="445" height="34" class="box-dark"/><text x="76" y="316" class="mono">(acc=3, 2026-05-02, id=8)</text>
  <text x="60" y="358" class="label">WHERE created_at = '2026-05-01' без account_id разбросан</text>
  <text x="60" y="378" class="label">по разным частям дерева → нужен отдельный индекс или Skip Scan.</text>

  <rect x="556" y="94" width="446" height="316" rx="6" class="box"/>
  <text x="779" y="122" text-anchor="middle" class="mono-orange">ЗОЛОТОЕ ПРАВИЛО ПОРЯДКА: E → S → R</text>
  <rect x="580" y="146" width="398" height="72" class="box-accent"/>
  <text x="598" y="172" class="mono-blue">1. Equality (=): account_id = $1</text>
  <text x="598" y="196" class="label">Фиксирует узкую ветку дерева; дальше ключи отсортированы!</text>
  <rect x="580" y="230" width="398" height="72" class="box-dark"/>
  <text x="598" y="256" class="mono-bold">2. Sort (ORDER BY) / 3. Range (&lt;, &gt;)</text>
  <text x="598" y="280" class="label">created_at DESC, id DESC для keyset-курсора</text>
  <rect x="580" y="314" width="398" height="74" class="box-warm"/>
  <text x="598" y="340" class="mono-orange">Если поставить Range раньше Equality:</text>
  <text x="598" y="364" class="label">после диапазона порядок по следующему полю теряется.</text>
'''
    },
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "explain-analyze-buffers-output.svg",
        "w": 1040, "h": 460,
        "title": "РЕАЛЬНЫЙ ВЫВОД EXPLAIN (ANALYZE, BUFFERS): ЧТО ИСКАТЬ В ПЛАНЕ",
        "subtitle": "Сравнение медленного Seq Scan с отсевом 99% строк против Index-Only Scan по покрывающему индексу LedgerPulse",
        "caption": "Разбор реального вывода EXPLAIN (ANALYZE, BUFFERS): сравнение cost, actual time, rows, shared hit/read и Heap Fetches",
        "alt": "Терминальный план EXPLAIN ANALYZE BUFFERS: сравнение Seq Scan и Index-Only Scan",
        "body": '''
  <rect x="38" y="94" width="964" height="158" rx="6" class="box-warm"/>
  <text x="60" y="120" class="mono-orange">ДО: Seq Scan (отброшено 499 850 строк, сотни чтений с диска)</text>
  <rect x="60" y="132" width="920" height="104" class="box"/>
  <text x="76" y="156" class="mono-sm">Seq Scan on ledger_entries  (cost=0.00..14820.00 rows=150 width=36) (actual time=0.14..84.31 rows=150 loops=1)</text>
  <text x="76" y="178" class="mono-sm">  Filter: (account_id = 42 AND created_at &gt;= '2026-05-01')</text>
  <text x="76" y="200" class="mono-orange">  Rows Removed by Filter: 499850</text>
  <text x="76" y="222" class="mono-sm">  Buffers: shared hit=3120 read=5450   &lt;-- вымывает Buffer Pool!</text>

  <rect x="38" y="270" width="964" height="162" rx="6" class="box-accent"/>
  <text x="60" y="296" class="mono-blue">ПОСЛЕ: Index-Only Scan по idx_ledger_entries_account_created (... INCLUDE (amount, currency))</text>
  <rect x="60" y="308" width="920" height="108" class="box"/>
  <text x="76" y="332" class="mono-sm">Limit  (cost=0.43..12.85 rows=50 width=36) (actual time=0.032..0.095 rows=50 loops=1)</text>
  <text x="76" y="354" class="mono-sm">  -&gt; Index Only Scan using idx_ledger_entries_account_created on ledger_entries</text>
  <text x="76" y="376" class="mono-blue">       Index Cond: (account_id = 42 AND created_at &lt; '2026-05-10')   |   Heap Fetches: 0</text>
  <text x="76" y="398" class="mono-sm">       Buffers: shared hit=5   &lt;-- 887× меньше затронутых страниц, 0 обращений к диску</text>
'''
    },
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "join-algorithms-comparison.svg",
        "w": 1040, "h": 440,
        "title": "ТРИ ФИЗИЧЕСКИХ АЛГОРИТМА JOIN: NESTED LOOP, HASH JOIN И MERGE JOIN",
        "subtitle": "Как планировщик выбирает стратегию соединения в зависимости от размеров таблиц, индексов и work_mem",
        "caption": "Сравнение Nested Loop Join, Hash Join (с риском spill на диск при нехватке work_mem) и Merge Join",
        "alt": "Сравнение алгоритмов физического соединения таблиц Nested Loop, Hash Join и Merge Join",
        "body": '''
  <rect x="38" y="96" width="305" height="314" rx="6" class="box-accent"/>
  <text x="190" y="124" text-anchor="middle" class="mono-blue">1. Nested Loop Join</text>
  <text x="190" y="150" text-anchor="middle" class="mono-sm">O(|Outer| × log|Inner|)</text>
  <rect x="60" y="170" width="260" height="90" class="box"/>
  <text x="190" y="196" text-anchor="middle" class="mono-bold">Малая внешняя выборка</text>
  <text x="190" y="218" text-anchor="middle" class="label">+ B-Tree индекс на внутренней</text>
  <text x="190" y="240" text-anchor="middle" class="label">Отдаёт первые строки сразу</text>
  <text x="60" y="294" class="mono-orange">Риск при ошибке оценки:</text>
  <text x="60" y="316" class="label">Если вместо 5 строк пришло</text>
  <text x="60" y="336" class="label">100 000, цикл убивает CPU.</text>

  <rect x="368" y="96" width="305" height="314" rx="6" class="box-warm"/>
  <text x="520" y="124" text-anchor="middle" class="mono-orange">2. Hash Join</text>
  <text x="520" y="150" text-anchor="middle" class="mono-sm">O(|Build| + |Probe|)</text>
  <rect x="390" y="170" width="260" height="90" class="box"/>
  <text x="520" y="196" text-anchor="middle" class="mono-bold">Большие таблицы без индекса</text>
  <text x="520" y="218" text-anchor="middle" class="label">1. Build hash-таблицы в work_mem</text>
  <text x="520" y="240" text-anchor="middle" class="label">2. Probe потоком второй таблицы</text>
  <text x="390" y="294" class="mono-orange">Риск work_mem:</text>
  <text x="390" y="316" class="label">Если таблица не влезла в RAM,</text>
  <text x="390" y="336" class="label">Multi-batch сбрасывает на диск.</text>

  <rect x="698" y="96" width="304" height="314" rx="6" class="box-dark"/>
  <text x="850" y="124" text-anchor="middle" class="mono-bold">3. Merge Join</text>
  <text x="850" y="150" text-anchor="middle" class="mono-sm">O(|A| + |B|) если оба sorted</text>
  <rect x="720" y="170" width="260" height="90" class="box"/>
  <text x="850" y="196" text-anchor="middle" class="mono-bold">Два отсортированных потока</text>
  <text x="850" y="218" text-anchor="middle" class="label">По индексу или после Sort</text>
  <text x="850" y="240" text-anchor="middle" class="label">Два указателя идут параллельно</text>
  <text x="720" y="294" class="mono-blue">Плюс для больших отчётов:</text>
  <text x="720" y="316" class="label">Минимум RAM при готовых</text>
  <text x="720" y="336" class="label">индексах; поддерживает &lt;, &gt;.</text>
'''
    },

    # --- МОДУЛЬ 5 (4 схемы) ---
    {
        "dir": "sources/5. Транзакции, ACID, MVCC и WAL",
        "filename": "mvcc-xmin-xmax-timeline.svg",
        "w": 1040, "h": 450,
        "title": "MVCC В ДЕЙСТВИИ: СНИМКИ ВРЕМЕНИ И ЦЕПОЧКА ВЕРСИЙ XMIN / XMAX",
        "subtitle": "Почему долгая аналитическая транзакция видит старый баланс 500, пока новые клиенты уже видят 600 — без единой блокировки чтения",
        "caption": "Шкала времени MVCC: видимость кортежей по xmin/xmax для транзакций с разными снимками (Snapshot Isolation)",
        "alt": "Таймлайн MVCC с версиями кортежа xmin и xmax и видимостью для двух параллельных транзакций",
        "body": '''
  <rect x="38" y="96" width="964" height="190" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">ЦЕПОЧКА ВЕРСИЙ БАЛАНСА НА ВРЕМЕННОЙ ШКАЛЕ (STEP 05 MVCCENGINE)</text>
  <line x1="70" y1="210" x2="965" y2="210" class="line" marker-end="url(#arrow)"/>
  <rect x="75" y="145" width="235" height="52" class="box-accent"/>
  <text x="192" y="168" text-anchor="middle" class="mono-bold">v1: balance=500</text>
  <text x="192" y="186" text-anchor="middle" class="mono-sm">xmin=10, xmax=12</text>

  <rect x="375" y="145" width="250" height="52" class="box-warm"/>
  <text x="500" y="168" text-anchor="middle" class="mono-orange">v2: balance=600</text>
  <text x="500" y="186" text-anchor="middle" class="mono-sm">xmin=12, xmax=0 (актуальна)</text>

  <rect x="705" y="145" width="255" height="52" class="box-dark"/>
  <text x="832" y="168" text-anchor="middle" class="mono-bold">VACUUM (после XID 11)</text>
  <text x="832" y="186" text-anchor="middle" class="label">Удалит v1 только после ухода tx11</text>

  <text x="90" y="236" class="mono-sm">t1: tx10 COMMIT</text>
  <text x="275" y="236" class="mono-blue">t2: tx11 BEGIN (снимок {10})</text>
  <text x="485" y="236" class="mono-orange">t3: tx12 UPDATE + COMMIT</text>
  <text x="720" y="236" class="mono-sm">t4: tx13 BEGIN (снимок {10,12})</text>

  <rect x="38" y="306" width="465" height="114" rx="6" class="box-accent"/>
  <text x="60" y="334" class="mono-blue">Транзакция tx11 (Snapshot {10})</text>
  <text x="60" y="358" class="label">v1: xmin=10 виден, xmax=12 ещё НЕ закоммичен в её снимке → читает 500.</text>
  <text x="60" y="380" class="label">v2: xmin=12 не входит в снимок → игнорируется.</text>
  <text x="60" y="402" class="mono-sm">Писатель tx12 не блокировал читателя tx11!</text>

  <rect x="533" y="306" width="469" height="114" rx="6" class="box-warm"/>
  <text x="555" y="334" class="mono-orange">Конфликт First-Committer-Wins (tx14 vs tx12)</text>
  <text x="555" y="358" class="label">Если tx14 стартовала до коммита tx12 и меняет ту же строку,</text>
  <text x="555" y="380" class="label">при Commit она получит SQLSTATE 40001 (ErrWriteConflict in step05).</text>
  <text x="555" y="402" class="label">Пока tx11 жива, VACUUM не может освободить старую версию v1.</text>
'''
    },
    {
        "dir": "sources/5. Транзакции, ACID, MVCC и WAL",
        "filename": "wal-sequential-vs-heap-random.svg",
        "w": 1040, "h": 450,
        "title": "ПУТЬ ЗАПИСИ WAL + ARIES: ПОСЛЕДОВАТЕЛЬНЫЙ ЖУРНАЛ ПРОТИВ HEAP",
        "subtitle": "Как СУБД обеспечивает долговечность (Durability) за один fsync в WAL и восстанавливается после внезапного сбоя питания",
        "caption": "Схема работы WAL, буферного пула, Checkpointer и трёх фаз восстановления ARIES (Analysis → Redo → Undo)",
        "alt": "Схема записи транзакции в WAL, грязных страниц в Buffer Pool и восстановления ARIES",
        "body": '''
  <rect x="38" y="96" width="964" height="190" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">ПУТЬ ОДНОЙ ТРАНЗАКЦИИ (WAL RULE: ЛОГ ВСЕГДА ПИШЕТСЯ РАНЬШЕ ДАННЫХ)</text>
  <rect x="60" y="148" width="175" height="90" class="box-accent"/>
  <text x="147" y="176" text-anchor="middle" class="mono-bold">1. COMMIT</text>
  <text x="147" y="198" text-anchor="middle" class="label">Запись LSN + CRC32</text>
  <text x="147" y="218" text-anchor="middle" class="label">в WAL Buffers</text>

  <line x1="235" y1="193" x2="275" y2="193" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="278" y="148" width="285" height="90" class="box-warm"/>
  <text x="420" y="176" text-anchor="middle" class="mono-orange">2. Append-Only WAL + fsync()</text>
  <text x="420" y="198" text-anchor="middle" class="label">1 последовательная запись на диск</text>
  <text x="420" y="218" text-anchor="middle" class="label">→ Клиент сразу получает OK</text>

  <line x1="563" y1="193" x2="603" y2="193" class="line-dash" marker-end="url(#arrow)"/>

  <rect x="606" y="148" width="175" height="90" class="box-dark"/>
  <text x="693" y="176" text-anchor="middle" class="mono-bold">3. Buffer Pool</text>
  <text x="693" y="198" text-anchor="middle" class="label">Грязная 8-КБ</text>
  <text x="693" y="218" text-anchor="middle" class="label">страница в RAM</text>

  <line x1="781" y1="193" x2="818" y2="193" class="line-dash" marker-end="url(#arrow)"/>

  <rect x="821" y="148" width="160" height="90" class="box"/>
  <text x="901" y="176" text-anchor="middle" class="mono-bold">4. Heap (SSD)</text>
  <text x="901" y="198" text-anchor="middle" class="label">Плавный сброс</text>
  <text x="901" y="218" text-anchor="middle" class="label">на Checkpoint</text>

  <rect x="38" y="306" width="964" height="114" rx="6" class="box-dark"/>
  <text x="60" y="334" class="mono-bold">ВОССТАНОВЛЕНИЕ ПОСЛЕ СБОЯ (АЛГОРИТМ ARIES / WALStore.recover В STEP 05)</text>
  <rect x="60" y="348" width="285" height="54" class="box-accent"/>
  <text x="202" y="372" text-anchor="middle" class="mono-blue">1. Analysis</text>
  <text x="202" y="390" text-anchor="middle" class="label">От Redo-точки последнего чекпоинта</text>
  <rect x="370" y="348" width="295" height="54" class="box-warm"/>
  <text x="517" y="372" text-anchor="middle" class="mono-orange">2. Redo (Repeating History)</text>
  <text x="517" y="390" text-anchor="middle" class="label">Накат всех записей + защита CRC32</text>
  <rect x="690" y="348" width="290" height="54" class="box"/>
  <text x="835" y="372" text-anchor="middle" class="mono-bold">3. Undo / Drop Uncommitted</text>
  <text x="835" y="390" text-anchor="middle" class="label">Откат незавершённых (нет COMMIT)</text>
'''
    },
    {
        "dir": "sources/5. Транзакции, ACID, MVCC и WAL",
        "filename": "isolation-anomalies-matrix.svg",
        "w": 1040, "h": 440,
        "title": "МАТРИЦА УРОВНЕЙ ИЗОЛЯЦИИ И АНОМАЛИЙ КОНКУРЕНТНОСТИ",
        "subtitle": "Почему стандарта ANSI SQL-92 недостаточно и где кроются Lost Update и Write Skew под Repeatable Read",
        "caption": "Сводная матрица аномалий (Dirty Read, Non-Repeatable Read, Phantom Read, Lost Update, Write Skew) по уровням изоляции PostgreSQL и InnoDB",
        "alt": "Таблица уровней изоляции транзакций и допускаемых ими аномалий конкурентности",
        "body": '''
  <rect x="38" y="96" width="964" height="316" rx="6" class="box"/>
  <rect x="58" y="114" width="924" height="38" class="box-dark"/>
  <text x="165" y="138" text-anchor="middle" class="mono-bold">Уровень изоляции</text>
  <text x="345" y="138" text-anchor="middle" class="mono-bold">Dirty Read</text>
  <text x="495" y="138" text-anchor="middle" class="mono-bold">Fuzzy Read</text>
  <text x="645" y="138" text-anchor="middle" class="mono-bold">Phantom</text>
  <text x="785" y="138" text-anchor="middle" class="mono-bold">Lost Update</text>
  <text x="918" y="138" text-anchor="middle" class="mono-bold">Write Skew</text>

  <text x="72" y="182" class="mono">Read Uncommitted (ANSI)</text>
  <text x="345" y="182" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="495" y="182" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="645" y="182" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="785" y="182" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="918" y="182" text-anchor="middle" class="mono-orange">Возможна</text>
  <line x1="58" y1="198" x2="982" y2="198" stroke="#cbd5e1"/>

  <text x="72" y="228" class="mono-bold">Read Committed (PG def.)</text>
  <text x="345" y="228" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="495" y="228" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="645" y="228" text-anchor="middle" class="mono-orange">Возможна</text>
  <text x="785" y="228" text-anchor="middle" class="mono-orange">При Read-Modify</text>
  <text x="918" y="228" text-anchor="middle" class="mono-orange">Возможна</text>
  <line x1="58" y1="244" x2="982" y2="244" stroke="#cbd5e1"/>

  <text x="72" y="274" class="mono-bold">Repeatable Read (PG / SI)</text>
  <text x="345" y="274" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="495" y="274" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="645" y="274" text-anchor="middle" class="mono-blue">Запрещена в PG</text>
  <text x="785" y="274" text-anchor="middle" class="mono-blue">Ошибка 40001</text>
  <text x="918" y="274" text-anchor="middle" class="mono-orange">Возможна (SI!)</text>
  <line x1="58" y1="290" x2="982" y2="290" stroke="#cbd5e1"/>

  <text x="72" y="320" class="mono-blue">Serializable (PG SSI)</text>
  <text x="345" y="320" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="495" y="320" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="645" y="320" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="785" y="320" text-anchor="middle" class="mono-blue">Запрещена</text>
  <text x="918" y="320" text-anchor="middle" class="mono-blue">Ошибка 40001</text>
  <line x1="58" y1="340" x2="982" y2="340" stroke="#cbd5e1"/>

  <text x="72" y="376" class="label">В PostgreSQL Read Uncommitted физически работает как Read Committed; Repeatable Read даёт Snapshot Isolation;</text>
  <text x="72" y="396" class="label">в MySQL InnoDB Repeatable Read блокирует фантомы при Current Read через Gap Locks и Next-Key Locks.</text>
'''
    },
    {
        "dir": "sources/5. Транзакции, ACID, MVCC и WAL",
        "filename": "deadlock-wait-for-graph.svg",
        "w": 1040, "h": 440,
        "title": "ВЗАИМОБЛОКИРОВКА (DEADLOCK): ГРАФ ОЖИДАНИЙ И КАНОНИЧЕСКИЙ ПОРЯДОК",
        "subtitle": "Почему встречный перевод Alice ↔ Bob приводит к циклу ожидания и как сортировка id1 &lt; id2 устраняет его навсегда",
        "caption": "Граф ожиданий Wait-For Graph при встречной блокировке счетов и устранение цикла через упорядоченный захват ресурсов",
        "alt": "Схема возникновения Deadlock в графе ожиданий и его устранение через канонический порядок блокировок",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box-warm"/>
  <text x="270" y="124" text-anchor="middle" class="mono-orange">ЦИКЛ В ГРАФЕ ОЖИДАНИЙ (DEADLOCK)</text>
  <rect x="70" y="155" width="160" height="62" class="box"/>
  <text x="150" y="182" text-anchor="middle" class="mono-bold">Tx1 (A → B)</text>
  <text x="150" y="202" text-anchor="middle" class="label">Держит lock(A)</text>

  <rect x="315" y="155" width="160" height="62" class="box"/>
  <text x="395" y="182" text-anchor="middle" class="mono-bold">Tx2 (B → A)</text>
  <text x="395" y="202" text-anchor="middle" class="label">Держит lock(B)</text>

  <path d="M 230 172 L 312 172" class="line-orange" marker-end="url(#arrowOrange)"/>
  <text x="271" y="162" text-anchor="middle" class="mono-sm">ждёт B</text>
  <path d="M 315 202 L 233 202" class="line-orange" marker-end="url(#arrowOrange)"/>
  <text x="271" y="220" text-anchor="middle" class="mono-sm">ждёт A</text>

  <rect x="70" y="255" width="405" height="128" class="box"/>
  <text x="90" y="282" class="mono-bold">Детектор HasDeadlockCycle (step05/mvcc_wal.go)</text>
  <text x="90" y="306" class="label">После deadlock_timeout (1 с в PG) обходит Wait-For Graph</text>
  <text x="90" y="328" class="label">трёхцветным DFS; при обнаружении цикла откатывает жертву</text>
  <text x="90" y="350" class="mono-orange">с ошибкой SQLSTATE 40P01 (deadlock detected).</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box-accent"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">РЕШЕНИЕ: КАНОНИЧЕСКИЙ ПОРЯДОК (id1 &lt; id2)</text>
  <rect x="560" y="155" width="415" height="82" class="box"/>
  <text x="580" y="182" class="mono-bold">if req.FromAccountID &lt; req.ToAccountID { ... }</text>
  <text x="580" y="206" class="label">Обе транзакции Tx1 и Tx2 всегда сначала блокируют min(A, B),</text>
  <text x="580" y="224" class="label">и только потом max(A, B) — ориентированный граф ацикличен!</text>

  <rect x="560" y="255" width="415" height="128" class="box-dark"/>
  <text x="580" y="282" class="mono-blue">Реализация в project/final/service.go:</text>
  <text x="580" y="306" class="label">20 конкурентных встречных горутин A→B и B→A под -race</text>
  <text x="580" y="328" class="label">завершаются с 0 дедлоков и точным сохранением суммы.</text>
  <text x="580" y="350" class="label">Дополнительная страховка: SET LOCAL lock_timeout = '2s'.</text>
'''
    },

    # --- МОДУЛЬ 6 (3 схемы) ---
    {
        "dir": "sources/6. PostgreSQL под капотом",
        "filename": "pg-processes-shared-buffers.svg",
        "w": 1040, "h": 450,
        "title": "ПРОЦЕССНАЯ АРХИТЕКТУРА POSTGRESQL И РАЗДЕЛЯЕМАЯ ПАМЯТЬ",
        "subtitle": "Почему прямое подключение 5 000 горутин убивает память и как PgBouncer в режиме transaction pooling спасает сервер",
        "caption": "Схема процессов PostgreSQL: PgBouncer, postmaster, бэкенды, shared_buffers, WAL buffers и фоновые процессы",
        "alt": "Архитектура процессов и общей памяти PostgreSQL с PgBouncer, бэкендами и фоновыми воркерами",
        "body": '''
  <rect x="38" y="96" width="210" height="205" rx="6" class="box-accent"/>
  <text x="143" y="124" text-anchor="middle" class="mono-blue">Go + PgBouncer</text>
  <text x="143" y="152" text-anchor="middle" class="mono">5 000 горутин</text>
  <text x="143" y="176" text-anchor="middle" class="label">↓ мультиплексирование</text>
  <text x="143" y="200" text-anchor="middle" class="mono-bold">transaction mode</text>
  <text x="143" y="226" text-anchor="middle" class="label">100 серверных коннектов</text>
  <text x="143" y="256" text-anchor="middle" class="mono-orange">Осторожно: Prepared</text>
  <text x="143" y="274" text-anchor="middle" class="label">Statements по сессии</text>

  <line x1="248" y1="198" x2="290" y2="198" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="293" y="96" width="709" height="205" rx="6" class="box"/>
  <text x="647" y="124" text-anchor="middle" class="mono-bold">СЕРВЕР POSTGRESQL (POSTMASTER ФОРКАЕТ ОТДЕЛЬНЫЙ ПРОЦЕСС ОС НА СЕССИЮ)</text>
  <rect x="315" y="142" width="160" height="62" class="box-dark"/>
  <text x="395" y="168" text-anchor="middle" class="mono-bold">Backend #1</text>
  <text x="395" y="190" text-anchor="middle" class="label">PID + work_mem</text>
  <rect x="495" y="142" width="160" height="62" class="box-dark"/>
  <text x="575" y="168" text-anchor="middle" class="mono-bold">Backend #2</text>
  <text x="575" y="190" text-anchor="middle" class="label">PID + work_mem</text>
  <rect x="675" y="142" width="305" height="62" class="box-warm"/>
  <text x="827" y="168" text-anchor="middle" class="mono-orange">Фоновые воркеры</text>
  <text x="827" y="190" text-anchor="middle" class="label">checkpointer · bgwriter · walwriter · autovacuum</text>

  <rect x="315" y="218" width="665" height="64" class="box-accent"/>
  <text x="647" y="245" text-anchor="middle" class="mono-blue">Shared Memory (IPC): shared_buffers (25% RAM) + WAL Buffers + Lock Table + ProcArray</text>
  <text x="647" y="266" text-anchor="middle" class="label">Двойное кэширование: shared_buffers ↔ Page Cache ядра Linux ↔ NVMe SSD</text>

  <rect x="38" y="320" width="964" height="96" rx="6" class="box-dark"/>
  <text x="60" y="348" class="mono-bold">Физика масштаба: 1 бэкенд PostgreSQL ≈ 5–10 МБ базовой памяти + N × work_mem (на каждый Sort/Hash узел).</text>
  <text x="60" y="372" class="label">Лишние 3 000 idle-соединений тратят гигабайты RAM и тормозят обход ProcArray при взятии каждого снимка MVCC.</text>
'''
    },
    {
        "dir": "sources/6. PostgreSQL под капотом",
        "filename": "pg-heap-8kb-toast-hot.svg",
        "w": 1040, "h": 450,
        "title": "HEAP-СТРАНИЦА POSTGRESQL: HOT-ОБНОВЛЕНИЕ И ВЫНОС В TOAST",
        "subtitle": "Как Heap-Only Tuple избегает правки всех индексов при наличии места на странице и куда уходят длинные JSONB",
        "caption": "Внутреннее устройство Heap-страницы PostgreSQL: HOT-цепочка без обновления B-Tree индексов и ссылка на таблицу TOAST",
        "alt": "Схема HOT-цепочки версий кортежа внутри 8-КБ Heap-страницы и внешнего хранилища TOAST",
        "body": '''
  <rect x="38" y="96" width="585" height="314" rx="6" class="box"/>
  <text x="330" y="124" text-anchor="middle" class="mono-blue">8-КБ HEAP-СТРАНИЦА: ЦЕПОЧКА HOT (HEAP-ONLY TUPLE)</text>
  <rect x="60" y="148" width="165" height="64" class="box-dark"/>
  <text x="142" y="175" text-anchor="middle" class="mono">B-Tree Индекс</text>
  <text x="142" y="195" text-anchor="middle" class="mono-sm">ctid = (0, 1)</text>
  <line x1="225" y1="180" x2="270" y2="180" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="273" y="148" width="155" height="64" class="box-warm"/>
  <text x="350" y="172" text-anchor="middle" class="mono-orange">Tuple [0,1] (dead)</text>
  <text x="350" y="194" text-anchor="middle" class="mono-sm">xmax=20 · ctid→[0,2]</text>
  <line x1="428" y1="180" x2="455" y2="180" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="458" y="148" width="145" height="64" class="box-accent"/>
  <text x="530" y="172" text-anchor="middle" class="mono-blue">Tuple [0,2] (live)</text>
  <text x="530" y="194" text-anchor="middle" class="mono-sm">xmin=20 · HOT</text>

  <rect x="60" y="238" width="543" height="148" class="box-dark"/>
  <text x="80" y="266" class="mono-bold">Два строгих условия для HOT-обновления:</text>
  <text x="80" y="290" class="label">1. Не изменён НИ ОДИН столбец, входящий в любой индекс таблицы.</text>
  <text x="80" y="312" class="label">2. Новая версия кортежа физически помещается на ТОЙ ЖЕ 8-КБ странице.</text>
  <text x="80" y="342" class="mono-blue">Задавайте fillfactor = 70–85 для часто обновляемых таблиц!</text>
  <text x="80" y="364" class="label">Тогда 6 индексов не перестраиваются на каждый UPDATE статуса.</text>

  <rect x="648" y="96" width="354" height="314" rx="6" class="box-accent"/>
  <text x="825" y="124" text-anchor="middle" class="mono-blue">TOAST (&gt; ~2 КБ НА КОРТЕЖ)</text>
  <rect x="672" y="148" width="306" height="84" class="box"/>
  <text x="825" y="174" text-anchor="middle" class="mono-bold">Кортеж Heap (~24 Б заголовок)</text>
  <text x="825" y="198" text-anchor="middle" class="mono-sm">18-байтовый TOAST Pointer</text>
  <text x="825" y="218" text-anchor="middle" class="label">сжатие LZ4 / pglz (EXTENDED)</text>
  <line x1="825" y1="232" x2="825" y2="272" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="672" y="275" width="306" height="110" class="box-warm"/>
  <text x="825" y="302" text-anchor="middle" class="mono-orange">pg_toast.pg_toast_NNN</text>
  <text x="825" y="326" text-anchor="middle" class="label">Чанки по ~2 КБ. Если не выбирать</text>
  <text x="825" y="346" text-anchor="middle" class="label">тяжёлый JSONB (избегая SELECT *),</text>
  <text x="825" y="366" text-anchor="middle" class="label">таблица TOAST вообще не читается!</text>
'''
    },
    {
        "dir": "sources/6. PostgreSQL под капотом",
        "filename": "pg-gin-vs-brin-index.svg",
        "w": 1040, "h": 440,
        "title": "ИНВЕРТИРОВАННЫЙ GIN ПРОТИВ СВЕРХКОМПАКТНОГО BRIN В POSTGRESQL",
        "subtitle": "Почему GIN идеален для JSONB и массивов, а BRIN сжимает индекс лога на 1 ТБ до нескольких мегабайт",
        "caption": "Сравнение структуры GIN (Entry Tree + Posting List/Tree) и BRIN (Min/Max по диапазонам физических страниц)",
        "alt": "Сравнение архитектуры индексов GIN для JSONB и BRIN для монотонных временных рядов",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box"/>
  <text x="270" y="124" text-anchor="middle" class="mono-blue">GIN: ENTRY TREE + POSTING LISTS (JSONB / FTS)</text>
  <rect x="62" y="148" width="175" height="90" class="box-accent"/>
  <text x="149" y="174" text-anchor="middle" class="mono-bold">B-Tree ключей</text>
  <text x="149" y="198" text-anchor="middle" class="mono-sm">"tier:pro"</text>
  <text x="149" y="218" text-anchor="middle" class="mono-sm">"region:eu"</text>
  <line x1="237" y1="193" x2="275" y2="193" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="278" y="148" width="202" height="90" class="box-dark"/>
  <text x="379" y="174" text-anchor="middle" class="mono-bold">Posting List / Tree</text>
  <text x="379" y="198" text-anchor="middle" class="mono-sm">[(0,4), (1,9), (4,2)]</text>
  <text x="379" y="218" text-anchor="middle" class="label">Отсортированные ctid</text>
  <rect x="62" y="258" width="418" height="126" class="box-warm"/>
  <text x="80" y="286" class="mono-orange">Цена записи: fastupdate + pending list</text>
  <text x="80" y="310" class="label">Одна строка JSONB дробится на десятки токенов в GIN.</text>
  <text x="80" y="332" class="label">Буфер pending list сливается пакетно, но может вызвать</text>
  <text x="80" y="354" class="label">внезапный скачок задержки у несчастной транзакции.</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box-accent"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">BRIN: BLOCK RANGE INDEX (APPEND-ONLY ЛОГИ)</text>
  <rect x="558" y="148" width="420" height="44" class="box"/>
  <text x="768" y="175" text-anchor="middle" class="mono">Блоки 0..127    → min: May 01, max: May 02</text>
  <rect x="558" y="200" width="420" height="44" class="box"/>
  <text x="768" y="227" text-anchor="middle" class="mono">Блоки 128..255  → min: May 02, max: May 04</text>
  <rect x="558" y="258" width="420" height="126" class="box-dark"/>
  <text x="578" y="286" class="mono-blue">Мизерный размер (до 1000× меньше B-Tree)</text>
  <text x="578" y="310" class="label">Хранит только границы [min, max] на каждые 128 страниц</text>
  <text x="578" y="332" class="label">(pages_per_range). Мгновенно отбрасывает лишние диапазоны,</text>
  <text x="578" y="354" class="label">если данные пишутся хронологически (created_at, id).</text>
'''
    },

    # --- МОДУЛЬ 7 (3 схемы) ---
    {
        "dir": "sources/7. MySQL, InnoDB и форки",
        "filename": "innodb-clustered-vs-secondary.svg",
        "w": 1040, "h": 450,
        "title": "INNODB: КЛАСТЕРНЫЙ ПЕРВИЧНЫЙ КЛЮЧ И ДВОЙНОЙ ПОИСК ПО ВТОРИЧНОМУ ИНДЕКСУ",
        "subtitle": "Почему вторичный индекс в InnoDB хранит не адрес страницы, а значение PRIMARY KEY, и как длинный PK раздувает все индексы",
        "caption": "Схема хранения данных в InnoDB: кластерный индекс с целыми строками в листьях и двойной спуск при поиске по вторичному ключу",
        "alt": "Схема кластерного индекса и вторичного индекса InnoDB с двойным спуском по B+ Tree",
        "body": '''
  <rect x="38" y="96" width="465" height="318" rx="6" class="box"/>
  <text x="270" y="124" text-anchor="middle" class="mono-blue">1. ВТОРИЧНЫЙ ИНДЕКС idx_account_id</text>
  <rect x="175" y="146" width="190" height="42" class="box-dark"/>
  <text x="270" y="172" text-anchor="middle" class="mono">Root (16 КБ страница)</text>
  <line x1="270" y1="188" x2="270" y2="225" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="70" y="228" width="400" height="72" class="box-accent"/>
  <text x="270" y="254" text-anchor="middle" class="mono-bold">Лист: (account_id=42) → PK id=9015</text>
  <text x="270" y="278" text-anchor="middle" class="label">НЕ хранит номер страницы! (Пережил page split без правок)</text>
  <text x="70" y="338" class="mono-orange">Если запрос читает только (account_id, id):</text>
  <text x="70" y="360" class="label">срабатывает Covering Index (Using index) — второй спуск не нужен.</text>

  <line x1="470" y1="264" x2="558" y2="174" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="533" y="96" width="469" height="318" rx="6" class="box-warm"/>
  <text x="767" y="124" text-anchor="middle" class="mono-orange">2. КЛАСТЕРНЫЙ ИНДЕКС (PRIMARY KEY)</text>
  <rect x="650" y="146" width="235" height="42" class="box"/>
  <text x="767" y="172" text-anchor="middle" class="mono">Root PK → спуск по id=9015</text>
  <line x1="767" y1="188" x2="767" y2="225" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="560" y="228" width="415" height="72" class="box"/>
  <text x="767" y="254" text-anchor="middle" class="mono-bold">Лист PK: id=9015 + ВСЕ СТОЛБЦЫ СТРОКИ</text>
  <text x="767" y="278" text-anchor="middle" class="label">amount, currency, metadata, DB_TRX_ID, DB_ROLL_PTR</text>
  <text x="560" y="338" class="mono-bold">Цена выбора PK (UUID CHAR(36) vs BIGINT):</text>
  <text x="560" y="360" class="label">36-байтовый PK копируется в лист КАЖДОГО вторичного индекса</text>
  <text x="560" y="380" class="label">и ломает последовательную вставку в крайний правый лист.</text>
'''
    },
    {
        "dir": "sources/7. MySQL, InnoDB и форки",
        "filename": "innodb-buffer-pool-redo-undo.svg",
        "w": 1040, "h": 450,
        "title": "АРХИТЕКТУРА ДВИЖКА INNODB: BUFFER POOL, CHANGE BUFFER, DOUBLEWRITE, REDO И UNDO",
        "subtitle": "Защита 16-КБ страниц от частичной записи и сканирования таблиц с помощью двухзонного LRU-кэша",
        "caption": "Внутренние компоненты InnoDB: Buffer Pool (New/Old LRU), Change Buffer, Doublewrite Buffer, Redo Log и Undo Log",
        "alt": "Архитектурная схема InnoDB: Buffer Pool с зонами New и Old, Doublewrite Buffer, Redo Log и Undo Log",
        "body": '''
  <rect x="38" y="96" width="585" height="210" rx="6" class="box"/>
  <text x="330" y="124" text-anchor="middle" class="mono-blue">INNODB BUFFER POOL (16 КБ СТРАНИЦЫ В RAM)</text>
  <rect x="60" y="144" width="320" height="76" class="box-accent"/>
  <text x="220" y="170" text-anchor="middle" class="mono-bold">New Sublist (5/8 горячих страниц)</text>
  <text x="220" y="196" text-anchor="middle" class="label">Продвижение только после innodb_old_blocks_time</text>
  <rect x="380" y="144" width="220" height="76" class="box-dark"/>
  <text x="490" y="170" text-anchor="middle" class="mono-bold">Old Sublist (3/8)</text>
  <text x="490" y="196" text-anchor="middle" class="label">Midpoint защищает от mysqldump</text>
  <rect x="60" y="232" width="260" height="54" class="box-warm"/>
  <text x="190" y="264" text-anchor="middle" class="mono-orange">Change Buffer (неуникальные индексы)</text>
  <rect x="340" y="232" width="260" height="54" class="box"/>
  <text x="470" y="264" text-anchor="middle" class="mono">Adaptive Hash Index (O(1) в RAM)</text>

  <rect x="648" y="96" width="354" height="210" rx="6" class="box"/>
  <text x="825" y="124" text-anchor="middle" class="mono-orange">ДИСКОВАЯ НАДЁЖНОСТЬ И MVCC</text>
  <rect x="672" y="144" width="306" height="44" class="box-warm"/>
  <text x="825" y="171" text-anchor="middle" class="mono-orange">Redo Log (последовательный fsync)</text>
  <rect x="672" y="198" width="306" height="44" class="box-dark"/>
  <text x="825" y="225" text-anchor="middle" class="mono-bold">Doublewrite Buffer (от Torn 16 КБ Page)</text>
  <rect x="672" y="252" width="306" height="40" class="box-accent"/>
  <text x="825" y="277" text-anchor="middle" class="mono-blue">Undo Log (откат + Read View MVCC)</text>

  <rect x="38" y="325" width="964" height="90" rx="6" class="box-dark"/>
  <text x="60" y="355" class="mono-bold">Почему 16-КБ страница InnoDB уязвима к порванной записи на Linux (4-КБ блоки ОС):</text>
  <text x="60" y="378" class="label">Перед сбросом грязной страницы в .ibd InnoDB пишет её целиком в Doublewrite Buffer, и только затем — в рабочий файл.</text>
'''
    },
    {
        "dir": "sources/7. MySQL, InnoDB и форки",
        "filename": "innodb-gap-next-key-locks.svg",
        "w": 1040, "h": 440,
        "title": "БЛОКИРОВКИ В INNODB: RECORD LOCK, GAP LOCK И NEXT-KEY LOCK",
        "subtitle": "Как InnoDB в уровне Repeatable Read закрывает интервалы между ключами от вставки фантомных строк",
        "caption": "Схема областей действия Record Lock, Gap Lock и Next-Key Lock (-∞, 10], (10, 25], (25, +∞) в B+ Tree индексе InnoDB",
        "alt": "Диаграмма интервалов Record Lock, Gap Lock и Next-Key Lock на оси ключей индекса InnoDB",
        "body": '''
  <rect x="38" y="96" width="964" height="200" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">ОСЬ КЛЮЧЕЙ ИНДЕКСА (В ТАБЛИЦЕ СУЩЕСТВУЮТ ЗАПИСИ 10, 25 И 40)</text>
  <line x1="65" y1="210" x2="975" y2="210" class="line"/>

  <rect x="85" y="156" width="150" height="36" class="box-dark"/>
  <text x="160" y="179" text-anchor="middle" class="mono-sm">Gap (-∞, 10)</text>
  <circle cx="265" cy="210" r="14" fill="#0369a1"/>
  <text x="265" y="215" text-anchor="middle" font-family="JetBrains Mono" font-size="13" font-weight="700" fill="#ffffff">10</text>
  <text x="265" y="246" text-anchor="middle" class="mono-blue">Record Lock</text>

  <rect x="305" y="156" width="175" height="36" class="box-warm"/>
  <text x="392" y="179" text-anchor="middle" class="mono-orange">Gap (10, 25)</text>
  <circle cx="515" cy="210" r="14" fill="#0369a1"/>
  <text x="515" y="215" text-anchor="middle" font-family="JetBrains Mono" font-size="13" font-weight="700" fill="#ffffff">25</text>

  <rect x="555" y="156" width="175" height="36" class="box-warm"/>
  <text x="642" y="179" text-anchor="middle" class="mono-orange">Gap (25, 40)</text>
  <circle cx="765" cy="210" r="14" fill="#1e293b"/>
  <text x="765" y="215" text-anchor="middle" font-family="JetBrains Mono" font-size="13" font-weight="700" fill="#ffffff">40</text>

  <rect x="805" y="156" width="145" height="36" class="box-dark"/>
  <text x="877" y="179" text-anchor="middle" class="mono-sm">Gap (40, +∞)</text>

  <path d="M 305 262 L 530 262" class="line-orange"/>
  <text x="417" y="282" text-anchor="middle" class="mono-orange">Next-Key Lock = Gap (10, 25) + Record 25 → (10, 25]</text>

  <rect x="38" y="314" width="964" height="98" rx="6" class="box-dark"/>
  <text x="60" y="344" class="mono-bold">Скрытая цена Gap Locks при высокой конкурентности вставок:</text>
  <text x="60" y="368" class="label">Два разных Gap Lock совместимы между собой, но оба блокируют INSERT Intent Lock в этот интервал — это частая причина</text>
  <text x="60" y="388" class="label">Error 1213 (Deadlock) на высоконагруженных очередях; переход на READ COMMITTED отключает Gap Locks.</text>
'''
    },

    # --- МОДУЛЬ 8 (4 схемы) ---
    {
        "dir": "sources/8. Распределённые базы данных, репликация и шардирование",
        "filename": "replication-sync-semisync-async.svg",
        "w": 1040, "h": 450,
        "title": "РЕПЛИКАЦИЯ: СИНХРОННАЯ, ПОЛУСИНХРОННАЯ И АСИНХРОННАЯ",
        "subtitle": "В какой момент клиент получает ответ COMMIT OK — баланс между сетевым RTT и нулевой потерей данных (RPO = 0)",
        "caption": "Таймлайны Async, Semi-Sync (ожидание 1 реплики) и Sync репликации между Leader и Follower-узлами",
        "alt": "Сравнение таймлайнов подтверждения транзакции при асинхронной, полусинхронной и синхронной репликации",
        "body": '''
  <rect x="38" y="96" width="305" height="314" rx="6" class="box"/>
  <text x="190" y="124" text-anchor="middle" class="mono-bold">1. ASYNC (Макс. скорость)</text>
  <rect x="60" y="148" width="260" height="44" class="box-accent"/>
  <text x="190" y="175" text-anchor="middle" class="mono">Leader WAL fsync → OK клиенту</text>
  <line x1="190" y1="192" x2="190" y2="232" class="line-dash" marker-end="url(#arrow)"/>
  <rect x="60" y="235" width="260" height="44" class="box-dark"/>
  <text x="190" y="262" text-anchor="middle" class="mono-sm">WAL уходит репликам позже</text>
  <text x="60" y="316" class="mono-orange">Риск при отказе Leader:</text>
  <text x="60" y="338" class="label">Закоммиченные последние мс</text>
  <text x="60" y="358" class="label">транзакций теряются (RPO &gt; 0).</text>

  <rect x="368" y="96" width="305" height="314" rx="6" class="box-accent"/>
  <text x="520" y="124" text-anchor="middle" class="mono-blue">2. SEMI-SYNC (Баланс)</text>
  <rect x="390" y="148" width="260" height="44" class="box"/>
  <text x="520" y="175" text-anchor="middle" class="mono">Leader WAL + 1 Sync Follower</text>
  <line x1="520" y1="192" x2="520" y2="232" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="390" y="235" width="260" height="44" class="box"/>
  <text x="520" y="262" text-anchor="middle" class="mono-blue">Только потом → OK клиенту</text>
  <text x="390" y="316" class="mono-blue">Устойчивость и скорость:</text>
  <text x="390" y="338" class="label">Отказ 1 узла без потерь (RPO=0);</text>
  <text x="390" y="358" class="label">остальные реплики не тормозят.</text>

  <rect x="698" y="96" width="304" height="314" rx="6" class="box-warm"/>
  <text x="850" y="124" text-anchor="middle" class="mono-orange">3. FULL SYNC (Все узлы)</text>
  <rect x="720" y="148" width="260" height="44" class="box"/>
  <text x="850" y="175" text-anchor="middle" class="mono">Ждёт fsync всех N реплик</text>
  <line x1="850" y1="192" x2="850" y2="232" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="720" y="235" width="260" height="44" class="box"/>
  <text x="850" y="262" text-anchor="middle" class="mono-orange">Хвостовая задержка = max(RTT)</text>
  <text x="720" y="316" class="mono-orange">Хрупкость доступности:</text>
  <text x="720" y="338" class="label">Остановка одной медленной</text>
  <text x="720" y="358" class="label">реплики вешает все записи.</text>
'''
    },
    {
        "dir": "sources/8. Распределённые базы данных, репликация и шардирование",
        "filename": "consistent-hashing-vnodes-ring.svg",
        "w": 1040, "h": 460,
        "title": "КОЛЬЦО КОНСИСТЕНТНОГО ХЕШИРОВАНИЯ С ВИРТУАЛЬНЫМИ УЗЛАМИ (STEP 06)",
        "subtitle": "Почему hash(key) % N перетасовывает почти всю базу при добавлении сервера, а кольцо переносит лишь ~1/N ключей",
        "caption": "Модель ShardRouter (project/step06/sharding.go): кольцо 0..2⁶⁴-1, виртуальные узлы (vnodes) и движение по часовой стрелке",
        "alt": "Кольцо консистентного хеширования с виртуальными узлами и маршрутизацией ключа по часовой стрелке",
        "body": '''
  <rect x="38" y="94" width="485" height="334" rx="6" class="box"/>
  <text x="280" y="122" text-anchor="middle" class="mono-blue">КОЛЬЦО SHA-256 (0 .. 2⁶⁴ - 1)</text>
  <circle cx="280" cy="258" r="115" fill="#f0f9ff" stroke="#0369a1" stroke-width="2.5"/>
  <!-- vnodes -->
  <circle cx="280" cy="143" r="10" fill="#0369a1"/><text x="280" y="130" text-anchor="middle" class="mono-sm">S1#0</text>
  <circle cx="385" cy="212" r="10" fill="#c2410c"/><text x="424" y="216" class="mono-orange">S2#0</text>
  <circle cx="360" cy="340" r="10" fill="#1e293b"/><text x="398" y="355" class="mono-sm">S3#0</text>
  <circle cx="195" cy="340" r="10" fill="#0369a1"/><text x="155" y="355" class="mono-sm">S1#1</text>
  <circle cx="170" cy="222" r="10" fill="#c2410c"/><text x="130" y="226" class="mono-orange">S2#1</text>
  <!-- key point -->
  <rect x="325" y="152" width="12" height="12" fill="#16a34a"/>
  <text x="372" y="152" class="mono-bold">key="acc:42"</text>
  <path d="M 336 164 Q 368 184 380 202" class="line-orange" marker-end="url(#arrowOrange)"/>
  <text x="280" y="254" text-anchor="middle" class="mono-bold">BinarySearchFunc</text>
  <text x="280" y="274" text-anchor="middle" class="label">по часовой стрелке → S2</text>

  <rect x="548" y="94" width="454" height="334" rx="6" class="box-accent"/>
  <text x="775" y="122" text-anchor="middle" class="mono-blue">ЗАЧЕМ НУЖНЫ ВИРТУАЛЬНЫЕ УЗЛЫ (VNODES)</text>
  <rect x="572" y="148" width="406" height="84" class="box"/>
  <text x="590" y="174" class="mono-bold">1. Равномерное распределение без перекосов</text>
  <text x="590" y="198" class="label">С 3 физическими точками сектора сильно не равны.</text>
  <text x="590" y="218" class="label">С 128 vnodes/шард дисбаланс падает до нескольких %.</text>

  <rect x="572" y="246" width="406" height="84" class="box-warm"/>
  <text x="590" y="272" class="mono-orange">2. Минимальная миграция при росте кластера</text>
  <text x="590" y="296" class="label">Добавление 4-го шарда в TestConsistentHashing...</text>
  <text x="590" y="316" class="label">переносит ~25% ключей вместо ~75% при hash % N.</text>

  <text x="572" y="362" class="mono-sm">Код тома: project/step06/sharding.go (ShardRouter)</text>
  <text x="572" y="384" class="label">При добавлении железа более мощному серверу дают больше vnodes.</text>
'''
    },
    {
        "dir": "sources/8. Распределённые базы данных, репликация и шардирование",
        "filename": "partitioning-range-list-hash.svg",
        "w": 1040, "h": 440,
        "title": "ПАРТИЦИОНИРОВАНИЕ ВНУТРИ ОДНОЙ БД: RANGE, LIST И HASH + PRUNING",
        "subtitle": "Разделение гигантской таблицы на компактные партиции для локальных индексов и мгновенного удаления старых месяцев",
        "caption": "Три стратегии декларативного партиционирования (Range, List, Hash) и отсечение лишних партиций Partition Pruning",
        "alt": "Схема стратегий Range, List и Hash партиционирования таблицы и Partition Pruning",
        "body": '''
  <rect x="38" y="96" width="305" height="205" rx="6" class="box-accent"/>
  <text x="190" y="124" text-anchor="middle" class="mono-blue">RANGE (created_at)</text>
  <rect x="62" y="144" width="256" height="36" class="box"/><text x="190" y="167" text-anchor="middle" class="mono-sm">p_2026_03 [Mar 1..Apr 1)</text>
  <rect x="62" y="188" width="256" height="36" class="box"/><text x="190" y="211" text-anchor="middle" class="mono-sm">p_2026_04 [Apr 1..May 1)</text>
  <rect x="62" y="232" width="256" height="36" class="box-warm"/><text x="190" y="255" text-anchor="middle" class="mono-orange">p_2026_05 (горячая!)</text>

  <rect x="368" y="96" width="305" height="205" rx="6" class="box"/>
  <text x="520" y="124" text-anchor="middle" class="mono-bold">LIST (region / currency)</text>
  <rect x="392" y="144" width="256" height="36" class="box-dark"/><text x="520" y="167" text-anchor="middle" class="mono-sm">p_eu IN ('EUR', 'GBP')</text>
  <rect x="392" y="188" width="256" height="36" class="box-dark"/><text x="520" y="211" text-anchor="middle" class="mono-sm">p_ru IN ('RUB')</text>
  <rect x="392" y="232" width="256" height="36" class="box-dark"/><text x="520" y="255" text-anchor="middle" class="mono-sm">p_default (DEFAULT)</text>

  <rect x="698" y="96" width="304" height="205" rx="6" class="box-dark"/>
  <text x="850" y="124" text-anchor="middle" class="mono-bold">HASH (account_id)</text>
  <rect x="722" y="144" width="256" height="36" class="box"/><text x="850" y="167" text-anchor="middle" class="mono-sm">p_0 (MOD 4, REM 0)</text>
  <rect x="722" y="188" width="256" height="36" class="box"/><text x="850" y="211" text-anchor="middle" class="mono-sm">p_1 (MOD 4, REM 1)</text>
  <rect x="722" y="232" width="256" height="36" class="box"/><text x="850" y="255" text-anchor="middle" class="mono-sm">p_2, p_3 (равные бакеты)</text>

  <rect x="38" y="320" width="964" height="92" rx="6" class="box"/>
  <text x="60" y="348" class="mono-blue">PARTITION PRUNING + МГНОВЕННОЕ УДАЛЕНИЕ ИСТОРИИ (DATA RETENTION):</text>
  <text x="60" y="372" class="label">1. Запрос с WHERE created_at &gt;= '2026-05-01' сканирует только p_2026_05 и её маленький B-Tree в RAM.</text>
  <text x="60" y="394" class="label">2. Удаление года архивов: DETACH PARTITION CONCURRENTLY + DROP TABLE за миллисекунды без нагрузки на VACUUM!</text>
'''
    },
    {
        "dir": "sources/8. Распределённые базы данных, репликация и шардирование",
        "filename": "two-phase-commit-blocking-window.svg",
        "w": 1040, "h": 450,
        "title": "ДВУХФАЗНЫЙ КОММИТ (2PC): БЛОКИРУЮЩЕЕ ОКНО ПРИ ОТКАЗЕ КООРДИНАТОРА",
        "subtitle": "Почему участники, ответившие YES в фазе Prepare, обязаны вечно держать блокировки строк до возврата координатора",
        "caption": "Таймлайн протокола 2PC (Prepare / Commit) и зона неопределённости (In-Doubt State) при падении координатора",
        "alt": "Последовательность сообщений 2PC и блокирующее окно при отказе координатора после фазы Prepare",
        "body": '''
  <rect x="38" y="96" width="964" height="225" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">ФАЗЫ ПРОТОКОЛА 2PC (X/OPEN DTP)</text>
  <rect x="65" y="148" width="160" height="44" class="box-accent"/><text x="145" y="175" text-anchor="middle" class="mono-blue">Координатор</text>
  <rect x="65" y="218" width="160" height="44" class="box-dark"/><text x="145" y="245" text-anchor="middle" class="mono-bold">Участник A / B</text>

  <rect x="275" y="142" width="230" height="145" class="box"/>
  <text x="390" y="166" text-anchor="middle" class="mono-bold">Фаза 1: PREPARE</text>
  <text x="295" y="196" class="mono-sm">1. Coordinator → PREPARE</text>
  <text x="295" y="220" class="mono-sm">2. A, B пишут WAL + fsync</text>
  <text x="295" y="244" class="mono-sm">3. A, B отвечают VOTE_YES</text>
  <text x="295" y="270" class="mono-orange">Право на откат потеряно!</text>

  <line x1="505" y1="214" x2="540" y2="214" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="543" y="142" width="225" height="145" class="box-warm"/>
  <text x="655" y="166" text-anchor="middle" class="mono-orange">ОКНО БЛОКИРОВКИ</text>
  <text x="562" y="196" class="mono-orange">Координатор упал!</text>
  <text x="562" y="220" class="label">Участники не знают:</text>
  <text x="562" y="240" class="label">Commit или Abort?</text>
  <text x="562" y="264" class="mono-sm">Row Locks держатся часами!</text>

  <line x1="768" y1="214" x2="800" y2="214" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="803" y="142" width="175" height="145" class="box-accent"/>
  <text x="890" y="166" text-anchor="middle" class="mono-blue">Фаза 2: COMMIT</text>
  <text x="820" y="196" class="mono-sm">4. Log COMMIT</text>
  <text x="820" y="220" class="mono-sm">5. Рассылка узлам</text>
  <text x="820" y="244" class="mono-sm">6. Снятие замков</text>

  <rect x="38" y="338" width="964" height="80" rx="6" class="box-dark"/>
  <text x="60" y="366" class="mono-bold">Вывод: 2PC является блокирующим протоколом — именно поэтому в микросервисах и шардированных системах</text>
  <text x="60" y="390" class="label">его либо заменяют на Saga + Outbox, либо защищают сам координатор консенсусом (Raft/Paxos, как в CockroachDB).</text>
'''
    },

    # --- МОДУЛЬ 9 (4 схемы) ---
    {
        "dir": "sources/9. NoSQL, аналитические и специализированные базы",
        "filename": "redis-event-loop-pipelining.svg",
        "w": 1040, "h": 440,
        "title": "REDIS: ОДНОПОТОЧНЫЙ EVENT LOOP (EPOLL) И ПАЙПЛАЙНИНГ В GO",
        "subtitle": "Почему 100 одиночных команд упираются в сетевой RTT, а Pipeline проталкивает их за 1 круговой проход без блокировок",
        "caption": "Механика однопоточного цикла событий Redis (ae / epoll) и ускорение через RESP Pipelining из Go",
        "alt": "Сравнение одиночных запросов и RESP Pipelining в однопоточном event loop Redis",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box"/>
  <text x="270" y="124" text-anchor="middle" class="mono-blue">ОДНОПОТОЧНЫЙ EVENT LOOP (AE / EPOLL)</text>
  <rect x="65" y="148" width="180" height="72" class="box-dark"/>
  <text x="155" y="176" text-anchor="middle" class="mono-bold">I/O Threads (6.0+)</text>
  <text x="155" y="198" text-anchor="middle" class="label">Парсинг сокетов RESP</text>
  <line x1="245" y1="184" x2="285" y2="184" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="288" y="148" width="190" height="72" class="box-accent"/>
  <text x="383" y="176" text-anchor="middle" class="mono-blue">1 Main Thread</text>
  <text x="383" y="198" text-anchor="middle" class="label">Исполнение команд</text>
  <rect x="65" y="242" width="413" height="142" class="box-warm"/>
  <text x="85" y="270" class="mono-orange">Цена блокирующей команды:</text>
  <text x="85" y="294" class="label">Любая долгая операция (KEYS *, гигантский HGETALL)</text>
  <text x="85" y="316" class="label">останавливает 100% остальных клиентов на этом ядре.</text>
  <text x="85" y="346" class="label">fork() при RDB/AOF создаёт риск OOM из-за Copy-on-Write.</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box-accent"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">RTT: ПОСЛЕДОВАТЕЛЬНО ПРОТИВ PIPELINE</text>
  <rect x="558" y="148" width="420" height="94" class="box-warm"/>
  <text x="578" y="174" class="mono-orange">100 запросов по 1 команде = 100 × RTT</text>
  <text x="578" y="198" class="mono-sm">GET k1 → ответ → GET k2 → ответ ... (50 мс при RTT 0.5 мс)</text>
  <text x="578" y="220" class="label">99% времени горутина спит в netpoller, ожидая сеть.</text>

  <rect x="558" y="258" width="420" height="126" class="box"/>
  <text x="578" y="286" class="mono-blue">Pipeline (1 батч из 100 команд) = 1 × RTT</text>
  <text x="578" y="310" class="mono-sm">[GET k1, GET k2, ..., GET k100] → [v1, v2, ..., v100]</text>
  <text x="578" y="336" class="label">Резкий рост пропускной способности и экономия syscalls.</text>
  <text x="578" y="358" class="label">В отличие от MULTI/EXEC, Pipeline не блокирует другие клиенты.</text>
'''
    },
    {
        "dir": "sources/9. NoSQL, аналитические и специализированные базы",
        "filename": "lsm-tree-memtable-sstable.svg",
        "w": 1040, "h": 450,
        "title": "АРХИТЕКТУРА LSM-TREE: COMMITLOG + MEMTABLE → SSTABLE + BLOOM FILTER",
        "subtitle": "Как Cassandra, RocksDB и Pebble превращают случайную запись на диск в строго последовательную",
        "caption": "Путь записи и чтения в LSM-Tree: CommitLog, Memtable (RAM), Flush в иммутабельные SSTable L0..L2, Bloom Filter и Compaction",
        "alt": "Схема работы LSM-Tree с CommitLog, Memtable, слоями SSTable L0-L2, Bloom Filter и фоновой компактификацией",
        "body": '''
  <rect x="38" y="96" width="320" height="215" rx="6" class="box-accent"/>
  <text x="198" y="124" text-anchor="middle" class="mono-blue">1. ЗАПИСЬ (APPEND-ONLY O(1))</text>
  <rect x="62" y="146" width="272" height="54" class="box-warm"/>
  <text x="198" y="170" text-anchor="middle" class="mono-orange">CommitLog (Диск, seq write)</text>
  <text x="198" y="190" text-anchor="middle" class="label">Защита от падения питания</text>
  <rect x="62" y="218" width="272" height="66" class="box"/>
  <text x="198" y="245" text-anchor="middle" class="mono-bold">Memtable (SkipList в RAM)</text>
  <text x="198" y="266" text-anchor="middle" class="label">Сортировка ключей на лету</text>

  <line x1="358" y1="250" x2="408" y2="250" class="line-blue" marker-end="url(#arrowBlue)"/>
  <text x="383" y="236" text-anchor="middle" class="mono-sm">Flush</text>

  <rect x="411" y="96" width="591" height="215" rx="6" class="box"/>
  <text x="706" y="124" text-anchor="middle" class="mono-bold">2. ИММУТАБЕЛЬНЫЕ SSTABLE НА ДИСКЕ + COMPACTION</text>
  <rect x="435" y="146" width="160" height="72" class="box-dark"/>
  <text x="515" y="172" text-anchor="middle" class="mono-bold">Level 0 (L0)</text>
  <text x="515" y="196" text-anchor="middle" class="label">Сырые сбросы (overlap)</text>
  <line x1="595" y1="182" x2="625" y2="182" class="line" marker-end="url(#arrow)"/>
  <rect x="628" y="146" width="165" height="72" class="box-accent"/>
  <text x="710" y="172" text-anchor="middle" class="mono-blue">Level 1 (L1)</text>
  <text x="710" y="196" text-anchor="middle" class="label">Слито, без пересечений</text>
  <line x1="793" y1="182" x2="823" y2="182" class="line" marker-end="url(#arrow)"/>
  <rect x="826" y="146" width="155" height="72" class="box-accent"/>
  <text x="903" y="172" text-anchor="middle" class="mono-blue">Level 2 (L2)</text>
  <text x="903" y="196" text-anchor="middle" class="label">10× объёма L1</text>

  <rect x="435" y="234" width="546" height="56" class="box-warm"/>
  <text x="708" y="259" text-anchor="middle" class="mono-orange">Tombstone + Compaction (STCS / LCS / TWCS)</text>
  <text x="708" y="278" text-anchor="middle" class="label">Удаление — это запись маркера; физически место освобождается только при слиянии</text>

  <rect x="38" y="330" width="964" height="88" rx="6" class="box-dark"/>
  <text x="60" y="358" class="mono-bold">Ускорение чтения: Bloom Filter в RAM (Filter.db) мгновенно отсекает SSTable, где ключа точно нет;</text>
  <text x="60" y="382" class="label">индекс Index.db находит смещение блока в Data.db — иначе пришлось бы проверять десятки файлов на диске.</text>
'''
    },
    {
        "dir": "sources/9. NoSQL, аналитические и специализированные базы",
        "filename": "clickhouse-columnar-mergetree.svg",
        "w": 1040, "h": 450,
        "title": "CLICKHOUSE MERGETREE: КОЛОНКИ, ГРАНУЛЫ 8192 И ВЕКТОРИЗАЦИЯ (STEP 07)",
        "subtitle": "Почему OLAP читает только нужные столбцы, сжимает однородные массивы в 10× и избегает одиночных INSERT",
        "caption": "Схема колоночного парта ClickHouse MergeTree: файлы *.bin, метки *.mrk2, разреженный индекс primary.idx и MergeTreeSimulator",
        "alt": "Архитектура хранения колонок в ClickHouse MergeTree с гранулами 8192 и разреженным первичным индексом",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box"/>
  <text x="270" y="124" text-anchor="middle" class="mono-blue">СТРОКОВОЕ (OLTP) vs КОЛОНОЧНОЕ (OLAP)</text>
  <rect x="62" y="148" width="418" height="72" class="box-warm"/>
  <text x="271" y="174" text-anchor="middle" class="mono-orange">Row-Oriented (PostgreSQL Heap)</text>
  <text x="271" y="198" text-anchor="middle" class="mono-sm">[id, date, curr, kind, desc, amount] → читает все поля!</text>

  <rect x="62" y="238" width="418" height="148" class="box-accent"/>
  <text x="271" y="264" text-anchor="middle" class="mono-blue">Column-Oriented (001_ledger_events.sql)</text>
  <text x="82" y="292" class="mono-sm">currency.bin:    [RUB, RUB, RUB, USD, ...]</text>
  <text x="82" y="316" class="mono-sm">amount_minor.bin:[500, -200, 800, 100, ...]</text>
  <text x="82" y="344" class="label">SUM(amount) читает только 2 файла + SIMD AVX2!</text>
  <text x="82" y="366" class="mono-sm">В Go: MergeTreeSimulator (project/step07/)</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">АНАТОМИЯ ПАРТА MERGETREE (ГРАНУЛА = 8 192 СТРОК)</text>
  <rect x="558" y="148" width="195" height="82" class="box-dark"/>
  <text x="655" y="174" text-anchor="middle" class="mono-bold">primary.idx (RAM)</text>
  <text x="655" y="198" text-anchor="middle" class="label">1 ключ на каждые</text>
  <text x="655" y="216" text-anchor="middle" class="label">8 192 строк (разреженный)</text>

  <line x1="753" y1="189" x2="788" y2="189" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="791" y="148" width="188" height="82" class="box-accent"/>
  <text x="885" y="174" text-anchor="middle" class="mono-blue">marks (*.mrk2)</text>
  <text x="885" y="198" text-anchor="middle" class="label">Смещение сжатого</text>
  <text x="885" y="216" text-anchor="middle" class="label">блока LZ4/ZSTD</text>

  <rect x="558" y="248" width="420" height="138" class="box-warm"/>
  <text x="578" y="276" class="mono-orange">Правило батчинга и SummingMergeTree:</text>
  <text x="578" y="300" class="label">1. Вставляйте пачками (10k–100k строк), иначе фоновые</text>
  <text x="578" y="320" class="label">   слияния не успеют и упрутся в Too many parts.</text>
  <text x="578" y="344" class="label">2. Витрина mv_daily_turnover агрегирует данные инкрементально</text>
  <text x="578" y="364" class="label">   при вставке блока — в SELECT нужен SUM/GROUP BY или FINAL.</text>
'''
    },
    {
        "dir": "sources/9. NoSQL, аналитические и специализированные базы",
        "filename": "hnsw-multilayer-vector-graph.svg",
        "w": 1040, "h": 440,
        "title": "ВЕКТОРНЫЙ ИНДЕКС HNSW: ИЕРАРХИЯ СЛОЁВ И ПРИБЛИЖЁННЫЙ ПОИСК K-NN",
        "subtitle": "Как многослойный граф на малых мирах (Small World) находит ближайшие эмбеддинги за O(log N) без полного скана",
        "caption": "Схема многослойного графа HNSW: быстрые длинные прыжки на верхнем слое и точное уточнение соседей на базовом слое 0",
        "alt": "Схема многослойного графа HNSW для приближённого поиска ближайших векторов",
        "body": '''
  <rect x="38" y="96" width="600" height="314" rx="6" class="box"/>
  <text x="338" y="124" text-anchor="middle" class="mono-blue">ЖАДНЫЙ СПУСК ОТ ЭКСПРЕСС-СЛОЯ К БАЗОВОМУ СЛОЮ 0</text>
  <!-- Layer 2 -->
  <rect x="65" y="142" width="545" height="68" class="box-dark"/>
  <text x="80" y="166" class="mono-sm">Слой 2 (редкие хабы)</text>
  <circle cx="240" cy="176" r="8" fill="#0369a1"/><line x1="248" y1="176" x2="472" y2="176" class="line-blue" marker-end="url(#arrowBlue)"/>
  <circle cx="480" cy="176" r="8" fill="#c2410c"/>
  <!-- Layer 1 -->
  <rect x="65" y="222" width="545" height="68" class="box-accent"/>
  <text x="80" y="246" class="mono-sm">Слой 1 (средний шаг)</text>
  <circle cx="240" cy="256" r="7" fill="#475569"/><circle cx="360" cy="256" r="7" fill="#475569"/>
  <circle cx="480" cy="256" r="8" fill="#c2410c"/><line x1="480" y1="184" x2="480" y2="246" class="line-dash" marker-end="url(#arrow)"/>
  <line x1="488" y1="256" x2="538" y2="256" class="line-orange" marker-end="url(#arrowOrange)"/>
  <circle cx="546" cy="256" r="8" fill="#c2410c"/>
  <!-- Layer 0 -->
  <rect x="65" y="302" width="545" height="84" class="box"/>
  <text x="80" y="326" class="mono-sm">Слой 0 (все векторы)</text>
  <circle cx="200" cy="352" r="6" fill="#475569"/><circle cx="280" cy="352" r="6" fill="#475569"/>
  <circle cx="360" cy="352" r="6" fill="#475569"/><circle cx="440" cy="352" r="6" fill="#475569"/>
  <circle cx="546" cy="352" r="10" fill="#16a34a"/>
  <line x1="546" y1="264" x2="546" y2="340" class="line-orange" marker-end="url(#arrowOrange)"/>
  <text x="546" y="376" text-anchor="middle" class="mono-bold">Найден k-NN</text>

  <rect x="665" y="96" width="337" height="314" rx="6" class="box-accent"/>
  <text x="833" y="124" text-anchor="middle" class="mono-blue">ТРИ РЫЧАГА HNSW И ПАМЯТЬ</text>
  <rect x="688" y="148" width="290" height="72" class="box"/>
  <text x="705" y="174" class="mono-bold">m и ef_construction</text>
  <text x="705" y="198" class="label">Степень графа и точность сборки</text>
  <rect x="688" y="234" width="290" height="72" class="box-warm"/>
  <text x="705" y="260" class="mono-orange">ef_search + iterative_scan</text>
  <text x="705" y="284" class="label">Точность vs ms и фильтр tenant_id</text>
  <text x="688" y="336" class="label">Граф обязан лежать в RAM; для</text>
  <text x="688" y="356" class="label">экономии применяют halfvec / PQ</text>
  <text x="688" y="376" class="label">и гибрид RRF с tsvector.</text>
'''
    },

    # --- МОДУЛЬ 10 (3 схемы) ---
    {
        "dir": "sources/10. Практика БД в Go и HighLoad-эксплуатация",
        "filename": "database-sql-pool-states.svg",
        "w": 1040, "h": 450,
        "title": "ПУЛ СОЕДИНЕНИЙ DATABASE/SQL В GO: МАШИНА СОСТОЯНИЙ, TX-PINNING И ERRBADCONN",
        "subtitle": "Как *sql.DB управляет idle/inUse сокетами, почему транзакция прибивает соединение и как работает db.retry",
        "caption": "Внутренняя механика пула *sql.DB: freeConn (LIFO), connOpener, блокировка при MaxOpenConns, Tx-pinning и повтор при ErrBadConn",
        "alt": "Схема состояний соединений в пуле database/sql, работы connOpener и привязки транзакции Tx",
        "body": '''
  <rect x="38" y="96" width="964" height="205" rx="6" class="box"/>
  <text x="60" y="124" class="mono-blue">ЖИЗНЕННЫЙ ЦИКЛ СОЕДИНЕНИЯ В ПУЛЕ *SQL.DB (GO STDLIB)</text>
  <rect x="60" y="152" width="190" height="90" class="box-accent"/>
  <text x="155" y="180" text-anchor="middle" class="mono-bold">Query / Exec</text>
  <text x="155" y="202" text-anchor="middle" class="label">Берёт с конца freeConn</text>
  <text x="155" y="222" text-anchor="middle" class="label">(LIFO — свежее)</text>

  <line x1="250" y1="197" x2="295" y2="197" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="298" y="152" width="210" height="90" class="box-dark"/>
  <text x="403" y="178" text-anchor="middle" class="mono-bold">freeConn (Idle)</text>
  <text x="403" y="200" text-anchor="middle" class="label">Лимит MaxIdleConns</text>
  <text x="403" y="220" text-anchor="middle" class="label">TTL: ConnMaxLifetime</text>

  <line x1="508" y1="197" x2="553" y2="197" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="556" y="152" width="215" height="90" class="box-warm"/>
  <text x="663" y="178" text-anchor="middle" class="mono-orange">Если open == MaxOpen</text>
  <text x="663" y="200" text-anchor="middle" class="label">Горутина ждёт в очереди</text>
  <text x="663" y="220" text-anchor="middle" class="label">connRequests до ctx.Done()</text>

  <line x1="771" y1="197" x2="810" y2="197" class="line" marker-end="url(#arrow)"/>

  <rect x="813" y="152" width="168" height="90" class="box"/>
  <text x="897" y="178" text-anchor="middle" class="mono-bold">connOpener</text>
  <text x="897" y="200" text-anchor="middle" class="label">Фоновая горутина</text>
  <text x="897" y="220" text-anchor="middle" class="label">асинхронного Dial</text>

  <rect x="38" y="318" width="465" height="100" rx="6" class="box-warm"/>
  <text x="60" y="346" class="mono-orange">Tx-Pinning и Prepared Statements</text>
  <text x="60" y="370" class="label">BeginTx привязывает 1 соединение до Commit/Rollback (забыли rows.Close —</text>
  <text x="60" y="390" class="label">исчерпали пул!). db.Prepare пересоздаётся на каждом новом соединении пула.</text>

  <rect x="533" y="318" width="469" height="100" rx="6" class="box-accent"/>
  <text x="555" y="346" class="mono-blue">Повтор при driver.ErrBadConn (ledgerdriver test)</text>
  <text x="555" y="370" class="label">QueryContext/ExecContext повторяются до maxBadConnRetries=2 на</text>
  <text x="555" y="390" class="label">кэшированном коннекте + 1 alwaysNewConn; PingContext — вне db.retry.</text>
'''
    },
    {
        "dir": "sources/10. Практика БД в Go и HighLoad-эксплуатация",
        "filename": "cache-aside-singleflight-stampede.svg",
        "w": 1040, "h": 450,
        "title": "ЗАЩИТА ОТ CACHE STAMPEDE: CACHE-ASIDE + TTL JITTER + SINGLEFLIGHT",
        "subtitle": "Как SingleflightCache (project/step07/) сворачивает 32 одновременных промаха кэша в ровно 1 запрос к базе данных",
        "caption": "Сравнение лавины промахов (Cache Stampede) и слияния параллельных запросов через Singleflight + TTL с джиттером",
        "alt": "Схема защиты Cache-Aside от Cache Stampede с помощью Singleflight и случайного джиттера TTL",
        "body": '''
  <rect x="38" y="96" width="465" height="314" rx="6" class="box-warm"/>
  <text x="270" y="124" text-anchor="middle" class="mono-orange">БЕЗ ЗАЩИТЫ: CACHE STAMPEDE (THUNDERING HERD)</text>
  <rect x="65" y="152" width="160" height="100" class="box"/>
  <text x="145" y="182" text-anchor="middle" class="mono-bold">1 000 горутин</text>
  <text x="145" y="206" text-anchor="middle" class="label">Одновременный</text>
  <text x="145" y="226" text-anchor="middle" class="label">Cache Miss (TTL=0)</text>
  <line x1="225" y1="180" x2="295" y2="165" class="line-orange" marker-end="url(#arrowOrange)"/>
  <line x1="225" y1="202" x2="295" y2="202" class="line-orange" marker-end="url(#arrowOrange)"/>
  <line x1="225" y1="224" x2="295" y2="240" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="298" y="152" width="180" height="100" class="box"/>
  <text x="388" y="182" text-anchor="middle" class="mono-orange">PostgreSQL</text>
  <text x="388" y="206" text-anchor="middle" class="label">1 000 одинаковых</text>
  <text x="388" y="226" text-anchor="middle" class="label">тяжёлых запросов!</text>
  <text x="65" y="294" class="label">Пул *sql.DB исчерпывается за миллисекунды,</text>
  <text x="65" y="316" class="label">CPU базы 100%, каскадный таймаут всего сервиса.</text>

  <rect x="533" y="96" width="469" height="314" rx="6" class="box-accent"/>
  <text x="767" y="124" text-anchor="middle" class="mono-blue">SINGLEFLIGHT + JITTER (STEP07/CACHE_OLAP.GO)</text>
  <rect x="560" y="152" width="130" height="100" class="box"/>
  <text x="625" y="182" text-anchor="middle" class="mono-bold">32 горутины</text>
  <text x="625" y="206" text-anchor="middle" class="label">ключ "acc:42"</text>
  <line x1="690" y1="202" x2="725" y2="202" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="728" y="152" width="125" height="100" class="box-accent"/>
  <text x="790" y="182" text-anchor="middle" class="mono-blue">inflight</text>
  <text x="790" y="206" text-anchor="middle" class="label">wg.Wait()</text>
  <text x="790" y="226" text-anchor="middle" class="label">31 ждут 1-го</text>
  <line x1="853" y1="202" x2="882" y2="202" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="885" y="152" width="95" height="100" class="box"/>
  <text x="932" y="190" text-anchor="middle" class="mono-bold">1 SQL</text>
  <text x="932" y="212" text-anchor="middle" class="label">hit=1</text>
  <text x="560" y="294" class="mono-blue">Случайный джиттер TTL ±15%:</text>
  <text x="560" y="316" class="label">ключ истекает не синхронно в 00:00, а плавно;</text>
  <text x="560" y="338" class="label">при Transfer кэш сразу инвалидируется.</text>
'''
    },
    {
        "dir": "sources/10. Практика БД в Go и HighLoad-эксплуатация",
        "filename": "expand-and-contract-phases.svg",
        "w": 1040, "h": 440,
        "title": "МИГРАЦИИ БЕЗ ПРОСТОЯ: ЧЕТЫРЕ ШАГА EXPAND-AND-CONTRACT",
        "subtitle": "Как переименовать или изменить столбец на живой базе, пока в Kubernetes одновременно работают версии кода N и N+1",
        "caption": "Схема четырёх этапов zero-downtime миграции Expand-and-Contract с окном совместимости версий сервиса N и N+1",
        "alt": "Четыре этапа миграции базы данных Expand-and-Contract без остановки сервиса",
        "body": '''
  <rect x="38" y="96" width="225" height="225" rx="6" class="box-accent"/>
  <text x="150" y="124" text-anchor="middle" class="mono-blue">1. EXPAND (БД)</text>
  <text x="55" y="158" class="mono-sm">ADD COLUMN new_col</text>
  <text x="55" y="180" class="mono-sm">  NULL (без lock!)</text>
  <text x="55" y="210" class="label">Версия N ничего не</text>
  <text x="55" y="230" class="label">знает о new_col и</text>
  <text x="55" y="250" class="label">продолжает работать.</text>

  <line x1="263" y1="208" x2="288" y2="208" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="291" y="96" width="225" height="225" rx="6" class="box"/>
  <text x="403" y="124" text-anchor="middle" class="mono-bold">2. DUAL-WRITE (N+1)</text>
  <text x="308" y="158" class="mono-sm">Код N+1 пишет в</text>
  <text x="308" y="180" class="mono-sm">old_col и new_col</text>
  <text x="308" y="210" class="label">Батчевый backfill</text>
  <text x="308" y="230" class="label">старых строк порциями</text>
  <text x="308" y="250" class="label">по PK с паузами.</text>

  <line x1="516" y1="208" x2="541" y2="208" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="544" y="96" width="225" height="225" rx="6" class="box-dark"/>
  <text x="656" y="124" text-anchor="middle" class="mono-bold">3. SWITCH READ (N+2)</text>
  <text x="561" y="158" class="mono-sm">CHECK NOT VALID →</text>
  <text x="561" y="180" class="mono-sm">VALIDATE CONSTRAINT</text>
  <text x="561" y="210" class="label">Чтение переключено на</text>
  <text x="561" y="230" class="label">new_col; old_col больше</text>
  <text x="561" y="250" class="label">не запрашивается.</text>

  <line x1="769" y1="208" x2="794" y2="208" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="797" y="96" width="205" height="225" rx="6" class="box-warm"/>
  <text x="899" y="124" text-anchor="middle" class="mono-orange">4. CONTRACT (БД)</text>
  <text x="812" y="158" class="mono-sm">DROP COLUMN old_col</text>
  <text x="812" y="180" class="mono-sm">с lock_timeout='2s'</text>
  <text x="812" y="210" class="label">Только после полного</text>
  <text x="812" y="230" class="label">ухода всех подов N.</text>

  <rect x="38" y="338" width="964" height="78" rx="6" class="box-dark"/>
  <text x="60" y="366" class="mono-bold">Золотое правило: НИКОГДА не делайте RENAME COLUMN или NOT NULL на горячей таблице за 1 миграцию —</text>
  <text x="60" y="390" class="label">используйте SET lock_timeout, CREATE INDEX CONCURRENTLY и явный список колонок вместо SELECT * в Go.</text>
'''
    },
]


def main() -> int:
    assert len(DIAGRAMS) == 35, f"expected 35 diagrams, got {len(DIAGRAMS)}"
    for item in DIAGRAMS:
        media_dir = os.path.join(ROOT, item["dir"], "media")
        os.makedirs(media_dir, exist_ok=True)
        svg = wrap_svg(item["w"], item["h"], item["title"], item["subtitle"], item["body"])
        ET.fromstring(svg)
        dest = os.path.join(media_dir, item["filename"])
        with open(dest, "w", encoding="utf-8", newline="\n") as fp:
            fp.write(svg)
        kb = len(svg.encode("utf-8")) / 1024
        size = image_size(dest)
        if kb > 300 or (size and max(size) > 1600):
            raise RuntimeError(f"{dest}: size {size}, {kb:.1f} KB exceeds limits")
        credits_path = os.path.join(media_dir, "credits.toml")
        block = credits_block(
            item["filename"],
            {
                "caption": item["caption"],
                "alt": item["alt"],
                "author": "Серия go-textbook-v2",
                "license": "own",
                "invert_dark": True,
            },
            [f"Техническая SVG-схема Тома 2 ({size[0]}×{size[1]}, {kb:.1f} КБ)"],
        )
        write_credits(credits_path, item["filename"], block)
        load_credits(credits_path)
        print(f"OK   {os.path.relpath(dest, ROOT)} ({size[0]}×{size[1]}, {kb:.1f} КБ)")
    print(f"\nСгенерировано схем: {len(DIAGRAMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
