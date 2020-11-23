<!--
 * @Author         : yanyongyu
 * @Date           : 2020-11-23 20:23:12
 * @LastEditors    : yanyongyu
 * @LastEditTime   : 2020-11-23 22:15:54
 * @Description    : None
 * @GitHub         : https://github.com/yanyongyu
-->

<p align="center">
  <a href="https://v2.nonebot.dev/">
    <img src="https://raw.githubusercontent.com/nonebot/nonebot2/master/docs/.vuepress/public/logo.png" height="100" alt="nonebot">
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

配置项具体含义参考: [Sentry Docs](https://docs.sentry.io/platforms/python/configuration/options/)

- `sentry_dsn: str`
- `sentry_debug: bool = False`
- `sentry_release: Optional[str] = None`
- `sentry_release: Optional[str] = None`
- `sentry_environment: Optional[str] = nonebot env`
- `sentry_server_name: Optional[str] = None`
- `sentry_sample_rate: float = 1.`
- `sentry_max_breadcrumbs: int = 100`
- `sentry_attach_stacktrace: bool = False`
- `sentry_send_default_pii: bool = False`
- `sentry_in_app_include: List[str] = Field(default_factory=lambda: [])`
- `sentry_in_app_exclude: List[str] = Field(default_factory=lambda: [])`
- `sentry_request_bodies: str = "medium"`
- `sentry_with_locals: bool = True`
- `sentry_ca_certs: Optional[str] = None`
- `sentry_before_send: Optional[Callable[[Any, Any], Optional[Any]]] = None`
- `sentry_before_breadcrumb: Optional[Callable[[Any, Any], Optional[Any]]] = None`
- `sentry_transport: Optional[Any] = None`
- `sentry_http_proxy: Optional[str] = None`
- `sentry_https_proxy: Optional[str] = None`
- `sentry_shutdown_timeout: int = 2`
