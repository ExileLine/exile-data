# -*- coding: utf-8 -*-

from typing import Any, Type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_exception import CustomException
from app.core.response import api_response
from app.core.sql_guard import validate_read_only_sql
from app.db.session import get_db_session
from app.models.bi import BIChart, BIDashboard, BIDataSource, BIDataset
from app.models.base import CustomBaseModel
from app.schemas.bi import (
    ChartCreate,
    ChartUpdate,
    DashboardCreate,
    DashboardUpdate,
    DataSourceCreate,
    DataSourceUpdate,
    DatasetCreate,
    DatasetUpdate,
    SqlRiskCheckRequest,
)
from app.services.bi import create_resource, delete_resource, get_resource, list_resources, update_resource

router = APIRouter(prefix="/bi", tags=["bi"])

DATA_SOURCE_EXCLUDE = {"password"}


def _ensure_dataset_sql_read_only(sql_text: str) -> None:
    is_valid, _risk, message = validate_read_only_sql(sql_text, allow_multi_statement=False)
    if not is_valid:
        raise CustomException(status_code=400, custom_code=10005, detail=message or "数据集 SQL 校验失败")


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
        BIDataSource,
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
        BIDataSource,
        payload.model_dump(exclude_unset=True),
        exclude=DATA_SOURCE_EXCLUDE,
    )


@router.get("/data-sources/{resource_id}", summary="数据源详情")
async def get_data_source(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, BIDataSource, resource_id, exclude=DATA_SOURCE_EXCLUDE)


@router.put("/data-sources/{resource_id}", summary="更新数据源")
async def update_data_source(
    resource_id: int,
    payload: DataSourceUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    return await _update_endpoint(
        session,
        BIDataSource,
        resource_id,
        payload.model_dump(exclude_unset=True),
        exclude=DATA_SOURCE_EXCLUDE,
    )


@router.delete("/data-sources/{resource_id}", summary="删除数据源")
async def delete_data_source(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, BIDataSource, resource_id)


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


@router.get("/datasets", summary="数据集列表")
async def list_datasets(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    data_source_id: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(
        session,
        BIDataset,
        page=page,
        size=size,
        keyword=keyword,
        filters={"data_source_id": data_source_id},
    )


@router.post("/datasets", summary="创建数据集")
async def create_dataset(payload: DatasetCreate, session: AsyncSession = Depends(get_db_session)):
    _ensure_dataset_sql_read_only(payload.sql_text)
    return await _create_endpoint(session, BIDataset, payload.model_dump(exclude_unset=True))


@router.get("/datasets/{resource_id}", summary="数据集详情")
async def get_dataset(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, BIDataset, resource_id)


@router.put("/datasets/{resource_id}", summary="更新数据集")
async def update_dataset(resource_id: int, payload: DatasetUpdate, session: AsyncSession = Depends(get_db_session)):
    update_data = payload.model_dump(exclude_unset=True)
    if "sql_text" in update_data:
        _ensure_dataset_sql_read_only(update_data["sql_text"])
    return await _update_endpoint(session, BIDataset, resource_id, update_data)


@router.delete("/datasets/{resource_id}", summary="删除数据集")
async def delete_dataset(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, BIDataset, resource_id)


@router.get("/charts", summary="图表列表")
async def list_charts(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    dataset_id: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(
        session,
        BIChart,
        page=page,
        size=size,
        keyword=keyword,
        filters={"dataset_id": dataset_id},
    )


@router.post("/charts", summary="创建图表")
async def create_chart(payload: ChartCreate, session: AsyncSession = Depends(get_db_session)):
    return await _create_endpoint(session, BIChart, payload.model_dump(exclude_unset=True))


@router.get("/charts/{resource_id}", summary="图表详情")
async def get_chart(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, BIChart, resource_id)


@router.put("/charts/{resource_id}", summary="更新图表")
async def update_chart(resource_id: int, payload: ChartUpdate, session: AsyncSession = Depends(get_db_session)):
    return await _update_endpoint(session, BIChart, resource_id, payload.model_dump(exclude_unset=True))


@router.delete("/charts/{resource_id}", summary="删除图表")
async def delete_chart(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, BIChart, resource_id)


@router.get("/dashboards", summary="仪表盘列表")
async def list_dashboards(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    keyword: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
):
    return await _list_endpoint(session, BIDashboard, page=page, size=size, keyword=keyword)


@router.post("/dashboards", summary="创建仪表盘")
async def create_dashboard(payload: DashboardCreate, session: AsyncSession = Depends(get_db_session)):
    return await _create_endpoint(session, BIDashboard, payload.model_dump(exclude_unset=True))


@router.get("/dashboards/{resource_id}", summary="仪表盘详情")
async def get_dashboard(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _get_endpoint(session, BIDashboard, resource_id)


@router.put("/dashboards/{resource_id}", summary="更新仪表盘")
async def update_dashboard(
    resource_id: int,
    payload: DashboardUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    return await _update_endpoint(session, BIDashboard, resource_id, payload.model_dump(exclude_unset=True))


@router.delete("/dashboards/{resource_id}", summary="删除仪表盘")
async def delete_dashboard(resource_id: int, session: AsyncSession = Depends(get_db_session)):
    return await _delete_endpoint(session, BIDashboard, resource_id)
