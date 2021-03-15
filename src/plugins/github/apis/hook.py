#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-16 01:11:47
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 01:13:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI

# from ..libs.hook import get_repo_hook

app: FastAPI = nonebot.get_driver().server_app


@app.post("/api/github/hook/{hook_id}")
async def hook(hook_id: str):
    # TODO
    return {"message": "ok"}
