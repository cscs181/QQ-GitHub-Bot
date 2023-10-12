"""
@Author         : yanyongyu
@Date           : 2022-09-06 07:31:43
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-11 13:25:58
@Description    : Group model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import cast
from typing_extensions import Self

from pydantic import parse_obj_as
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session
from sqlalchemy.dialects.postgresql import JSONB, insert

from src.providers.platform import GroupInfo


class Group(Model):
    """Group model"""

    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[dict] = mapped_column(JSONB, unique=True, index=True, nullable=False)
    bind_repo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def to_group_info(self) -> GroupInfo:
        """Convert to group info"""
        return parse_obj_as(GroupInfo, self.group)

    @classmethod
    async def from_info(cls, info: GroupInfo) -> Self | None:
        """Get group model by group info"""
        sql = select(cls).where(cls.group == info.dict())
        result = await get_session().execute(sql)
        return result.scalar_one_or_none()

    @classmethod
    async def create_or_update_by_info(
        cls, info: GroupInfo | Self, bind_repo: str | None
    ) -> Self:
        """Create or update group model by group info"""
        if isinstance(info, cls):
            info = info.to_group_info()

        info = cast(GroupInfo, info)

        insert_sql = insert(cls).values(user=info.dict(), bind_repo=bind_repo)
        update_sql = insert_sql.on_conflict_do_update(
            set_={"bind_repo": insert_sql.excluded.bind_repo}
        ).returning(cls)

        result = await get_session().execute(update_sql)
        return result.scalar_one()

    async def unbind(self) -> None:
        """Unbind group and repo"""
        self.bind_repo = None
        session = get_session()
        session.add(self)
        await session.commit()

    @classmethod
    async def unbind_by_info(cls, info: GroupInfo) -> bool:
        """Unbind group and repo by group info"""
        if group := await cls.from_info(info):
            await group.unbind()
            return True
        return False
