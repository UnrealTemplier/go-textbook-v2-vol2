#!/usr/bin/env python3
"""
Автолинтер стиля, структуры, KaTeX-безопасности и упражнений для Тома 2 (`go-textbook-v2-vol2`).

Использование:
    python3 book/tools/check_style_vol2.py sources
    python3 book/tools/check_style_vol2.py "sources/1. Фундамент баз данных и моделирование"
"""

import os
import re
import sys

AI_CLICHES = [
    r"в современном мире",
    r"в эпоху высоконагруженных",
    r"важно понимать,\s*что",
    r"стоит отметить,\s*что",
    r"давайте погрузимся",
    r"не секрет,\s*что",
    r"подводя итог",
    r"итак,\s*в этом уроке",
    r"как известно,\s*в",
    r"добро пожаловать в удивительный мир",
]

ROLEPLAY_PATTERNS = [
    r"\bмы с кеном\b",
    r"\bв моей практике\b",
    r"\bя помню\b",
    r"\bкогда я работал в bell labs\b",
    r"\bмы с деннисом\b",
]

MECH_SYMP_PATTERN = re.compile(
    r"mechanical sympathy|механическ\w+\s+сочувств\w*|механическ\w+\s+симпати\w*",
    re.I,
)

# Голые PostgreSQL-параметры $1, $2... или dollar-quoting $$ вне кода и LaTeX
BARE_PG_PARAM_RE = re.compile(r"(?<![\\A-Za-z0-9_])\$[1-9][0-9]*(?!\s*\\)")


def strip_fences_and_inline_code(text: str) -> str:
    """Удаляет fenced code blocks (в т. ч. внутри цитат/спойлеров `> `) и inline code."""
    out_lines = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        # Снимаем префикс цитаты `> ` для корректного распознавания code fences внутри [!solution]
        unquoted = re.sub(r"^(?:\s*>\s*)+", "", line)
        stripped = unquoted.lstrip()
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
            elif stripped.startswith(fence_marker * len(marker)):
                in_fence = False
                fence_marker = ""
            out_lines.append("")
            continue
        if in_fence:
            out_lines.append("")
            continue
        # Удаляем inline code (`...`)
        cleaned = re.sub(r"`[^`\n]+`", "", unquoted)
        out_lines.append(cleaned)
    return "\n".join(out_lines)


