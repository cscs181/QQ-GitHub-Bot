<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2022-10-06 09:03:37
 * @Description    : README
 * @GitHub         : https://github.com/yanyongyu
-->

# QQ-GitHub-Bot

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![NoneBot Version](https://img.shields.io/badge/nonebot-2+-red.svg)

![CQHTTP Version](https://img.shields.io/badge/CQHTTP%2011-Bot+-black.svg?style=social)

GitHub Bot for QQ

## 简介

在 QQ 内 **订阅**, **查看**, **处理** GitHub Issue and Pull Request 。

## 配置

配置项参考 [.env 文件](./.env)，部分选项为可选。

在项目目录下创建 `.env.prod` 文件以覆盖默认 `.env` 配置，配置项留空将会从环境变量寻找。

## 独立部署

1. 下载 [`docker-compose.yml`](./docker-compose.yml), [`.env`](./.env) 配置文件以及 [`bot`](./bot) 目录至任意空目录
2. 修改 `.env` 中的如下配置项：

   ```dotenv
   HOST=0.0.0.0
   PORT=8086
   SUPERUSERS=["机器人管理号"]

   # postgres 数据库配置项
   POSTGRES_USER=bot
   POSTGRES_PASSWORD=postgres_password
   POSTGRES_DB=bot

   # redis 数据库配置项
   REDIS_PASSWORD=redis_password

   # Sentry DSN 网址，如果不使用可以不修改
   SENTRY_DSN=https://xxxxxxxx.sentry.io/123123

   # Github App 配置
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

3. 修改 `bot/config.yml` 配置文件，参考 [go-cqhttp](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF) 修改帐号、密码配置项。如需修改连接配置，请保证与 `.env` 中的配置项一致。
4. 启动

   安装 `docker` 以及 `docker-compose` 并在目录下执行 `docker compose up -d` (`docker-compose up -d`) 即可。
