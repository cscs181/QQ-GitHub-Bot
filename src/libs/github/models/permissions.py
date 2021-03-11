#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 16:00:01
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 16:00:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from . import BaseModel


class Permissions(BaseModel):
    pull: bool
    push: bool
    admin: bool
