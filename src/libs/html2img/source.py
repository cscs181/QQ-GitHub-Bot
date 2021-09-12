#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-06 23:52:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-08 23:52:35
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import os
import abc
from typing_extensions import Literal

from .typing import SOURCE_TYPE


class Source(abc.ABC):
    def __init__(self, source: SOURCE_TYPE):
        self.source = source

    @property
    @abc.abstractmethod
    def type(self) -> str:
        raise NotImplementedError

    def get_source(self) -> SOURCE_TYPE:
        return self.source


class StringSource(Source):
    def __init__(self, source: str):
        self.source = source

    @property
    def type(self) -> Literal["string"]:
        return "string"

    def get_source(self) -> str:
        return self.source


class FileSource(Source):
    def __init__(self, source: SOURCE_TYPE):
        super(FileSource, self).__init__(source)
        self.check_files()

    @property
    def type(self) -> Literal["file"]:
        return "file"

    def check_files(self):
        if isinstance(self.source, list):
            for path in self.source:
                if not isinstance(path, str):
                    raise IOError(f"Unknown file type: {path}")
                if not os.path.exists(path):
                    raise IOError(f"No such file: {path}")
        else:
            if not isinstance(self.source, str):
                raise IOError(f"Unknown file type: {self.source}")
            if not os.path.exists(self.source):
                raise IOError(f"No such file: {self.source}")


class URLSource(Source):
    @property
    def type(self) -> Literal["url"]:
        return "url"
