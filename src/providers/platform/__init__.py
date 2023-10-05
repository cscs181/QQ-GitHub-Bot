from typing import Annotated, TypeAlias

from nonebot.params import Depends

from .entities import User as User
from .entities import Group as Group
from .entities import Channel as Channel
from .entities import Message as Message
from .entities import BaseUser as BaseUser
from .typing import PLATFORMS as PLATFORMS
from .entities import BaseGroup as BaseGroup
from .entities import BaseChannel as BaseChannel
from .entities import BaseMessage as BaseMessage
from .extractors import extract_user as extract_user
from .extractors import extract_group as extract_group
from .extractors import extract_channel as extract_channel
from .extractors import extract_message as extract_message
from .extractors import extract_platform as extract_platform
from .extractors import extract_is_private as extract_is_private
from .extractors import extract_sent_message as extract_sent_message

PLATFORM: TypeAlias = Annotated[PLATFORMS | None, Depends(extract_platform)]
USER: TypeAlias = Annotated[User | None, Depends(extract_user)]
GROUP: TypeAlias = Annotated[Group | None, Depends(extract_group)]
CHANNEL: TypeAlias = Annotated[Channel | None, Depends(extract_channel)]
IS_PRIVATE: TypeAlias = Annotated[bool | None, Depends(extract_is_private)]
MESSAGE: TypeAlias = Annotated[Message | None, Depends(extract_message)]
