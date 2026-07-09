from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.bi import DataSourceCreate
from app.services.bi import build_question_plan


client = TestClient(app)


def test_ai_question_routes_registered_in_openapi() -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/ai-question/data-sources" in paths
    assert "/api/v1/ai-question/semantic-models" in paths
    assert "/api/v1/ai-question/sql/risk" in paths
    assert "/api/v1/ai-question/questions/plan" in paths
    assert "/api/v1/ai-question/questions" in paths


def test_data_source_schema_validation() -> None:
    try:
        DataSourceCreate.model_validate(
            {
                "name": "主库",
                "code": "main_db",
                "source_type": "mysql",
                "port": 70000,
            }
        )
    except ValidationError as exc:
        errors = exc.errors()
    else:
        raise AssertionError("expected data source port validation to fail")

    assert errors[0]["loc"] == ("port",)
    assert errors[0]["type"] == "less_than_equal"


def test_sql_risk_endpoint_detects_write_sql() -> None:
    response = client.post("/api/v1/ai-question/sql/risk", json={"sql": "delete from orders"})

    assert response.status_code == 200
    assert response.json()["data"] == {
        "is_read_only": False,
        "risk": "write",
        "message": "只允许只读 SQL，当前风险级别为 write",
    }


def test_build_question_plan_with_semantic_model() -> None:
    plan = build_question_plan(
        "按订单状态统计销售金额",
        {
            "id": 1,
            "name": "订单语义模型",
            "code": "orders",
            "table_name": "orders",
            "fields": [
                {"name": "订单状态", "field": "status"},
                {"name": "销售金额", "field": "amount"},
            ],
            "dimensions": [{"name": "订单状态", "field": "status"}],
            "metrics": [{"name": "销售金额", "field": "amount"}],
            "terms": [{"term": "销售金额", "alias": "GMV"}],
        },
    )

    assert plan["matched_semantic_model"]["code"] == "orders"
    assert plan["candidate_fields"] == ["status", "amount"]
    assert plan["generated_sql"] == "select status, amount from orders limit 100"
