#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-06 23:06:56
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-09 00:56:26
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional, overload
from typing_extensions import Literal

from .config import Config
from .imgkit import IMGKit
from .typing import CSS_TYPE, OPTION_TYPE, OUTPUT_TYPE, SOURCE_TYPE


@overload
async def from_url(
    url: SOURCE_TYPE,
    output_path: str,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    config: Config = ...,
) -> None:
    ...


@overload
async def from_url(
    url: SOURCE_TYPE,
    output_path: Optional[Literal[False]] = ...,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    config: Config = ...,
) -> bytes:
    ...


async def from_url(
    url: SOURCE_TYPE,
    output_path: OUTPUT_TYPE = None,
    options: Optional[OPTION_TYPE] = None,
    toc: Optional[OPTION_TYPE] = None,
    cover: str = None,
    cover_first: bool = False,
    config: Config = None,
):
    """
    Convert URL/URLs to IMG file/files

    :param url: URL or list of URLs to be saved
    :param output_path: (optional) path to output PDF file/files. False means file will be returned as string
    :param options: (optional) dict with wkhtmltopdf global and page options, with or w/o "--"
    :param toc: (optional) dict with toc-specific wkhtmltopdf options, with or w/o "--"
    :param cover: (optional) string with url/filename with a cover html page
    :param css: style of input
    :param cover_first: (optional) if True, cover always precedes TOC
    :param config: (optional) instance of imgkit.config.Config()
    :return: True when success
    """
    rtn = await IMGKit(
        url,
        "url",
        options=options,
        toc=toc,
        cover=cover,
        config=config,
        cover_first=cover_first,
    )
    return await rtn.to_img(output_path)


@overload
async def from_file(
    filename: SOURCE_TYPE,
    output_path: str,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    css: Optional[CSS_TYPE] = ...,
    config: Config = ...,
) -> None:
    ...


@overload
async def from_file(
    filename: SOURCE_TYPE,
    output_path: Optional[Literal[False]] = ...,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    css: Optional[CSS_TYPE] = ...,
    config: Config = ...,
) -> bytes:
    ...


async def from_file(
    filename: SOURCE_TYPE,
    output_path: OUTPUT_TYPE = None,
    options: Optional[OPTION_TYPE] = None,
    toc: Optional[OPTION_TYPE] = None,
    cover: str = None,
    cover_first: bool = False,
    css: Optional[CSS_TYPE] = None,
    config: Config = None,
):
    """
    Convert HTML file/files to IMG file/files

    :param filename: path of HTML file or list with paths
    :param output_path: (optional) path to output PDF file/files. False means file will be returned as string
    :param options: (optional) dict with wkhtmltopdf global and page options, with or w/o "--"
    :param toc: (optional) dict with toc-specific wkhtmltopdf options, with or w/o "--"
    :param cover: (optional) string with url/filename with a cover html page
    :param cover_first: (optional) if True, cover always precedes TOC
    :param css: (optional) style of input
    :param config: (optional) instance of imgkit.config.Config()
    :return: True when success
    """
    rtn = await IMGKit(
        filename,
        "file",
        options=options,
        toc=toc,
        cover=cover,
        css=css,
        config=config,
        cover_first=cover_first,
    )
    return await rtn.to_img(output_path)


@overload
async def from_string(
    string: str,
    output_path: str,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    css: Optional[CSS_TYPE] = ...,
    config: Config = ...,
) -> None:
    ...


@overload
async def from_string(
    string: str,
    output_path: Optional[Literal[False]] = ...,
    options: Optional[OPTION_TYPE] = ...,
    toc: Optional[OPTION_TYPE] = ...,
    cover: str = ...,
    cover_first: bool = ...,
    css: Optional[CSS_TYPE] = ...,
    config: Config = ...,
) -> bytes:
    ...


async def from_string(
    string: str,
    output_path: OUTPUT_TYPE = None,
    options: Optional[OPTION_TYPE] = None,
    toc: Optional[OPTION_TYPE] = None,
    cover: str = None,
    cover_first: bool = False,
    css: Optional[CSS_TYPE] = None,
    config: Config = None,
):
    """
    Convert given string/strings to IMG file

    :param string: simple string
    :param output_path: (optional) path to output PDF file/files. False means file will be returned as string
    :param options: (optional) dict with wkhtmltopdf global and page options, with or w/o "--"
    :param toc: (optional) dict with toc-specific wkhtmltopdf options, with or w/o "--"
    :param cover: (optional) string with url/filename with a cover html page
    :param cover_first: (optional) if True, cover always precedes TOC
    :param css: (optional) style of input
    :param config: (optional) instance of imgkit.config.Config()
    :return: True when success
    """
    rtn = await IMGKit(
        string,
        "string",
        options=options,
        toc=toc,
        cover=cover,
        css=css,
        config=config,
        cover_first=cover_first,
    )
    return await rtn.to_img(output_path)


async def config(
    wkhtmltoimage: Optional[str] = None, meta_tag_prefix: str = "imgkit-"
) -> Config:
    """
    Constructs and returns a :class:`Config` with given options

    :param wkhtmltoimage: path to binary
    :param meta_tag_prefix: the prefix for ``pdfkit`` specific meta tags
    """

    return await Config(
        wkhtmltoimage=wkhtmltoimage, meta_tag_prefix=meta_tag_prefix
    )
