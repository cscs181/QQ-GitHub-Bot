"""
@Author         : yanyongyu
@Date           : 2023-10-18 16:20:28
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-18 16:20:28
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Generator
from contextlib import contextmanager
from contextvars import Token, ContextVar

from nonebot.adapters.github import OAuthBot, GitHubBot

from src.plugins.github import config
from src.plugins.github.utils import get_oauth_bot

_context_bot: ContextVar[GitHubBot | OAuthBot] = ContextVar("bot")


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
