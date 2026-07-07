# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CustomBaseModel


class BIDataSource(CustomBaseModel):
    __table_name__ = "bi_data_source"

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


class BIDataset(CustomBaseModel):
    __table_name__ = "bi_dataset"

    data_source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bi_data_source.id"),
        nullable=False,
        index=True,
        comment="数据源ID",
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="数据集名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True, comment="数据集编码")
    sql_text: Mapped[str] = mapped_column(Text, nullable=False, comment="数据集SQL")
    dimensions: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="维度配置")
    metrics: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="指标配置")
    filters: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="筛选器配置")
    cache_ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="缓存秒数")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="说明")
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="负责人")
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="负责人ID")


class BIChart(CustomBaseModel):
    __table_name__ = "bi_chart"

    dataset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bi_dataset.id"),
        nullable=False,
        index=True,
        comment="数据集ID",
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="图表名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True, comment="图表编码")
    chart_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="图表类型")
    query_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="查询配置")
    display_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="展示配置")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="说明")
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="负责人")
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="负责人ID")


class BIDashboard(CustomBaseModel):
    __table_name__ = "bi_dashboard"

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="仪表盘名称")
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True, comment="仪表盘编码")
    layout_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="布局配置")
    chart_config: Mapped[list] = mapped_column(JSON, nullable=False, default=list, comment="图表编排配置")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="说明")
    owner: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="负责人")
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="负责人ID")
