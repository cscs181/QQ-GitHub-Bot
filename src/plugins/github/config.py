"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:46:53
@Description    : Config for github plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Any, Literal

from nonebot.adapters.github.config import OAuthApp, GitHubApp
from pydantic import Field, BaseModel, TypeAdapter, model_validator


class GitHubAPP(GitHubApp):
    """GitHub App config for github plugin"""

    client_id: str
    client_secret: str


class Config(BaseModel):
    github_app: GitHubAPP
    oauth_app: OAuthApp | None = None
    github_theme: Literal["light", "dark"] = "light"
    github_webhook_priority: int = Field(1, gt=0)
    github_command_priority: int = Field(50, gt=0)

    @model_validator(mode="before")
    @classmethod
    def validate_app(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Auto get app from github adapter config"""

        if not (apps := values.get("github_apps")):
            raise ValueError(
                "A GitHub App must be provided to use the bot. "
                "See https://github.com/nonebot/adapter-github for more information."
            )
        apps = TypeAdapter(list[GitHubApp | OAuthApp]).validate_python(apps)
        if not (
            github_app := next(
                (app for app in apps if isinstance(app, GitHubApp)), None
            )
        ):
            raise ValueError(
                "A GitHub App must be provided to use the bot. "
                "See https://github.com/nonebot/adapter-github for more information."
            )
        values.setdefault("github_app", github_app)
        if oauth_app := next((app for app in apps if isinstance(app, OAuthApp)), None):
            values.setdefault("oauth_app", oauth_app)
        return values
