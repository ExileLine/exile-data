# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


DataSourceType = Literal["mysql", "postgresql", "api", "file", "sqlite", "clickhouse"]
ChartType = Literal["table", "line", "bar", "pie", "scatter", "indicator", "funnel", "map", "custom"]


class BIBaseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class BIResourceRead(BIBaseSchema):
    id: int
    name: str
    code: str
    description: str | None = None
    owner: str | None = None
    owner_id: int | None = None
    status: int | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class DataSourceCreate(BIBaseSchema):
    name: str = Field(min_length=1, max_length=128, description="数据源名称")
    code: str = Field(min_length=1, max_length=128, description="数据源编码")
    source_type: DataSourceType = Field(description="数据源类型")
    host: str | None = Field(default=None, max_length=255, description="主机地址")
    port: int | None = Field(default=None, ge=1, le=65535, description="端口")
    database: str | None = Field(default=None, max_length=128, description="数据库名")
    username: str | None = Field(default=None, max_length=128, description="用户名")
    password: str | None = Field(default=None, max_length=512, description="密码/密钥")
    read_only: bool = Field(default=True, description="是否只读")
    extra_config: dict[str, Any] = Field(default_factory=dict, description="扩展配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")


class DataSourceUpdate(BIBaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=128, description="数据源名称")
    source_type: DataSourceType | None = Field(default=None, description="数据源类型")
    host: str | None = Field(default=None, max_length=255, description="主机地址")
    port: int | None = Field(default=None, ge=1, le=65535, description="端口")
    database: str | None = Field(default=None, max_length=128, description="数据库名")
    username: str | None = Field(default=None, max_length=128, description="用户名")
    password: str | None = Field(default=None, max_length=512, description="密码/密钥")
    read_only: bool | None = Field(default=None, description="是否只读")
    extra_config: dict[str, Any] | None = Field(default=None, description="扩展配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")
    status: int | None = Field(default=None, description="状态")


class DatasetCreate(BIBaseSchema):
    data_source_id: int = Field(gt=0, description="数据源ID")
    name: str = Field(min_length=1, max_length=128, description="数据集名称")
    code: str = Field(min_length=1, max_length=128, description="数据集编码")
    sql_text: str = Field(min_length=1, description="数据集SQL")
    dimensions: list[dict[str, Any]] = Field(default_factory=list, description="维度配置")
    metrics: list[dict[str, Any]] = Field(default_factory=list, description="指标配置")
    filters: list[dict[str, Any]] = Field(default_factory=list, description="筛选器配置")
    cache_ttl_seconds: int = Field(default=0, ge=0, le=86400, description="缓存秒数")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")


class DatasetUpdate(BIBaseSchema):
    data_source_id: int | None = Field(default=None, gt=0, description="数据源ID")
    name: str | None = Field(default=None, min_length=1, max_length=128, description="数据集名称")
    sql_text: str | None = Field(default=None, min_length=1, description="数据集SQL")
    dimensions: list[dict[str, Any]] | None = Field(default=None, description="维度配置")
    metrics: list[dict[str, Any]] | None = Field(default=None, description="指标配置")
    filters: list[dict[str, Any]] | None = Field(default=None, description="筛选器配置")
    cache_ttl_seconds: int | None = Field(default=None, ge=0, le=86400, description="缓存秒数")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")
    status: int | None = Field(default=None, description="状态")


class ChartCreate(BIBaseSchema):
    dataset_id: int = Field(gt=0, description="数据集ID")
    name: str = Field(min_length=1, max_length=128, description="图表名称")
    code: str = Field(min_length=1, max_length=128, description="图表编码")
    chart_type: ChartType = Field(description="图表类型")
    query_config: dict[str, Any] = Field(default_factory=dict, description="查询配置")
    display_config: dict[str, Any] = Field(default_factory=dict, description="展示配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")


class ChartUpdate(BIBaseSchema):
    dataset_id: int | None = Field(default=None, gt=0, description="数据集ID")
    name: str | None = Field(default=None, min_length=1, max_length=128, description="图表名称")
    chart_type: ChartType | None = Field(default=None, description="图表类型")
    query_config: dict[str, Any] | None = Field(default=None, description="查询配置")
    display_config: dict[str, Any] | None = Field(default=None, description="展示配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")
    status: int | None = Field(default=None, description="状态")


class DashboardCreate(BIBaseSchema):
    name: str = Field(min_length=1, max_length=128, description="仪表盘名称")
    code: str = Field(min_length=1, max_length=128, description="仪表盘编码")
    layout_config: dict[str, Any] = Field(default_factory=dict, description="布局配置")
    chart_config: list[dict[str, Any]] = Field(default_factory=list, description="图表编排配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")


class DashboardUpdate(BIBaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=128, description="仪表盘名称")
    layout_config: dict[str, Any] | None = Field(default=None, description="布局配置")
    chart_config: list[dict[str, Any]] | None = Field(default=None, description="图表编排配置")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")
    status: int | None = Field(default=None, description="状态")


class SqlRiskCheckRequest(BIBaseSchema):
    sql: str = Field(min_length=1, description="待检查SQL")
    allow_multi_statement: bool = Field(default=False, description="是否允许多语句")


class SqlRiskCheckResponse(BIBaseSchema):
    is_read_only: bool
    risk: str
    message: str | None = None
