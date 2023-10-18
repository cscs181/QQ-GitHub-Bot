"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:25
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-18 10:32:17
@Description    : Sentry plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import sentry_sdk
from nonebot import logger, get_driver
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="Sentry日志监控",
    description="使用Sentry监控机器人日志并处理报错",
    usage="在配置文件中填写Sentry DSN即可启用",
    type="application",
    homepage="https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_sentry",
    config=Config,
    supported_adapters=None,
)

driver = get_driver()
global_config = driver.config
config = Config(**global_config.dict())


def init_sentry(config: Config):
    sentry_config = {key[7:]: value for key, value in config.dict().items()}
    sentry_sdk.init(**sentry_config)


if config.sentry_dsn:
    init_sentry(config)
else:
    logger.warning("Sentry DSN not provided! Sentry plugin disabled!")
