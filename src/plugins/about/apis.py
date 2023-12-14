"""
@Author         : yanyongyu
@Date           : 2023-12-14 16:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-14 16:58:12
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from . import HOMEPAGE

app: FastAPI = nonebot.get_app()


@app.get("/")
async def redirect_to_homepage() -> RedirectResponse:
    return RedirectResponse(HOMEPAGE)
