"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:06:43
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:49:05
@Description    : OAuth state cache
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from uuid import uuid4
from datetime import timedelta

from pydantic import TypeAdapter

from src.providers.platform import UserInfo
from src.providers.redis import redis_client

STATE_CACHE_KEY = "cache:github:auth:state:{state_id}"
STATE_CACHE_EXPIRE = timedelta(minutes=10)


async def create_state(user: UserInfo) -> str:
    """Create state cache

    Args:
        data: State data

    Returns:
        State id
    """
    state_id = uuid4().hex
    await redis_client.set(
        STATE_CACHE_KEY.format(state_id=state_id),
        user.json(),
        ex=STATE_CACHE_EXPIRE,
    )
    return state_id


async def get_state(state_id: str) -> UserInfo | None:
    """Get state cache

    Args:
        state_id: State id

    Returns:
        Existing state data
    """
    if data := await redis_client.get(STATE_CACHE_KEY.format(state_id=state_id)):
        return TypeAdapter(UserInfo).validate_json(data)


async def delete_state(state_id: str) -> None:
    """Delete state cache

    Args:
        state_id: State id
    """
    await redis_client.delete(STATE_CACHE_KEY.format(state_id=state_id))
