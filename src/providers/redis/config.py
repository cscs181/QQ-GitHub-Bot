"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:45:54
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:52:12
@Description    : Config for Redis provider
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pydantic import BaseModel, field_validator


class Config(BaseModel):
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: str | None = None
    redis_username: str | None = None

    @field_validator("redis_db", mode="before")
    def replace_empty(cls, value):
        return value or 0
