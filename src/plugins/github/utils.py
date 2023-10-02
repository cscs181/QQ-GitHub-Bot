"""
@Author         : yanyongyu
@Date           : 2022-09-07 12:14:14
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 20:41:19
@Description    : Utils for github plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Generator
from contextlib import contextmanager
from contextvars import Token, ContextVar

import nonebot
from githubkit import GitHub
from nonebot.adapters.onebot.v11 import Bot as QQBot
from nonebot.adapters.github import OAuthBot, GitHubBot

from . import config

_context_bot: ContextVar[GitHubBot | OAuthBot] = ContextVar("bot")


def get_github_bot() -> GitHubBot:
    """Get the GitHub bot instance"""
    return nonebot.get_bot(config.github_app.app_id)  # type: ignore


def get_oauth_bot() -> OAuthBot:
    """Get the OAuth bot instance"""
    if not config.oauth_app:
        raise ValueError("No OAuth app configured")
    return nonebot.get_bot(config.oauth_app.client_id)  # type: ignore


def get_context_bot() -> GitHubBot | OAuthBot:
    """Get the context bot instance.

    Defaults to OAuth bot for compatibility.
    """
    if config.oauth_app:
        return _context_bot.get(get_oauth_bot())
    return _context_bot.get()


@contextmanager
def set_context_bot(bot: GitHubBot | OAuthBot) -> Generator[Token, None, None]:
    """Set the context bot instance"""
    t = _context_bot.set(bot)
    try:
        yield t
    finally:
        _context_bot.reset(t)


def get_github() -> GitHub:
    """Get the github app client"""
    return get_github_bot().github


def get_oauth_github() -> GitHub:
    """Get the oauth app client"""
    return get_oauth_bot().github


def get_qq_bot() -> QQBot:
    """Get the QQ bot instance"""
    return next(bot for bot in nonebot.get_bots().values() if isinstance(bot, QQBot))


def get_qqguild_bot():
    ...
