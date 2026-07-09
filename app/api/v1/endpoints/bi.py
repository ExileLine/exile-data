# -*- coding: utf-8 -*-

from typing import Any, Type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import api_response
from app.core.sql_guard import validate_read_only_sql
from app.db.session import get_db_session
from app.models.bi import AIDataSource, AIQuestionSession, AISemanticModel
from app.models.base import CustomBaseModel
from app.schemas.bi import (
    DataSourceCreate,
    DataSourceUpdate,
    QuestionPlanRequest,
    SemanticModelCreate,
    SemanticModelUpdate,
    SqlRiskCheckRequest,
)
from app.services.bi import (
    create_question_plan,
    create_resource,
    delete_resource,
    get_resource,
    list_resources,
    update_resource,
)

router = APIRouter(prefix="/ai-question", tags=["ai-question"])

DATA_SOURCE_EXCLUDE = {"password"}


async def _list_endpoint(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    *,
    page: int,
    size: int,
    keyword: str | None,
    filters: dict[str, Any] | None = None,
    exclude: set[str] | None = None,
):
    data = await list_resources(
        session,
        model,
        page=page,
        size=size,
        keyword=keyword,
        filters=filters,
        exclude=exclude,
    )
    return api_response(data=data)


async def _get_endpoint(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    resource_id: int,
    *,
    exclude: set[str] | None = None,
):
    data = await get_resource(session, model, resource_id, exclude=exclude)
    if data is None:
        return api_response(http_code=404, code=10002)
    return api_response(data=data)


async def _create_endpoint(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    payload: dict[str, Any],
    *,
    exclude: set[str] | None = None,
):
    data = await create_resource(session, model, payload, exclude=exclude)
    return api_response(http_code=201, code=201, data=data)


async def _update_endpoint(
    session: AsyncSession,
    model: Type[CustomBaseModel],
    resource_id: int,
    payload: dict[str, Any],
    *,
    exclude: set[str] | None = None,
):
    data = await update_resource(session, model, resource_id, payload, exclude=exclude)
    if data is None:
        return api_response(http_code=404, code=10002)
    return api_response(code=203, data=data)


async def _delete_endpoint(session: AsyncSession, model: Type[CustomBaseModel], resource_id: int):
    deleted = await delete_resource(session, model, resource_id)
    if not deleted:
        return api_response(http_code=404, code=10002)
    return api_response(code=204)


@router.get("/data-sources", summary="数据源列表")
async def list_data_sources(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(
        session,
        AIDataSource,
        page=page,
        size=size,
        keyword=keyword,
        filters={"source_type": source_type},
        exclude=DATA_SOURCE_EXCLUDE,
    )


@router.post("/data-sources", summary="创建数据源")
async def create_data_source(payload: DataSourceCreate, session: AsyncSession = Depends(get_db_session)):
    return await _create_endpoint(
        session,
        AIDataSource,
        payload.model_dump(exclude_unset=True),
        exclude=DATA_SOURCE_EXCLUDE,
    )


@router.get("/data-sources/{resource_id}", summary="数据源详情")
async def get_data_source(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, AIDataSource, resource_id, exclude=DATA_SOURCE_EXCLUDE)


@router.put("/data-sources/{resource_id}", summary="更新数据源")
async def update_data_source(
    resource_id: int,
    payload: DataSourceUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    return await _update_endpoint(
        session,
        AIDataSource,
        resource_id,
        payload.model_dump(exclude_unset=True),
        exclude=DATA_SOURCE_EXCLUDE,
    )


@router.delete("/data-sources/{resource_id}", summary="删除数据源")
async def delete_data_source(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, AIDataSource, resource_id)


@router.get("/semantic-models", summary="语义模型列表")
async def list_semantic_models(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    data_source_id: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(
        session,
        AISemanticModel,
        page=page,
        size=size,
        keyword=keyword,
        filters={"data_source_id": data_source_id},
    )


@router.post("/semantic-models", summary="创建语义模型")
async def create_semantic_model(payload: SemanticModelCreate, session: AsyncSession = Depends(get_db_session)):
    return await _create_endpoint(session, AISemanticModel, payload.model_dump(exclude_unset=True))


@router.get("/semantic-models/{resource_id}", summary="语义模型详情")
async def get_semantic_model(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, AISemanticModel, resource_id)


@router.put("/semantic-models/{resource_id}", summary="更新语义模型")
async def update_semantic_model(
    resource_id: int,
    payload: SemanticModelUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    return await _update_endpoint(session, AISemanticModel, resource_id, payload.model_dump(exclude_unset=True))


@router.delete("/semantic-models/{resource_id}", summary="删除语义模型")
async def delete_semantic_model(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, AISemanticModel, resource_id)


@router.post("/sql/risk", summary="SQL 风险检查")
async def check_sql_risk(payload: SqlRiskCheckRequest):
    is_valid, risk, message = validate_read_only_sql(
        payload.sql,
        allow_multi_statement=payload.allow_multi_statement,
    )
    data = {
        "is_read_only": is_valid,
        "risk": risk.value,
        "message": message,
    }
    return api_response(data=data)


@router.post("/questions/plan", summary="生成问数计划")
async def plan_question(payload: QuestionPlanRequest, session: AsyncSession = Depends(get_db_session)):
    data = await create_question_plan(
        session,
        question=payload.question,
        semantic_model_id=payload.semantic_model_id,
        requester=payload.requester,
        requester_id=payload.requester_id,
    )
    return api_response(http_code=201, code=201, data=data)


@router.get("/questions", summary="问数记录列表")
async def list_question_sessions(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    semantic_model_id: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(
        session,
        AIQuestionSession,
        page=page,
        size=size,
        keyword=keyword,
        filters={"semantic_model_id": semantic_model_id},
    )


@router.get("/questions/{resource_id}", summary="问数记录详情")
async def get_question_session(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, AIQuestionSession, resource_id)
