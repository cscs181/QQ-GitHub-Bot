"""
@Author         : yanyongyu
@Date           : 2022-09-06 07:31:43
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 17:38:28
@Description    : Group model
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing_extensions import Self

from tortoise import fields
from pydantic import parse_obj_as
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from src.providers.platform import GroupInfo


class Group(Model):
    """Group model"""

    id = fields.BigIntField(pk=True)
    group = fields.JSONField(unique=True, null=False)
    bind_repo = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "group"

    def to_group_info(self) -> GroupInfo:
        """Convert to group info"""
        return parse_obj_as(GroupInfo, self.group)

    @classmethod
    async def from_info(cls, info: GroupInfo) -> Self | None:
        """Get group model by group info"""
        try:
            return await cls.get(group=info.dict())
        except DoesNotExist:
            return None

    @classmethod
    async def create_or_update_by_info(
        cls, info: GroupInfo | Self, bind_repo: str | None
    ) -> Self:
        """Create or update group model by group info"""
        data = {"bind_repo": bind_repo}

        if isinstance(info, cls):
            await info.update_from_dict(data).save()
            return info

        group, _ = await cls.update_or_create(group=info.dict(), defaults=data)
        return group

    async def unbind(self) -> None:
        """Unbind group and repo"""
        self.bind_repo = None
        await self.save()

    @classmethod
    async def unbind_by_info(cls, info: GroupInfo) -> bool:
        """Unbind group and repo by group info"""
        if group := await cls.from_info(info):
            await group.unbind()
            return True
        return False
