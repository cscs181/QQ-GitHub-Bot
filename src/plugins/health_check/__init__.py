#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-10 06:57:31
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-10 07:44:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from fastapi import FastAPI
from nonebot.log import logger
from fastapi.responses import JSONResponse
from tortoise.connection import connections

from src.plugins.redis import redis_client
from src.plugins.playwright import get_browser
from src.plugins.tortoise import tortoise_config

app: FastAPI = nonebot.get_app()


@app.get("/health")
async def health_check():
    # check postgres connection
    try:
        for conn_name in tortoise_config["connections"]:
            conn = connections.get(conn_name)
            await conn.execute_query("SELECT 1")
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
        assert get_browser().is_connected()
    except Exception as e:
        logger.opt(exception=e).error("Playwright connection health check failed.")
        return JSONResponse(
            {"status": "error", "component": "playwright"}, status_code=503
        )

    return JSONResponse({"status": "ok"}, status_code=200)
