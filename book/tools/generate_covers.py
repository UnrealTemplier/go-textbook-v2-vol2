#!/usr/bin/env python3
"""
book/tools/generate_covers.py
Генерация 10 обложек разделов Тома 2 в едином стиле инженерного чертежа
(Bell Labs Technical Journal / Blueprint, 1200×675, светлый фон #fcfaf5 + тёмные линии + акценты #0369a1 и #c2410c,
invert_dark = true, license = "own") и обновление соответствующих media/credits.toml.
"""

import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from book.tools.commons_fetch import credits_block, write_credits  # noqa: E402
from engine.media import load_credits  # noqa: E402

HEADER = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
  <defs>
    <pattern id="minorGrid" width="25" height="25" patternUnits="userSpaceOnUse">
      <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e2e8f0" stroke-width="0.8"/>
    </pattern>
    <pattern id="majorGrid" width="125" height="125" patternUnits="userSpaceOnUse">
      <rect width="125" height="125" fill="url(#minorGrid)"/>
      <path d="M 125 0 L 0 0 0 125" fill="none" stroke="#cbd5e1" stroke-width="1.4"/>
    </pattern>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1e293b"/>
    </marker>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0369a1"/>
    </marker>
    <marker id="arrowOrange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c2410c"/>
    </marker>
  </defs>
  <style>
    .bg { fill: #fcfaf5; }
    .frame { fill: none; stroke: #1e293b; stroke-width: 2.5; }
    .inner-frame { fill: none; stroke: #475569; stroke-width: 1; }
    .box { fill: #ffffff; stroke: #1e293b; stroke-width: 2; }
    .box-accent { fill: #f0f9ff; stroke: #0369a1; stroke-width: 2.2; }
    .box-warm { fill: #fff7ed; stroke: #c2410c; stroke-width: 2.2; }
    .box-dark { fill: #f1f5f9; stroke: #334155; stroke-width: 2; }
    .line { fill: none; stroke: #1e293b; stroke-width: 2.2; }
    .line-blue { fill: none; stroke: #0369a1; stroke-width: 2.4; }
    .line-orange { fill: none; stroke: #c2410c; stroke-width: 2.4; }
    .line-dash { fill: none; stroke: #64748b; stroke-width: 1.6; stroke-dasharray: 6 4; }
    .title { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 23px; font-weight: 700; fill: #0f172a; }
    .sub { font-family: "Inter", "IBM Plex Sans", sans-serif; font-size: 15px; fill: #334155; }
    .mono { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 14px; fill: #0f172a; }
    .mono-bold { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 15px; font-weight: 700; fill: #0f172a; }
    .mono-blue { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 14px; font-weight: 700; fill: #0369a1; }
    .mono-orange { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 14px; font-weight: 700; fill: #c2410c; }
    .label { font-family: "Inter", "IBM Plex Sans", sans-serif; font-size: 13px; fill: #475569; }
    .stamp { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 11px; fill: #475569; letter-spacing: 0.5px; }
  </style>
  <rect width="1200" height="675" class="bg"/>
  <rect x="25" y="25" width="1150" height="625" fill="url(#majorGrid)"/>
  <rect x="25" y="25" width="1150" height="625" class="frame"/>
  <rect x="31" y="31" width="1138" height="613" class="inner-frame"/>
'''


def footer_block(code: str, title: str, subtitle: str) -> str:
    return f'''
  <rect x="31" y="31" width="1138" height="68" fill="#f8fafc" stroke="#1e293b" stroke-width="1.5"/>
  <rect x="31" y="31" width="135" height="68" fill="#0369a1"/>
  <text x="98" y="72" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="22" font-weight="700" fill="#ffffff">{code}</text>
  <text x="188" y="61" class="title">{title}</text>
  <text x="188" y="84" class="sub">{subtitle}</text>

  <rect x="775" y="592" width="394" height="52" fill="#f8fafc" stroke="#1e293b" stroke-width="1.5"/>
  <line x1="910" y1="592" x2="910" y2="644" stroke="#475569" stroke-width="1"/>
  <line x1="1060" y1="592" x2="1060" y2="644" stroke="#475569" stroke-width="1"/>
  <text x="842" y="613" text-anchor="middle" class="stamp">GO-TEXTBOOK-V2</text>
  <text x="842" y="632" text-anchor="middle" class="mono-blue">VOL.2 · GO 1.24</text>
  <text x="985" y="613" text-anchor="middle" class="stamp">ЛИСТ / ЧЕРТЁЖ</text>
  <text x="985" y="632" text-anchor="middle" class="mono">{code}</text>
  <text x="1115" y="613" text-anchor="middle" class="stamp">МАСШТАБ</text>
  <text x="1115" y="632" text-anchor="middle" class="mono">1 : 1</text>
</svg>
'''


COVERS = [
    {
        "dir": "sources/1. Фундамент баз данных и моделирование",
        "filename": "cover-module-01-modeling.svg",
        "code": "MOD 01",
        "title": "ФУНДАМЕНТ БАЗ ДАННЫХ И РЕЛЯЦИОННОЕ МОДЕЛИРОВАНИЕ",
        "subtitle": "16 глав: множества против объектов, ключи и ограничения, 3VL NULL, нормализация 1NF–BCNF и схема LedgerPulse",
        "caption": "Инженерная карта Модуля 1: от аномалий и трёхзначной логики NULL к нормализованной ER-схеме LedgerPulse в project/step01/",
        "alt": "Инженерный чертёж Модуля 1: реляционная модель, нормализация 1NF-3NF, ограничения целостности и таблицы LedgerPulse",
        "body": '''
  <rect x="60" y="135" width="320" height="240" rx="6" class="box"/>
  <text x="220" y="164" text-anchor="middle" class="mono-blue">1. СДВИГ К МНОЖЕСТВАМ</text>
  <rect x="85" y="185" width="270" height="52" class="box-warm"/>
  <text x="220" y="208" text-anchor="middle" class="mono-orange">JSON-файл / Граф объектов</text>
  <text x="220" y="226" text-anchor="middle" class="label">Гонки, O(N) перезапись, нет связей</text>
  <line x1="220" y1="237" x2="220" y2="275" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="85" y="278" width="270" height="72" class="box-accent"/>
  <text x="220" y="302" text-anchor="middle" class="mono-blue">Реляционные отношения</text>
  <text x="220" y="322" text-anchor="middle" class="mono">PK · FK · CHECK · NOT NULL</text>
  <text x="220" y="340" text-anchor="middle" class="label">Страницы 8 КБ и 3VL (TRUE/FALSE/UNK)</text>

  <rect x="425" y="135" width="340" height="240" rx="6" class="box"/>
  <text x="595" y="164" text-anchor="middle" class="mono-blue">2. НОРМАЛИЗАЦИЯ (1NF → BCNF)</text>
  <rect x="450" y="185" width="290" height="44" class="box-dark"/>
  <text x="595" y="212" text-anchor="middle" class="mono-bold">1NF: Атомарные поля без списков</text>
  <rect x="450" y="242" width="290" height="44" class="box-dark"/>
  <text x="595" y="269" text-anchor="middle" class="mono-bold">2NF: Полная зависимость от PK</text>
  <rect x="450" y="299" width="290" height="52" class="box-accent"/>
  <text x="595" y="323" text-anchor="middle" class="mono-blue">3NF / BCNF: Только от ключа</text>
  <text x="595" y="341" text-anchor="middle" class="label">Ноль аномалий вставки и удаления</text>

  <rect x="810" y="135" width="330" height="240" rx="6" class="box-accent"/>
  <text x="975" y="164" text-anchor="middle" class="mono-blue">3. СХЕМА LEDGERPULSE (STEP 01)</text>
  <rect x="835" y="186" width="280" height="52" class="box"/>
  <text x="975" y="208" text-anchor="middle" class="mono-bold">accounts (BIGINT balance &gt;= 0)</text>
  <text x="975" y="226" text-anchor="middle" class="label">UNIQUE external_id · CHECK currency</text>
  <rect x="835" y="250" width="280" height="48" class="box"/>
  <text x="975" y="271" text-anchor="middle" class="mono-bold">transactions (reference_id)</text>
  <text x="975" y="288" text-anchor="middle" class="label">1 : N проводки</text>
  <rect x="835" y="310" width="280" height="48" class="box-warm"/>
  <text x="975" y="331" text-anchor="middle" class="mono-orange">ledger_entries (SUM = 0)</text>
  <text x="975" y="348" text-anchor="middle" class="label">Двойная запись без float64</text>

  <line x1="380" y1="255" x2="422" y2="255" class="line-blue" marker-end="url(#arrowBlue)"/>
  <line x1="765" y1="255" x2="807" y2="255" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="60" y="405" width="1080" height="160" rx="6" class="box"/>
  <text x="85" y="438" class="mono-bold">ГРАНИЦА ПОЗИЦИОННОГО И ПРОИЗВОЛЬНОГО АДРЕСА: ОТ ПЕРФОКАРТ К БУФЕРНОМУ ПУЛУ</text>
  <rect x="85" y="458" width="235" height="82" class="box-dark"/>
  <text x="202" y="486" text-anchor="middle" class="mono-bold">OLTP vs OLAP</text>
  <text x="202" y="510" text-anchor="middle" class="label">Строки 8 КБ vs колонки</text>
  <rect x="350" y="458" width="235" height="82" class="box-dark"/>
  <text x="467" y="486" text-anchor="middle" class="mono-bold">Денормализация</text>
  <text x="467" y="510" text-anchor="middle" class="label">Предрасчитанный balance</text>
  <rect x="615" y="458" width="235" height="82" class="box-warm"/>
  <text x="732" y="486" text-anchor="middle" class="mono-orange">Антипаттерны</text>
  <text x="732" y="510" text-anchor="middle" class="label">EAV · FLOAT · UUIDv4 · Jaywalking</text>
  <rect x="880" y="458" width="235" height="82" class="box-accent"/>
  <text x="997" y="486" text-anchor="middle" class="mono-blue">project/step01/</text>
  <text x="997" y="510" text-anchor="middle" class="label">Money + PostEntries + Tests</text>
'''
    },
    {
        "dir": "sources/2. Базовый SQL с нуля",
        "filename": "cover-module-02-basic-sql.svg",
        "code": "MOD 02",
        "title": "БАЗОВЫЙ SQL С НУЛЯ: ОТ SELECT ДО KEYSET-ПАГИНАЦИИ",
        "subtitle": "13 глав: логический порядок выполнения запроса, JOIN, GROUP BY, EXISTS vs IN, CASE, NULL и project/step02/",
        "caption": "Инженерная карта Модуля 2: логический конвейер SQL от FROM до LIMIT, объединения JOIN и безопасный конструктор запросов в project/step02/",
        "alt": "Инженерный чертёж Модуля 2: этапы выполнения SQL-запроса, JOIN, агрегация GROUP BY и keyset-пагинация",
        "body": '''
  <rect x="60" y="135" width="1080" height="190" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">ЛОГИЧЕСКИЙ ПОРЯДОК ВЫПОЛНЕНИЯ SQL (ПОЧЕМУ ALIAS ИЗ SELECT НЕ ВИДЕН В WHERE)</text>
  <g transform="translate(85, 185)">
    <rect x="0" y="0" width="130" height="62" class="box-accent"/><text x="65" y="28" text-anchor="middle" class="mono-blue">1. FROM</text><text x="65" y="48" text-anchor="middle" class="label">JOIN таблиц</text>
    <line x1="130" y1="31" x2="152" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="155" y="0" width="130" height="62" class="box-dark"/><text x="220" y="28" text-anchor="middle" class="mono-bold">2. WHERE</text><text x="220" y="48" text-anchor="middle" class="label">Фильтр строк</text>
    <line x1="285" y1="31" x2="307" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="310" y="0" width="130" height="62" class="box-dark"/><text x="375" y="28" text-anchor="middle" class="mono-bold">3. GROUP BY</text><text x="375" y="48" text-anchor="middle" class="label">Свёртка групп</text>
    <line x1="440" y1="31" x2="462" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="465" y="0" width="130" height="62" class="box-dark"/><text x="530" y="28" text-anchor="middle" class="mono-bold">4. HAVING</text><text x="530" y="48" text-anchor="middle" class="label">Фильтр групп</text>
    <line x1="595" y1="31" x2="617" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="620" y="0" width="130" height="62" class="box-accent"/><text x="685" y="28" text-anchor="middle" class="mono-blue">5. SELECT</text><text x="685" y="48" text-anchor="middle" class="label">Проекция / CASE</text>
    <line x1="750" y1="31" x2="772" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="775" y="0" width="130" height="62" class="box-warm"/><text x="840" y="28" text-anchor="middle" class="mono-orange">6. ORDER BY</text><text x="840" y="48" text-anchor="middle" class="label">Сортировка</text>
    <line x1="905" y1="31" x2="927" y2="31" class="line" marker-end="url(#arrow)"/>
    <rect x="930" y="0" width="100" height="62" class="box-warm"/><text x="980" y="28" text-anchor="middle" class="mono-orange">7. LIMIT</text><text x="980" y="48" text-anchor="middle" class="label">Срез N</text>
  </g>
  <text x="85" y="295" class="label">Ключевое правило: EXISTS останавливается на первом совпадении (Semi-Join), а NOT IN с хотя бы одним NULL возвращает пустоту.</text>

  <rect x="60" y="355" width="520" height="210" rx="6" class="box"/>
  <text x="85" y="388" class="mono-blue">ПАГИНАЦИЯ: OFFSET O(N) ПРОТИВ KEYSET O(log N)</text>
  <rect x="85" y="408" width="470" height="62" class="box-warm"/>
  <text x="105" y="434" class="mono-orange">OFFSET 100000 LIMIT 50</text>
  <text x="105" y="456" class="label">Читает и выбрасывает 100 000 строк; страницы плывут при новых вставках</text>
  <rect x="85" y="485" width="470" height="62" class="box-accent"/>
  <text x="105" y="511" class="mono-blue">WHERE (created_at, id) &lt; ($4, $5) LIMIT $6</text>
  <text x="105" y="533" class="label">Сразу спускается по B-Tree к курсору · step02/query.go</text>

  <rect x="615" y="355" width="525" height="210" rx="6" class="box-dark"/>
  <text x="640" y="388" class="mono-bold">ЗАЩИТА И ИДИОМАТИКА DML + GO 1.24</text>
  <rect x="640" y="408" width="230" height="62" class="box"/>
  <text x="755" y="434" text-anchor="middle" class="mono-bold">INSERT ... RETURNING</text>
  <text x="755" y="454" text-anchor="middle" class="label">ID за 1 сетевой RTT</text>
  <rect x="890" y="408" width="225" height="62" class="box"/>
  <text x="1002" y="434" text-anchor="middle" class="mono-bold">COALESCE / NULLIF</text>
  <text x="1002" y="454" text-anchor="middle" class="label">Защита от деления на 0</text>
  <rect x="640" y="485" width="475" height="62" class="box-accent"/>
  <text x="877" y="511" text-anchor="middle" class="mono-blue">Параметры $1, $2 + allowlist столбцов сортировки</text>
  <text x="877" y="533" text-anchor="middle" class="label">0 склейки строк в SQL → полная защита от SQL-инъекций</text>
'''
    },
    {
        "dir": "sources/3. Продвинутый SQL и аналитика",
        "filename": "cover-module-03-advanced-sql.svg",
        "code": "MOD 03",
        "title": "ПРОДВИНУТЫЙ SQL: CTE, ОКОННЫЕ ФУНКЦИИ, JSONB И PL/PGSQL",
        "subtitle": "12 глав: рекурсивные графы, ранжирование, LAG/LEAD, скользящие окна, ROLLUP, триггеры, MatView и project/step03/",
        "caption": "Инженерная карта Модуля 3: конвейер аналитики от WITH/RECURSIVE и оконных рамок OVER до JSONB и материализованных представлений",
        "alt": "Инженерный чертёж Модуля 3: CTE, рекурсивные запросы, оконные функции OVER, JSONB, триггеры и Materialized View",
        "body": '''
  <rect x="60" y="135" width="540" height="225" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">ОКОННЫЕ ФУНКЦИИ (OVER PARTITION BY ... ORDER BY)</text>
  <rect x="85" y="185" width="235" height="150" class="box-dark"/>
  <text x="202" y="210" text-anchor="middle" class="mono-bold">GROUP BY</text>
  <text x="202" y="235" text-anchor="middle" class="label">Схлопывает N строк в 1</text>
  <text x="202" y="262" text-anchor="middle" class="mono">SELECT account_id,</text>
  <text x="202" y="282" text-anchor="middle" class="mono">  SUM(amount)</text>
  <text x="202" y="302" text-anchor="middle" class="mono">GROUP BY account_id</text>

  <rect x="340" y="185" width="235" height="150" class="box-accent"/>
  <text x="457" y="210" text-anchor="middle" class="mono-blue">OVER (PARTITION ...)</text>
  <text x="457" y="235" text-anchor="middle" class="label">Сохраняет каждую строку</text>
  <text x="457" y="262" text-anchor="middle" class="mono">ROW_NUMBER / DENSE_RANK</text>
  <text x="457" y="282" text-anchor="middle" class="mono">LAG(delta) / LEAD(delta)</text>
  <text x="457" y="302" text-anchor="middle" class="mono-orange">ROWS BETWEEN 2 PRECEDING</text>

  <rect x="630" y="135" width="510" height="225" rx="6" class="box"/>
  <text x="655" y="165" class="mono-blue">РЕКУРСИВНЫЕ CTE И АНАЛИТИЧЕСКИЕ СВОДКИ</text>
  <rect x="655" y="185" width="220" height="72" class="box-dark"/>
  <text x="765" y="210" text-anchor="middle" class="mono-bold">WITH RECURSIVE</text>
  <text x="765" y="232" text-anchor="middle" class="label">WorkTable + защита CYCLE</text>
  <rect x="895" y="185" width="220" height="72" class="box-warm"/>
  <text x="1005" y="210" text-anchor="middle" class="mono-orange">ROLLUP / CUBE</text>
  <text x="1005" y="232" text-anchor="middle" class="label">FILTER (WHERE ...) в 1 проход</text>
  <rect x="655" y="272" width="460" height="63" class="box-accent"/>
  <text x="885" y="298" text-anchor="middle" class="mono-blue">project/step03/analytics.go — ComputeAccountWindow</text>
  <text x="885" y="319" text-anchor="middle" class="label">Нарастающий итог, скользящее среднее 3 строк и DailySummarySQL</text>

  <rect x="60" y="390" width="1080" height="175" rx="6" class="box"/>
  <text x="85" y="422" class="mono-bold">ГИБРИДНЫЕ ТИПЫ И СЕРВЕРНЫЕ ОБЪЕКТЫ (ЦЕНЫ И КОМПРОМИССЫ)</text>
  <rect x="85" y="445" width="240" height="95" class="box-accent"/>
  <text x="205" y="473" text-anchor="middle" class="mono-blue">JSONB &amp; Массивы</text>
  <text x="205" y="497" text-anchor="middle" class="label">JEntry, UNNEST батчи,</text>
  <text x="205" y="516" text-anchor="middle" class="label">границы vs 1NF</text>
  <rect x="350" y="445" width="240" height="95" class="box-warm"/>
  <text x="470" y="473" text-anchor="middle" class="mono-orange">PL/pgSQL &amp; Триггеры</text>
  <text x="470" y="497" text-anchor="middle" class="label">Code-to-Data, риск</text>
  <text x="470" y="516" text-anchor="middle" class="label">скрытой стоимости DML</text>
  <rect x="615" y="445" width="240" height="95" class="box-dark"/>
  <text x="735" y="473" text-anchor="middle" class="mono-bold">VIEW</text>
  <text x="735" y="497" text-anchor="middle" class="label">Подстановка AST на лету,</text>
  <text x="735" y="516" text-anchor="middle" class="label">security_invoker</text>
  <rect x="880" y="445" width="235" height="95" class="box-accent"/>
  <text x="997" y="473" text-anchor="middle" class="mono-blue">MATERIALIZED VIEW</text>
  <text x="997" y="497" text-anchor="middle" class="label">REFRESH CONCURRENTLY</text>
  <text x="997" y="516" text-anchor="middle" class="label">без блокировки чтения</text>
'''
    },
    {
        "dir": "sources/4. Индексы, планировщик и EXPLAIN",
        "filename": "cover-module-04-indexes-explain.svg",
        "code": "MOD 04",
        "title": "ИНДЕКСЫ, ПЛАНИРОВЩИК ЗАПРОСОВ И EXPLAIN ANALYZE",
        "subtitle": "16 глав: страницы B+ Tree и page split, GIN/GiST/Bitmap, Cost-Based Optimizer, борьба с N+1 и project/step04/",
        "caption": "Инженерная карта Модуля 4: дерево B+ Tree с высоким fanout, выбор Cost-Based Optimizer и чтение планов EXPLAIN (ANALYZE, BUFFERS)",
        "alt": "Инженерный чертёж Модуля 4: структура B+ Tree, покрывающие и частичные индексы, EXPLAIN ANALYZE и алгоритмы JOIN",
        "body": '''
  <rect x="60" y="135" width="540" height="235" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">B+ TREE: ВЫСОКИЙ FANOUT (3–4 УРОВНЯ НА 10⁹ СТРОК)</text>
  <rect x="235" y="182" width="190" height="38" class="box-accent"/>
  <text x="330" y="206" text-anchor="middle" class="mono-bold">Root Page (8 КБ RAM)</text>
  <line x1="280" y1="220" x2="170" y2="250" class="line-blue" marker-end="url(#arrowBlue)"/>
  <line x1="380" y1="220" x2="490" y2="250" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="90" y="252" width="160" height="36" class="box-dark"/>
  <text x="170" y="275" text-anchor="middle" class="mono">Branch 1</text>
  <rect x="410" y="252" width="160" height="36" class="box-dark"/>
  <text x="490" y="275" text-anchor="middle" class="mono">Branch 2</text>
  <line x1="170" y1="288" x2="145" y2="314" class="line" marker-end="url(#arrow)"/>
  <line x1="170" y1="288" x2="295" y2="314" class="line" marker-end="url(#arrow)"/>
  <line x1="490" y1="288" x2="465" y2="314" class="line" marker-end="url(#arrow)"/>
  <rect x="85" y="316" width="125" height="38" class="box-warm"/><text x="147" y="340" text-anchor="middle" class="mono">Leaf [ctid]</text>
  <line x1="210" y1="335" x2="236" y2="335" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="238" y="316" width="125" height="38" class="box-warm"/><text x="300" y="340" text-anchor="middle" class="mono">Leaf [ctid]</text>
  <line x1="363" y1="335" x2="398" y2="335" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="400" y="316" width="135" height="38" class="box-warm"/><text x="467" y="340" text-anchor="middle" class="mono">Leaf [ctid]</text>

  <rect x="630" y="135" width="510" height="235" rx="6" class="box"/>
  <text x="655" y="165" class="mono-blue">СТОИМОСТНОЙ ОПТИМИЗАТОР (CBO) И EXPLAIN</text>
  <rect x="655" y="185" width="220" height="72" class="box-dark"/>
  <text x="765" y="210" text-anchor="middle" class="mono-bold">Статистика (ANALYZE)</text>
  <text x="765" y="232" text-anchor="middle" class="label">MCV, гистограммы, n_distinct</text>
  <rect x="895" y="185" width="220" height="72" class="box-accent"/>
  <text x="1005" y="210" text-anchor="middle" class="mono-blue">Выбор плана</text>
  <text x="1005" y="232" text-anchor="middle" class="label">Seq vs Index vs Index-Only</text>
  <rect x="655" y="275" width="460" height="76" class="box-warm"/>
  <text x="675" y="300" class="mono-orange">Index-Only Scan using idx_ledger_entries_account_created</text>
  <text x="675" y="322" class="mono">Buffers: shared hit=42 read=0 · Heap Fetches: 0</text>
  <text x="675" y="340" class="label">project/step04/btree.go (EstimatePlan) + 002_indexes.sql</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">АРСЕНАЛ ИНДЕКСОВ И ОПТИМИЗАЦИИ В LEDGERPULSE</text>
  <rect x="85" y="446" width="240" height="98" class="box-accent"/>
  <text x="205" y="472" text-anchor="middle" class="mono-blue">Composite + INCLUDE</text>
  <text x="205" y="496" text-anchor="middle" class="label">Правило левого префикса,</text>
  <text x="205" y="516" text-anchor="middle" class="label">покрывающие поля без Heap</text>
  <rect x="350" y="446" width="240" height="98" class="box-dark"/>
  <text x="470" y="472" text-anchor="middle" class="mono-bold">Partial · GIN · GiST</text>
  <text x="470" y="496" text-anchor="middle" class="label">WHERE status = 'pending',</text>
  <text x="470" y="516" text-anchor="middle" class="label">JSONB и интервалы</text>
  <rect x="615" y="446" width="240" height="98" class="box-dark"/>
  <text x="735" y="472" text-anchor="middle" class="mono-bold">Nested / Hash / Merge</text>
  <text x="735" y="496" text-anchor="middle" class="label">Алгоритмы JOIN и SARGable</text>
  <text x="735" y="516" text-anchor="middle" class="label">условия без обёрток</text>
  <rect x="880" y="446" width="235" height="98" class="box-warm"/>
  <text x="997" y="472" text-anchor="middle" class="mono-orange">Анти-N+1 и Батчи</text>
  <text x="997" y="496" text-anchor="middle" class="label">ANY($1) · UNNEST · COPY</text>
  <text x="997" y="516" text-anchor="middle" class="label">вместо тысяч RTT</text>
'''
    },
    {
        "dir": "sources/5. Транзакции, ACID, MVCC и WAL",
        "filename": "cover-module-05-transactions-mvcc-wal.svg",
        "code": "MOD 05",
        "title": "ТРАНЗАКЦИИ, ACID, MVCC, БЛОКИРОВКИ И ЖУРНАЛ WAL",
        "subtitle": "12 глав: аномалии изоляции, 2PL и Deadlock, многоверсионность, последовательный WAL, ARIES, VACUUM и SSI",
        "caption": "Инженерная карта Модуля 5: путь записи через WAL с fsync(), многоверсионный контроль MVCC и предотвращение Write Skew",
        "alt": "Инженерный чертёж Модуля 5: ACID, уровни изоляции, MVCC-версии, WAL с CRC32, Checkpointing и восстановление ARIES",
        "body": '''
  <rect x="60" y="135" width="520" height="235" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">ДОЛГОВЕЧНОСТЬ: ПОСЛЕДОВАТЕЛЬНЫЙ WAL ПРОТИВ СЛУЧАЙНЫХ СТРАНИЦ</text>
  <rect x="85" y="188" width="150" height="62" class="box-accent"/>
  <text x="160" y="215" text-anchor="middle" class="mono-bold">COMMIT Tx</text>
  <text x="160" y="235" text-anchor="middle" class="label">LSN + CRC32</text>
  <line x1="235" y1="219" x2="275" y2="219" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="278" y="188" width="275" height="62" class="box-warm"/>
  <text x="415" y="213" text-anchor="middle" class="mono-orange">WAL (Append-Only + fsync)</text>
  <text x="415" y="233" text-anchor="middle" class="label">1 последовательная запись → безопасно</text>
  <rect x="85" y="275" width="215" height="72" class="box-dark"/>
  <text x="192" y="303" text-anchor="middle" class="mono-bold">Buffer Pool (RAM)</text>
  <text x="192" y="324" text-anchor="middle" class="label">Грязные страницы 8 КБ</text>
  <line x1="300" y1="311" x2="345" y2="311" class="line-dash" marker-end="url(#arrow)"/>
  <rect x="348" y="275" width="205" height="72" class="box-dark"/>
  <text x="450" y="303" text-anchor="middle" class="mono-bold">Checkpoint → Heap</text>
  <text x="450" y="324" text-anchor="middle" class="label">Фоновый сброс на диск</text>

  <rect x="615" y="135" width="525" height="235" rx="6" class="box"/>
  <text x="640" y="165" class="mono-blue">MVCC: ЧИТАТЕЛИ НЕ БЛОКИРУЮТ ПИСАТЕЛЕЙ</text>
  <rect x="640" y="188" width="230" height="74" class="box-accent"/>
  <text x="755" y="213" text-anchor="middle" class="mono-bold">Версия v1 (xmin=10, xmax=15)</text>
  <text x="755" y="234" text-anchor="middle" class="label">Видна снимку XID 12</text>
  <line x1="870" y1="225" x2="905" y2="225" class="line-blue" marker-end="url(#arrowBlue)"/>
  <rect x="908" y="188" width="208" height="74" class="box-warm"/>
  <text x="1012" y="213" text-anchor="middle" class="mono-orange">Версия v2 (xmin=15, xmax=0)</text>
  <text x="1012" y="234" text-anchor="middle" class="label">Видна новым транзакциям</text>
  <rect x="640" y="278" width="476" height="68" class="box-dark"/>
  <text x="878" y="305" text-anchor="middle" class="mono-bold">project/step05/mvcc_wal.go — WALStore + MVCCEngine + HasDeadlockCycle</text>
  <text x="878" y="326" text-anchor="middle" class="label">Восстановление ARIES (Analysis → Redo → Undo), VACUUM и SSI</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">ИЗОЛЯЦИЯ, АНОМАЛИИ И ПРОФИЛАКТИКА DEADLOCK</text>
  <rect x="85" y="446" width="240" height="98" class="box-dark"/>
  <text x="205" y="472" text-anchor="middle" class="mono-bold">Read Committed</text>
  <text x="205" y="496" text-anchor="middle" class="label">Новый снимок на каждый</text>
  <text x="205" y="516" text-anchor="middle" class="label">запрос в транзакции</text>
  <rect x="350" y="446" width="240" height="98" class="box-accent"/>
  <text x="470" y="472" text-anchor="middle" class="mono-blue">Snapshot Isolation</text>
  <text x="470" y="496" text-anchor="middle" class="label">First-Committer-Wins,</text>
  <text x="470" y="516" text-anchor="middle" class="label">остаётся риск Write Skew</text>
  <rect x="615" y="446" width="240" height="98" class="box-warm"/>
  <text x="735" y="472" text-anchor="middle" class="mono-orange">Serializable (SSI)</text>
  <text x="735" y="496" text-anchor="middle" class="label">Предикатные замки SIREAD</text>
  <text x="735" y="516" text-anchor="middle" class="label">ловят циклы rw-зависимостей</text>
  <rect x="880" y="446" width="235" height="98" class="box-dark"/>
  <text x="997" y="472" text-anchor="middle" class="mono-bold">2PL &amp; SKIP LOCKED</text>
  <text x="997" y="496" text-anchor="middle" class="label">Порядок id1 &lt; id2</text>
  <text x="997" y="516" text-anchor="middle" class="label">и граф ожиданий DFS</text>
'''
    },
    {
        "dir": "sources/6. PostgreSQL под капотом",
        "filename": "cover-module-06-postgresql.svg",
        "code": "MOD 06",
        "title": "POSTGRESQL ПОД КАПОТОМ: ПРОЦЕССЫ, HEAP, TOAST И ТЮНИНГ",
        "subtitle": "11 глав: postmaster и shared_buffers, HOT-обновления, 6 типов индексов, FTS, PostGIS, PgBouncer, Autovacuum и репликация",
        "caption": "Инженерная карта Модуля 6: архитектура процессов PostgreSQL, Slotted Page с HOT-цепочками, TOAST и потоковая/логическая репликация",
        "alt": "Инженерный чертёж Модуля 6: процессная архитектура PostgreSQL, shared_buffers, Heap, TOAST, HOT и PgBouncer",
        "body": '''
  <rect x="60" y="135" width="350" height="235" rx="6" class="box"/>
  <text x="235" y="165" text-anchor="middle" class="mono-blue">1. ПРОЦЕССНАЯ АРХИТЕКТУРА</text>
  <rect x="85" y="185" width="300" height="44" class="box-accent"/>
  <text x="235" y="212" text-anchor="middle" class="mono-blue">postmaster + PgBouncer</text>
  <rect x="85" y="242" width="142" height="48" class="box-dark"/>
  <text x="156" y="270" text-anchor="middle" class="mono">Backend 1..N</text>
  <rect x="243" y="242" width="142" height="48" class="box-dark"/>
  <text x="314" y="270" text-anchor="middle" class="mono">checkpointer</text>
  <rect x="85" y="302" width="300" height="48" class="box-warm"/>
  <text x="235" y="330" text-anchor="middle" class="mono-orange">shared_buffers + WAL buffers</text>

  <rect x="440" y="135" width="355" height="235" rx="6" class="box"/>
  <text x="617" y="165" text-anchor="middle" class="mono-blue">2. ХРАНЕНИЕ: HEAP, TOAST И HOT</text>
  <rect x="465" y="185" width="305" height="52" class="box-accent"/>
  <text x="617" y="208" text-anchor="middle" class="mono-bold">8 КБ Slotted Page</text>
  <text x="617" y="226" text-anchor="middle" class="label">ItemId → HeapTuple (xmin, xmax, ctid)</text>
  <rect x="465" y="248" width="145" height="48" class="box-dark"/>
  <text x="537" y="276" text-anchor="middle" class="mono-bold">HOT Chain</text>
  <rect x="625" y="248" width="145" height="48" class="box-warm"/>
  <text x="697" y="276" text-anchor="middle" class="mono-orange">TOAST (&gt;2 КБ)</text>
  <rect x="465" y="308" width="305" height="42" class="box-dark"/>
  <text x="617" y="334" text-anchor="middle" class="mono">Visibility Map + FSM + Freeze XID</text>

  <rect x="825" y="135" width="315" height="235" rx="6" class="box-accent"/>
  <text x="982" y="165" text-anchor="middle" class="mono-blue">3. ИНДЕКСЫ И РАСШИРЕНИЯ</text>
  <rect x="850" y="185" width="265" height="48" class="box"/>
  <text x="982" y="214" text-anchor="middle" class="mono-bold">B-Tree · GIN · GiST · BRIN · Hash</text>
  <rect x="850" y="245" width="265" height="48" class="box"/>
  <text x="982" y="274" text-anchor="middle" class="mono">FTS (tsvector) · pg_trgm · PostGIS</text>
  <rect x="850" y="305" width="265" height="45" class="box-warm"/>
  <text x="982" y="332" text-anchor="middle" class="mono-orange">pg_stat_statements · pgcrypto</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">ЭКСПЛУАТАЦИЯ POSTGRESQL В ПРОДАКШЕНЕ</text>
  <rect x="85" y="448" width="320" height="96" class="box-dark"/>
  <text x="245" y="476" text-anchor="middle" class="mono-bold">Тюнинг памяти и пулов</text>
  <text x="245" y="498" text-anchor="middle" class="label">PgBouncer (transaction mode)</text>
  <text x="245" y="518" text-anchor="middle" class="label">против исчерпания PID и RAM</text>
  <rect x="435" y="448" width="330" height="96" class="box-warm"/>
  <text x="600" y="476" text-anchor="middle" class="mono-orange">Autovacuum &amp; XID Wraparound</text>
  <text x="600" y="498" text-anchor="middle" class="label">Борьба с раздуванием таблиц</text>
  <text x="600" y="518" text-anchor="middle" class="label">и заморозка age(datfrozenxid)</text>
  <rect x="795" y="448" width="320" height="96" class="box-accent"/>
  <text x="955" y="476" text-anchor="middle" class="mono-blue">Потоковая и логическая репликация</text>
  <text x="955" y="498" text-anchor="middle" class="label">walsender/walreceiver и слоты CDC</text>
  <text x="955" y="518" text-anchor="middle" class="label">(max_slot_wal_keep_size)</text>
'''
    },
    {
        "dir": "sources/7. MySQL, InnoDB и форки",
        "filename": "cover-module-07-mysql-innodb.svg",
        "code": "MOD 07",
        "title": "MYSQL, ДВИЖОК INNODB И ОБЛАЧНЫЕ ФОРКИ",
        "subtitle": "9 глав: потоки ОС, кластерный индекс, Redo/Undo Log, Gap &amp; Next-Key Locks, Binlog/GTID, Percona, MariaDB и Vitess",
        "caption": "Инженерная карта Модуля 7: потоковая модель MySQL, кластерный первичный ключ InnoDB (16 КБ) и сравнение с PostgreSQL",
        "alt": "Инженерный чертёж Модуля 7: архитектура MySQL, кластерный индекс InnoDB, Gap Locks, Binlog/GTID и форки Percona/MariaDB/Vitess",
        "body": '''
  <rect x="60" y="135" width="530" height="235" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">INNODB: КЛАСТЕРНЫЙ PK И ВТОРИЧНЫЙ ИНДЕКС (16 КБ)</text>
  <rect x="85" y="188" width="225" height="158" class="box-accent"/>
  <text x="197" y="214" text-anchor="middle" class="mono-blue">Вторичный индекс</text>
  <text x="197" y="242" text-anchor="middle" class="mono">(account_id) → PK</text>
  <text x="197" y="268" text-anchor="middle" class="label">Хранит Primary Key,</text>
  <text x="197" y="288" text-anchor="middle" class="label">а не физический адрес</text>
  <text x="197" y="318" text-anchor="middle" class="mono-orange">Change Buffer</text>
  <line x1="310" y1="265" x2="345" y2="265" class="line-orange" marker-end="url(#arrowOrange)"/>
  <rect x="348" y="188" width="220" height="158" class="box-warm"/>
  <text x="458" y="214" text-anchor="middle" class="mono-orange">Clustered PK Index</text>
  <text x="458" y="242" text-anchor="middle" class="mono">PK → Вся строка</text>
  <text x="458" y="268" text-anchor="middle" class="label">Двойной поиск при</text>
  <text x="458" y="288" text-anchor="middle" class="label">отсутствии покрытия</text>
  <text x="458" y="318" text-anchor="middle" class="mono-bold">Doublewrite + Redo</text>

  <rect x="620" y="135" width="520" height="235" rx="6" class="box"/>
  <text x="645" y="165" class="mono-blue">ТРАНЗАКЦИИ И РЕПЛИКАЦИЯ MYSQL 8.0</text>
  <rect x="645" y="188" width="225" height="72" class="box-dark"/>
  <text x="757" y="213" text-anchor="middle" class="mono-bold">Undo Log (MVCC)</text>
  <text x="757" y="234" text-anchor="middle" class="label">In-place update + откат версий</text>
  <rect x="890" y="188" width="225" height="72" class="box-warm"/>
  <text x="1002" y="213" text-anchor="middle" class="mono-orange">Gap &amp; Next-Key Locks</text>
  <text x="1002" y="234" text-anchor="middle" class="label">Защита от Phantom Read</text>
  <rect x="645" y="276" width="470" height="70" class="box-accent"/>
  <text x="880" y="303" text-anchor="middle" class="mono-blue">Внутренний 2PC: Redo Log ↔ Binlog + GTID</text>
  <text x="880" y="324" text-anchor="middle" class="label">Потоковая, Semi-Sync (AFTER_SYNC) и Group Replication</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">СРАВНЕНИЕ С POSTGRESQL И ЭКОСИСТЕМА ФОРКОВ</text>
  <rect x="85" y="446" width="245" height="98" class="box-accent"/>
  <text x="207" y="472" text-anchor="middle" class="mono-blue">PostgreSQL vs MySQL</text>
  <text x="207" y="496" text-anchor="middle" class="label">Heap + VACUUM против</text>
  <text x="207" y="516" text-anchor="middle" class="label">Clustered PK + Undo</text>
  <rect x="355" y="446" width="245" height="98" class="box-dark"/>
  <text x="477" y="472" text-anchor="middle" class="mono-bold">Percona Server</text>
  <text x="477" y="496" text-anchor="middle" class="label">XtraBackup без блокировки,</text>
  <text x="477" y="516" text-anchor="middle" class="label">pt-online-schema-change</text>
  <rect x="625" y="446" width="240" height="98" class="box-dark"/>
  <text x="745" y="472" text-anchor="middle" class="mono-bold">MariaDB</text>
  <text x="745" y="496" text-anchor="middle" class="label">Aria, MyRocks, Galera</text>
  <text x="745" y="516" text-anchor="middle" class="label">и расхождение ветвей</text>
  <rect x="890" y="446" width="225" height="98" class="box-warm"/>
  <text x="1002" y="472" text-anchor="middle" class="mono-orange">Aurora · AliDB · Vitess</text>
  <text x="1002" y="496" text-anchor="middle" class="label">Отдельный Storage 4/6 AZ</text>
  <text x="1002" y="516" text-anchor="middle" class="label">и шардирование VTGate</text>
'''
    },
    {
        "dir": "sources/8. Распределённые базы данных, репликация и шардирование",
        "filename": "cover-module-08-distributed-db.svg",
        "code": "MOD 08",
        "title": "РАСПРЕДЕЛЁННЫЕ БАЗЫ ДАННЫХ, РЕПЛИКАЦИЯ И ШАРДИРОВАНИЕ",
        "subtitle": "11 глав: Sync/Async, кворумы, Consistent Hashing в project/step06/, CAP/PACELC, 2PC, Saga и fencing tokens",
        "caption": "Инженерная карта Модуля 8: от топологий репликации и кольца консистентного хеширования до CAP/PACELC, 2PC, Saga и fencing tokens",
        "alt": "Инженерный чертёж Модуля 8: репликация Leader-Follower, шардирование, кольцо консистентного хеширования, 2PC и fencing tokens",
        "body": '''
  <rect x="60" y="135" width="350" height="235" rx="6" class="box"/>
  <text x="235" y="165" text-anchor="middle" class="mono-blue">1. РЕПЛИКАЦИЯ И ЛАГ</text>
  <rect x="90" y="188" width="290" height="48" class="box-accent"/>
  <text x="235" y="217" text-anchor="middle" class="mono-blue">Leader (запись + RYW-маршрут)</text>
  <line x1="170" y1="236" x2="150" y2="275" class="line-orange" marker-end="url(#arrowOrange)"/>
  <line x1="300" y1="236" x2="320" y2="275" class="line-dash" marker-end="url(#arrow)"/>
  <rect x="85" y="278" width="135" height="62" class="box-warm"/>
  <text x="152" y="304" text-anchor="middle" class="mono-bold">Sync Replica</text>
  <text x="152" y="324" text-anchor="middle" class="label">RTT + fsync</text>
  <rect x="245" y="278" width="140" height="62" class="box-dark"/>
  <text x="315" y="304" text-anchor="middle" class="mono-bold">Async Replica</text>
  <text x="315" y="324" text-anchor="middle" class="label">Лаг чтения</text>

  <rect x="440" y="135" width="350" height="235" rx="6" class="box"/>
  <text x="615" y="165" text-anchor="middle" class="mono-blue">2. КОЛЬЦО ХЕШИРОВАНИЯ (STEP 06)</text>
  <circle cx="615" cy="268" r="76" fill="#f0f9ff" stroke="#0369a1" stroke-width="2.4"/>
  <circle cx="615" cy="192" r="9" fill="#0369a1"/>
  <circle cx="688" cy="245" r="9" fill="#c2410c"/>
  <circle cx="660" cy="332" r="9" fill="#0369a1"/>
  <circle cx="542" cy="285" r="9" fill="#1e293b"/>
  <text x="615" y="263" text-anchor="middle" class="mono-bold">ShardRouter</text>
  <text x="615" y="283" text-anchor="middle" class="label">128 vnodes / шард</text>
  <text x="615" y="358" text-anchor="middle" class="label">Перебалансировка ~1/N ключей</text>

  <rect x="820" y="135" width="320" height="235" rx="6" class="box-accent"/>
  <text x="980" y="165" text-anchor="middle" class="mono-blue">3. СОГЛАСОВАННОСТЬ И КВОРУМЫ</text>
  <rect x="845" y="188" width="270" height="50" class="box"/>
  <text x="980" y="211" text-anchor="middle" class="mono-bold">Dynamo: W + R &gt; N</text>
  <text x="980" y="229" text-anchor="middle" class="label">Read Repair &amp; Hinted Handoff</text>
  <rect x="845" y="248" width="270" height="48" class="box"/>
  <text x="980" y="271" text-anchor="middle" class="mono-bold">CAP → PACELC (PC/EC vs PA/EL)</text>
  <text x="980" y="288" text-anchor="middle" class="label">Strong · Causal · Read-Your-Writes</text>
  <rect x="845" y="306" width="270" height="44" class="box-warm"/>
  <text x="980" y="333" text-anchor="middle" class="mono-orange">Partitioning: Range / List / Hash</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">КООРДИНАЦИЯ МЕЖДУ УЗЛАМИ И ЗАЩИТА ОТ ГОНКИ ПОСЛЕ ПАУЗЫ GC</text>
  <rect x="85" y="448" width="320" height="96" class="box-warm"/>
  <text x="245" y="476" text-anchor="middle" class="mono-orange">Двухфазный коммит (2PC)</text>
  <text x="245" y="498" text-anchor="middle" class="label">Prepare + Commit, блокировка</text>
  <text x="245" y="518" text-anchor="middle" class="label">In-Doubt при падении координатора</text>
  <rect x="435" y="448" width="330" height="96" class="box-dark"/>
  <text x="600" y="476" text-anchor="middle" class="mono-bold">Saga со стороны БД</text>
  <text x="600" y="498" text-anchor="middle" class="label">Локальные транзакции + LIFO</text>
  <text x="600" y="518" text-anchor="middle" class="label">компенсации без глобальной изоляции</text>
  <rect x="795" y="448" width="320" height="96" class="box-accent"/>
  <text x="955" y="476" text-anchor="middle" class="mono-blue">FencedStorage (step06)</text>
  <text x="955" y="498" text-anchor="middle" class="label">Монотонный fencing token</text>
  <text x="955" y="518" text-anchor="middle" class="label">отвергает устаревшего лидера</text>
'''
    },
    {
        "dir": "sources/9. NoSQL, аналитические и специализированные базы",
        "filename": "cover-module-09-nosql-olap-vector.svg",
        "code": "MOD 09",
        "title": "NOSQL, CLICKHOUSE, NEWSQL И ВЕКТОРНЫЕ БАЗЫ ДАННЫХ",
        "subtitle": "15 глав: LSM-Tree, Redis/Valkey и пайплайнинг, Memcached, MongoDB, Cassandra, MergeTree (step07/), CockroachDB и HNSW",
        "caption": "Инженерная карта Модуля 9: спектр специализированных хранилищ от оперативных структур Redis/Memcached и LSM-деревьев до ClickHouse и HNSW",
        "alt": "Инженерный чертёж Модуля 9: Redis/Valkey, Memcached, MongoDB, Cassandra LSM-Tree, ClickHouse MergeTree, CockroachDB и векторные индексы HNSW",
        "body": '''
  <rect x="60" y="135" width="350" height="235" rx="6" class="box"/>
  <text x="235" y="165" text-anchor="middle" class="mono-blue">1. IN-MEMORY И КЭШИ</text>
  <rect x="85" y="185" width="300" height="74" class="box-accent"/>
  <text x="235" y="210" text-anchor="middle" class="mono-blue">Redis / Valkey (RESP + epoll)</text>
  <text x="235" y="230" text-anchor="middle" class="label">Event loop, ZSet/Streams, RDB+AOF,</text>
  <text x="235" y="248" text-anchor="middle" class="label">Pipeline в Go против RTT</text>
  <rect x="85" y="274" width="300" height="74" class="box-dark"/>
  <text x="235" y="302" text-anchor="middle" class="mono-bold">Memcached (Multi-Thread)</text>
  <text x="235" y="324" text-anchor="middle" class="label">Slab-аллокатор и защита от фрагментации</text>

  <rect x="440" y="135" width="350" height="235" rx="6" class="box"/>
  <text x="615" y="165" text-anchor="middle" class="mono-blue">2. ДОКУМЕНТЫ И LSM-ДЕРЕВЬЯ</text>
  <rect x="465" y="185" width="300" height="74" class="box-dark"/>
  <text x="615" y="210" text-anchor="middle" class="mono-bold">MongoDB (WiredTiger)</text>
  <text x="615" y="230" text-anchor="middle" class="label">BSON-документы, Replica Set,</text>
  <text x="615" y="248" text-anchor="middle" class="label">шардирование через mongos</text>
  <rect x="465" y="274" width="300" height="74" class="box-warm"/>
  <text x="615" y="302" text-anchor="middle" class="mono-orange">Cassandra (LSM + SSTable)</text>
  <text x="615" y="324" text-anchor="middle" class="label">Memtable → Bloom Filter + Compaction</text>

  <rect x="820" y="135" width="320" height="235" rx="6" class="box-accent"/>
  <text x="980" y="165" text-anchor="middle" class="mono-blue">3. OLAP CLICKHOUSE (STEP 07)</text>
  <rect x="845" y="185" width="270" height="74" class="box"/>
  <text x="980" y="210" text-anchor="middle" class="mono-bold">Колонки + MergeTree</text>
  <text x="980" y="230" text-anchor="middle" class="label">Гранулы 8192, SIMD-векторизация,</text>
  <text x="980" y="248" text-anchor="middle" class="label">SummingMergeTree витрина</text>
  <rect x="845" y="274" width="270" height="74" class="box-warm"/>
  <text x="980" y="302" text-anchor="middle" class="mono-orange">MergeTreeSimulator</text>
  <text x="980" y="324" text-anchor="middle" class="label">project/step07/ + 001_ledger_events.sql</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">РАСПРЕДЕЛЁННЫЙ SQL И ПОИСК ПО ВЕКТОРАМ (AI / RAG)</text>
  <rect x="85" y="448" width="500" height="96" class="box-dark"/>
  <text x="335" y="476" text-anchor="middle" class="mono-bold">NewSQL: CockroachDB поверх Raft</text>
  <text x="335" y="498" text-anchor="middle" class="label">Ranges 512 МБ, Leaseholder, HLC, Parallel Commits</text>
  <text x="335" y="518" text-anchor="middle" class="label">Честный Serializable + SQLSTATE 40001 ретраи в Go</text>
  <rect x="615" y="448" width="500" height="96" class="box-accent"/>
  <text x="865" y="476" text-anchor="middle" class="mono-blue">Векторные БД: HNSW, IVF и RAG-конвейеры</text>
  <text x="865" y="498" text-anchor="middle" class="label">Приближённый k-NN, квантование PQ, гибрид BM25 + RRF</text>
  <text x="865" y="518" text-anchor="middle" class="label">pgvector, Qdrant, Milvus и изоляция по tenant_id</text>
'''
    },
    {
        "dir": "sources/10. Практика БД в Go и HighLoad-эксплуатация",
        "filename": "cover-module-10-go-highload-final.svg",
        "code": "MOD 10",
        "title": "ПРАКТИКА БД В GO, HIGHLOAD И ФИНАЛ LEDGERPULSE",
        "subtitle": "25 глав: database/sql под капотом, Repository/UoW, миграции, Singleflight, Outbox, PITR, метрики и финал project/final/",
        "caption": "Инженерная карта Модуля 10: сквозная архитектура финального сервиса LedgerPulse от HTTP API и Singleflight до ledgerdriver и Outbox",
        "alt": "Инженерный чертёж Модуля 10: финал LedgerPulse поверх database/sql, TxManager, Idempotency, Outbox, Singleflight, PITR и безопасность БД",
        "body": '''
  <rect x="60" y="135" width="1080" height="235" rx="6" class="box"/>
  <text x="85" y="165" class="mono-blue">СКВОЗНАЯ АРХИТЕКТУРА ФИНАЛА LEDGERPULSE (PROJECT/FINAL/)</text>
  <rect x="85" y="192" width="185" height="145" class="box-accent"/>
  <text x="177" y="220" text-anchor="middle" class="mono-blue">HTTP API (server.go)</text>
  <text x="177" y="246" text-anchor="middle" class="mono">POST /transfers</text>
  <text x="177" y="268" text-anchor="middle" class="mono">GET /accounts/{id}</text>
  <text x="177" y="290" text-anchor="middle" class="mono">GET /metrics/db</text>
  <text x="177" y="316" text-anchor="middle" class="label">Go 1.24 ServeMux</text>

  <line x1="270" y1="264" x2="305" y2="264" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="308" y="192" width="230" height="145" class="box"/>
  <text x="423" y="220" text-anchor="middle" class="mono-bold">LedgerService</text>
  <text x="423" y="246" text-anchor="middle" class="mono">SingleflightCache</text>
  <text x="423" y="268" text-anchor="middle" class="mono">TxManager.WithinTx</text>
  <text x="423" y="290" text-anchor="middle" class="mono-orange">Порядок ID (Deadlock=0)</text>
  <text x="423" y="316" text-anchor="middle" class="label">Cache-Aside + OLAP</text>

  <line x1="538" y1="264" x2="573" y2="264" class="line-blue" marker-end="url(#arrowBlue)"/>

  <rect x="576" y="192" width="250" height="145" class="box-dark"/>
  <text x="701" y="220" text-anchor="middle" class="mono-bold">*sql.DB + ledgerdriver</text>
  <text x="701" y="246" text-anchor="middle" class="mono">Pool (idle / inUse)</text>
  <text x="701" y="268" text-anchor="middle" class="mono">Tx-pinning + ErrBadConn</text>
  <text x="701" y="290" text-anchor="middle" class="mono">Prepared Statements</text>
  <text x="701" y="316" text-anchor="middle" class="label">SlowQueryHook + db.Stats()</text>

  <line x1="826" y1="264" x2="861" y2="264" class="line-orange" marker-end="url(#arrowOrange)"/>

  <rect x="864" y="192" width="250" height="145" class="box-warm"/>
  <text x="989" y="220" text-anchor="middle" class="mono-orange">ACID Хранилище (001–003)</text>
  <text x="989" y="246" text-anchor="middle" class="mono">accounts + entries</text>
  <text x="989" y="268" text-anchor="middle" class="mono">idempotency_keys</text>
  <text x="989" y="290" text-anchor="middle" class="mono">outbox_events + RLS</text>
  <text x="989" y="316" text-anchor="middle" class="label">Всё в одной транзакции</text>

  <rect x="60" y="395" width="1080" height="170" rx="6" class="box"/>
  <text x="85" y="425" class="mono-bold">ПРОМЫШЛЕННАЯ ЭКСПЛУАТАЦИЯ: ОТ МИГРАЦИЙ И HIGHLOAD ДО PITR И БЕЗОПАСНОСТИ</text>
  <rect x="85" y="446" width="245" height="98" class="box-dark"/>
  <text x="207" y="472" text-anchor="middle" class="mono-bold">Миграции &amp; ORM/SQL</text>
  <text x="207" y="496" text-anchor="middle" class="label">Expand-and-Contract,</text>
  <text x="207" y="516" text-anchor="middle" class="label">pgx · sqlx · sqlc · GORM</text>
  <rect x="355" y="446" width="245" height="98" class="box-accent"/>
  <text x="477" y="472" text-anchor="middle" class="mono-blue">HighLoad &amp; Skew</text>
  <text x="477" y="496" text-anchor="middle" class="label">Write Salting, реплики,</text>
  <text x="477" y="516" text-anchor="middle" class="label">CQRS/ES со стороны БД</text>
  <rect x="625" y="446" width="240" height="98" class="box-warm"/>
  <text x="745" y="472" text-anchor="middle" class="mono-orange">PITR &amp; Disaster Recovery</text>
  <text x="745" y="496" text-anchor="middle" class="label">pg_basebackup + WAL архив,</text>
  <text x="745" y="516" text-anchor="middle" class="label">RPO / RTO и учения</text>
  <rect x="890" y="446" width="225" height="98" class="box-dark"/>
  <text x="1002" y="472" text-anchor="middle" class="mono-bold">Observability &amp; Sec</text>
  <text x="1002" y="496" text-anchor="middle" class="label">pg_stat_statements, TLS,</text>
  <text x="1002" y="516" text-anchor="middle" class="label">защита от SQLi, RBAC, RLS</text>
'''
    },
]


def main() -> int:
    for item in COVERS:
        media_dir = os.path.join(ROOT, item["dir"], "media")
        os.makedirs(media_dir, exist_ok=True)
        svg = HEADER + item["body"] + footer_block(item["code"], item["title"], item["subtitle"])
        # Валидация XML перед записью
        ET.fromstring(svg)
        dest = os.path.join(media_dir, item["filename"])
        with open(dest, "w", encoding="utf-8", newline="\n") as fp:
            fp.write(svg)
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
            [f"Инженерная обложка {item['code']} Тома 2 ({len(svg.encode('utf-8')) // 1024} КБ)"],
        )
        write_credits(credits_path, item["filename"], block)
        load_credits(credits_path)
        print(f"OK   {os.path.relpath(dest, ROOT)}")
    print(f"\nСгенерировано обложек: {len(COVERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
