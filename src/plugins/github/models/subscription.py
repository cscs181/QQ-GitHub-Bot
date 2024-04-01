"""
@Author         : yanyongyu
@Date           : 2022-10-26 14:54:12
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:54:56
@Description    : User subscription model
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Self, TypedDict, cast

from pydantic import TypeAdapter
from sqlalchemy import cast as sql_cast
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session
from sqlalchemy import Index, String, UniqueConstraint, case
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, insert
from sqlalchemy import func, select, update, distinct, bindparam

from src.providers.platform import TargetInfo


class SubData(TypedDict):
    """Subscription data"""

    owner: str
    repo: str
    event: str
    action: list[str] | None


UNIQUE_SUBSCRIPTION = UniqueConstraint("subscriber", "owner", "repo", "event")


class Subscription(Model):
    """GitHub event subscription model"""

    __tablename__ = "subscription"
    __table_args__ = (
        Index(None, "owner", "repo", "event", "action"),
        UNIQUE_SUBSCRIPTION,
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber: Mapped[dict] = mapped_column(JSONB, index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(), nullable=False)
    repo: Mapped[str] = mapped_column(String(), nullable=False)
    event: Mapped[str] = mapped_column(String(), nullable=False)
    action: Mapped[list[str] | None] = mapped_column(ARRAY(String()), nullable=True)

    def to_subscriber_info(self) -> TargetInfo:
        """Convert to subscriber info"""
        return TypeAdapter(TargetInfo).validate_python(self.subscriber)

    @classmethod
    async def from_info(cls, info: TargetInfo) -> list[Self]:
        """List subscriptions by subscriber info"""
        sql = select(cls).where(cls.subscriber == info.model_dump())
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
                    "subscriber": info.model_dump(),
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
            .scalar_subquery()
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

        update_sql = insert_sql.on_conflict_do_update(
            constraint=UNIQUE_SUBSCRIPTION, set_={"action": new_action}
        )
        async with get_session() as session:
            await session.execute(update_sql)
            await session.commit()

    @classmethod
    async def unsubscribe_by_info(
        cls, info: TargetInfo | Self, *unsubsciptions: SubData
    ) -> None:
        """Delete user subscription by user info"""
        if isinstance(info, cls):
            info = info.to_subscriber_info()

        info = cast(TargetInfo, info)

        old_action_elements = func.unnest(cls.action).alias()
        sql = (
            update(cls)
            .where(
                cls.subscriber == bindparam("tmp_subscriber"),
                cls.owner == bindparam("tmp_owner"),
                cls.repo == bindparam("tmp_repo"),
                cls.event == bindparam("tmp_event"),
            )
            .values(
                action=case(
                    # do nothing if origin action is None
                    (cls.action.is_(None), None),
                    # remove all actions if unsubscription["action"] is None
                    (sql_cast(bindparam("tmp_action"), ARRAY(String())).is_(None), []),
                    # remove any value in unsubscription["action"]
                    else_=(
                        select(func.array_agg(old_action_elements.column))
                        .select_from(old_action_elements)
                        .where(
                            old_action_elements.column
                            != func.all(bindparam("tmp_action"))
                        )
                        .scalar_subquery()
                    ),
                )
            )
        )
        async with get_session() as session:
            conn = await session.connection()
            await conn.execute(
                sql,
                [
                    {
                        "tmp_subscriber": info.model_dump(),
                        "tmp_owner": unsubscription["owner"],
                        "tmp_repo": unsubscription["repo"],
                        "tmp_event": unsubscription["event"],
                        "tmp_action": unsubscription["action"],
                    }
                    for unsubscription in unsubsciptions
                ],
            )
            await conn.commit()

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
                cls.subscriber == info.model_dump(),
                cls.owner == owner,
                cls.repo == repo,
            )
            # set to empty array
            .values(action=[])
        )
        async with get_session() as session:
            await session.execute(clear_sql)
            await session.commit()

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
