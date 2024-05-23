"""
@Author         : yanyongyu
@Date           : 2024-05-23 16:57:27
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-23 16:57:27
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from datetime import timedelta

from src.providers.redis import redis_client

OPENGRAPH_CACHE_KEY = "cache:github:opengraph:{type}:{identifier}"
OPENGRAPH_CACHE_EXPIRE = timedelta(days=1)


async def save_opengraph(type: str, identifier: str, img: bytes) -> None:
    """Save opengraph image to Redis."""
    await redis_client.set(
        OPENGRAPH_CACHE_KEY.format(type=type, identifier=identifier),
        img,
        ex=OPENGRAPH_CACHE_EXPIRE,
    )


async def get_opengraph(type: str, identifier: str) -> bytes | None:
    """Get opengraph image from Redis."""
    return await redis_client.get(
        OPENGRAPH_CACHE_KEY.format(type=type, identifier=identifier)
    )
