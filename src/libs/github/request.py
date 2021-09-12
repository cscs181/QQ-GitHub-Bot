#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 17:34:53
@LastEditors    : yanyongyu
@LastEditTime   : 2021-06-15 22:14:45
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64
import urllib.parse
from typing import Any, Optional

import httpx


class Requester:
    def __init__(
        self,
        token_or_client_id: Optional[str],
        client_secret: Optional[str],
        base_url: str,
        timeout: int,
        user_agent: str,
        per_page: int,
        verify: bool,
    ):
        if client_secret:
            b64 = base64.b64encode(
                f"{token_or_client_id}:{client_secret}".encode()
            ).decode()
            self._authorization: str = f"Basic {b64}"
        elif token_or_client_id:
            self._authorization: str = f"token {token_or_client_id}"
        else:
            self._authorization: str = ""

        self._base_url = base_url
        self._timeout = timeout
        self._user_agent = user_agent
        self._per_page = per_page
        self._verify = verify

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            headers = {
                "User-Agent": self._user_agent,
                "Authorization": self._authorization,
                "Accept": "application/vnd.github.v3+json",
            }
            self._client = httpx.AsyncClient(
                headers=headers, verify=self._verify, timeout=self._timeout
            )
        return self._client

    async def request_json(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Any = None,
    ):
        return await self.request(method, url, params, headers, None, json)

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Any = None,
    ):
        url = urllib.parse.urljoin(self._base_url, url)
        response = await self.client.request(
            method, url, params=params, headers=headers, data=data, json=json
        )
        response.raise_for_status()
        return response

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
