"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 13:40:21
@Description    : Status plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import inspect
import contextlib
from typing import Any

from jinja2 import Environment
from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from jinja2.meta import find_undeclared_variables

from .config import Config
from .helpers import humanize_date, relative_time, humanize_delta
from .data_source import (
    get_uptime,
    get_cpu_status,
    get_disk_usage,
    per_cpu_status,
    get_swap_status,
    get_memory_status,
    get_bot_connect_time,
    get_nonebot_run_time,
)

__plugin_meta__ = PluginMetadata(
    name="服务器状态查看",
    description="通过戳一戳获取服务器状态",
    usage=(
        "通过QQ私聊戳一戳或拍一拍头像获取机器人服务器状态\n"
        "或者通过发送指令 `status/状态` 获取机器人服务器状态\n"
        "可以通过配置文件修改服务器状态模板"
    ),
    type="application",
    homepage="https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status",
    config=Config,
    supported_adapters=None,
)

global_config = get_driver().config
status_config = Config.parse_obj(global_config)
status_permission = (status_config.server_status_only_superusers or None) and SUPERUSER

_ev = Environment(
    trim_blocks=True, lstrip_blocks=True, autoescape=False, enable_async=True
)
_ev.globals["relative_time"] = relative_time
_ev.filters["relative_time"] = relative_time
_ev.filters["humanize_date"] = humanize_date
_ev.globals["humanize_date"] = humanize_date
_ev.filters["humanize_delta"] = humanize_delta
_ev.globals["humanize_delta"] = humanize_delta

_t_ast = _ev.parse(status_config.server_status_template)
_t_vars = find_undeclared_variables(_t_ast)
_t = _ev.from_string(_t_ast)

KNOWN_VARS = {
    "cpu_usage": get_cpu_status,
    "per_cpu_usage": per_cpu_status,
    "memory_usage": get_memory_status,
    "swap_usage": get_swap_status,
    "disk_usage": get_disk_usage,
    "uptime": get_uptime,
    "runtime": get_nonebot_run_time,
    "bot_connect_time": get_bot_connect_time,
}
"""Available variables for template rendering."""


if not set(_t_vars).issubset(KNOWN_VARS):
    raise ValueError(
        "Unknown variables in status template:"
        f" {', '.join(set(_t_vars) - set(KNOWN_VARS))}"
    )


async def _solve_required_vars() -> dict[str, Any]:
    """Solve required variables for template rendering."""
    return (
        {
            k: await v() if inspect.iscoroutinefunction(v) else v()
            for k, v in KNOWN_VARS.items()
            if k in _t_vars
        }
        if status_config.server_status_truncate
        else {
            k: await v() if inspect.iscoroutinefunction(v) else v()
            for k, v in KNOWN_VARS.items()
        }
    )


async def render_template() -> str:
    """Render status template with required variables."""
    message = await _t.render_async(**(await _solve_required_vars()))
    return message.strip("\n")


async def server_status(matcher: Matcher):
    """Server status matcher handler."""
    await matcher.send(message=await render_template())


from . import common as common

with contextlib.suppress(ImportError):
    import nonebot.adapters.onebot.v11  # noqa: F401

    from . import onebot_v11 as onebot_v11
