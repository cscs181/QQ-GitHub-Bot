"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:56:01
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 21:00:29
@Description    : Message tag cache
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from src.providers.redis import redis_client

MESSAGE_TAG_CACHE_KEY = "cache:github:message:{platform}:{message_id}:tag"
MESSAGE_TAG_CACHE_EXPIRE = timedelta(days=1)


async def create_message_tag(platform: str, message_id: str, data: str) -> None:
    """Create message tag cache

    Args:
        platform: Platform name
        message_id: Message id
        data: Tag data
    """

    await redis_client.set(
        MESSAGE_TAG_CACHE_KEY.format(platform=platform, message_id=message_id),
        data.encode("UTF-8"),
        ex=MESSAGE_TAG_CACHE_EXPIRE,
    )


async def get_message_tag(platform: str, message_id: str) -> str | None:
    """Get message tag cache

    Args:
        platform: Platform name
        message_id: Message id

    Returns:
        Existing tag data
    """
    data = await redis_client.get(
        MESSAGE_TAG_CACHE_KEY.format(platform=platform, message_id=message_id)
    )
    return data if data is None else data.decode("UTF-8")
