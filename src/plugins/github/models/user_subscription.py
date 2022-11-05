#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-26 14:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-31 17:10:12
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQUserMixin:
    qq_id = fields.BigIntField(null=True, index=True)


class QQGuildMixin:
    qqguild_id = fields.CharField(max_length=255, null=True, index=True)


class PlatformUser(QQUserMixin, QQGuildMixin, Model):
    @property
    def user_id(self) -> int | str:
        return self.qq_id or self.qqguild_id

    class Meta:
        abstract = True


class UserSubscription(PlatformUser, Model):
    id = fields.BigIntField(pk=True)
    owner = fields.CharField(max_length=255, null=False)
    repo = fields.CharField(max_length=255, null=False)
    event = fields.CharField(max_length=255, null=False)
    action: list[str] | None = fields.JSONField(null=True)

    class Meta:
        table = "user_subscription"
        indexes = (("owner", "repo", "event"),)
        unique_together = (("qq_id", "qqguild_id", "owner", "repo", "event"),)
