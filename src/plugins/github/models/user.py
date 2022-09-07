#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 09:50:07
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 07:35:01
@Description    : QQ Tables
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQUserMixin:
    qq_id = fields.BigIntField(null=True, unique=True, index=True)


class QQGuildMixin:
    qqguild_id = fields.CharField(max_length=255, null=True, unique=True, index=True)


class User(QQUserMixin, QQGuildMixin, Model):
    id = fields.BigIntField(pk=True)
    access_token = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "user"

    @property
    def user_id(self) -> int | str:
        return self.qq_id or self.qqguild_id
