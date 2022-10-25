<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2022-10-25 07:28:50
 * @Description    : README
 * @GitHub         : https://github.com/yanyongyu
-->

# QQ-GitHub-Bot

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![NoneBot Version](https://img.shields.io/badge/nonebot-2+-red.svg)

![CQHTTP Version](https://img.shields.io/badge/CQHTTP%2011-Bot-black.svg?style=social)

GitHub Bot for QQ

## 简介

在 QQ 内 **订阅**, **查看**, **处理** GitHub Issue and Pull Request 。

## 功能简介

主要功能有 (持续更新中)：

|                   功能                   |                          描述                           |
| :--------------------------------------: | :-----------------------------------------------------: |
|                 `/状态`                  |  获取当前机器人及所在服务器运行状态，支持分布式多节点   |
|        `/install [check\|revoke]`        | 安装 GitHub APP 集成（将用于 Issue/PR, WebHook 等管理） |
|         `/auth [check\|revoke]`          |               授权 APP 以进行用户快捷操作               |
|           `/bind [owner/repo]`           |            群绑定指定仓库以进行仓库快捷操作             |
|   `owner/repo[#number]` 或 GitHub 链接   |            快捷查看仓库 Issue/PR, PR diff 等            |
|            `/star`, `/unstar`            |                        快捷 star                        |
|                 `/diff`                  |                      查看 PR diff                       |
|       `/close [reason]`, `/reopen`       |                    关闭或重新开启 PR                    |
|           `/approve [message]`           |                         批准 PR                         |
| `/label [label ...]`, `/unlabel [label]` |                      添加删除标签                       |
|                  sentry                  |                   日志监控，上报错误                    |
|               health check               |           访问路由地址 `/health` 即可进行自检           |

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
   3. 权限为 `Issues (Read and Write)`, `Pull requests (Read and Write)`, `Metadata (Read Only)` 和 `Starring (Read and Write)`
   4. 取消勾选 `Expire user authorization tokens` 或在 app optional feature 中 `opt-out`
   5. 勾选 `Request user authorization (OAuth) during installation`
   6. 记录 `app_id`, `client_id`，生成并下载 `private_key`, `client_secret` 备用
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

配置项参考 [.env 文件](./.env)，部分选项为可选。在项目目录下创建 `.env.dev` 文件以覆盖默认 `.env` 配置，配置项留空将会从环境变量寻找。

启动项目：

```bash
python bot.py
```
