"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 08:34:04
@Description    : Platform lib
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Literal

PLATFORMS = Literal["qq", "qqguild"]

from .info import UserInfo as UserInfo
from .info import GroupInfo as GroupInfo
from .user_crud import get_user as get_user
from .bot import get_user_bot as get_user_bot
from .group_crud import get_group as get_group
from .bot import get_group_bot as get_group_bot
from .user_crud import delete_user as delete_user
from .group_crud import delete_group as delete_group
from .user_crud import create_or_update_user as create_or_update_user
from .group_crud import create_or_update_group as create_or_update_group
from .user_subscription_crud import list_subscribed_users as list_subscribed_users
from .group_subscription_crud import list_subscribed_groups as list_subscribed_groups
from .user_subscription_crud import list_user_subscriptions as list_user_subscriptions
from .user_subscription_crud import delete_user_subscription as delete_user_subscription
from .group_subscription_crud import (
    list_group_subscriptions as list_group_subscriptions,
)
from .group_subscription_crud import (
    delete_group_subscription as delete_group_subscription,
)
from .user_subscription_crud import (
    delete_all_user_subscriptions as delete_all_user_subscriptions,
)
from .group_subscription_crud import (
    delete_all_group_subscriptions as delete_all_group_subscriptions,
)
from .user_subscription_crud import (
    create_or_update_user_subscriptions as create_or_update_user_subscriptions,
)
from .group_subscription_crud import (
    create_or_update_group_subscriptions as create_or_update_group_subscriptions,
)
