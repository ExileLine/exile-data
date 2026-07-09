# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CustomBaseModel


class AIDataSource(CustomBaseModel):
    __table_name__ = "ai_data_source"

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="数据源名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True, comment="数据源编码")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="数据源类型")
    host: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="主机地址")
    port: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="端口")
    database: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="数据库名")
    username: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="用户名")
    password: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="密码/密钥")
    read_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否只读")
    extra_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="扩展配置")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="说明")
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="负责人")
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="负责人ID")


class AISemanticModel(CustomBaseModel):
    __table_name__ = "ai_semantic_model"

    data_source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_data_source.id"),
        nullable=False,
        index=True,
        comment="数据源ID",
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="语义模型名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True, comment="语义模型编码")
    table_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="主表名")
    table_description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="表说明")
    fields: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="字段配置")
    metrics: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="指标配置")
    dimensions: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="维度配置")
    terms: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="业务术语")
    example_questions: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="示例问题")
    prompt_hints: Mapped[str | None] = mapped_column(Text, nullable=True, comment="提示词补充说明")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="说明")
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="负责人")
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="负责人ID")


class AIQuestionSession(CustomBaseModel):
    __table_name__ = "ai_question_session"

    question: Mapped[str] = mapped_column(Text, nullable=False, comment="用户问题")
    semantic_model_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("ai_semantic_model.id"),
        nullable=True,
        index=True,
        comment="语义模型ID",
    )
    generated_sql: Mapped[str | None] = mapped_column(Text, nullable=True, comment="生成SQL")
    sql_risk: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="SQL风险等级")
    plan: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="问数计划")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="结果摘要")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="planned", comment="状态")
    requester: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="提问人")
    requester_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="提问人ID")
