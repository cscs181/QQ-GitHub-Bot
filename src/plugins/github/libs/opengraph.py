"""
@Author         : yanyongyu
@Date           : 2024-05-23 16:57:48
@LastEditors    : yanyongyu
@LastEditTime   : 2024-08-18 16:45:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio
import secrets
from venv import logger
from hashlib import sha256

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

FORBIDDEN_FALLBACK_HASH = (
    "74f3b5add54f7102230ed682fbf9d23b5b3a78e6229dbfd49719748e7b806988"
)

driver = nonebot.get_driver()
assert isinstance(driver, HTTPClientMixin)


async def get_opengraph_image(tag: Tag) -> bytes | None:
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

    retry_count = 3

    while retry_count > 0:
        resp = await driver.request(
            Request(
                "GET",
                link,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    )
                },
            )
        )

        if 400 <= resp.status_code < 600 or not (content := resp.content):
            logger.error(f"Failed to download opengraph for {tag!r}: {resp}")
        else:
            if isinstance(content, str):
                content = content.encode("utf-8")
            if sha256(content).hexdigest() == FORBIDDEN_FALLBACK_HASH:
                logger.warning(f"Got fallback opengraph for {tag!r}, retrying")
            else:
                break

        retry_count -= 1
        await asyncio.sleep(0.1)
    else:
        return None

    await save_opengraph(cache_type, cache_identifier, content)
    return content
