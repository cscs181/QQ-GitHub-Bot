<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2022-01-13 16:07:58
 * @Description    : README
 * @GitHub         : https://github.com/yanyongyu
-->

# QQ-GitHub-Bot

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![NoneBot Version](https://img.shields.io/badge/nonebot-2+-red.svg)
![CQHTTP Version](https://img.shields.io/badge/cqhttp-11+-black.svg)

GitHub Bot for QQ

## 简介

在 QQ 内 **订阅**, **查看**, **处理** GitHub Issue and Pull Request 。

## 配置

配置项参考 [.env 文件](./.env)，部分选项为可选。

在项目目录下创建 `.env.prod` 文件以覆盖默认 `.env` 配置，配置项留空将会从环境变量寻找。

## 独立部署

独立部署 `QQ-GitHub-Bot` 前，需要先行部署 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 或其他 [OneBot V11 协议实现](https://11.onebot.dev/) 并配置连接。

配置连接的方法参考 `nonebot2` 文档: [配置协议端](https://v2.nonebot.dev/guide/cqhttp-guide.html#%E9%85%8D%E7%BD%AE-cqhttp-%E5%8D%8F%E8%AE%AE%E7%AB%AF-%E4%BB%A5-qq-%E4%B8%BA%E4%BE%8B)

1. 下载 [`docker-compose.yml`](./docker-compose.yml) 以及 [`.env`](./.env) 配置文件至任意空目录，修改 `.env` 中的如下配置项：

   ```dotenv
   HOST=0.0.0.0
   PORT=8080
   SUPERUSERS=["机器人管理号"]

   # Sentry DSN 网址，如果不使用可以留空
   SENTRY_DSN=

   # Github OAuth App 配置，留空将功能受限
   GITHUB_CLIENT_ID=
   GITHUB_CLIENT_SECRET=
   GITHUB_SELF_HOST=
   ```

   > `docker-compose.yml` 中的配置视情况修改，**如无必要请勿修改！**

2. 启动

   安装 `docker-compose` 并在目录下执行 `docker-compose up -d` 即可。
