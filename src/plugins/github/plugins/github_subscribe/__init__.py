#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-22 14:35:43
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:57:44
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re

from nonebot import on_command
from nonebot.log import logger
from nonebot.rule import is_type
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event, Message
from nonebot.params import Depends, CommandArg, ArgPlainText
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.models import User, UserSubscription, GroupSubscription
from src.plugins.github.libs.platform import (
    delete_user_subscription,
    delete_group_subscription,
    delete_all_user_subscriptions,
    delete_all_group_subscriptions,
    create_or_update_user_subscriptions,
    create_or_update_group_subscriptions,
)
from src.plugins.github.helpers import (
    GROUP_EVENT,
    PRIVATE_PERM,
    PRIVATE_EVENT,
    FULLREPO_REGEX,
    GROUP_SUPERPERM,
    NO_GITHUB_EVENT,
    get_user_info,
    get_group_info,
    run_when_group,
    get_current_user,
    run_when_private,
    allow_cancellation,
)

from .dependencies import list_user, list_group, bypass_create

__plugin_meta__ = PluginMetadata(
    "GitHub 事件订阅",
    "订阅 GitHub 仓库事件",
    (
        "/subscribe: 查看当前已有订阅\n"
        "/subscribe owner/repo [event/action ...]: 订阅指定仓库的某类事件\n"
        "/unsubscribe owner/repo [event/action ...]: 取消订阅指定仓库的某类事件"
    ),
)

SUBSCRIBE_DEFAULT_MESSAGE = "默认"
DEFAULT_SUBSCRIPTION = {
    "issues": ["opened", "edited", "closed", "reopened"],
    "issue_comment": ["created", "edited"],
    "pull_request": ["opened", "closed", "reopened"],
    "release": ["published"],
}
UNSUBSCRIBE_ALL_MESSAGE = "全部"


def subsciption_to_message(
    subs: list[UserSubscription] | list[GroupSubscription],
) -> str:
    repos: dict[str, list[str]] = {}
    for sub in subs:
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
    is_type(*PRIVATE_EVENT, *GROUP_EVENT) & NO_GITHUB_EVENT,
    permission=PRIVATE_PERM | GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@subscribe.handle()
async def process_subscribe_arg(matcher: Matcher, arg: Message = CommandArg()):
    if args := arg.extract_plain_text().strip().split(" "):
        repo, *events = args
        if repo:
            matcher.set_arg("full_name", arg.__class__(repo))
        if e := " ".join(events):
            matcher.set_arg("events", arg.__class__(e))


@subscribe.handle(parameterless=(Depends(bypass_create), Depends(run_when_private)))
async def list_user_subscription(
    subsciptions: list[UserSubscription] = Depends(list_user),
):
    if subsciptions:
        await subscribe.finish("当前已订阅：\n" + subsciption_to_message(subsciptions))


@subscribe.handle(parameterless=(Depends(bypass_create), Depends(run_when_group)))
async def list_group_subscription(
    subsciptions: list[GroupSubscription] = Depends(list_group),
):
    if subsciptions:
        await subscribe.finish("当前已订阅：\n" + subsciption_to_message(subsciptions))


@subscribe.handle()
async def handle_check(user: None = Depends(get_current_user)):
    await subscribe.finish("你还没有授权 GitHub 帐号，请私聊使用 /install 进行安装")


@subscribe.got(
    "full_name",
    prompt="订阅仓库的全名？(e.g. owner/repo)",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_subscribe_repo(
    state: T_State,
    full_name: str = ArgPlainText(),
    user: User = Depends(get_current_user),
):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await subscribe.reject(f"仓库名 {full_name} 不合法！请重新发送或取消")

    bot = get_github_bot()
    owner: str
    repo: str
    owner = state["owner"] = matched["owner"]
    repo = state["repo"] = matched["repo"]
    try:
        repo_installation = await bot.rest.apps.async_get_repo_installation(
            owner=owner, repo=repo
        )
    except ActionTimeout:
        await subscribe.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await subscribe.reject(f"仓库 {owner}/{repo} 未安装 APP！请重新发送或取消")
        logger.opt(exception=e).error(
            f"Failed while getting repo installation in group subscribe: {e}"
        )
        await subscribe.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while getting repo installation in group subscribe: {e}"
        )
        await subscribe.finish("未知错误发生，请尝试重试或联系管理员")

    try:
        async with bot.as_user(user.access_token):
            async for accessible_repo in bot.github.paginate(
                bot.rest.apps.async_list_installation_repos_for_authenticated_user,
                map_func=lambda r: r.parsed_data.repositories,
                installation_id=repo_installation.parsed_data.id,
            ):
                if accessible_repo.full_name == full_name:
                    break
            else:
                await subscribe.reject(f"你没有权限访问仓库 {owner}/{repo} ！请重新发送或取消")
    except ActionTimeout:
        await subscribe.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code in {403, 404}:
            await subscribe.reject(f"你没有权限访问仓库 {owner}/{repo} ！请重新发送或取消")
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


