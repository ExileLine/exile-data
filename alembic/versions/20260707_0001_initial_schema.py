"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-07 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="ID"),
        sa.Column("create_time", sa.DateTime(timezone=True), nullable=False, comment="创建时间"),
        sa.Column("update_time", sa.DateTime(timezone=True), nullable=False, comment="更新时间"),
        sa.Column("create_timestamp", sa.BigInteger(), nullable=False, comment="创建时间戳"),
        sa.Column("update_timestamp", sa.BigInteger(), nullable=False, comment="更新时间戳"),
        sa.Column("is_deleted", sa.BigInteger(), nullable=True, comment="逻辑删除标识"),
        sa.Column("status", sa.BigInteger(), nullable=True, comment="状态(通用字段)"),
        sa.PrimaryKeyConstraint("id"),
    ]


def upgrade() -> None:
    op.create_table(
        "admin",
        sa.Column("username", sa.String(length=255), nullable=True, comment="用户名"),
        sa.Column("password", sa.String(length=255), nullable=False, comment="密码"),
        sa.Column("nickname", sa.String(length=128), nullable=True, comment="昵称"),
        sa.Column("phone", sa.String(length=64), nullable=True, comment="手机号"),
        sa.Column("mail", sa.String(length=256), nullable=True, comment="邮箱"),
        sa.Column("code", sa.String(length=64), nullable=True, comment="用户编号"),
        sa.Column("seat", sa.String(length=64), nullable=True, comment="座位编号"),
        sa.Column("department", sa.String(length=64), nullable=True, comment="部门"),
        sa.Column("position", sa.String(length=64), nullable=True, comment="职位"),
        sa.Column("superior", sa.String(length=64), nullable=True, comment="上级"),
        sa.Column("login_type", sa.String(length=64), nullable=True, comment="登录类型:single;many"),
        sa.Column("is_tourist", sa.Integer(), nullable=False, comment="0-游客账户;1-非游客账户"),
        sa.Column("creator", sa.String(length=32), nullable=True, comment="创建人"),
        sa.Column("creator_id", sa.BigInteger(), nullable=True, comment="创建人id"),
        sa.Column("modifier", sa.String(length=32), nullable=True, comment="更新人"),
        sa.Column("modifier_id", sa.BigInteger(), nullable=True, comment="更新人id"),
        sa.Column("remark", sa.String(length=255), nullable=True, comment="备注"),
        *_audit_columns(),
    )

    op.create_table(
        "aps_tasks",
        sa.Column("task_id", sa.String(length=64), nullable=False, comment="任务id"),
        sa.Column("trigger_type", sa.String(length=16), nullable=False, comment="触发器类型:date;interval;cron"),
        sa.Column("trigger_param", sa.JSON(), nullable=False, comment="触发器参数"),
        sa.Column("task_function_name", sa.String(length=255), nullable=True, comment="任务函数名称"),
        sa.Column("task_function_args", sa.JSON(), nullable=False, comment="任务参数:args"),
        sa.Column("task_function_kwargs", sa.JSON(), nullable=False, comment="任务参数:kwargs"),
        *_audit_columns(),
    )

    op.create_table(
        "bi_data_source",
        sa.Column("name", sa.String(length=128), nullable=False, comment="数据源名称"),
        sa.Column("code", sa.String(length=128), nullable=False, comment="数据源编码"),
        sa.Column("source_type", sa.String(length=32), nullable=False, comment="数据源类型"),
        sa.Column("host", sa.String(length=255), nullable=True, comment="主机地址"),
        sa.Column("port", sa.Integer(), nullable=True, comment="端口"),
        sa.Column("database", sa.String(length=128), nullable=True, comment="数据库名"),
        sa.Column("username", sa.String(length=128), nullable=True, comment="用户名"),
        sa.Column("password", sa.String(length=512), nullable=True, comment="密码/密钥"),
        sa.Column("read_only", sa.Boolean(), nullable=False, comment="是否只读"),
        sa.Column("extra_config", sa.JSON(), nullable=False, comment="扩展配置"),
        sa.Column("description", sa.Text(), nullable=True, comment="说明"),
        sa.Column("owner", sa.String(length=64), nullable=True, comment="负责人"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True, comment="负责人ID"),
        *_audit_columns(),
    )
    op.create_index("ix_bi_data_source_code", "bi_data_source", ["code"], unique=True)

    op.create_table(
        "bi_dataset",
        sa.Column("data_source_id", sa.Integer(), nullable=False, comment="数据源ID"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="数据集名称"),
        sa.Column("code", sa.String(length=128), nullable=False, comment="数据集编码"),
        sa.Column("sql_text", sa.Text(), nullable=False, comment="数据集SQL"),
        sa.Column("dimensions", sa.JSON(), nullable=False, comment="维度配置"),
        sa.Column("metrics", sa.JSON(), nullable=False, comment="指标配置"),
        sa.Column("filters", sa.JSON(), nullable=False, comment="筛选器配置"),
        sa.Column("cache_ttl_seconds", sa.Integer(), nullable=False, comment="缓存秒数"),
        sa.Column("description", sa.Text(), nullable=True, comment="说明"),
        sa.Column("owner", sa.String(length=64), nullable=True, comment="负责人"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True, comment="负责人ID"),
        *_audit_columns(),
        sa.ForeignKeyConstraint(["data_source_id"], ["bi_data_source.id"]),
    )
    op.create_index("ix_bi_dataset_code", "bi_dataset", ["code"], unique=True)
    op.create_index("ix_bi_dataset_data_source_id", "bi_dataset", ["data_source_id"], unique=False)

    op.create_table(
        "bi_chart",
        sa.Column("dataset_id", sa.Integer(), nullable=False, comment="数据集ID"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="图表名称"),
        sa.Column("code", sa.String(length=128), nullable=False, comment="图表编码"),
        sa.Column("chart_type", sa.String(length=32), nullable=False, comment="图表类型"),
        sa.Column("query_config", sa.JSON(), nullable=False, comment="查询配置"),
        sa.Column("display_config", sa.JSON(), nullable=False, comment="展示配置"),
        sa.Column("description", sa.Text(), nullable=True, comment="说明"),
        sa.Column("owner", sa.String(length=64), nullable=True, comment="负责人"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True, comment="负责人ID"),
        *_audit_columns(),
        sa.ForeignKeyConstraint(["dataset_id"], ["bi_dataset.id"]),
    )
    op.create_index("ix_bi_chart_code", "bi_chart", ["code"], unique=True)
    op.create_index("ix_bi_chart_dataset_id", "bi_chart", ["dataset_id"], unique=False)

    op.create_table(
        "bi_dashboard",
        sa.Column("name", sa.String(length=128), nullable=False, comment="仪表盘名称"),
        sa.Column("code", sa.String(length=128), nullable=False, comment="仪表盘编码"),
        sa.Column("layout_config", sa.JSON(), nullable=False, comment="布局配置"),
        sa.Column("chart_config", sa.JSON(), nullable=False, comment="图表编排配置"),
        sa.Column("description", sa.Text(), nullable=True, comment="说明"),
        sa.Column("owner", sa.String(length=64), nullable=True, comment="负责人"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True, comment="负责人ID"),
        *_audit_columns(),
    )
    op.create_index("ix_bi_dashboard_code", "bi_dashboard", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_bi_dashboard_code", table_name="bi_dashboard")
    op.drop_table("bi_dashboard")
    op.drop_index("ix_bi_chart_dataset_id", table_name="bi_chart")
    op.drop_index("ix_bi_chart_code", table_name="bi_chart")
    op.drop_table("bi_chart")
    op.drop_index("ix_bi_dataset_data_source_id", table_name="bi_dataset")
    op.drop_index("ix_bi_dataset_code", table_name="bi_dataset")
    op.drop_table("bi_dataset")
    op.drop_index("ix_bi_data_source_code", table_name="bi_data_source")
    op.drop_table("bi_data_source")
    op.drop_table("aps_tasks")
    op.drop_table("admin")
