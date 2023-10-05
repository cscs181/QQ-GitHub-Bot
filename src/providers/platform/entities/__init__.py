from ._base import Entity as Entity

# isort: split

from .user import User as User
from .user import QQUser as QQUser
from .user import BaseUser as BaseUser
from .user import QQGuildUser as QQGuildUser

# isort: split

from .group import Group as Group
from .group import QQGroup as QQGroup
from .group import BaseGroup as BaseGroup
from .group import QQOfficialGroup as QQOfficialGroup

# isort: split

from .channel import Channel as Channel
from .channel import BaseChannel as BaseChannel
from .channel import QQGuildChannel as QQGuildChannel

# isort: split

from .message import Message as Message
from .message import QQMessage as QQMessage
from .message import BaseMessage as BaseMessage
from .message import QQGuildMessage as QQGuildMessage
