#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-10-04 16:32:00
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 16:58:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import BaseSettings


class Config(BaseSettings):
    server_status_cpu: bool = True
    server_status_per_cpu: bool = False
    server_status_memory: bool = True
    server_status_disk: bool = True

    class Config:
        extra = "ignore"
