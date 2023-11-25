"""
@Author         : yanyongyu
@Date           : 2022-10-26 14:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-25 19:32:56
@Description    : User subscription model
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import TypedDict, cast
from typing_extensions import Self

from pydantic import parse_obj_as
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, insert
from sqlalchemy import (
    Index,
    String,
    UniqueConstraint,
    case,
    func,
    select,
    update,
    distinct,
    bindparam,
)

from src.providers.platform import TargetInfo


class SubData(TypedDict):
    """Subscription data"""

    owner: str
    repo: str
    event: str
    action: list[str] | None


class Subscription(Model):
    """GitHub event subscription model"""

    __tablename__ = "subscription"
    __table_args__ = (
        Index(None, "owner", "repo", "event", "action"),
        UniqueConstraint("subscriber", "owner", "repo", "event"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber: Mapped[dict] = mapped_column(JSONB, index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(), nullable=False)
    repo: Mapped[str] = mapped_column(String(), nullable=False)
    event: Mapped[str] = mapped_column(String(), nullable=False)
    action: Mapped[list[str] | None] = mapped_column(ARRAY(String()), nullable=True)

    def to_subscriber_info(self) -> TargetInfo:
        """Convert to subscriber info"""
        return parse_obj_as(TargetInfo, self.subscriber)

    @classmethod
    async def from_info(cls, info: TargetInfo) -> list[Self]:
        """List subscriptions by subscriber info"""
        sql = select(cls).where(cls.subscriber == info.dict())
        async with get_session() as session:
            result = await session.execute(sql)
            return list(result.scalars().all())

    @classmethod
    async def subscribe_by_info(
        cls, info: TargetInfo | Self, *subsciptions: SubData
    ) -> None:
        """Create or update user subscriptions by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        insert_sql = insert(cls).values(
            [
                {
                    "subscriber": info.dict(),
                    **subscription,
                }
                for subscription in subsciptions
            ]
        )

        # create new actions
        merge_action = insert_sql.excluded.action + cls.action
        merge_action_elements = func.unnest(merge_action).alias()
        # deduplicate
        merge_action = (
            select(func.array_agg(distinct(merge_action_elements.column)))
            .select_from(merge_action_elements)
            .subquery()
        )
        # handle on conflict special case
        new_action = case(
            # new action is None, subscribe all
            (insert_sql.excluded.action.is_(None), None),
            # old action is None, do nothing
            (cls.action.is_(None), None),
            # append when action is not None
            else_=merge_action,
        )

        update_sql = insert_sql.on_conflict_do_update(set_={"action": new_action})
        async with get_session() as session:
            await session.execute(update_sql)

    @classmethod
    async def unsubscribe_by_info(
        cls, info: TargetInfo | Self, *unsubsciptions: SubData
    ) -> None:
        """Delete user subscription by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        old_action_elements = func.unnest(cls.action).alias()
        update_data = [
            {
                "subscriber": info.dict(),
                "owner": unsubscription["owner"],
                "repo": unsubscription["repo"],
                "event": unsubscription["event"],
                "action": (
                    # remove all actions
                    []
                    if unsubscription["action"] is None
                    else case(
                        # do no action when origin action is None
                        (cls.action.is_(None), None),
                        # remove any value in unsubscription["action"]
                        else_=(
                            select(func.array_agg(old_action_elements))
                            .select_from(old_action_elements)
                            .where(
                                old_action_elements.column
                                != func.all(unsubscription["action"])
                            )
                            .subquery()
                        ),
                    )
                ),
            }
            for unsubscription in unsubsciptions
        ]
        async with get_session() as session:
            async with await session.connection() as conn:
                await conn.execute(
                    update(cls).where(
                        cls.subscriber == bindparam("subscriber"),
                        cls.owner == bindparam("owner"),
                        cls.repo == bindparam("repo"),
                        cls.event == bindparam("event"),
                    ),
                    update_data,
                )

    @classmethod
    async def unsubscribe_all_by_info(
        cls, info: TargetInfo | Self, owner: str, repo: str
    ) -> None:
        """Delete all user subscriptions of the repo by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        clear_sql = (
            update(cls).where(
                cls.subscriber == info.dict(), cls.owner == owner, cls.repo == repo
            )
            # set to empty array
            .values(action=[])
        )
        async with get_session() as session:
            await session.execute(clear_sql)

    @classmethod
    async def list_subscribers(
        cls, owner: str, repo: str, event: str, action: str | None = None
    ) -> list[Self]:
        """List subscribers from repo webhook event name"""
        action_filter = cls.action.is_(None)
        if action is not None:
            # pg operation `@>` array contains another array
            action_filter |= cls.action.contains([action])

        list_sql = select(cls).where(
            cls.owner == owner, cls.repo == repo, cls.event == event, action_filter
        )
        async with get_session() as session:
            result = await session.execute(list_sql)
            return list(result.scalars().all())
