#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-16 01:11:47
@LastEditors    : yanyongyu
@LastEditTime   : 2021-08-04 13:40:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from nonebot.log import logger
from fastapi import Body, FastAPI

# from ..libs.hook import get_repo_hook

app: FastAPI = nonebot.get_app()


@app.post("/api/github/hook/{hook_id}")
async def hook(hook_id: str, data: dict = Body(...)):
    # TODO
    logger.info(f"Received event hook:", data)
    return {"message": "ok"}
