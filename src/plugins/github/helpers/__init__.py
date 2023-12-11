"""
@Author         : yanyongyu
@Date           : 2022-09-07 12:17:55
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-13 17:35:27
@Description    : Helpers for github plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from .cancellation import is_cancellation as is_cancellation
from .cancellation import allow_cancellation as allow_cancellation

# isort: split

from .rule import REPLY_PR as REPLY_PR
from .rule import REPLY_ANY as REPLY_ANY
from .rule import NO_GITHUB_EVENT as NO_GITHUB_EVENT
from .rule import MATCH_WHEN_GROUP as MATCH_WHEN_GROUP
from .rule import REPLY_ISSUE_OR_PR as REPLY_ISSUE_OR_PR
from .rule import MATCH_WHEN_PRIVATE as MATCH_WHEN_PRIVATE
from .rule import MATCH_WHEN_PRIVATE_OR_GROUP as MATCH_WHEN_PRIVATE_OR_GROUP

# isort: split

from .permission import PRIVATE_PERM as PRIVATE_PERM
from .permission import GROUP_SUPERPERM as GROUP_SUPERPERM
