"""
@Author         : yanyongyu
@Date           : 2021-03-25 15:20:47
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-27 14:13:59
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    "GitHub 消息快捷命令",
    "通过回复 GitHub 消息来快速进行 Issue、PR 相关操作",
    "/link: 获取 Issue/PR 链接\n"
    "/repo: 获取仓库链接\n"
    "/readme: 获取仓库 README\n"
    "/license: 获取仓库 LICENSE\n"
    "/release [tag]: 获取仓库最新或指定 Release\n"
    "/deployment: 获取仓库 Deployment 列表\n"
    "/star: star 仓库（仅仓库安装 APP 后有效）\n"
    "/unstar: unstar 仓库（仅仓库安装 APP 后有效）\n"
    "/content: 查看 Issue、PR 信息及事件\n"
    "/diff: 查看 PR diff\n"
    "/comment content: 评论 Issue/PR\n"
    '/label [label "label with space" ...]: 批量添加标签\n'
    "/unlabel label: 移除单个标签\n"
    "/close [reason]: 关闭 Issue/PR，可选 reason 有 completed、not_planned\n"
    "/reopen: 重新开启 Issue/PR\n"
    "/approve [content]: 批准 PR\n"
    "/merge [commit title]: Merge PR\n"
    "/squash [commit title]: Squash PR\n"
    "/rebase: Rebase PR",
)


from . import diff as diff
from . import link as link
from . import repo as repo
from . import star as star
from . import close as close
from . import label as label
from . import merge as merge
from . import readme as readme
from . import reopen as reopen
from . import unstar as unstar
from . import approve as approve
from . import comment as comment
from . import content as content
from . import license as license
from . import release as release
from . import unlabel as unlabel
from . import deployment as deployment
