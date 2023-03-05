<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2023-03-05 11:35:27
 * @Description    : README
 * @GitHub         : https://github.com/yanyongyu
-->

# QQ-GitHub-Bot

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
[![NoneBot Version](https://img.shields.io/badge/nonebot-2+-red.svg)](https://v2.nonebot.dev/)
[![Release](https://github.com/cscs181/QQ-GitHub-Bot/actions/workflows/release.yml/badge.svg?branch=master)](https://hub.docker.com/r/cscs181/qq-github-bot)

![CQHTTP Version](https://img.shields.io/badge/CQHTTP%2011-Bot-black.svg?style=social)

GitHub Bot for QQ

## 简介

在 QQ 内 **订阅**, **查看**, **处理** GitHub Issue and Pull Request 。

## 功能简介

主要功能有 (持续更新中)：

|                   功能                   |                          描述                           |
| :--------------------------------------: | :-----------------------------------------------------: |
|           `/状态` 或 `/status`           |  获取当前机器人及所在服务器运行状态，支持分布式多节点   |
|        `/install [check\|revoke]`        | 安装 GitHub APP 集成（将用于 Issue/PR, WebHook 等管理） |
|         `/auth [check\|revoke]`          |               授权 APP 以进行用户快捷操作               |
|           `/bind [owner/repo]`           |            群绑定指定仓库以进行仓库快捷操作             |
|  `/subscribe owner/repo event[/action]`  |        订阅指定仓库的指定事件（支持多事件订阅）         |
|   `owner/repo[#number]` 或 GitHub 链接   |            快捷查看仓库 Issue/PR, PR diff 等            |
|            `/star`, `/unstar`            |                        快捷 star                        |
|                 `/diff`                  |                      查看 PR diff                       |
|                `/comment`                |                      评论 Issue/PR                      |
|       `/close [reason]`, `/reopen`       |                    关闭或重新开启 PR                    |
|           `/approve [message]`           |                         批准 PR                         |
| `/label [label ...]`, `/unlabel [label]` |                      添加删除标签                       |
|                  sentry                  |                   日志监控，上报错误                    |
|               health check               |           访问路由地址 `/health` 即可进行自检           |

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
   3. 权限为 `Issues (Read and Write)`, `Pull requests (Read and Write)`, `Metadata (Read Only)`, `Content (Read Only)` 和 `Starring (Read and Write)`
   4. Webhook 事件参考 [事件订阅](#事件订阅) 自行选择需要的事件
   5. 取消勾选 `Expire user authorization tokens` 或在 app optional feature 中 `opt-out`
   6. 勾选 `Request user authorization (OAuth) during installation`
   7. 记录 `app_id`, `client_id`，生成并下载 `private_key`, `client_secret` 备用
3. 下载 [`docker-compose.yml`](./docker-compose.yml) 以及 [`bot`](./bot) 目录至任意空目录
4. 在 `docker-compose.yml` 同目录下创建 `.env` 并写入如下配置项：

   ```dotenv
   # 可选，参考 nonebot superuser 格式
   SUPERUSERS=["机器人管理号"]

   # onebot
   # 可选
   ONEBOT_ACCESS_TOKEN=your_access_token
   # 可选
   ONEBOT_SECRET=your_secret
   # 修改此处的 QQ 号
   ONEBOT_API_ROOTS={"你的QQ号": "http://go-cqhttp:15700/"}

   # 必填，postgres 数据库配置项
   POSTGRES_USER=bot
   POSTGRES_PASSWORD=postgres_password
   POSTGRES_DB=bot

   # 必填，redis 数据库配置项
   REDIS_PASSWORD=redis_password

   # 可选，Sentry DSN 网址
   SENTRY_DSN=https://xxxxxxxx.sentry.io/123123

   # Github App 配置
   # 可选，图片主题，light/dark
   GITHUB_THEME=light
   # 必填，github app 配置
   # 可选，oauth app 配置，用于没有权限时的 fallback
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

5. 修改 `bot/config.yml` 配置文件，参考 [go-cqhttp](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF) 修改 `uin`, `password`, `access-token`, `secret` 配置项。如需修改连接配置，请保证与 `.env` 中的配置项一致。
6. 启动

   在目录下执行 `docker compose up -d` (旧版方式 `docker-compose up -d`) 即可。

### Kubernetes

~~待完善，可自行尝试使用 `k8s/bot/` 目录下的 helm chart~~

## 开发

使用 Codespaces (Dev Container) 一键配置开发环境 (Python、Redis、Postgres)：

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=master&repo=294357266)

修改 `.env.dev` 文件中的部分配置项，然后执行 `python bot.py` 即可。

如需连接到 Redis 或 Postgres 数据库调试，请确保 VSCode 已正确映射端口 (必要时可以重新映射 6379、5432 端口)，使用本地工具远程连接即可。
