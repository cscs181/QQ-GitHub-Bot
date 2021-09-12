#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-07 11:18:27
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-08 23:39:54
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing_extensions import Literal
from typing import Dict, List, Tuple, Union

SOURCE_TYPE = Union[str, List[str]]
OUTPUT_TYPE = Union[str, None, Literal[False]]
OPTION_TYPE = Dict[str, Union[str, List[str], Tuple[str]]]
CSS_TYPE = Union[str, List[str]]
