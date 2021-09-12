#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-07 00:01:16
@LastEditors    : yanyongyu
@LastEditTime   : 2021-09-12 12:54:16
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re
import sys
import asyncio
from asyncio import subprocess
from typing_extensions import Literal
from typing import Tuple, Union, Optional, Generator

from .config import Config
from .source import Source, URLSource, FileSource, StringSource
from .typing import CSS_TYPE, OPTION_TYPE, OUTPUT_TYPE, SOURCE_TYPE


class IMGKit(object):
    class SourceError(Exception):
        """Wrong source type for stylesheets"""

        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message

    def __init__(
        self,
        source: SOURCE_TYPE,
        source_type: Literal["url", "file", "string"],
        options: Optional[OPTION_TYPE] = None,
        toc: Optional[OPTION_TYPE] = None,
        cover: str = None,
        cover_first: bool = False,
        css: CSS_TYPE = None,
        config: Optional[Config] = None,
    ):
        self._source = (
            URLSource(source)
            if source_type == "url"
            else FileSource(source)
            if source_type == "file"
            else StringSource(source)  # type: ignore
        )
        self._config: Optional[Config] = config

        self.options: OPTION_TYPE = options or {}

        self.toc = toc or {}
        self.cover = cover
        self.cover_first = cover_first
        self.css = css

    def __await__(self):
        if not self._config:
            self._config = yield from Config().__await__()

        if isinstance(self._source, StringSource):
            self.options = {
                **self._find_options_in_meta(self._source.get_source()),
                **self.options,
            }
        return self

    @property
    def source(self) -> Source:
        return self._source

    @source.setter
    def source(self, source: Source):
        self._source = source

    @property
    def config(self):
        if not self._config:
            raise RuntimeError(f"ImgKit {self} is never awaited!")
        return self._config

    @config.setter
    def config(self, value: Config):
        self._config = value

    @property
    def wkhtmltoimage(self):
        return self.config.wkhtmltoimage

    @property
    def xvfb(self):
        return self.config.xvfb

    def _gegetate_args(
        self, options: OPTION_TYPE
    ) -> Generator[str, None, None]:
        """
        Generator of args parts based on options specification.
        """
        for optkey, optval in self._normalize_options(options):
            yield optkey
            yield optval

    def _normalize_options(
        self, options: OPTION_TYPE
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Generator of 2-tuples (option-key, option-value).
        When options spec is a list, generate a 2-tuples per list item.

        :param options: dict {option: value}

        returns:
          iterator (option-key, option-value)
          - option names lower cased and prepended with
          "--" if necessary. Non-empty values cast to str
        """
        for key, value in list(options.items()):
            if "--" in key:
                normalized_key = self._normalize_arg(key)
            else:
                normalized_key = f"--{self._normalize_arg(key)}"

            if isinstance(value, (list, tuple)):
                for opt_val in value:
                    yield (normalized_key, opt_val)
            else:
                yield (normalized_key, str(value) if value else value)

    def _normalize_arg(self, arg: str) -> str:
        return arg.lower()

    def _prepend_css(self, css_file: CSS_TYPE):
        source = self.source.get_source()
        if isinstance(self.source, URLSource) or isinstance(source, list):
            raise self.SourceError(
                "CSS files can be added only to a single file or string"
            )

        if not isinstance(css_file, list):
            css_file = [css_file]

        css_data = []
        for p in css_file:
            with open(p, encoding="utf-8") as f:
                css_data.append(f.read())
        css_data = "\n".join(css_data)

        if isinstance(self.source, FileSource):
            with open(source, encoding="utf-8") as f:
                inp = f.read()

            if "</head>" in source:
                self.source = StringSource(
                    inp.replace(
                        "</head>", self._style_tag(css_data) + "</head>"
                    )
                )
            else:
                self.source = StringSource(self._style_tag(css_data) + inp)
        elif isinstance(self.source, StringSource):
            if "</head>" in source:
                self.source.source = source.replace(
                    "</head>", self._style_tag(css_data) + "</head>"
                )
            else:
                self.source.source = self._style_tag(css_data) + source

    def _style_tag(self, stylesheet: str) -> str:
        return f"<style>{stylesheet}</style>"

    def _command(
        self, output_path: OUTPUT_TYPE = None
    ) -> Generator[Union[str, bytes], None, None]:
        """
        Generator of all command parts
        :type options: object
        :return:
        """
        options = list(self._gegetate_args(self.options))

        if self.css:
            self._prepend_css(self.css)

        if "--xvfb" in options:
            options.remove("--xvfb")
            yield self.xvfb
            # auto servernum option to prevent failure on concurrent runs
            # https://bugs.launchpad.net/ubuntu/+source/xorg-server/+bug/348052
            yield "-a"

        yield self.wkhtmltoimage

        yield from filter(lambda x: x, options)

        if self.cover and self.cover_first:
            yield "cover"
            yield self.cover

        if self.toc:
            yield "toc"
            yield from filter(lambda x: x, self._gegetate_args(self.toc))

        if self.cover and not self.cover_first:
            yield "cover"
            yield self.cover

        # If the source is a string then we will pipe it into wkhtmltoimage
        # If the source is file-like then we will read from it and pipe it in
        if isinstance(self.source, StringSource):
            yield "-"
        else:
            source = self.source.get_source()
            if isinstance(source, str):
                yield source
            else:
                for s in source:
                    yield s

        # If output_path evaluates to False append "-" to end of args
        # and wkhtmltoimage will pass generated IMG to stdout
        if output_path:
            yield output_path
        else:
            yield "-"

    def command(self, output_path: OUTPUT_TYPE = None):
        return list(self._command(output_path))

    def _find_options_in_meta(self, content: str) -> OPTION_TYPE:
        """Reads "content" and extracts options encoded in HTML meta tags

        :param content: str - contains HTML to parse

        :returns:
            dict: {config option: value}
        """

        found: OPTION_TYPE = {}

        for x in re.findall(r"<meta [^>]*>", content):
            if re.search(rf"name=[\"']{self.config.meta_tag_prefix}", x):
                name = re.findall(
                    rf"name=[\"']{self.config.meta_tag_prefix}([^\"']*)", x
                )[0]
                found[name] = re.findall(r"content=[\"']([^\"']*)", x)[0]

        return found

    async def to_img(self, output_path: OUTPUT_TYPE = None) -> Optional[bytes]:
        args = self.command(output_path)

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # If the source is a string then we will pipe it into wkhtmltoimage.
        # If we want to add custom CSS to file then we read input file to
        # string and prepend css to it and then pass it to stdin.
        # This is a workaround for a bug in wkhtmltoimage (look closely in README)
        source = self.source.get_source()
        if isinstance(self.source, StringSource):
            string = source.encode("utf-8")  # type: ignore
        else:
            string = None
        stdout, stderr = await proc.communicate(input=string)
        stderr = stderr or stdout
        try:
            stderr = stderr.decode("utf-8")
        except UnicodeDecodeError:
            stderr = ""
        exit_code = proc.returncode

        if "cannot connect to X server" in stderr:
            raise IOError(
                f"{stderr}\n"
                "You will need to run wkhtmltoimage within a 'virtual' X server.\n"
                "Go to the link below for more information\n"
                "http://wkhtmltopdf.org"
            )

        if "Error" in stderr:
            raise IOError("wkhtmltoimage reported an error:\n" + stderr)

        if exit_code != 0:
            xvfb_error = ""
            if "QXcbConnection" in stderr:
                xvfb_error = "You need to install xvfb(sudo apt-get install xvfb, yum install xorg-x11-server-Xvfb, etc), then add option: {'xvfb': ''}."
            raise IOError(
                f"wkhtmltoimage exited with non-zero code {exit_code}. error:\n{stderr}\n\n{xvfb_error}"
            )

        # Since wkhtmltoimage sends its output to stderr we will capture it
        # and properly send to stdout
        if "--quiet" not in args:
            sys.stdout.write(stderr)

        if not output_path:
            return stdout
        else:
            try:
                with open(output_path, mode="rb") as f:
                    text = f.read(4)
                    if text == "":
                        raise IOError(
                            f"Command failed: {args}\n"
                            'Check whhtmltoimage output without "--quiet" option'
                        )
                    return None
            except IOError as e:
                raise IOError(
                    f"Command failed: {args}\n"
                    'Check whhtmltoimage output without "--quiet" option'
                )
