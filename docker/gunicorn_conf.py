import os
import json
import multiprocessing

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_bind = bind_env or f"{host}:{port}"

use_loglevel = os.getenv("LOG_LEVEL", "info")
accesslog_var = os.getenv("ACCESS_LOG", "-")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("ERROR_LOG", "-")
use_errorlog = errorlog_var or None

cores = multiprocessing.cpu_count()
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
max_workers_str = os.getenv("MAX_WORKERS")
use_max_workers = int(max_workers_str) if max_workers_str else None
if web_concurrency_str := os.getenv("WEB_CONCURRENCY", None):
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if use_max_workers:
        web_concurrency = min(web_concurrency, use_max_workers)

graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)
keyfile = os.getenv("KEYFILE", None)
certfile = os.getenv("CERTFILE", None)

logconfig_dict = {
    "root": {"level": "INFO", "handlers": ["default"]},
    "handlers": {"default": {"class": "nonebot.log.LoguruHandler"}},
    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": True,
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": True,
            "qualname": "gunicorn.access",
        },
    },
}

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "use_max_workers": use_max_workers,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