def check_file(path: str) -> tuple[list[str], list[str], int]:
    """Возвращает (errors, warnings, word_count)."""
    errors: list[str] = []
    warnings: list[str] = []

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    words = len(raw.split())
    basename = os.path.basename(path)
    is_index = bool(re.match(r"^0+\. ", basename))

    # 1. Запрет # H1 вне fenced blocks
    no_code = strip_fences_and_inline_code(raw)
    for idx, line in enumerate(no_code.splitlines(), 1):
        if re.match(r"^#\s+", line):
            errors.append(f"L{idx}: найден заголовок '# H1' (движок генерирует H1 из имени файла)")

    # 2. Первая непустая строка должна быть курсивным подзаголовком *...*
    non_empty = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not non_empty:
        errors.append("пустой файл")
        return errors, warnings, 0
    first = non_empty[0]
    if not (first.startswith("*") and first.endswith("*") and len(first) > 4):
        errors.append("первая строка должна быть курсивным подзаголовком *...*")

    # 3. Запрет Mechanical Sympathy
    if MECH_SYMP_PATTERN.search(raw):
        errors.append("найден запрещённый штамп 'Mechanical Sympathy / механическое сочувствие'")

    # 4. Запрет ролеплея и 1-го лица
    for pat in ROLEPLAY_PATTERNS:
        if re.search(pat, no_code, re.I):
            errors.append(f"найден запрещённый ролеплей от 1-го лица: {pat}")

    # 5. Запрет AI-клише
    for pat in AI_CLICHES:
        if re.search(pat, no_code, re.I):
            errors.append(f"найдено AI-клише: {pat}")

    # 6. Запрет '!' в авторской прозе (игнорируем callout-теги, картинки, !=, прямые цитаты)
    for idx, line in enumerate(no_code.splitlines(), 1):
        # Пропускаем строки-цитаты с > "..." (прямые цитаты или callout-маркеры)
        s = line.strip()
        if s.startswith("> [!"):
            s = re.sub(r"^>\s*\[![A-Za-z0-9_-]+\]", "", s)
        # Убираем markdown-картинки ![alt](url) и != / !== / !important
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
        s = s.replace("!=", "")
        if "!" in s:
            errors.append(f"L{idx}: найден восклицательный знак '!' в прозе: {s[:80]}")

    # 7. Голые PostgreSQL-параметры $1, $2 в тексте (конфликт с KaTeX)
    # Допускаем только если это явный LaTeX с двумя $ вокруг формулы без кириллицы
    no_latex = re.sub(r"\$\$[^$]+\$\$", "", no_code, flags=re.S)
    no_latex = re.sub(r"\$[^$\n]+\$", "", no_latex)
    for idx, line in enumerate(no_latex.splitlines(), 1):
        if BARE_PG_PARAM_RE.search(line):
            errors.append(f"L{idx}: обнаружен голый параметр $N вне бэктиков (сломает KaTeX)")

    # Также проверим незакрытый $$ или голый $$ в прозе
    bare_dollar_count = no_code.count("$$")
    if bare_dollar_count % 2 != 0:
        errors.append("нечётное число '$$' в тексте (сломает KaTeX или это голый dollar-quoting PG)")

    # 8. Проверка грейдов на врезках «Собеседование»
    for idx, line in enumerate(raw.splitlines(), 1):
        if re.search(r"\[!tip\]\s*Собеседован|\[!info\]\s*Собеседован|\[!check\]\s*Собеседован", line, re.I):
            if not re.search(r"\[(Junior|Middle|Senior/Staff|Senior|Staff)\]", line):
                errors.append(f"L{idx}: врезка 'Собеседование' без грейда [Junior]/[Middle]/[Senior/Staff]")

    # 9. Упражнения и объём (только для обычных уроков, не 00. О разделе.md)
    if not is_index:
        sol_count = raw.count("> [!solution]")
        if sol_count < 2:
            errors.append(f"найдено только {sol_count} блоков '> [!solution]' (минимум 2)")
        if words < 1100:
            errors.append(f"слишком короткий урок: {words} слов (минимум 1100, цель 1500–2300)")
        elif words < 1350:
            warnings.append(f"коротковатый урок: {words} слов (цель 1500–2300)")
        elif words > 2800:
            warnings.append(f"длинноватый урок: {words} слов (цель 1500–2300)")

    return errors, warnings, words


def main() -> int:
    targets = sys.argv[1:] or ["sources"]
    files: list[str] = []
    for t in targets:
        if os.path.isfile(t):
            files.append(t)
        elif os.path.isdir(t):
            for root, _, names in os.walk(t):
                for name in sorted(names):
                    if name.endswith(".md"):
                        files.append(os.path.join(root, name))
        else:
            print(f"ERROR: путь не найден: {t}", file=sys.stderr)
            return 2

    files.sort()
    total_err = 0
    total_warn = 0
    total_words = 0

    for fp in files:
        errs, warns, words = check_file(fp)
        total_words += words
        if errs:
            total_err += len(errs)
            print(f"FAIL {fp} ({words}w):")
            for e in errs:
                print(f"  [ERR]  {e}")
        if warns:
            total_warn += len(warns)
            if not errs:
                print(f"WARN {fp} ({words}w):")
            for w in warns:
                print(f"  [WARN] {w}")

    print(
        f"\nПроверено файлов: {len(files)}, всего слов: {total_words:,}, "
        f"ошибок: {total_err}, предупреждений: {total_warn}."
    )
    return 1 if total_err > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
