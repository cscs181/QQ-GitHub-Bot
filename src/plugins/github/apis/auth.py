#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 20:18:19
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-22 14:50:06
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI

from src.plugins.github.models import User
from src.plugins.github.libs.auth import (
    get_state_data,
    create_auth_user,
    delete_state_data,
    get_token_by_code,
)

app: FastAPI = nonebot.get_app()


@app.get("/github/auth")
async def auth(code: str, state: str | None = None):
    try:
        token = await get_token_by_code(code)
    except Exception:
        return {"message": "invalid oauth code"}

    if not state:
        return {"message": "installation completed!"}

    user_info = await get_state_data(state)
    if not user_info:
        return {"message": "oauth session expired"}

    await delete_state_data(state)
    user: User = await create_auth_user(user_info, access_token=token)
    return {"message": f"{user.user_id} ok!"}
