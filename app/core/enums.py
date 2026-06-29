# -*- coding: utf-8 -*-
# @Time    : 2026-06-29 19:59:08
# @Author  : yangyuexiong
# @File    : enums.py

from enum import Enum


class UserStatus(str, Enum):
    normal = "正常"
    disable = "禁用"