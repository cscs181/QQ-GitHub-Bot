import nonebot
from nonebot.adapters.github import GitHubBot
from githubkit import GitHub, TokenAuthStrategy

from . import config


def get_bot() -> GitHubBot:
    return nonebot.get_bot(config.github_app.app_id)  # type: ignore


def get_github() -> GitHub:
    return get_bot().github


def get_user_github(access_token: str) -> GitHub[TokenAuthStrategy]:
    return GitHub(TokenAuthStrategy(access_token), config=get_github().config)
