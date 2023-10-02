import re
import sys
import asyncio
from pathlib import Path
from typing import Optional
from argparse import ArgumentParser

from nonebot import logger, get_adapter
from nonebot.adapters.github import Adapter

logger.remove()
root = Path(__file__).parent.parent

sys.path.append(str(root))

from src.plugins.github import config
from src.plugins.github.utils import get_oauth_github
from src.plugins.github.helpers import ISSUE_REGEX, FULLREPO_REGEX
from src.plugins.github.libs.renderer.render import issue_to_html, pr_diff_to_html

parser = ArgumentParser()
sub_parser = parser.add_subparsers(required=True)


async def gen_issue_html(issue: str, output_file: Optional[str] = None):
    m = re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", issue)
    if not m:
        print("Invalid issue format, should be: <owner>/<repo>#<issue>")
        return

    owner, repo, issue_number = m.groups()
    resp = await get_oauth_github().rest.issues.async_get(
        owner, repo, int(issue_number)
    )
    html = await issue_to_html(resp.parsed_data, config.github_theme)
    if not output_file:
        print(html)
        return
    Path(output_file).write_text(html)


issue = sub_parser.add_parser("issue")
issue.set_defaults(func=gen_issue_html)
issue.add_argument("issue", help="issue to render (owner/repo#issue)")
issue.add_argument("-o", "--output-file", required=False, help="output file path")


async def gen_diff_html(pr: str, output_file: Optional[str] = None):
    m = re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", pr)
    if not m:
        print("Invalid pr format, should be: <owner>/<repo>#<issue>")
        return

    owner, repo, issue_number = m.groups()
    resp = await get_oauth_github().rest.issues.async_get(
        owner, repo, int(issue_number)
    )
    issue = resp.parsed_data
    if not issue.pull_request:
        print("Not a pull request")
    html = await pr_diff_to_html(issue, config.github_theme)
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
