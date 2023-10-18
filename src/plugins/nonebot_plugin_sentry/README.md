<!--
 * @Author         : yanyongyu
 * @Date           : 2020-11-23 20:23:12
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2023-10-18 10:29:34
 * @Description    : None
 * @GitHub         : https://github.com/yanyongyu
-->

<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://nonebot.dev/">
    <img src="https://nonebot.dev/logo.png" height="100" alt="nonebot">
  </a>
  <a href="https://sentry.io">
    <img src="https://sentry-brand.storage.googleapis.com/sentry-logo-black.png" height="100" alt="sentry">
  </a>
</p>

<div align="center">

# nonebot-plugin-sentry

_✨ 在 Sentry.io 上进行 NoneBot 服务日志查看、错误处理 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/cscs181/QQ-Github-Bot/master/LICENSE">
    <img src="https://img.shields.io/github/license/cscs181/QQ-Github-Bot.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-sentry">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-sentry.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 使用方式

填写必须配置项 `SENTRY_DSN` ，即刻开始 sentry 之旅！

## 配置项

配置项需要添加前缀 `SENTRY_`，所有参数以及具体含义参考: [Sentry Docs](https://docs.sentry.io/platforms/python/configuration/options/)

所有以 `SENTRY_` 开头的配置项将会被自动读取。
