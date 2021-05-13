#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 17:13:37
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-15 23:36:46
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing_extensions import Literal
from typing import List, Optional, overload

from .request import Requester
from .models import LazyRepository, Repository

DEFAULT_BASE_URL = "https://api.github.com"
DEFAULT_STATUS_URL = "https://status.github.com"
DEFAULT_TIMEOUT = 15
DEFAULT_PER_PAGE = 30


class Github:

    def __init__(self,
                 token_or_client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 base_url: str = DEFAULT_BASE_URL,
                 timeout: int = DEFAULT_TIMEOUT,
                 user_agent: str = "Python/GitHub",
                 per_page: int = DEFAULT_PER_PAGE,
                 verify: bool = True):
        self._requester = Requester(token_or_client_id, client_secret, base_url,
                                    timeout, user_agent, per_page, verify)

    async def close(self):
        return await self._requester.close()

    @overload
    async def get_repo(self, full_name: str,
                       lazy: Literal[True]) -> LazyRepository:
        ...

    @overload
    async def get_repo(self, full_name: str,
                       lazy: Literal[False]) -> Repository:
        ...

    async def get_repo(self,
                       full_name: str,
                       lazy: bool = False) -> LazyRepository:
        """
        GET /repos/:owner/:repo
        
        https://docs.github.com/en/rest/reference/repos#get-a-repository
        """
        url = f"/repos/{full_name}"
        if lazy:
            return LazyRepository(full_name=full_name,
                                  requester=self._requester)
        response = await self._requester.request_json("GET", url)
        return Repository.parse_obj({
            "requester": self._requester,
            **response.json()
        })

    async def render_markdown(self,
                              text: str,
                              context: Optional[Repository] = None):
        """
        POST /markdown
        
        https://docs.github.com/en/rest/reference/markdown#render-a-markdown-document
        """
        data = {"text": text}
        # TODO
        # if context:
        #     data["mode"] = "gfm"
        #     data["context"] = context._identity
        response = await self._requester.request_json("POST",
                                                      "/markdown",
                                                      json=data)
        return response.text

    # def get_repos(
    #         self,
    #         since: Optional[int] = None,
    #         visibility: Literal["all", "public", "private", None] = None,
    #         affiliation: Optional[List[Literal["owner", "collaborator",
    #                                            "organization_member"]]] = None,
    #         type: Optional[Literal["all", "owner", "public", "private",
    #                                "member"]] = None,
    #         sort: Optional[Literal["created", "updated", "pushed",
    #                                "full_name"]] = None,
    #         direction: Optional[Literal["asc", "desc"]] = None):
    #     """
    #     GET /user/repos

    #     https://docs.github.com/en/rest/reference/repos#list-repositories-for-the-authenticated-user
    #     """
    #     url_parameters = dict()
    #     if since is not None:
    #         url_parameters["since"] = since
    #     if visibility is not None:
    #         url_parameters["visibility"] = visibility
    #     if affiliation is not None:
    #         url_parameters["affiliation"] = ",".join(affiliation)
    #     if type is not None:
    #         url_parameters["type"] = type
    #     if sort is not None:
    #         url_parameters["sort"] = sort
    #     if direction is not None:
    #         url_parameters["direction"] = direction
    #     return github.PaginatedList.PaginatedList(
    #         github.Repository.Repository,
    #         self._requester,
    #         "/repositories",
    #         url_parameters,
    #     )

    # async def get_rate_limit(self):
    #     """
    #     GET /rate_limit

    #     https://docs.github.com/en/rest/reference/rate-limit#get-rate-limit-status-for-the-authenticated-user
    #     """
    #     response = await self._requester.request_json("GET", "/rate_limit")
    #     return RateLimit.RateLimit(self._requester, headers, data["resources"],
    #                                True)

    # async def get_license(self, key: str):
    #     """
    #     GET /license/:license

    #     https://docs.github.com/en/rest/reference/licenses#get-a-license
    #     """
    #     response = await self._requester.request_json("GET", f"/licenses/{key}")
    #     return License.License(self._requester, headers, data, completed=True)

    # def get_licenses(self):
    #     """
    #     GET /licenses

    #     https://docs.github.com/en/rest/reference/licenses#get-all-commonly-used-licenses
    #     """
    #     url_parameters = dict()
    #     return github.PaginatedList.PaginatedList(github.License.License,
    #                                               self._requester, "/licenses",
    #                                               url_parameters)

    # def get_events(self):
    #     """
    #     GET /events

    #     https://docs.github.com/en/rest/reference/activity#list-public-events
    #     """
    #     return github.PaginatedList.PaginatedList(github.Event.Event,
    #                                               self._requester, "/events",
    #                                               None)

    # def get_user(self, username: Optional[str] = None):
    #     """
    #     GET /users/:user

    #     https://docs.github.com/en/rest/reference/users#get-a-user

    #     GET /user
    #     https://docs.github.com/en/rest/reference/users#get-the-authenticated-user
    #     """
    #     if not username:
    #         return AuthenticatedUser.AuthenticatedUser(self._requester, {},
    #                                                    {"url": "/user"},
    #                                                    completed=False)
    #     else:
    #         headers, data = self._requester.request_json(
    #             "GET", f"/users/{username}")
    #         return github.NamedUser.NamedUser(self._requester,
    #                                           headers,
    #                                           data,
    #                                           completed=True)

    # def get_users(self, since: Optional[int] = None):
    #     """
    #     GET /users

    #     https://docs.github.com/en/rest/reference/users#list-users
    #     """
    #     url_parameters = dict()
    #     if since is not None:
    #         url_parameters["since"] = since
    #     return github.PaginatedList.PaginatedList(github.NamedUser.NamedUser,
    #                                               self._requester, "/users",
    #                                               url_parameters)

    # def get_organization(self, org):
    #     """
    #     GET /orgs/:org

    #     https://docs.github.com/en/rest/reference/orgs#get-an-organization
    #     """
    #     headers, data = self._requester.request_json("GET", f"/orgs/{org}")
    #     return github.Organization.Organization(self._requester,
    #                                             headers,
    #                                             data,
    #                                             completed=True)

    # def get_organizations(self, since: Optional[int] = None):
    #     """
    #     GET /organizations

    #     https://docs.github.com/en/rest/reference/orgs#list-organizations
    #     """
    #     url_parameters = dict()
    #     if since is not None:
    #         url_parameters["since"] = since
    #     return github.PaginatedList.PaginatedList(
    #         github.Organization.Organization,
    #         self._requester,
    #         "/organizations",
    #         url_parameters,
    #     )

    # def get_project(self, id: int):
    #     """
    #     GET /projects/:project_id

    #     https://docs.github.com/en/rest/reference/projects#get-a-project
    #     """
    #     headers, data = self._requester.request_json(
    #         "GET",
    #         f"/projects/{id}",
    #         headers={"Accept": Consts.mediaTypeProjectsPreview},
    #     )
    #     return github.Project.Project(self._requester,
    #                                   headers,
    #                                   data,
    #                                   completed=True)

    # def get_project_column(self, id):
    #     """
    #     GET /projects/columns/:column_id

    #     https://docs.github.com/en/rest/reference/projects#get-a-project-column
    #     """
    #     headers, data = self._requester.request_json(
    #         "GET",
    #         "/projects/columns/%d" % id,
    #         headers={"Accept": Consts.mediaTypeProjectsPreview},
    #     )
    #     return github.ProjectColumn.ProjectColumn(self._requester,
    #                                               headers,
    #                                               data,
    #                                               completed=True)

    # def get_gist(self, id: str):
    #     """
    #     GET /gists/:id

    #     https://docs.github.com/en/rest/reference/gists#get-a-gist
    #     """
    #     headers, data = self._requester.request_json("GET", f"/gists/{id}")
    #     return github.Gist.Gist(self._requester, headers, data, completed=True)

    # def get_gists(self, since: Optional[datetime.datetime] = None):
    #     """
    #     GET /gists/public

    #     https://docs.github.com/en/rest/reference/gists#list-public-gists
    #     """
    #     url_parameters = dict()
    #     if since:
    #         url_parameters["since"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    #     return github.PaginatedList.PaginatedList(github.Gist.Gist,
    #                                               self._requester,
    #                                               "/gists/public",
    #                                               url_parameters)

    # def get_emojis(self):
    #     """
    #     GET /emojis

    #     https://docs.github.com/en/rest/reference/emojis#get-emojis
    #     """
    #     headers, attributes = self._requester.request_json("GET", "/emojis")
    #     return attributes
