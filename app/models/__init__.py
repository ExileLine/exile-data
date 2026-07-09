# -*- coding: utf-8 -*-
# @Time    : 2026-06-29 19:59:08
# @Author  : yangyuexiong
# @File    : __init__.py

# 新增模型后，请在这里导入，供 Alembic 自动发现
from app.models.admin import Admin
from app.models.aps_task import ApsTask
from app.models.bi import AIDataSource, AIQuestionSession, AISemanticModel

__all__ = [
    "Admin",
    "AIDataSource",
    "AIQuestionSession",
    "AISemanticModel",
    "ApsTask",
]
