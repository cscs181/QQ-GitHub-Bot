#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-06 23:07:39
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-25 16:06:57
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import sys
import asyncio
from asyncio import subprocess
from typing import Union, Optional


class Config(object):
    def __init__(
        self,
        wkhtmltoimage: Optional[str] = None,
        meta_tag_prefix: str = "imgkit-",
    ):
        self.meta_tag_prefix = meta_tag_prefix
        self._wkhtmltoimage = wkhtmltoimage
        self._xvfb = None

    def __await__(self):
        proc: asyncio.subprocess.Process
        stdout: bytes

        if not self._wkhtmltoimage:
            if sys.platform == "win32":
                proc = yield from asyncio.create_subprocess_exec(
                    "where", "wkhtmltoimage", stdout=subprocess.PIPE
                ).__await__()
                stdout, _ = yield from proc.communicate().__await__()
                self._wkhtmltoimage = stdout.strip()
            else:
                proc = yield from asyncio.create_subprocess_exec(
                    "which", "wkhtmltoimage", stdout=subprocess.PIPE
                ).__await__()
                stdout, _ = yield from proc.communicate().__await__()
                self._wkhtmltoimage = stdout.strip()

        if not self._xvfb:
            if sys.platform == "win32":
                proc = yield from asyncio.create_subprocess_exec(
                    "where", "xvfb-run", stdout=subprocess.PIPE
                ).__await__()
                stdout, _ = yield from proc.communicate().__await__()
                self._xvfb = stdout.strip()
            else:
                proc = yield from asyncio.create_subprocess_exec(
                    "which", "xvfb-run", stdout=subprocess.PIPE
                ).__await__()
                stdout, _ = yield from proc.communicate().__await__()
                self._xvfb = stdout.strip()

        try:
            with open(self._wkhtmltoimage):
                pass
        except IOError:
            raise IOError(
                f"No wkhtmltoimage executable found: '{self._wkhtmltoimage}'\n"
                "If this file exists please check that this process can "
                "read it. Otherwise please install wkhtmltopdf - "
                "http://wkhtmltopdf.org\n"
            ) from None

        return self

    @property
    def wkhtmltoimage(self) -> Union[str, bytes]:
        if not self._wkhtmltoimage:
            raise RuntimeError(
                f"wkhtmltox not installed or Config {self} is never awaited!"
            )
        return self._wkhtmltoimage

    @wkhtmltoimage.setter
    def wkhtmltoimage(self, value: Union[str, bytes]):
        self._wkhtmltoimage = value

    @property
    def xvfb(self) -> Union[str, bytes]:
        if not self._xvfb:
            raise RuntimeError(
                f"xvfb not installed or Config {self} is never awaited!"
            )
        return self._xvfb

    @xvfb.setter
    def xvfb(self, value: Union[str, bytes]):
        self._xvfb = value
