<!--
 * @Author         : yanyongyu
 * @Date           : 2020-11-15 14:40:25
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2020-11-15 15:07:47
 * @Description    : None
 * @GitHub         : https://github.com/yanyongyu
-->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/nonebot2/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-status

_✨ NoneBot 服务器状态（CPU, Memory, Disk Usage）查看插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/cscs181/QQ-Github-Bot/master/LICENSE">
    <img src="https://img.shields.io/github/license/cscs181/QQ-Github-Bot.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-status">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-status.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 使用方式

- 发送 Command `状态`
- 向机器人发送戳一戳表情
- 双击机器人头像戳一戳

## 配置项

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可。

### server_status_cpu

- 类型: `bool`
- 默认: `True`
- 说明: 是否显示 CPU 占用百分比

### server_status_memory

- 类型: `bool`
- 默认: `True`
- 说明: 是否显示 Memory 占用百分比

### server_status_disk

- 类型: `bool`
- 默认: `True`
- 说明: 是否显示磁盘占用百分比
