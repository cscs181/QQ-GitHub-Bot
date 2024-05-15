"""
@Author         : yanyongyu
@Date           : 2022-09-14 03:31:15
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 00:36:21
@Description    : GitHub helpers
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

URL_PCHAR = r"(?:[a-zA-Z0-9\-._~!$&'()*+,;=:@]|%[0-9a-fA-F]{2})"
URL_QUERY_REGEX = rf"(?:\?(?:{URL_PCHAR}|[/?])*)?"

OWNER_REGEX = r"(?P<owner>[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)"
REPO_REGEX = r"(?P<repo>[a-zA-Z0-9_\-\.]+)"
FULLREPO_REGEX = rf"{OWNER_REGEX}/{REPO_REGEX}"
COMMIT_HASH_REGEX = r"(?P<commit>[0-9a-f]{5,40})"
ISSUE_REGEX = r"(?P<issue>\d+)"
ISSUE_COMMENT_REGEX = r"(?:#issuecomment-(?P<comment>\d+))?"

GITHUB_LINK_REGEX = r"github\.com"
GITHUB_REPO_LINK_REGEX = rf"{GITHUB_LINK_REGEX}/{FULLREPO_REGEX}"
GITHUB_COMMIT_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/commit/{COMMIT_HASH_REGEX}"
GITHUB_ISSUE_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/issues/{ISSUE_REGEX}"
    rf"{URL_QUERY_REGEX}{ISSUE_COMMENT_REGEX}"
)
GITHUB_PR_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/pull/{ISSUE_REGEX}"
    rf"{URL_QUERY_REGEX}{ISSUE_COMMENT_REGEX}"
)
GITHUB_ISSUE_OR_PR_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/(?:issues|pull)/{ISSUE_REGEX}"
    rf"{URL_QUERY_REGEX}{ISSUE_COMMENT_REGEX}"
)
GITHUB_PR_COMMIT_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/commits/{COMMIT_HASH_REGEX}"
GITHUB_PR_FILE_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/files"
GITHUB_RELEASE_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/releases/tag/(?P<tag>{URL_PCHAR}+)"
)
