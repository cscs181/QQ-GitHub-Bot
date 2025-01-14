<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2024-05-31 15:44:56
 * @Description    : README
 * @GitHub         : https://github.com/yanyongyu
-->

<!-- markdownlint-disable MD033 MD041 -->

<p align="center">
  <a href="https://github.com/cscs181/QQ-GitHub-Bot"><img src="https://github.com/cscs181/QQ-GitHub-Bot/raw/master/assets/logo.svg" width="150" height="150" alt="qq-github-bot"></a>
</p>

<div align="center">

# QQ-GitHub-Bot

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_✨ GitHub Bot for QQ ✨_
<!-- prettier-ignore-end -->

</div>

<p align="center">

[![Docker Hub](https://img.shields.io/docker/v/cscs181/qq-github-bot/latest?logo=docker)](https://hub.docker.com/r/cscs181/qq-github-bot)
[![LICENSE](https://img.shields.io/github/license/cscs181/QQ-GitHub-Bot)](https://github.com/cscs181/QQ-GitHub-Bot/blob/master/LICENSE)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg?logo=python&logoColor=edb641)
[![NoneBot Version](https://img.shields.io/badge/nonebot-2+-red.svg)](https://nonebot.dev/)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&logoColor=edb641)
![Pyright](https://img.shields.io/badge/types-pyright-797952.svg?logo=python&logoColor=edb641)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)

[![Release](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/release.yml/badge.svg?branch=master)](https://hub.docker.com/r/cscs181/qq-github-bot)
[![Pre-Commit](https://results.pre-commit.ci/badge/github/cscs181/QQ-GitHub-Bot/master.svg)](https://results.pre-commit.ci/latest/github/cscs181/QQ-GitHub-Bot/master)
[![Pyright](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/pyright.yml/badge.svg?branch=master&event=push)](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/pyright.yml)
[![Ruff](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/ruff.yml/badge.svg?branch=master&event=push)](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/ruff.yml)

![OneBot V11](https://img.shields.io/badge/OneBot-v11-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==)
![QQ](https://img.shields.io/badge/QQ-Bot-lightgrey?style=social&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMTIuODIgMTMwLjg5Ij48ZyBkYXRhLW5hbWU9IuWbvuWxgiAyIj48ZyBkYXRhLW5hbWU9IuWbvuWxgiAxIj48cGF0aCBkPSJNNTUuNjMgMTMwLjhjLTcgMC0xMy45LjA4LTIwLjg2IDAtMTkuMTUtLjI1LTMxLjcxLTExLjQtMzQuMjItMzAuMy00LjA3LTMwLjY2IDE0LjkzLTU5LjIgNDQuODMtNjYuNjQgMi0uNTEgNS4yMS0uMzEgNS4yMS0xLjYzIDAtMi4xMy4xNC0yLjEzLjE0LTUuNTcgMC0uODktMS4zLTEuNDYtMi4yMi0yLjMxLTYuNzMtNi4yMy03LjY3LTEzLjQxLTEtMjAuMTggNS40LTUuNTIgMTEuODctNS40IDE3LjgtLjU5IDYuNDkgNS4yNiA2LjMxIDEzLjA4LS44NiAyMS0uNjguNzQtMS43OCAxLjYtMS43OCAyLjY3djQuMjFjMCAxLjM1IDIuMiAxLjYyIDQuNzkgMi4zNSAzMS4wOSA4LjY1IDQ4LjE3IDM0LjEzIDQ1IDY2LjM3LTEuNzYgMTguMTUtMTQuNTYgMzAuMjMtMzIuNyAzMC42My04LjAyLjE5LTE2LjA3LS4wMS0yNC4xMy0uMDF6IiBmaWxsPSIjMDI5OWZlIi8+PHBhdGggZD0iTTMxLjQ2IDExOC4zOGMtMTAuNS0uNjktMTYuOC02Ljg2LTE4LjM4LTE3LjI3LTMtMTkuNDIgMi43OC0zNS44NiAxOC40Ni00Ny44MyAxNC4xNi0xMC44IDI5Ljg3LTEyIDQ1LjM4LTMuMTkgMTcuMjUgOS44NCAyNC41OSAyNS44MSAyNCA0NS4yOS0uNDkgMTUuOS04LjQyIDIzLjE0LTI0LjM4IDIzLjUtNi41OS4xNC0xMy4xOSAwLTE5Ljc5IDAiIGZpbGw9IiNmZWZlZmUiLz48cGF0aCBkPSJNNDYuMDUgNzkuNThjLjA5IDUgLjIzIDkuODItNyA5Ljc3LTcuODItLjA2LTYuMS01LjY5LTYuMjQtMTAuMTktLjE1LTQuODItLjczLTEwIDYuNzMtOS44NHM2LjM3IDUuNTUgNi41MSAxMC4yNnoiIGZpbGw9IiMxMDlmZmUiLz48cGF0aCBkPSJNODAuMjcgNzkuMjdjLS41MyAzLjkxIDEuNzUgOS42NC01Ljg4IDEwLTcuNDcuMzctNi44MS00LjgyLTYuNjEtOS41LjItNC4zMi0xLjgzLTEwIDUuNzgtMTAuNDJzNi41OSA0Ljg5IDYuNzEgOS45MnoiIGZpbGw9IiMwODljZmUiLz48L2c+PC9nPjwvc3ZnPg==)

</p>

## 简介

在 QQ 内 **订阅**, **查看**, **处理** GitHub Issue and Pull Request 。

## 功能简介

主要功能有 (持续更新中)：

|                       功能                       |                          描述                           |
| :----------------------------------------------: | :-----------------------------------------------------: |
|               `/状态` 或 `/status`               |  获取当前机器人及所在服务器运行状态，支持分布式多节点   |
|            `/install [check\|revoke]`            | 安装 GitHub APP 集成（将用于 Issue/PR, WebHook 等管理） |
|             `/auth [check\|revoke]`              |               授权 APP 以进行用户快捷操作               |
|               `/bind [owner/repo]`               |            群绑定指定仓库以进行仓库快捷操作             |
|      `/subscribe owner/repo event[/action]`      |        订阅指定仓库的指定事件（支持多事件订阅）         |
|        `/search [code\|repo\|user] query`        |              搜索 GitHub 代码、仓库、用户               |
|                 `/contribution`                  |                  获取最近一年的贡献图                   |
|       `owner/repo[#number]` 或 GitHub 链接       |            快捷查看仓库 Issue/PR, PR diff 等            |
|                 `/link`, `/repo`                 |                 获取 Issue/PR、仓库链接                 |
|                    `/readme`                     |                     查看仓库 README                     |
|                    `/license`                    |                     获取仓库许可证                      |
|                 `/release [tag]`                 |       获取仓库最新 Release，或指定 tag 的 Release       |
|                  `/deployment`                   |                获取仓库 Deployment 列表                 |
|                `/star`, `/unstar`                |                        快捷 star                        |
|                     `/diff`                      |                      查看 PR diff                       |
|                    `/comment`                    |                      评论 Issue/PR                      |
|     `/label [label ...]`, `/unlabel [label]`     |                      添加删除标签                       |
|           `/close [reason]`, `/reopen`           |                    关闭或重新开启 PR                    |
|               `/approve [message]`               |                         批准 PR                         |
| `/merge [commit]`, `/squash [commit]`, `/rebase` |                         合并 PR                         |
|                      sentry                      |                   日志监控，上报错误                    |
|                   health check                   |       访问路由地址 `/health` 即可进行服务状态自检       |

### 事件订阅

支持的事件根据 GitHub APP 配置的 Webhook 事件列表而定，可以自行选择和更改，推荐选择的事件有：

|      事件类型       |               事件描述                |
| :-----------------: | :-----------------------------------: |
|       Issues        | 任何开启、关闭、修改等 Issue 相关操作 |
|    Issue Comment    |   创建、修改、删除 Issue/PR 的评论    |
|    Pull Request     |  任何开启、关闭、修改等 PR 相关操作   |
| Pull Request Review |          PR Review 相关操作           |
|        Star         |           star、unstar 仓库           |
|        Push         |          push commit 到仓库           |
|       Release       |  创建、修改、发布等 Release 相关操作  |

## 部署

> [!WARNING]
> 请注意，[go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的部署方式已不再提供说明，请自行配置连接。
> 如果使用 docker 部署，可以参考使用 `docker compose --profile go-cqhttp up -d` 命令启动。

### Docker

1. 部署要求

   - Docker & Docker Compose

     ```bash
     curl -sSL https://get.docker.com/ | sh
     ```

   - 1+ CPU Core
   - 1+ GB RAM
   - 能够访问 GitHub API 的网络环境

   对于内存大小的限制，可以通过修改 `docker-compose.yml` 中的 `deploy.resources.limits.memory` 来调整，由于采用了 playwright(chromium) 渲染图片，不限制内存可能会导致渲染大图时直接卡死服务器。

2. 注册 GitHub App
   配置 GitHub App：
   1. callback URL 为 `http://<your-domain>/github/auth`
   2. webhook URL 为 `http://<your-domain>/github/webhooks/<app_id>`，可在 app 创建完成后添加
   3. 权限为 `Contents (Read Only)`, `Deployments (Read Only)`, `Issues (Read and Write)`, `Pull requests (Read and Write)`, `Metadata (Read Only)` 和 `Starring (Read and Write)`
   4. Webhook 事件参考 [事件订阅](#事件订阅) 自行选择需要的事件
   5. 取消勾选 `Expire user authorization tokens` 或在 app optional feature 中 `opt-out`
   6. 勾选 `Request user authorization (OAuth) during installation`
   7. 记录 `app_id`, `client_id`，生成并下载 `private_key`, `client_secret` 备用
3. 下载 [`docker-compose.yml`](./docker-compose.yml) 至任意空目录
4. 在 `docker-compose.yml` 同目录下创建 `.env` 并写入如下配置项：

   ```dotenv
   # 可选，参考 nonebot superuser 格式
   SUPERUSERS=["机器人管理号"]

   # 必填，可以访问到机器人的公网地址，用于上传图片
   FILEHOST_URL_BASE=https://<your-domain>

   # onebot
   # 可选
   ONEBOT_ACCESS_TOKEN=your_access_token
   # 可选
   ONEBOT_SECRET=your_secret

   # 可选，QQ 机器人配置项
   QQ_BOTS='
   [
     {
       "id": "xxx",
       "token": "xxx",
       "secret": "xxx",
       "intent": {
         "at_messages": false,
         "guild_messages": true,
         "direct_message": true
       }
     }
   ]
   '

   # 必填，postgres 数据库配置项
   # 如果使用 docker compose / helm 部署则无需修改
   POSTGRES_USER=bot
   POSTGRES_PASSWORD=postgres_password
   POSTGRES_DB=bot

   # 必填，redis 数据库配置项
   # 如果使用 docker compose / helm 部署则无需修改
   REDIS_PASSWORD=redis_password

   # 可选，Sentry DSN 网址
   SENTRY_DSN=https://xxxxxxxx.sentry.io/123123

   # Github App 配置
   # 可选，图片主题，light/dark
   GITHUB_THEME=light
   # 必填，github app 配置
   # 可选，oauth app 配置，用于没有权限时的 fallback
   # private_key 是从 github app 配置中下载的私钥
   # 私钥开头结尾应与示例一致，注意每行需要引号与逗号，结尾不应有逗号
   # webhook_secret 与 github app 配置中的 webhook secret 保持一致，如果没有设置则删除
   GITHUB_APPS='
   [
     {
       "app_id": "",
       "private_key": [
         "-----BEGIN RSA PRIVATE KEY-----",
         "~~ YOUR PRIVATE KEY HERE ~~",
         "-----END RSA PRIVATE KEY-----"
       ],
       "client_id": "",
       "client_secret": "",
       "webhook_secret": ""
     },
     {
       "client_id": "",
       "client_secret": ""
     }
   ]
   '
   ```

   > `docker-compose.yml` 中的配置视情况修改，**如无必要请勿修改！**

5. 启动

   在目录下执行 `docker compose up -d` (旧版方式 `docker-compose up -d`) 即可。

### Kubernetes

~~待完善，可自行尝试使用 `k8s/bot/` 目录下的 helm chart~~

下载或克隆 `k8s/bot/` 目录，新建文件 `values.yaml`，参考目录下的 `values.yaml` 填写覆盖配置项，然后执行 `helm install -n <botnamespace> --create-namespace -f values.yaml <botname> ./k8s/bot` 即可。其中 `<botnamespace>` 为命名空间，`<botname>` 为部署应用名称，请自行修改。

## 开发

使用 Codespaces (Dev Container) 一键配置开发环境 (Python、Redis、Postgres)：

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=master&repo=294357266)

修改 `.env.dev` 文件中的部分配置项，然后执行 `python bot.py` 即可。

如需连接到 Redis 或 Postgres 数据库调试，请确保 VSCode 已正确映射端口 (必要时可以重新映射 6379、5432 端口)，使用本地工具远程连接即可。
