#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 00:26:43
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-25 15:57:19
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from io import BytesIO
from typing_extensions import Literal
from typing import Any, Union, Mapping, Optional, Sequence, BinaryIO

import markdown

from src.libs import html2img


async def from_string(string: str,
                      extensions: Optional[Sequence[Union[
                          str, markdown.extensions.Extension]]] = None,
                      extension_configs: Optional[Mapping[str,
                                                          Mapping[str,
                                                                  Any]]] = None,
                      output_format: Optional[Literal["xhtml", "html"]] = None,
                      tab_length: Optional[int] = None) -> bytes:
    html = markdown.markdown(string,
                             extensions=extensions or [],
                             extension_configs=extension_configs or {},
                             output_format=output_format or "xhtml",
                             tab_length=tab_length or 4)
    return await html2img.from_string(html)


async def from_file(input: Optional[Union[str, BinaryIO]] = None,
                    encoding: Optional[str] = None,
                    extensions: Optional[Sequence[Union[
                        str, markdown.extensions.Extension]]] = None,
                    extension_configs: Optional[Mapping[str,
                                                        Mapping[str,
                                                                Any]]] = None,
                    output_format: Optional[Literal["xhtml", "html"]] = None,
                    tab_length: Optional[int] = None):
    output_ = BytesIO()
    markdown.markdownFromFile(input=input,
                              output=output_,
                              encoding=encoding or "utf-8",
                              extensions=extensions or [],
                              extension_configs=extension_configs or {},
                              output_format=output_format or "xhtml",
                              tab_length=tab_length or 4)

    html = output_.read()
    output_.close()
    html = html.decode(encoding or "utf-8")
    return await html2img.from_string(html)
