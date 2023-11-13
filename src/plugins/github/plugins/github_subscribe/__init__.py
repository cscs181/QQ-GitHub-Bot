"""
@Author         : yanyongyu
@Date           : 2022-10-22 14:35:43
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-13 17:35:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.exception import MatcherException
from nonebot.params import Depends, CommandArg, ArgPlainText
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.providers.platform import TARGET_INFO
from src.plugins.github.utils import get_github_bot
from src.plugins.github.models import SubData, Subscription
from src.plugins.github.dependencies import (
    SUBSCRIPTIONS,
    AUTHORIZED_USER,
    GITHUB_REPO_INSTALLATION,
)
from src.plugins.github.helpers import (
    PRIVATE_PERM,
    FULLREPO_REGEX,
    GROUP_SUPERPERM,
    NO_GITHUB_EVENT,
    MATCH_WHEN_PRIVATE_OR_GROUP,
    allow_cancellation,
)

from .dependencies import bypass_create, stop_unavailable_target

__plugin_meta__ = PluginMetadata(
    "GitHub 事件订阅",
    "订阅 GitHub 仓库事件",
    "/subscribe: 查看当前已有订阅\n"
    "/subscribe owner/repo [event/action ...]: 订阅指定仓库的某类事件\n"
    "/unsubscribe owner/repo [event/action ...]: 取消订阅指定仓库的某类事件",
)

SUBSCRIBE_DEFAULT_MESSAGE = "默认"
DEFAULT_SUBSCRIPTION = {
    "issues": ["opened", "edited", "closed", "reopened"],
    "issue_comment": ["created", "edited"],
    "pull_request": ["opened", "closed", "reopened"],
    "release": ["published"],
}
UNSUBSCRIBE_ALL_MESSAGE = "全部"


def subscriptions_to_message(subscriptions: list[Subscription]) -> str:
    repos: dict[str, list[str]] = {}
    for sub in subscriptions:
        events = repos.setdefault(f"{sub.owner}/{sub.repo}", [])
        events.append(
            f"{sub.event}/[{', '.join(sub.action)}]" if sub.action else sub.event
        )
    return (
        "\n".join(f"{repo}: {', '.join(events)}" for repo, events in repos.items())
        or "无订阅"
    )


subscribe = on_command(
    "subscribe",
    MATCH_WHEN_PRIVATE_OR_GROUP & NO_GITHUB_EVENT,
    permission=PRIVATE_PERM | GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@subscribe.handle(parameterless=(Depends(stop_unavailable_target),))
async def process_subscribe_arg(
    matcher: Matcher, user: AUTHORIZED_USER, arg: Message = CommandArg()
):
    if args := arg.extract_plain_text().strip().split(" "):
        repo, *events = args
        if repo:
            matcher.set_arg("full_name", arg.__class__(repo))
        if e := " ".join(events):
            matcher.set_arg("events", arg.__class__(e))


@subscribe.handle(parameterless=(Depends(bypass_create),))
async def list_user_subscription(subsciptions: SUBSCRIPTIONS):
    if subsciptions:
        await subscribe.finish(
            "当前已订阅：\n" + subscriptions_to_message(subsciptions)
        )


@subscribe.got("full_name", prompt="订阅仓库的全名？(e.g. owner/repo)")
async def parse_subscribe_repo(state: T_State, full_name: str = ArgPlainText()):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await subscribe.finish(f"仓库名 {full_name} 不合法！")

    state["owner"] = matched["owner"]
    state["repo"] = matched["repo"]


@subscribe.handle()
async def handle_subscribe_repo(
    state: T_State,
    user: AUTHORIZED_USER,
    repo_installation: GITHUB_REPO_INSTALLATION,
):
    bot = get_github_bot()

    owner = state["owner"]
    repo = state["repo"]
    full_name = f"{owner}/{repo}"

    try:
        async with bot.as_user(user.access_token):
            async for accessible_repo in bot.github.paginate(
                bot.rest.apps.async_list_installation_repos_for_authenticated_user,
                map_func=lambda r: r.parsed_data.repositories,
                installation_id=repo_installation.id,
            ):
                if accessible_repo.full_name == full_name:
                    break
            else:
                await subscribe.finish(f"你没有权限访问仓库 {full_name} ！")
    except MatcherException:
        raise
    except ActionTimeout:
        await subscribe.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code in {403, 404}:
            await subscribe.finish(f"你没有权限访问仓库 {full_name} ！请重新发送或取消")
        logger.opt(exception=e).error(
            f"Failed while checking user permission in group subscribe: {e}"
        )
        await subscribe.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while checking user permission in group subscribe: {e}"
        )
        await subscribe.finish("未知错误发生，请尝试重试或联系管理员")


@subscribe.got(
    "events",
    prompt=f"订阅哪些事件或{SUBSCRIBE_DEFAULT_MESSAGE}？(e.g. issues[/opened])",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_subscribe_event(state: T_State, events: str = ArgPlainText()):
    events = events.strip()
    if events == SUBSCRIBE_DEFAULT_MESSAGE:
        state["processed_events"] = DEFAULT_SUBSCRIPTION
        return

    processed_events: dict[str, set[str] | None] = {}
    for event in events.split(" "):
        if not event:
            continue
        if not (
            matched := re.match(
                r"^(?P<event>[a-zA-Z_]+)(?:/(?P<action>[a-zA-Z_]+))?$", event
            )
        ):
            await subscribe.reject(f"事件 {event} 不合法！请重新发送或取消")

        # deduplicate
        if (a := matched["action"]) and (
            e := processed_events.setdefault(matched["event"], set())
        ) is not None:
            e.add(matched["action"])
        elif a is None:
            processed_events[matched["event"]] = None

    state["processed_events"] = processed_events


@subscribe.handle()
async def create_user(target_info: TARGET_INFO, state: T_State):
    processed_events: dict[str, set[str] | None] = state["processed_events"]
    try:
        await Subscription.subscribe_by_info(
            target_info,
            *(
                SubData(
                    owner=state["owner"],
                    repo=state["repo"],
                    event=e,
                    action=list(a) if a is not None else None,
                )
                for e, a in processed_events.items()
            ),
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to create or update subscription: {e}")
        await subscribe.finish("订阅失败，请尝试重试或联系管理员")

    await subscribe.finish(
        "订阅成功，当前订阅：\n"
        + subscriptions_to_message(await Subscription.from_info(target_info))
    )


unsubscribe = on_command(
    "unsubscribe",
    MATCH_WHEN_PRIVATE_OR_GROUP & NO_GITHUB_EVENT,
    permission=PRIVATE_PERM | GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@unsubscribe.handle(parameterless=(Depends(stop_unavailable_target),))
async def process_unsubscribe_arg(matcher: Matcher, arg: Message = CommandArg()):
    if args := arg.extract_plain_text().strip().split(" "):
        repo, *events = args
        if repo:
            matcher.set_arg("full_name", arg.__class__(repo))
        if e := " ".join(events):
            matcher.set_arg("events", arg.__class__(e))


@unsubscribe.got("full_name", prompt="取消订阅仓库的全名？(e.g. owner/repo)")
async def process_unsubscribe_repo(state: T_State, full_name: str = ArgPlainText()):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await unsubscribe.finish(f"仓库名 {full_name} 不合法！")

    state["owner"] = matched["owner"]
    state["repo"] = matched["repo"]


@unsubscribe.got(
    "events",
    prompt=f"取消订阅哪些事件或{UNSUBSCRIBE_ALL_MESSAGE}？(e.g. issues[/opened])",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_unsubscribe_event(state: T_State, events: str = ArgPlainText()):
    events = events.strip()
    if events == UNSUBSCRIBE_ALL_MESSAGE:
        state["processed_events"] = events
        return

    processed_events: dict[str, set[str] | None] = {}
    for event in events.split(" "):
        if not event:
            continue
        if not (
            matched := re.match(
                r"^(?P<event>[a-zA-Z_]+)(?:/(?P<action>[a-zA-Z_]+))?$", event
            )
        ):
            await unsubscribe.reject(f"事件 {event} 不合法！请重新发送或取消")

        # deduplicate
        if (a := matched["action"]) and (
            e := processed_events.setdefault(matched["event"], set())
        ) is not None:
            e.add(matched["action"])
        elif a is None:
            processed_events[matched["event"]] = None

    state["processed_events"] = processed_events


@unsubscribe.handle()
async def delete_user(target_info: TARGET_INFO, state: T_State):
    try:
        if state["processed_events"] == UNSUBSCRIBE_ALL_MESSAGE:
            await Subscription.unsubscribe_all_by_info(
                target_info, state["owner"], state["repo"]
            )
        else:
            processed_events: dict[str, set[str] | None] = state["processed_events"]
            await Subscription.unsubscribe_by_info(
                target_info,
                *(
                    SubData(
                        owner=state["owner"],
                        repo=state["repo"],
                        event=e,
                        action=list(a) if a is not None else None,
                    )
                    for e, a in processed_events.items()
                ),
            )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to delete subscription: {e}")
        await unsubscribe.finish("取消订阅失败，请尝试重试或联系管理员")

    await subscribe.finish(
        "取消订阅成功，当前订阅：\n"
        + subscriptions_to_message(await Subscription.from_info(target_info))
    )
