from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.bi import DataSourceCreate


client = TestClient(app)


def test_bi_routes_registered_in_openapi() -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/bi/data-sources" in paths
    assert "/api/v1/bi/datasets" in paths
    assert "/api/v1/bi/charts" in paths
    assert "/api/v1/bi/dashboards" in paths
    assert "/api/v1/bi/sql/risk" in paths


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
    response = client.post("/api/v1/bi/sql/risk", json={"sql": "delete from orders"})

    assert response.status_code == 200
    assert response.json()["data"] == {
        "is_read_only": False,
        "risk": "write",
        "message": "只允许只读 SQL，当前风险级别为 write",
    }


def test_dataset_create_rejects_write_sql_before_db_execution() -> None:
    response = client.post(
        "/api/v1/bi/datasets",
        json={
            "data_source_id": 1,
            "name": "订单",
            "code": "orders",
            "sql_text": "update orders set amount = 1",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == 10005
