FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8
ENV TZ Asia/Shanghai
ENV DEBIAN_FRONTEND noninteractive

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak &&\
  echo "deb http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list\
  && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list\
  && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list\
  && apt-get update && apt-get install -y locales locales-all fonts-noto

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

RUN python3 -m pip install poetry && poetry config virtualenvs.create false

COPY ./ /app/

RUN poetry export --without-hashes -f requirements.txt \
  | poetry run pip install -r /dev/stdin \
  && echo "Install playwright headless browser..." \
  && poetry run playwright install chromium \
  && apt-get install -y libnss3-dev libxss1 libasound2 libxrandr2\
  libatk1.0-0 libgtk-3-0 libgbm-dev\
  && poetry install --no-dev

RUN echo "Install wkhtmltox renderer..." \
  && chmod +x ./scripts/download_wkhtmltox.sh \
  && ./scripts/download_wkhtmltox.sh buster_amd64 \
  && apt-get install -y xvfb ./wkhtmltox_*.deb\
  && rm wkhtmltox_*.deb
