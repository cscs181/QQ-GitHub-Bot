#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 20:18:19
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-22 15:42:01
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.plugins.github.models import User
from src.plugins.github.libs.auth import (
    get_state_data,
    create_auth_user,
    delete_state_data,
    get_token_by_code,
)

from . import env

app: FastAPI = nonebot.get_app()
template = env.get_template("auth.html.jinja")


@app.get("/github/auth", response_class=HTMLResponse)
async def auth(code: str, state: str | None = None):
    try:
        token = await get_token_by_code(code)
    except Exception:
        return await template.render_async(
            title="Oops...", text="Invalid oauth code!", icon="error"
        )

    if not state:
        return await template.render_async(title="Install Complete!", icon="success")

    user_info = await get_state_data(state)
    if not user_info:
        return await template.render_async(
            title="Oops...", text="OAuth Session Expired!", icon="error"
        )

    await delete_state_data(state)
    user: User = await create_auth_user(user_info, access_token=token)
    return await template.render_async(
        title="Install Complete!",
        text=f"Successfully bind user {user.user_id}",
        icon="success",
    )
