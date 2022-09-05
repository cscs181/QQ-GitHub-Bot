#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:33:18
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 11:37:45
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from tortoise import fields
from tortoise.models import Model


class QQGuildUser(Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=32, null=False, unique=True, index=True)
    access_token = fields.CharField(max_length=255, null=False)


class QQChannel(Model):
    id = fields.IntField(pk=True)
    group_id = fields.CharField(
        max_length=32, source_field="channel_id", null=False, unique=True, index=True
    )
    bind_repo = fields.CharField(max_length=255, null=True)
