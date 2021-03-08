#!/bin/bash
###
# @Author         : yanyongyu
# @Date           : 2021-03-08 22:03:15
# @LastEditors    : yanyongyu
# @LastEditTime   : 2021-03-09 01:37:02
# @Description    : None
# @GitHub         : https://github.com/yanyongyu
###

if [ ! -n "$1" ]; then
    echo "No system version provided! Available versions:"
    curl -s https://wkhtmltopdf.org/downloads.html |
        grep -Eo "wkhtmltox.*\.(deb|pkg|exe|rpm)"
    exit 1
fi

curl -s https://wkhtmltopdf.org/downloads.html |
    grep -Eo -m 1 "https://github.com/wkhtmltopdf/packaging/releases/download/.*$1.(deb|pkg|exe|rpm)" |
    wget -i -
