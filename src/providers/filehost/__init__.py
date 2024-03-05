"""
@Author         : yanyongyu
@Date           : 2023-12-05 17:10:52
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:53:23
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from hashlib import sha256
from datetime import timedelta
from urllib.parse import urljoin

import nonebot
from fastapi import FastAPI
from fastapi.responses import Response
from nonebot import logger, get_plugin_config
from nonebot.drivers import Request, HTTPClientMixin

from src.providers.redis import redis_client

from .config import Config

TTL = timedelta(days=1)
CACHE_KEY = "cache:image:{signature}"


app: FastAPI = nonebot.get_app()
driver = nonebot.get_driver()
assert isinstance(driver, HTTPClientMixin)

config = get_plugin_config(Config)


async def save_image(img: bytes, ex: timedelta = TTL) -> str:
    """Save image to Redis and return url."""
    img_hash = sha256(img).hexdigest()
    logger.debug(f"Saving image {img_hash}")
    await redis_client.set(CACHE_KEY.format(signature=img_hash), img, ex=ex)
    return urljoin(config.filehost_url_base, f"{config.filehost_url_prefix}/{img_hash}")


async def save_online_image(url: str, ex: timedelta = TTL) -> str:
    """Save online image to Redis and return url."""
    resp = await driver.request(
        Request(
            "GET",
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
                    " Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
    )
    if (400 <= resp.status_code < 600) or not resp.content:
        raise RuntimeError(f"Failed to download image {url}: {resp}")
    if isinstance((content := resp.content), str):
        content = content.encode("utf-8")
    return await save_image(content, ex=ex)


async def get_image(img_hash: str) -> bytes | None:
    """Get image from Redis."""
    return await redis_client.get(CACHE_KEY.format(signature=img_hash))


async def check_image(img_hash: str) -> bool:
    """Check if image exists in Redis."""
    return await redis_client.exists(CACHE_KEY.format(signature=img_hash))


@app.get(f"{config.filehost_url_prefix}/{{img_hash}}")
async def get_image_handler(img_hash: str) -> Response:
    """Get image from Redis."""
    img = await get_image(img_hash)
    if not img:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")


@app.head(f"{config.filehost_url_prefix}/{{img_hash}}")
async def check_image_handler(img_hash: str) -> Response:
    """Check if image exists in Redis."""
    if not await check_image(img_hash):
        return Response(status_code=404)
    return Response(status_code=204, media_type="image/png")