@subscribe.handle(parameterless=(Depends(run_when_private),))
async def create_user(event: Event, state: T_State):
    if info := get_user_info(event):
        processed_events: dict[str, set[str] | None] = state["processed_events"]
        await create_or_update_user_subscriptions(
            info,
            *(
                {
                    "owner": state["owner"],
                    "repo": state["repo"],
                    "event": e,
                    "action": a and list(a),
                }
                for e, a in processed_events.items()
            ),
        )
        await subscribe.finish(
            "操作成功，当前订阅：\n" + subsciption_to_message(await list_user(event))
        )
    else:
        logger.error(f"Unprocessed event type: {type(event)}")
        await subscribe.finish("内部错误，请联系管理员")


@subscribe.handle(parameterless=(Depends(run_when_group),))
async def create_group(event: Event, state: T_State):
    if info := get_group_info(event):
        processed_events: dict[str, set[str] | None] = state["processed_events"]
        await create_or_update_group_subscriptions(
            info,
            *(
                {
                    "owner": state["owner"],
                    "repo": state["repo"],
                    "event": e,
                    "action": a and list(a),
                }
                for e, a in processed_events.items()
            ),
        )
        await subscribe.finish(
            "操作成功，当前订阅：\n" + subsciption_to_message(await list_group(event))
        )
    else:
        logger.error(f"Unprocessed event type: {type(event)}")
        await subscribe.finish("内部错误，请联系管理员")


unsubscribe = on_command(
    "unsubscribe",
    is_type(*PRIVATE_EVENT, *GROUP_EVENT) & NO_GITHUB_EVENT,
    permission=PRIVATE_PERM | GROUP_SUPERPERM,
    priority=config.github_command_priority,
    block=True,
)


@unsubscribe.handle()
async def process_unsubscribe_arg(matcher: Matcher, arg: Message = CommandArg()):
    if args := arg.extract_plain_text().strip().split(" "):
        repo, *events = args
        if repo:
            matcher.set_arg("full_name", arg.__class__(repo))
        if e := " ".join(events):
            matcher.set_arg("events", arg.__class__(e))


@unsubscribe.got(
    "full_name",
    prompt="取消订阅仓库的全名？(e.g. owner/repo)",
    parameterless=(allow_cancellation("已取消"),),
)
async def process_unsubscribe_repo(state: T_State, full_name: str = ArgPlainText()):
    if not (matched := re.match(f"^{FULLREPO_REGEX}$", full_name)):
        await unsubscribe.reject(f"仓库名 {full_name} 不合法！请重新发送或取消")

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


@unsubscribe.handle(parameterless=(Depends(run_when_private),))
async def delete_user(event: Event, state: T_State):
    if info := get_user_info(event):
        if state["processed_events"] == UNSUBSCRIBE_ALL_MESSAGE:
            await delete_all_user_subscriptions(info, state["owner"], state["repo"])
        else:
            processed_events: dict[str, set[str] | None] = state["processed_events"]
            await delete_user_subscription(
                info,
                *(
                    {
                        "owner": state["owner"],
                        "repo": state["repo"],
                        "event": e,
                        "action": a and list(a),
                    }
                    for e, a in processed_events.items()
                ),
            )
        await subscribe.finish(
            "操作成功，当前订阅：\n" + subsciption_to_message(await list_user(event))
        )
    else:
        logger.error(f"Unprocessed event type: {type(event)}")
        await subscribe.finish("内部错误，请联系管理员")


@unsubscribe.handle(parameterless=(Depends(run_when_group),))
async def delete_group(event: Event, state: T_State):
    if info := get_group_info(event):
        if state["processed_events"] == UNSUBSCRIBE_ALL_MESSAGE:
            await delete_all_group_subscriptions(info, state["owner"], state["repo"])
        else:
            processed_events: dict[str, set[str] | None] = state["processed_events"]
            await delete_group_subscription(
                info,
                *(
                    {
                        "owner": state["owner"],
                        "repo": state["repo"],
                        "event": e,
                        "action": a and list(a),
                    }
                    for e, a in processed_events.items()
                ),
            )
        await subscribe.finish(
            "操作成功，当前订阅：\n" + subsciption_to_message(await list_group(event))
        )
    else:
        logger.error(f"Unprocessed event type: {type(event)}")
        await subscribe.finish("内部错误，请联系管理员")
