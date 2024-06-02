"""
@Author         : yanyongyu
@Date           : 2024-06-02 16:44:42
@LastEditors    : yanyongyu
@LastEditTime   : 2024-06-02 16:48:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.providers.filehost import save_image

QQOFFICIAL_IMAGE_MAX_SIZE = 2 * 1024 * 1024


async def qqofficial_conditional_image(image: bytes) -> QQOfficialMS:
    """Get the QQ official image message segment depends on image size"""
    if len(image) > QQOFFICIAL_IMAGE_MAX_SIZE:
        return QQOfficialMS.image(await save_image(image))
    return QQOfficialMS.file_image(image)
