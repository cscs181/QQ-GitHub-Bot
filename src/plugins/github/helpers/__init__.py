"""
@Author         : yanyongyu
@Date           : 2022-09-07 12:17:55
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 17:11:59
@Description    : Helpers for github plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from .cancellation import is_cancellation as is_cancellation
from .cancellation import allow_cancellation as allow_cancellation

# isort: split

from .github import REPO_REGEX as REPO_REGEX
from .github import ISSUE_REGEX as ISSUE_REGEX
from .github import OWNER_REGEX as OWNER_REGEX
from .github import FULLREPO_REGEX as FULLREPO_REGEX
from .github import COMMIT_HASH_REGEX as COMMIT_HASH_REGEX
from .github import GITHUB_LINK_REGEX as GITHUB_LINK_REGEX
from .github import GITHUB_PR_LINK_REGEX as GITHUB_PR_LINK_REGEX
from .github import GITHUB_REPO_LINK_REGEX as GITHUB_REPO_LINK_REGEX
from .github import GITHUB_ISSUE_LINK_REGEX as GITHUB_ISSUE_LINK_REGEX
from .github import GITHUB_COMMIT_LINK_REGEX as GITHUB_COMMIT_LINK_REGEX
from .github import GITHUB_PR_FILE_LINK_REGEX as GITHUB_PR_FILE_LINK_REGEX
from .github import GITHUB_RELEASE_LINK_REGEX as GITHUB_RELEASE_LINK_REGEX
from .github import GITHUB_PR_COMMIT_LINK_REGEX as GITHUB_PR_COMMIT_LINK_REGEX
from .github import GITHUB_ISSUE_OR_PR_LINK_REGEX as GITHUB_ISSUE_OR_PR_LINK_REGEX

# isort: split

from .rule import NO_GITHUB_EVENT as NO_GITHUB_EVENT

# isort: split

from .permission import PRIVATE_PERM as PRIVATE_PERM
from .permission import GROUP_SUPERPERM as GROUP_SUPERPERM
