#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-10-04 16:32:00
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-25 07:34:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from pydantic import Extra, BaseModel

CPU_TEMPLATE = "CPU: {{ '%02d' % cpu_usage }}%"
# PER_CPU_TEMPLATE = (
#     "CPU:\n"
#     "{%- for core in per_cpu_usage %}\n"
#     "  core{{ loop.index }}: {{ '%02d' % core }}%\n"
#     "{%- endfor %}"
# )
MEMORY_TEMPLATE = "Memory: {{ '%02d' % memory_usage.percent }}%"
SWAP_TEMPLATE = (
    "{% if swap_usage.total %}Swap: {{ '%02d' % swap_usage.percent }}%{% endif %}"
)
DISK_TEMPLATE = (
    "Disk:\n"
    "{% for name, usage in disk_usage.items() %}\n"
    "  {{ name }}: {{ '%02d' % usage.percent }}%\n"
    "{% endfor %}"
)
UPTIME_TEMPLATE = "Uptime: {{ uptime | relative_time | humanize_delta }}"
RUNTIME_TEMPLATE = "Runtime: {{ runtime | relative_time | humanize_delta }}"


class Config(BaseModel, extra=Extra.ignore):
    server_status_enabled: bool = True
    server_status_truncate: bool = True
    server_status_only_superusers: bool = True

    # template
    server_status_template: str = "\n".join(
        (CPU_TEMPLATE, MEMORY_TEMPLATE, RUNTIME_TEMPLATE, SWAP_TEMPLATE, DISK_TEMPLATE)
    )
