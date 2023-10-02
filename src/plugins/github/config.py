"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 20:36:55
@Description    : Config for github plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, Dict, Literal

from nonebot.adapters.github.config import OAuthApp, GitHubApp
from pydantic import Extra, BaseModel, validator, parse_obj_as, root_validator


class GitHubAPP(GitHubApp):
    """GitHub App config for github plugin"""

    client_id: str
    client_secret: str


class Config(BaseModel, extra=Extra.ignore):
    github_app: GitHubAPP
    oauth_app: OAuthApp | None = None
    github_theme: Literal["light", "dark"] = "light"
    github_webhook_priority: int = 1
    github_command_priority: int = 50

    @root_validator(pre=True)
    def validate_app(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Auto get app from github adapter config"""

        if not (apps := values.get("github_apps")):
            raise ValueError(
                "A GitHub App must be provided to use the bot. "
                "See https://github.com/nonebot/adapter-github for more information."
            )
        apps = parse_obj_as(list[GitHubApp | OAuthApp], apps)
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

    @validator("github_webhook_priority", "github_command_priority")
    def validate_priority(cls, v: int) -> int:
        if v < 1:
            raise ValueError("`priority` must be greater than 0")
        return v
