#!/usr/bin/env bash
###
# @Author         : yanyongyu
# @Date           : 2022-11-20 03:46:14
# @LastEditors    : yanyongyu
# @LastEditTime   : 2023-10-11 14:20:37
# @Description    : None
# @GitHub         : https://github.com/yanyongyu
###

poetry config virtualenvs.in-project true &&
  poetry install &&
  poetry run pre-commit install &&
  poetry run playwright install chromium

cat >.env.dev <<EOF
LOG_LEVEL=DEBUG

SUPERUSERS=[]

ONEBOT_API_ROOTS={}

POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=bot
POSTGRES_PASSWORD=bot_postgres
POSTGRES_DB=bot

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=bot_redis

# Github App 配置
GITHUB_THEME=light
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
  },
  {
    "client_id": "",
    "client_secret": ""
  }
]
'
EOF

poetry run python ./scripts/database.py upgrade
