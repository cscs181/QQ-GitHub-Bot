from typing import Dict, List

import psutil
import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_status(app: App, monkeypatch: pytest.MonkeyPatch):
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot, Adapter, Message
    from nonebot.adapters.onebot.v11.event import (
        Sender,
        PokeNotifyEvent,
        PrivateMessageEvent,
    )

    from src.plugins.nonebot_plugin_status import (
        command,
        group_poke,
        status_config,
    )

    driver = nonebot.get_driver()

    # patch status
    def _cpu_status() -> float:
        return 10.0

    def _disk_usage() -> Dict[str, psutil._common.sdiskusage]:
        return {"test": psutil._common.sdiskusage(0, 0, 0, 0)}

    def _memory_status() -> float:
        return 10.0

    def _per_cpu_status() -> List[float]:
        return [10.0, 11.0]

    monkeypatch.setattr(
        "src.plugins.nonebot_plugin_status.cpu_status", _cpu_status
    )
    monkeypatch.setattr(
        "src.plugins.nonebot_plugin_status.disk_usage", _disk_usage
    )
    monkeypatch.setattr(
        "src.plugins.nonebot_plugin_status.memory_status", _memory_status
    )
    monkeypatch.setattr(
        "src.plugins.nonebot_plugin_status.per_cpu_status", _per_cpu_status
    )

    with monkeypatch.context() as m:
        m.setattr(driver.config, "superusers", {"123"})

        async with app.test_matcher(command) as ctx:
            adapter = ctx.create_adapter(base=Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)

            event = PrivateMessageEvent(
                time=0,
                self_id=0,
                post_type="message",
                sub_type="friend",
                user_id=123,
                message_type="private",
                message_id=0,
                message=Message("/状态"),
                raw_message="/状态",
                font=0,
                sender=Sender(),
            )
            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "\n".join(
                    [
                        "CPU: 10%",
                        "Memory: 10%",
                        "Disk:",
                        "  test: 00%",
                    ]
                ),
                True,
            )

        async with app.test_matcher(group_poke) as ctx:
            adapter = ctx.create_adapter(base=Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)

            event = PokeNotifyEvent(
                time=0,
                self_id=0,
                post_type="notice",
                notice_type="notify",
                sub_type="poke",
                user_id=123,
                target_id=0,
            )
            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "\n".join(
                    [
                        "CPU: 10%",
                        "Memory: 10%",
                        "Disk:",
                        "  test: 00%",
                    ]
                ),
                True,
            )

        m.setattr(status_config, "server_status_per_cpu", True)

        async with app.test_matcher(command) as ctx:
            adapter = ctx.create_adapter(base=Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)

            event = PrivateMessageEvent(
                time=0,
                self_id=0,
                post_type="message",
                sub_type="friend",
                user_id=123,
                message_type="private",
                message_id=0,
                message=Message("/状态"),
                raw_message="/状态",
                font=0,
                sender=Sender(),
            )
            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "\n".join(
                    [
                        "CPU:",
                        "  core1: 10%",
                        "  core2: 11%",
                        "Memory: 10%",
                        "Disk:",
                        "  test: 00%",
                    ]
                ),
                True,
            )
