# -*- coding: utf-8 -*-

from typing import Any, Type

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.custom_exception import CustomException
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
