# -*- coding: utf-8 -*-

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


DataSourceType = Literal["mysql", "postgresql", "api", "file", "sqlite", "clickhouse"]


class AIBaseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class DataSourceCreate(AIBaseSchema):
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


class DataSourceUpdate(AIBaseSchema):
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


class SemanticModelCreate(AIBaseSchema):
    data_source_id: int = Field(gt=0, description="数据源ID")
    name: str = Field(min_length=1, max_length=128, description="语义模型名称")
    code: str = Field(min_length=1, max_length=128, description="语义模型编码")
    table_name: str = Field(min_length=1, max_length=128, description="主表名")
    table_description: str | None = Field(default=None, description="表说明")
    fields: list[dict[str, Any]] = Field(default_factory=list, description="字段配置")
    metrics: list[dict[str, Any]] = Field(default_factory=list, description="指标配置")
    dimensions: list[dict[str, Any]] = Field(default_factory=list, description="维度配置")
    terms: list[dict[str, Any]] = Field(default_factory=list, description="业务术语")
    example_questions: list[str] = Field(default_factory=list, description="示例问题")
    prompt_hints: str | None = Field(default=None, description="提示词补充说明")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")


class SemanticModelUpdate(AIBaseSchema):
    data_source_id: int | None = Field(default=None, gt=0, description="数据源ID")
    name: str | None = Field(default=None, min_length=1, max_length=128, description="语义模型名称")
    table_name: str | None = Field(default=None, min_length=1, max_length=128, description="主表名")
    table_description: str | None = Field(default=None, description="表说明")
    fields: list[dict[str, Any]] | None = Field(default=None, description="字段配置")
    metrics: list[dict[str, Any]] | None = Field(default=None, description="指标配置")
    dimensions: list[dict[str, Any]] | None = Field(default=None, description="维度配置")
    terms: list[dict[str, Any]] | None = Field(default=None, description="业务术语")
    example_questions: list[str] | None = Field(default=None, description="示例问题")
    prompt_hints: str | None = Field(default=None, description="提示词补充说明")
    description: str | None = Field(default=None, description="说明")
    owner: str | None = Field(default=None, max_length=64, description="负责人")
    owner_id: int | None = Field(default=None, description="负责人ID")
    status: int | None = Field(default=None, description="状态")


class QuestionPlanRequest(AIBaseSchema):
    question: str = Field(min_length=1, max_length=2000, description="自然语言问题")
    semantic_model_id: int | None = Field(default=None, gt=0, description="指定语义模型ID")
    requester: str | None = Field(default=None, max_length=64, description="提问人")
    requester_id: int | None = Field(default=None, description="提问人ID")


class SqlRiskCheckRequest(AIBaseSchema):
    sql: str = Field(min_length=1, description="待检查SQL")
    allow_multi_statement: bool = Field(default=False, description="是否允许多语句")


class SqlRiskCheckResponse(AIBaseSchema):
    is_read_only: bool
    risk: str
    message: str | None = None
