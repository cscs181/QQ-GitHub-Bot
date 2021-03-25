#!/bin/bash
###
# @Author         : yanyongyu
# @Date           : 2021-03-25 16:22:18
# @LastEditors    : yanyongyu
# @LastEditTime   : 2021-03-25 16:42:58
# @Description    : None
# @GitHub         : https://github.com/yanyongyu
###

docker run --rm --volumes-from $(docker-compose config --volumes) -v $(pwd):/backup busybox tar cvf /backup/backup-$(date +"%s").tar /data
