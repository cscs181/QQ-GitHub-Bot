#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-26 15:31:35
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-26 16:46:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional
from datetime import datetime

from .user import User
from . import BaseModel


class Comment(BaseModel):
    id: int
    node_id: str
    url: str
    html_url: str
    body: str
    body_text: Optional[str]
    body_html: Optional[str]
    user: User
    created_at: datetime
    updated_at: datetime
    issue_url: str
    author_association: str
