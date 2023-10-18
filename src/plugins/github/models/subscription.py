"""
@Author         : yanyongyu
@Date           : 2022-10-26 14:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-11 14:43:45
@Description    : User subscription model
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import TypedDict, cast
from typing_extensions import Self

from pydantic import parse_obj_as
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy import (
    Index,
    String,
    UniqueConstraint,
    case,
    func,
    delete,
    select,
    distinct,
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
        Index(None, "owner", "repo", "event"),
        UniqueConstraint("subscriber", "owner", "repo", "event"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber: Mapped[dict] = mapped_column(JSONB, index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    event: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    def to_subscriber_info(self) -> TargetInfo:
        """Convert to subscriber info"""
        return parse_obj_as(TargetInfo, self.subscriber)

    @classmethod
    async def from_info(cls, info: TargetInfo) -> list[Self]:
        """List subscriptions by subscriber info"""
        sql = select(cls).where(cls.subscriber == info.dict())
        result = await get_session().execute(sql)
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

        merge_action = insert_sql.excluded.action + cls.action
        merge_action_elements = func.jsonb_array_elements(merge_action).alias()
        merge_action = (
            select(func.jsonb_agg(distinct(merge_action_elements.column)))
            .select_from(merge_action_elements)
            .subquery()
        )
        new_action = case(
            (insert_sql.excluded.action.is_(None), None),
            (cls.action.is_(None), None),
            else_=merge_action,
        )
        update_sql = insert_sql.on_conflict_do_update(set_={"action": new_action})
        await get_session().execute(update_sql)

    @classmethod
    async def unsubscribe_by_info(
        cls, info: TargetInfo | Self, *unsubsciptions: SubData
    ) -> None:
        """Delete user subscription by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        session = get_session()
        async with session.begin():
            for unsubscription in unsubsciptions:
                instance_sql = select(cls).where(
                    cls.subscriber == info.dict(),
                    cls.owner == unsubscription["owner"],
                    cls.repo == unsubscription["repo"],
                    cls.event == unsubscription["event"],
                )
                instance = (await session.execute(instance_sql)).scalar_one_or_none()
                if instance:
                    if unsubscription["action"] is None:
                        await session.delete(instance)
                    elif instance.action:
                        new_action = list(
                            set(instance.action) - set(unsubscription["action"])
                        )
                        if not new_action:
                            await session.delete(instance)
                        else:
                            instance.action = new_action
                            session.add(instance)

    @classmethod
    async def unsubscribe_all_by_info(
        cls, info: TargetInfo | Self, owner: str, repo: str
    ) -> None:
        """Delete all user subscriptions of the repo by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        delete_sql = delete(cls).where(
            cls.subscriber == info.dict(), cls.owner == owner, cls.repo == repo
        )
        await get_session().execute(delete_sql)

    @classmethod
    async def list_subscribers(
        cls, owner: str, repo: str, event: str, action: str | None = None
    ) -> list[Self]:
        """List subscribers from repo webhook event name"""
        if action is None:
            list_sql = select(cls).where(
                cls.owner == owner,
                cls.repo == repo,
                cls.event == event,
                cls.action.is_(None),
            )
        else:
            list_sql = select(cls).where(
                cls.owner == owner,
                cls.repo == repo,
                cls.event == event,
                cls.action.contains(action),
            )
        result = await get_session().execute(list_sql)
        return list(result.scalars().all())
