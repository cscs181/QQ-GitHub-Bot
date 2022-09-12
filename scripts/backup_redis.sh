#!/usr/bin/env bash
###
# @Author         : yanyongyu
# @Date           : 2021-03-25 16:22:18
# @LastEditors    : yanyongyu
# @LastEditTime   : 2022-09-12 15:12:59
# @Description    : None
# @GitHub         : https://github.com/yanyongyu
###

docker run --rm --volumes-from bot_redis -v $(pwd):/backup busybox tar -cvf /backup/backup-$(date +"%s").tar -C /data/
