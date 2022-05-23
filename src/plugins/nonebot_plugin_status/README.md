<!--
 * @Author         : yanyongyu
 * @Date           : 2020-11-15 14:40:25
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2022-05-23 05:58:29
 * @Description    : None
 * @GitHub         : https://github.com/yanyongyu
-->

<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
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

通用:

- 发送 Command `状态`

OneBot:

- 向机器人发送戳一戳表情
- 双击机器人头像戳一戳

## 配置项

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可。

### server_status_only_superusers

- 类型: `bool`
- 默认: `True`
- 说明: 是否仅允许超级用户使用

> 超级用户需在配置文件中如下配置:
>
> ```dotenv
> SUPERUSERS=["your qq id"]
> ```

### server_status_template

- 类型: `str`
- 默认: 请参考示例
- 说明：发送的消息模板，支持的变量以及类型如下：
  - cpu_usage (`float`): CPU 使用率
  - memory_usage (`float`): 内存使用率
  - disk_usage (`Dict[str, psutil._common.sdiskusage]`): 磁盘使用率，包含 total, used, free, percent 属性
  - uptime (`timedelta`): 服务器运行时间

配置文件示例（默认模板）

```dotenv
SERVER_STATUS_TEMPLATE="
CPU: {{ '%02d' % cpu_usage }}%
Memory: {{ '%02d' % memory_usage }}%
Disk:
{%- for name, usage in disk_usage.items() %}
  {{ name }}: {{ '%02d' % usage.percent }}%
{%- endfor %}
Uptime: {{ uptime }}
"
```
