"""
@Author         : yanyongyu
@Date           : 2020-10-04 16:32:00
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 18:17:09
@Description    : Config for status plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from pydantic import Extra, BaseModel

CPU_TEMPLATE = r"CPU: {{ '%02d' % cpu_usage }}%"
"""Default CPU status template."""

# PER_CPU_TEMPLATE = (
#     "CPU:\n"
#     "{%- for core in per_cpu_usage %}\n"
#     "  core{{ loop.index }}: {{ '%02d' % core }}%\n"
#     "{%- endfor %}"
# )

MEMORY_TEMPLATE = r"Memory: {{ '%02d' % memory_usage.percent }}%"
"""Default memory status template."""

SWAP_TEMPLATE = (
    r"{% if swap_usage.total %}Swap: {{ '%02d' % swap_usage.percent }}%{% endif +%}"
)
"""Default swap status template."""

DISK_TEMPLATE = (
    "Disk:\n"
    "{% for name, usage in disk_usage.items() %}\n"
    "  {{ name }}: {{ '%02d' % usage.percent }}%\n"
    "{% endfor %}"
)
"""Default disk status template."""

UPTIME_TEMPLATE = "Uptime: {{ uptime | relative_time | humanize_delta }}"
"""Default uptime status template."""

RUNTIME_TEMPLATE = "Runtime: {{ runtime | relative_time | humanize_delta }}"
"""Default runtime status template."""


class Config(BaseModel, extra=Extra.ignore):
    server_status_enabled: bool = True
    """Whether to enable the server status commands."""
    server_status_truncate: bool = True
    """Whether to render the status template with used variables only."""
    server_status_only_superusers: bool = True
    """Whether to allow only superusers to use the status commands."""

    server_status_template: str = "\n".join(
        (CPU_TEMPLATE, MEMORY_TEMPLATE, RUNTIME_TEMPLATE, SWAP_TEMPLATE, DISK_TEMPLATE)
    )
    """Default server status template.

    Including:

    - CPU usage
    - Memory usage
    - Runtime
    - Swap usage
    - Disk usage
    """
