#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 09:50:07
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 10:55:49
@Description    : QQ Tables
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from tortoise import fields
from tortoise.models import Model


class QQUser(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(null=False, unique=True, index=True)
    access_token = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "qq_user"


class QQGroup(Model):
    id = fields.IntField(pk=True)
    group_id = fields.BigIntField(null=False, unique=True, index=True)
    bind_repo = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "qq_group"
