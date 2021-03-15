#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 20:18:19
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-15 22:50:28
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI

from ..libs.auth import _decode_state, get_token_by_code, set_user_token

app: FastAPI = nonebot.get_driver().server_app


@app.get("/api/github/auth")
async def auth(code: str, state: str):
    try:
        username = _decode_state(state)
    except Exception:
        return {"message": "invalid state"}
    if not username:
        return {"message": "oauth session expired"}
    token = await get_token_by_code(code)
    set_user_token(username, token)
    return {"message": "ok"}
