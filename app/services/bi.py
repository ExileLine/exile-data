# -*- coding: utf-8 -*-

from typing import Any, Type

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.custom_exception import CustomException
from app.core.sql_guard import validate_read_only_sql
from app.models.bi import AIQuestionSession, AISemanticModel
from app.models.base import CustomBaseModel


async def _commit(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise CustomException(
            status_code=400,
            custom_code=10003,
            detail="资源编码已存在，或关联资源不存在",
        ) from exc


async def list_resources(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    *,
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    filters: dict[str, Any] | None = None,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    conditions = [model.is_deleted == 0]

    if keyword:
        like_keyword = f"%{keyword}%"
        conditions.append(or_(model.name.like(like_keyword), model.code.like(like_keyword)))

    for key, value in (filters or {}).items():
        if value is not None and hasattr(model, key):
            conditions.append(getattr(model, key) == value)

    total_stmt = select(func.count()).select_from(model).where(*conditions)
    total = await session.scalar(total_stmt)

    stmt = (
        select(model)
        .where(*conditions)
        .order_by(model.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await session.scalars(stmt)
    records = [item.to_dict(exclude=exclude) for item in result.all()]

    return {
        "records": records,
        "now_page": page,
        "total": total or 0,
    }


async def get_resource(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    resource_id: int,
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any] | None:
    stmt = select(model).where(model.id == resource_id, model.is_deleted == 0)
    obj = await session.scalar(stmt)
    if obj is None:
        return None
    return obj.to_dict(exclude=exclude)


async def create_resource(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    payload: dict[str, Any],
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    obj = model(**payload)
    session.add(obj)
    await _commit(session)
    await session.refresh(obj)
    return obj.to_dict(exclude=exclude)


async def update_resource(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    resource_id: int,
    payload: dict[str, Any],
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any] | None:
    stmt = select(model).where(model.id == resource_id, model.is_deleted == 0)
    obj = await session.scalar(stmt)
    if obj is None:
        return None

    for key, value in payload.items():
        if hasattr(obj, key):
            setattr(obj, key, value)

    obj.touch()
    await _commit(session)
    await session.refresh(obj)
    return obj.to_dict(exclude=exclude)


async def delete_resource(session: AsyncSession, model: Type[CustomBaseModel], resource_id: int) -> bool:
    stmt = select(model).where(model.id == resource_id, model.is_deleted == 0)
    obj = await session.scalar(stmt)
    if obj is None:
        return False

    obj.is_deleted = 1
    obj.touch()
    await _commit(session)
    return True


def _normalize_question(value: str) -> str:
    return " ".join(value.strip().split())


def _match_tokens(question: str, values: list[str]) -> list[str]:
    normalized_question = question.lower()
    matches: list[str] = []
    for value in values:
        normalized_value = str(value).strip()
        if normalized_value and normalized_value.lower() in normalized_question:
            matches.append(normalized_value)
    return matches


def _semantic_field_matches(question: str, items: list[dict[str, Any]]) -> list[str]:
    normalized_question = question.lower()
    matches: list[str] = []
    for item in items:
        field = item.get("field")
        candidates = [item.get("name"), item.get("field"), item.get("alias")]
        for candidate in candidates:
            candidate_text = str(candidate).strip() if candidate else ""
            if candidate_text and candidate_text.lower() in normalized_question:
                if field:
                    matches.append(str(field))
                break
    return matches


def _extract_semantic_names(items: list[dict[str, Any]], *keys: str) -> list[str]:
    names: list[str] = []
    for item in items:
        for key in keys:
            value = item.get(key)
            if value:
                names.append(str(value))
    return names


def build_question_plan(question: str, semantic_model: dict[str, Any] | None) -> dict[str, Any]:
    normalized_question = _normalize_question(question)

    if semantic_model is None:
        return {
            "question": normalized_question,
            "matched_semantic_model": None,
            "matched_terms": [],
            "matched_dimensions": [],
            "matched_metrics": [],
            "candidate_fields": [],
            "generated_sql": None,
            "explanation": "未指定语义模型，当前仅生成问数记录，不生成 SQL 草案。",
        }

    fields = semantic_model.get("fields") or []
    dimensions = semantic_model.get("dimensions") or []
    metrics = semantic_model.get("metrics") or []
    terms = semantic_model.get("terms") or []
    table_name = semantic_model.get("table_name")

    field_names = _extract_semantic_names(fields, "field")
    term_names = _extract_semantic_names(terms, "term", "name", "alias")

    matched_dimensions = _semantic_field_matches(normalized_question, dimensions)
    matched_metrics = _semantic_field_matches(normalized_question, metrics)
    matched_terms = _match_tokens(normalized_question, term_names)

    selected_fields = matched_dimensions + matched_metrics
    if not selected_fields:
        selected_fields = field_names[:5]

    selected_fields = list(dict.fromkeys(selected_fields))
    generated_sql = None
    if table_name and selected_fields:
        generated_sql = f"select {', '.join(selected_fields)} from {table_name} limit 100"

    return {
        "question": normalized_question,
        "matched_semantic_model": {
            "id": semantic_model.get("id"),
            "name": semantic_model.get("name"),
            "code": semantic_model.get("code"),
            "table_name": table_name,
        },
        "matched_terms": matched_terms,
        "matched_dimensions": matched_dimensions,
        "matched_metrics": matched_metrics,
        "candidate_fields": selected_fields,
        "generated_sql": generated_sql,
        "explanation": "当前为规则版问数计划，用于验证语义层和 SQL 安全链路；后续接入大模型生成 SQL。",
    }


async def create_question_plan(
    session: AsyncSession,
    *,
    question: str,
    semantic_model_id: int | None = None,
    requester: str | None = None,
    requester_id: int | None = None,
) -> dict[str, Any]:
    semantic_model_data: dict[str, Any] | None = None

    if semantic_model_id is not None:
        semantic_model_data = await get_resource(session, AISemanticModel, semantic_model_id)
        if semantic_model_data is None:
            raise CustomException(status_code=404, custom_code=10002, detail="语义模型不存在")

    plan = build_question_plan(question, semantic_model_data)
    generated_sql = plan.get("generated_sql")
    sql_risk = None
    error_message = None
    state = "planned"

    if generated_sql:
        is_valid, risk, message = validate_read_only_sql(generated_sql, allow_multi_statement=False)
        sql_risk = risk.value
        if not is_valid:
            error_message = message
            state = "blocked"

    record = AIQuestionSession(
        question=plan["question"],
        semantic_model_id=semantic_model_id,
        generated_sql=generated_sql,
        sql_risk=sql_risk,
        plan=plan,
        error_message=error_message,
        state=state,
        requester=requester,
        requester_id=requester_id,
    )
    session.add(record)
    await _commit(session)
    await session.refresh(record)
    return record.to_dict()
