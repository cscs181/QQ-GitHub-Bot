"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:09:04
@LastEditors    : yanyongyu
@LastEditTime   : 2024-08-04 14:05:47
@Description    : Jinjia globals for renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


def scale_linear(value: int, width: int, changed: int) -> int:
    """Scale linear calculation of the diff stat

    See https://github.com/git/git/blob/bcd6bc478adc4951d57ec597c44b12ee74bc88fb/diff.c#L2500-L2511.
    """
    return value and (1 + int(value * (width - 1) / changed))
