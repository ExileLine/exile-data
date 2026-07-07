# -*- coding: utf-8 -*-

from enum import StrEnum
import re


class SqlRisk(StrEnum):
    READ_ONLY = "read_only"
    WRITE = "write"
    DDL = "ddl"
    TRANSACTION = "transaction"
    UNKNOWN = "unknown"


_DDL_KEYWORDS = {
    "alter",
    "create",
    "drop",
    "grant",
    "revoke",
    "truncate",
}
_WRITE_KEYWORDS = {
    "call",
    "copy",
    "delete",
    "exec",
    "execute",
    "insert",
    "merge",
    "replace",
    "update",
}
_TRANSACTION_KEYWORDS = {
    "begin",
    "commit",
    "rollback",
    "savepoint",
}
_READ_ONLY_KEYWORDS = {
    "desc",
    "describe",
    "explain",
    "select",
    "show",
    "with",
}


def split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    i = 0
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False

    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            buffer.append(char)
            if char == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            buffer.append(char)
            if char == "*" and next_char == "/":
                buffer.append(next_char)
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if not in_single_quote and not in_double_quote and not in_backtick:
            if char == "-" and next_char == "-":
                buffer.extend([char, next_char])
                in_line_comment = True
                i += 2
                continue
            if char == "/" and next_char == "*":
                buffer.extend([char, next_char])
                in_block_comment = True
                i += 2
                continue
            if char == ";":
                statement = "".join(buffer).strip()
                if statement:
                    statements.append(statement)
                buffer = []
                i += 1
                continue

        buffer.append(char)

        if char == "'" and not in_double_quote and not in_backtick:
            if in_single_quote and next_char == "'":
                buffer.append(next_char)
                i += 2
                continue
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote and not in_backtick:
            in_double_quote = not in_double_quote
        elif char == "`" and not in_single_quote and not in_double_quote:
            in_backtick = not in_backtick

        i += 1

    statement = "".join(buffer).strip()
    if statement:
        statements.append(statement)
    return statements


def _remove_comments_and_literals(sql: str) -> str:
    chars: list[str] = []
    i = 0
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False

    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            chars.append("\n" if char == "\n" else " ")
            if char == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            chars.append(" ")
            if char == "*" and next_char == "/":
                chars.append(" ")
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if not in_single_quote and not in_double_quote and not in_backtick:
            if char == "-" and next_char == "-":
                chars.extend([" ", " "])
                in_line_comment = True
                i += 2
                continue
            if char == "/" and next_char == "*":
                chars.extend([" ", " "])
                in_block_comment = True
                i += 2
                continue

        if in_single_quote or in_double_quote or in_backtick:
            chars.append(" ")
            if char == "'" and in_single_quote:
                if next_char == "'":
                    chars.append(" ")
                    i += 2
                    continue
                in_single_quote = False
            elif char == '"' and in_double_quote:
                in_double_quote = False
            elif char == "`" and in_backtick:
                in_backtick = False
            i += 1
            continue

        if char == "'":
            in_single_quote = True
            chars.append(" ")
        elif char == '"':
            in_double_quote = True
            chars.append(" ")
        elif char == "`":
            in_backtick = True
            chars.append(" ")
        else:
            chars.append(char)

        i += 1

    return "".join(chars)


def _keywords(sql: str) -> set[str]:
    clean_sql = _remove_comments_and_literals(sql)
    return {word.lower() for word in re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", clean_sql)}


def _first_keyword(sql: str) -> str | None:
    clean_sql = _remove_comments_and_literals(sql)
    match = re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", clean_sql)
    if match is None:
        return None
    return match.group(0).lower()


def classify_sql_risk(sql: str) -> SqlRisk:
    statements = split_sql_statements(sql)
    if not statements:
        return SqlRisk.UNKNOWN

    highest_risk = SqlRisk.READ_ONLY
    for statement in statements:
        first_keyword = _first_keyword(statement)
        keywords = _keywords(statement)

        if first_keyword is None:
            return SqlRisk.UNKNOWN
        if first_keyword in _TRANSACTION_KEYWORDS or "transaction" in keywords:
            return SqlRisk.TRANSACTION
        if first_keyword in _DDL_KEYWORDS or keywords & _DDL_KEYWORDS:
            highest_risk = SqlRisk.DDL
            continue
        if first_keyword in _WRITE_KEYWORDS or keywords & _WRITE_KEYWORDS:
            if highest_risk != SqlRisk.DDL:
                highest_risk = SqlRisk.WRITE
            continue
        if first_keyword not in _READ_ONLY_KEYWORDS:
            return SqlRisk.UNKNOWN

    return highest_risk


def validate_read_only_sql(sql: str, *, allow_multi_statement: bool = False) -> tuple[bool, SqlRisk, str | None]:
    statements = split_sql_statements(sql)
    if not statements:
        return False, SqlRisk.UNKNOWN, "SQL 不能为空"

    if not allow_multi_statement and len(statements) > 1:
        return False, classify_sql_risk(sql), "不允许多语句 SQL"

    risk = classify_sql_risk(sql)
    if risk != SqlRisk.READ_ONLY:
        return False, risk, f"只允许只读 SQL，当前风险级别为 {risk.value}"

    return True, risk, None
