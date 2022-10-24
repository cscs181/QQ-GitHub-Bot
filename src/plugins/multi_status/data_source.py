#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-15 09:01:57
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-24 06:40:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import asyncio
import contextlib
from uuid import UUID, uuid4

from nonebot import get_driver
from nonebot.log import logger

from src.plugins.redis import redis_client
from src.plugins.nonebot_plugin_status import render_template

CHANNEL = "bot:status"
REQUEST = b"bot:status:ping"
DURATION = 1
INTERVAL = 0.5
IDENTIFIER = uuid4()

driver = get_driver()
pubsub = redis_client.pubsub()
_task: asyncio.Task | None = None
_responses: dict[UUID, dict[str, str]] = {}


@driver.on_startup
async def _():
    global _task
    await pubsub.subscribe(CHANNEL)
    _task = asyncio.create_task(_listen_message())


@driver.on_shutdown
async def _():
    if _task:
        _task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await _task
    await pubsub.unsubscribe(CHANNEL)


async def _listen_message():
    while True:
        try:
            msg = await pubsub.get_message(ignore_subscribe_messages=True)
            if msg and msg["data"] == REQUEST:
                asyncio.create_task(_send_status())
            elif msg and msg["data"]:
                data = json.loads(msg["data"])
                for resp in _responses.values():
                    resp[data["id"]] = data["status"]
        except Exception as e:
            logger.opt(exception=e).warning(f"Error getting pubsub status message: {e}")

        await asyncio.sleep(INTERVAL)


async def get_all_status() -> str:
    request_id = uuid4()
    _responses[request_id] = {}
    await redis_client.publish(CHANNEL, REQUEST)
    await asyncio.sleep(DURATION)
    statuses = _responses.pop(request_id)
    return "\n\n".join(
        f"Pod {id.split('-')[-1]}:\n{status}" for id, status in statuses.items()
    )


async def _send_status() -> None:
    await redis_client.publish(
        CHANNEL, json.dumps({"id": str(IDENTIFIER), "status": await render_template()})
    )
