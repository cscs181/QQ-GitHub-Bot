#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-26 15:04:56
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-26 15:08:23
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import fields
from tortoise.models import Model


class QQGroupMixin:
    qq_group = fields.BigIntField(null=True, unique=True, index=True)


class QQGuildChannelMixin:
    qqguild_channel = fields.CharField(
        max_length=255, null=True, unique=True, index=True
    )


class PlatformGroup(QQGroupMixin, QQGuildChannelMixin, Model):
    @property
    def group_id(self) -> int | str:
        return self.qq_group or self.qqguild_channel

    class Meta:
        abstract = True


class GroupSubscription(PlatformGroup, Model):
    id = fields.BigIntField(pk=True)
    owner: str = fields.CharField(max_length=255, null=False)
    repo: str = fields.CharField(max_length=255, null=False)
    event: str = fields.CharField(max_length=255, null=False)
    action: str = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "group_subscription"
        indexes = (("owner", "repo", "event", "action"),)
