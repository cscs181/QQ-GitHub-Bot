FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

WORKDIR /app

ENV TZ Asia/Shanghai
ENV DEBIAN_FRONTEND noninteractive

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

ENV PYTHONPATH=/app

EXPOSE 8086

ENV MAX_WORKERS 1
ENV APP_MODULE bot:app

# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak &&\
#   echo "deb http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list

RUN apt-get update \
  && apt-get install -y fonts-noto \
  libnss3-dev libxss1 libasound2 libxrandr2 \
  libatk1.0-0 libgtk-3-0 libgbm-dev libxshmfence1

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN playwright install chromium

COPY ./bot.py ./src/ ./.env ./.env* /app/
