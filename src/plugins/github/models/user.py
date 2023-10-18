"""
@Author         : yanyongyu
@Date           : 2022-09-05 09:50:07
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-11 13:26:13
@Description    : User model
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

from src.providers.platform import UserInfo


class User(Model):
    """User model"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[dict] = mapped_column(JSONB, unique=True, index=True, nullable=False)
    access_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def to_user_info(self) -> UserInfo:
        """Convert to user info"""
        return parse_obj_as(UserInfo, self.user)

    @classmethod
    async def from_info(cls, info: UserInfo) -> Self | None:
        """Get user model by user info"""
        sql = select(cls).where(cls.user == info.dict())
        result = await get_session().execute(sql)
        return result.scalar_one_or_none()

    @classmethod
    async def create_or_update_by_info(
        cls, info: UserInfo | Self, access_token: str | None
    ) -> Self:
        """Create or update user model by user info"""
        if isinstance(info, cls):
            info = info.to_user_info()

        info = cast(UserInfo, info)

        insert_sql = insert(cls).values(user=info.dict(), access_token=access_token)
        update_sql = insert_sql.on_conflict_do_update(
            set_={"access_token": insert_sql.excluded.access_token}
        ).returning(cls)

        result = await get_session().execute(update_sql)
        return result.scalar_one()

    async def unauth(self) -> None:
        """UnAuth user"""
        self.access_token = None
        session = get_session()
        session.add(self)
        await session.commit()

    @classmethod
    async def unauth_by_info(cls, info: UserInfo) -> bool:
        """UnAuth user by user info"""
        if user := await cls.from_info(info):
            await user.unauth()
            return True
        return False
