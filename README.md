<!--
 * @Author         : yanyongyu
 * @Date           : 2020-09-10 17:11:45
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2020-09-10 17:28:03
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

配置项参考 [.env 文件](./.env)

## 部署

部署 `QQ-GitHub-Bot` 前，需要先行部署 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 并配置连接。
配置连接的方法参考 `nonebot2` 文档: [配置协议端](https://v2.nonebot.dev/guide/cqhttp-guide.html#%E9%85%8D%E7%BD%AE-cqhttp-%E5%8D%8F%E8%AE%AE%E7%AB%AF-%E4%BB%A5-qq-%E4%B8%BA%E4%BE%8B)

1. 使用 `nb-cli`

   ```bash
   pip install nb-cli[deploy]
   nb build
   nb up
   ```

2. 使用 `docker-compose`

   ```bash
   docker-compose up -d
   ```
