"""
@Author         : yanyongyu
@Date           : 2021-03-15 20:18:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 20:42:10
@Description    : External APIs for github plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pathlib import Path

import jinja2

env = jinja2.Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    enable_async=True,
)
