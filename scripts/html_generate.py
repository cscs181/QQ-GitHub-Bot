import re
import sys
import asyncio
from pathlib import Path
from argparse import ArgumentParser

from nonebot import logger, get_adapter
from nonebot.adapters.github import Adapter

logger.remove()
root = Path(__file__).parent.parent

sys.path.append(str(root))

import bot as _bot  # noqa: F401
from src.plugins.github import config
from src.plugins.github.utils import get_oauth_bot
from src.plugins.github.libs.github import ISSUE_REGEX, FULLREPO_REGEX
from src.plugins.github.libs.renderer.context import (
    DiffContext,
    IssueContext,
    ReadmeContext,
)
from src.plugins.github.libs.renderer.render import (
    issue_to_html,
    readme_to_html,
    pr_diff_to_html,
)

parser = ArgumentParser()
sub_parser = parser.add_subparsers(required=True)


async def gen_readme_html(repo: str, output_file: str | None = None):
    m = re.match(rf"^{FULLREPO_REGEX}$", repo)
    if not m:
        print("Invalid repo format, should be: <owner>/<repo>")
        return

    owner, repo = m.groups()
    bot = get_oauth_bot()
    resp = await bot.rest.repos.async_get(owner=owner, repo=repo)
    repository = resp.parsed_data
    resp = await bot.rest.repos.async_get_readme(
        owner=owner, repo=repo, headers={"Accept": "application/vnd.github.html"}
    )
    content = resp.text
    context = await ReadmeContext.from_repo_readme(bot, repository, content)
    html = await readme_to_html(context, config.github_theme)
    if not output_file:
        print(html)
        return
    Path(output_file).write_text(html)


readme = sub_parser.add_parser("readme")
readme.set_defaults(func=gen_readme_html)
readme.add_argument("repo", help="repo readme to render (owner/repo)")
readme.add_argument("-o", "--output-file", required=False, help="output file path")


async def gen_issue_html(
    issue: str, comment: int | None = None, output_file: str | None = None
):
    m = re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", issue)
    if not m:
        print("Invalid issue format, should be: <owner>/<repo>#<issue>")
        return

    owner, repo, issue_number = m.groups()
    bot = get_oauth_bot()
    resp = await bot.rest.issues.async_get(
        owner=owner, repo=repo, issue_number=int(issue_number)
    )
    i = resp.parsed_data
    context = await IssueContext.from_issue(bot, i, highlight_comment=comment)
    html = await issue_to_html(context, theme=config.github_theme)
    if not output_file:
        print(html)
        return
    Path(output_file).write_text(html)


issue = sub_parser.add_parser("issue")
issue.set_defaults(func=gen_issue_html)
issue.add_argument("issue", help="issue to render (owner/repo#issue)")
issue.add_argument("comment", nargs="?", type=int, help="comment to highlight")
issue.add_argument("-o", "--output-file", required=False, help="output file path")


async def gen_diff_html(pr: str, output_file: str | None = None):
    m = re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", pr)
    if not m:
        print("Invalid pr format, should be: <owner>/<repo>#<issue>")
        return

    owner, repo, issue_number = m.groups()
    bot = get_oauth_bot()
    resp = await bot.rest.issues.async_get(
        owner=owner, repo=repo, issue_number=int(issue_number)
    )
    issue = resp.parsed_data
    if not issue.pull_request:
        print("Not a pull request")

    context = await DiffContext.from_issue(bot, issue)
    html = await pr_diff_to_html(context, config.github_theme)
    if not output_file:
        print(html)
        return
    Path(output_file).write_text(html)


diff = sub_parser.add_parser("diff")
diff.set_defaults(func=gen_diff_html)
diff.add_argument("pr", help="pr to render (owner/repo#pr)")
diff.add_argument("-o", "--output-file", required=False, help="output file path")


async def main():
    adapter = get_adapter(Adapter)
    await adapter._startup()
    result = parser.parse_args()
    result = vars(result)
    command = result.pop("func")
    await command(**result)


if __name__ == "__main__":
    asyncio.run(main())
