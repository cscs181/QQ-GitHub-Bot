<!--
 * @Author         : yanyongyu
 * @Date           : 2020-11-15 14:40:25
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2022-10-24 02:29:44
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

> **warning**
> GitHub 仓库中的文档为最新 DEV 版本，配置方式请参考 [PyPI](https://pypi.org/project/nonebot-plugin-status/) 上的文档。

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可。

### server_status_enabled

- 类型：`bool`
- 默认值：`True`
- 说明：是否启用服务器状态查看功能

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
- 说明：发送的消息模板，支持的方法、变量以及类型如下：
  - relative_time (`Callable[[datetime], timedelta]`): 获取相对时间
  - humanize_date (`Callable[[datetime], str]`): [人性化时间](https://python-humanize.readthedocs.io/en/latest/time/#humanize.time.naturaldate)
  - humanize_delta (`Callable[[timedelta], str]`): [人性化时间差](https://python-humanize.readthedocs.io/en/latest/time/#humanize.time.precisiondelta)
  - cpu_usage (`float`): CPU 使用率
  - per_cpu_usage (`List[float]`): 每个 CPU 核心的使用率
  - memory_usage (`svmem`): 内存使用情况，包含 total, available, percent, used, free(, active, inactive, buffers, cached, shared) 属性
  - swap_usage (`sswap`): 内存使用情况，包含 total, used, free, percent, sin, sout 属性
  - disk_usage (`Dict[str, psutil._common.sdiskusage]`): 磁盘使用率，包含 total, used, free, percent 属性
  - uptime (`datetime`): 服务器运行时间
  - runtime (`datetime`): NoneBot 运行时间
  - bot_connect_time (`Dict[str, datetime]`): 机器人连接时间

配置文件示例（默认模板）

```dotenv
SERVER_STATUS_TEMPLATE='
CPU: {{ "%02d" % cpu_usage }}%
Memory: {{ "%02d" % memory_usage.percent }}%
Runtime: {{ runtime | relative_time | humanize_delta }}
{% if swap_usage.total %}Swap: {{ "%02d" % swap_usage.percent }}%{% endif %}
Disk:
{% for name, usage in disk_usage.items() %}
  {{ name }}: {{ "%02d" % usage.percent }}%
{% endfor %}
'
```
