import re
import sys
import asyncio
from pathlib import Path
from argparse import ArgumentParser
from typing import Literal, Optional

from nonebot.log import logger
from nonebot import get_adapter
from nonebot.adapters.github import Adapter

logger.remove()
root = Path(__file__).parent.parent

sys.path.append(str(root))

import bot
from src.plugins.github import config
from src.plugins.github.utils import get_oauth_github
from src.plugins.github.libs.renderer.render import issue_to_html
from src.plugins.github.helpers import ISSUE_REGEX, FULLREPO_REGEX

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


async def main():
    adapter = get_adapter(Adapter)
    await adapter._startup()
    result = parser.parse_args()
    result = vars(result)
    command = result.pop("func")
    await command(**result)


if __name__ == "__main__":
    asyncio.run(main())
