#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:18
@LastEditors    : yanyongyu
@LastEditTime   : 2020-11-23 22:15:27
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, List, Optional, Callable

from pydantic import Field, BaseSettings


class Config(BaseSettings):
    sentry_dsn: str
    sentry_debug: bool = False
    sentry_release: Optional[str] = None
    sentry_release: Optional[str] = None
    sentry_environment: Optional[str] = None
    sentry_server_name: Optional[str] = None
    sentry_sample_rate: float = 1.
    sentry_max_breadcrumbs: int = 100
    sentry_attach_stacktrace: bool = False
    sentry_send_default_pii: bool = False
    sentry_in_app_include: List[str] = Field(default_factory=lambda: [])
    sentry_in_app_exclude: List[str] = Field(default_factory=lambda: [])
    sentry_request_bodies: str = "medium"
    sentry_with_locals: bool = True
    sentry_ca_certs: Optional[str] = None
    sentry_before_send: Optional[Callable[[Any, Any], Optional[Any]]] = None
    sentry_before_breadcrumb: Optional[Callable[[Any, Any],
                                                Optional[Any]]] = None
    sentry_transport: Optional[Any] = None
    sentry_http_proxy: Optional[str] = None
    sentry_https_proxy: Optional[str] = None
    sentry_shutdown_timeout: int = 2

    class Config:
        extra = "ignore"
