#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-06 23:52:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-07 11:19:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import os
import io
import codecs
from typing import Any, overload
from typing_extensions import Literal

from .typing import SOURCE_TYPE


class Source(object):

    def __init__(self, url_or_file: SOURCE_TYPE, type_: Literal["url", "file",
                                                                "string"]):
        self.source = url_or_file
        self.type = type_

        if self.type == "file":
            self.check_files()

    def is_url(self):
        return self.type == "url"

    def is_file(self, path: Any = None):
        if path:
            return isinstance(path, io.IOBase) or isinstance(
                path, codecs.StreamReaderWriter)
        else:
            return self.type == "file"

    def check_files(self):
        if isinstance(self.source, list):
            for path in self.source:
                if isinstance(path, str) and not os.path.exists(path):
                    raise IOError(f"No such file: {path}")
                elif not hasattr(self.source, "read"):
                    raise IOError(f"No such file: {path}")
        else:
            if isinstance(self.source, str) and not os.path.exists(self.source):
                raise IOError(f"No such file: {self.source}")
            elif not hasattr(self.source, "read"):
                raise IOError(f"No such file: {self.source}")

    def is_string(self):
        return self.type == "string"

    def is_file_obj(self):
        return hasattr(self.source, "read")

    def get_source(self):
        return self.source
