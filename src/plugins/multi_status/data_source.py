"""
@Author         : yanyongyu
@Date           : 2022-10-15 09:01:57
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 16:42:26
@Description    : Getting status of multi pods
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import os
import json
import asyncio
import contextlib
from uuid import UUID, uuid4

from nonebot import logger, get_driver
from nonebot_plugin_status import render_template

from src.providers.redis import redis_client

CHANNEL = "bot:status"
REQUEST = b"bot:status:ping"
DURATION = 1
INTERVAL = 0.1
IDENTIFIER = os.getenv("HOSTNAME", str(uuid4()).split("-")[-1])

driver = get_driver()
pubsub = redis_client.pubsub()
_task: asyncio.Task | None = None
_response_tasks: set[asyncio.Task] = set()
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
                task = asyncio.create_task(_send_status())
                _response_tasks.add(task)
                task.add_done_callback(_response_tasks.discard)
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
    return "\n\n".join(f"Pod {id}:\n{status}" for id, status in statuses.items())


async def _send_status() -> None:
    await redis_client.publish(
        CHANNEL, json.dumps({"id": IDENTIFIER, "status": await render_template()})
    )
