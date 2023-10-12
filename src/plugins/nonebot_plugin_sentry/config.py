"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:18
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-11 11:24:03
@Description    : Config for Sentry plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, Dict, List, Optional

from nonebot import logger, get_driver
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.loguru import LoguruIntegration
from pydantic import Extra, Field, BaseModel, validator, root_validator

driver = get_driver()


class Config(BaseModel):
    sentry_dsn: Optional[str]
    sentry_environment: str = driver.env
    sentry_integrations: List[Integration] = Field(default_factory=list)

    # [FIXED] https://github.com/getsentry/sentry-python/issues/653
    # sentry_default_integrations: bool = False

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def filter_sentry_configs(cls, values: Dict[str, Any]):
        return {
            key: value for key, value in values.items() if key.startswith("sentry_")
        }

    @validator("sentry_dsn", allow_reuse=True)
    def validate_dsn(cls, v: Optional[str]):
        if not v:
            logger.warning("Sentry DSN not provided! Sentry plugin disabled!")
        return v

    @validator("sentry_integrations", allow_reuse=True)
    def validate_integrations(cls, v: List[Integration]):
        ids = {i.identifier for i in v}
        if LoguruIntegration.identifier not in ids:
            v.append(LoguruIntegration())
        return v
