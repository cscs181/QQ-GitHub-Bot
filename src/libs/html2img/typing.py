#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-07 11:18:27
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-07 11:37:29
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import io

from typing import List, Dict, Tuple, Union
from typing_extensions import Literal

_T = Union[str, io.IOBase]
SOURCE_TYPE = Union[_T, List[_T]]
OUTPUT_TYPE = Union[str, None, Literal[False]]
OPTION_TYPE = Dict[str, Union[str, List[str], Tuple[str]]]
CSS_TYPE = Union[str, List[str]]
