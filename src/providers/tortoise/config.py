#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 13:43:32
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 19:17:59
@Description    : Config for Tortoise provider
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
