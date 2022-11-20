#!/usr/bin/env bash
###
# @Author         : yanyongyu
# @Date           : 2022-11-20 03:46:14
# @LastEditors    : yanyongyu
# @LastEditTime   : 2022-11-20 04:01:23
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

POSTGRES_USER=bot
POSTGRES_PASSWORD=bot_postgres
POSTGRES_DB=bot

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
  }
]
'
EOF
