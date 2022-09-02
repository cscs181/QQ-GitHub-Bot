#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-10-04 16:32:00
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-02 11:29:12
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import warnings
from typing import Any, Dict

from pydantic import Extra, BaseModel, root_validator

CPU_TEMPLATE = "CPU: {{ '%02d' % cpu_usage }}%"
PER_CPU_TEMPLATE = (
    "CPU:\n"
    "{%- for core in per_cpu_usage %}\n"
    "  core{{ loop.index }}: {{ '%02d' % core }}%\n"
    "{%- endfor %}"
)
MEMORY_TEMPLATE = "Memory: {{ '%02d' % memory_usage }}%"
DISK_TEMPLATE = (
    "Disk:\n"
    "{%- for name, usage in disk_usage.items() %}\n"
    "  {{ name }}: {{ '%02d' % usage.percent }}%\n"
    "{%- endfor %}"
)
UPTIME_TEMPLATE = "Uptime: {{ uptime }}"


class Config(BaseModel, extra=Extra.ignore):
    server_status_only_superusers: bool = True

    # Deprecated: legacy settings
    server_status_cpu: bool = True
    server_status_per_cpu: bool = False
    server_status_memory: bool = True
    server_status_disk: bool = True

    # template
    server_status_template: str = "\n".join(
        (CPU_TEMPLATE, MEMORY_TEMPLATE, DISK_TEMPLATE, UPTIME_TEMPLATE)
    )

    @root_validator(pre=True)
    def transform_legacy_settings(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if "server_status_template" not in value and (
            "server_status_cpu" in value
            or "server_status_per_cpu" in value
            or "server_status_memory" in value
            or "server_status_disk" in value
        ):
            warnings.warn(
                "Settings for status plugin is deprecated, "
                "please use `server_status_template` instead.",
                DeprecationWarning,
            )
            templates = []
            if value.get("server_status_cpu"):
                templates.append(CPU_TEMPLATE)
            if value.get("server_status_per_cpu"):
                templates.append(PER_CPU_TEMPLATE)
            if value.get("server_status_memory"):
                templates.append(MEMORY_TEMPLATE)
            if value.get("server_status_disk"):
                templates.append(DISK_TEMPLATE)
            value.setdefault("server_status_template", "\n".join(templates))

        return value
