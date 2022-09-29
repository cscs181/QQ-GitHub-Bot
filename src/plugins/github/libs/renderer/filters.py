#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:07:50
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-29 02:53:46
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime, timezone

import humanize
from nonebot.log import logger
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_emoji import emoji_plugin
from markdown_it.utils import OptionsDict
from githubkit.rest import GitHubRestModel
from markdown_it.renderer import RendererProtocol
from mdit_py_plugins.tasklists import tasklists_plugin

REVIEW_STATES = {
    "commented": "reviewed",
    "changes_requested": "requested changes",
    "approved": "approved these changes",
}

title_md = MarkdownIt("zero").enable("backticks").use(emoji_plugin, shortcuts={})
emoji_md = MarkdownIt("zero").use(emoji_plugin, shortcuts={})
gfm_md = MarkdownIt("gfm-like").use(tasklists_plugin).use(emoji_plugin, shortcuts={})


def emoji_format(
    renderer: RendererProtocol,
    tokens: list[Token],
    idx: int,
    options: OptionsDict,
    env: dict,
) -> str:
    return f'<g-emoji class="g-emoji" alias="{tokens[idx].markup}">{tokens[idx].content}</g-emoji>'


title_md.add_render_rule("emoji", emoji_format)
emoji_md.add_render_rule("emoji", emoji_format)


def markdown_title(text: str) -> str:
    return title_md.renderInline(text)


def markdown_emoji(text: str) -> str:
    return emoji_md.renderInline(text)


def markdown_gfm(text: str) -> str:
    return gfm_md.render(text)


def relative_time(value: datetime | str) -> str:
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    if not value.tzinfo:
        value = value.replace(tzinfo=timezone.utc)
    now = datetime.now(value.tzinfo)
    delta = now - value
    if delta.microseconds > 0 and delta.days < 30:
        return humanize.naturaltime(delta)

    t = "%d %b" if value.year == now.year else "%d %b %Y"
    return f"on {humanize.naturalday(value, t)}"


def debug_event(event: GitHubRestModel) -> str:
    logger.debug(f"Unhandled event: {event.dict()}")
    logger.error(
        f"Unhandled event type: {event.__class__.__name__}",
        event=event.dict(),
    )
    return ""


def review_state(value: str) -> str:
    return REVIEW_STATES.get(value, value)
