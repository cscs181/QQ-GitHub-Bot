#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 20:18:19
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 12:20:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI

from ..libs.user_auth import (
    get_state_data,
    create_auth_user,
    delete_state_data,
    get_token_by_code,
)

app: FastAPI = nonebot.get_app()


@app.get("/api/github/auth")
async def auth(code: str, state: str):
    user_data = await get_state_data(state)
    if not user_data:
        return {"message": "oauth session expired"}

    token = await get_token_by_code(code)

    await delete_state_data(state)
    await create_auth_user(**user_data, access_token=token)
    return {"message": "ok"}
