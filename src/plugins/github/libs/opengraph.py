"""
@Author         : yanyongyu
@Date           : 2024-05-23 16:57:48
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-23 16:57:48
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import secrets

import nonebot
from nonebot.drivers import Request, HTTPClientMixin

from src.plugins.github.cache.opengraph import get_opengraph, save_opengraph
from src.plugins.github.cache.message_tag import (
    Tag,
    RepoTag,
    IssueTag,
    CommitTag,
    ReleaseTag,
    PullRequestTag,
)

driver = nonebot.get_driver()
assert isinstance(driver, HTTPClientMixin)


async def get_opengraph_image(tag: Tag) -> bytes:
    match tag:
        case IssueTag():
            cache_type = "issue"
            cache_identifier = f"{tag.owner}/{tag.repo}/{tag.number}"
            link = (
                f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                f"{tag.owner}/{tag.repo}/issues/{tag.number}"
            )
        case PullRequestTag():
            cache_type = "pr"
            cache_identifier = f"{tag.owner}/{tag.repo}/{tag.number}"
            link = (
                f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                f"{tag.owner}/{tag.repo}/pull/{tag.number}"
            )
        case CommitTag():
            cache_type = "commit"
            cache_identifier = f"{tag.owner}/{tag.repo}/{tag.commit}"
            link = (
                f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                f"{tag.owner}/{tag.repo}/commit/{tag.commit}"
            )
        case ReleaseTag():
            cache_type = "release"
            cache_identifier = f"{tag.owner}/{tag.repo}/{tag.tag}"
            link = (
                f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                f"{tag.owner}/{tag.repo}/releases/tag/{tag.tag}"
            )
        case RepoTag():
            cache_type = "repo"
            cache_identifier = f"{tag.owner}/{tag.repo}"
            link = (
                f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                f"{tag.owner}/{tag.repo}"
            )

    if image := await get_opengraph(cache_type, cache_identifier):
        return image

    assert isinstance(driver, HTTPClientMixin)

    resp = await driver.request(
        Request(
            "GET",
            link,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
                    " Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
    )
    if (400 <= resp.status_code < 600) or not (content := resp.content):
        raise RuntimeError(f"Failed to download opengraph for {tag!r}: {resp}")
    if isinstance(content, str):
        content = content.encode("utf-8")

    await save_opengraph(cache_type, cache_identifier, content)
    return content
