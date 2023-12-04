"""
@Author         : yanyongyu
@Date           : 2022-10-10 06:57:31
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-04 16:42:20
@Description    : Health check plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import nonebot
from nonebot import logger
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.responses import JSONResponse
from nonebot_plugin_orm import get_session

from src.providers.redis import redis_client
from src.providers.playwright import get_browser

app: FastAPI = nonebot.get_app()


@app.get("/health")
async def health_check():
    """Health check endpoint."""

    # check postgres connection
    try:
        async with get_session() as session:
            (await session.scalars(text("SELECT 1"))).all()
    except Exception as e:
        logger.opt(exception=e).error("Postgres connection health check failed.")
        return JSONResponse(
            {"status": "error", "component": "postgres"}, status_code=503
        )

    # check redis connection
    try:
        await redis_client.ping()
    except Exception as e:
        logger.opt(exception=e).error("Redis connection health check failed.")
        return JSONResponse({"status": "error", "component": "redis"}, status_code=503)

    # check playwright connection
    try:
        if not get_browser().is_connected():
            raise RuntimeError("Playwright browser is not connected.")
    except Exception as e:
        logger.opt(exception=e).error("Playwright connection health check failed.")
        return JSONResponse(
            {"status": "error", "component": "playwright"}, status_code=503
        )

    return JSONResponse({"status": "ok"}, status_code=200)
