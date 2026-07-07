from app.core.sql_guard import SqlRisk, classify_sql_risk, split_sql_statements, validate_read_only_sql


def test_split_sql_statements_ignores_semicolon_in_string() -> None:
    statements = split_sql_statements("select ';' as value; select 1")

    assert statements == ["select ';' as value", "select 1"]


def test_classify_read_only_sql() -> None:
    assert classify_sql_risk("select * from orders where status = 'delete'") == SqlRisk.READ_ONLY
    assert classify_sql_risk("with t as (select 1) select * from t") == SqlRisk.READ_ONLY


def test_classify_write_sql() -> None:
    assert classify_sql_risk("update orders set amount = 1") == SqlRisk.WRITE


def test_classify_ddl_sql() -> None:
    assert classify_sql_risk("drop table orders") == SqlRisk.DDL


def test_validate_read_only_sql_rejects_multi_statement() -> None:
    is_valid, risk, message = validate_read_only_sql("select 1; select 2")

    assert is_valid is False
    assert risk == SqlRisk.READ_ONLY
    assert message == "不允许多语句 SQL"
