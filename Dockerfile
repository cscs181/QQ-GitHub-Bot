# syntax=docker/dockerfile:1

FROM python:3.11-bookworm AS requirements-stage

WORKDIR /tmp

ENV POETRY_HOME="/opt/poetry" PATH="${PATH}:/opt/poetry/bin"

RUN curl -sSL https://install.python-poetry.org | python - -y && \
  poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with deploy

FROM python:3.11-bookworm AS build-stage

WORKDIR /wheel

COPY --from=requirements-stage /tmp/requirements.txt /wheel/requirements.txt

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

RUN pip wheel --wheel-dir=/wheel --no-cache-dir --requirement /wheel/requirements.txt

FROM python:3.11-bookworm AS metadata-stage

WORKDIR /tmp

RUN --mount=type=bind,source=./.git/,target=/tmp/.git/ \
  git describe --tags --exact-match > /tmp/VERSION 2>/dev/null \
  || git rev-parse --short HEAD > /tmp/VERSION \
  && echo "Building version: $(cat /tmp/VERSION)"

FROM python:3.11-slim-bookworm

WORKDIR /app

ENV TZ=Asia/Shanghai DEBIAN_FRONTEND=noninteractive

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

ENV PYTHONPATH=/app

EXPOSE 8086

ENV APP_MODULE=bot:app

# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak &&\
#   echo "deb http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl p7zip-full fontconfig fonts-noto-color-emoji \
  && curl -sSL https://github.com/be5invis/Sarasa-Gothic/releases/download/v1.0.14/Sarasa-TTC-1.0.14.7z -o /tmp/sarasa.7z \
  && 7z x /tmp/sarasa.7z -o/tmp/sarasa \
  && install -d /usr/share/fonts/sarasa-gothic \
  && install -m644 /tmp/sarasa/*.ttc /usr/share/fonts/sarasa-gothic \
  && fc-cache -fv \
  && apt-get purge -y --auto-remove curl p7zip-full \
  && rm -rf /tmp/sarasa /tmp/sarasa.7z /var/lib/apt/lists/*

COPY --from=build-stage /wheel /wheel

RUN pip install --no-cache-dir --no-index --find-links=/wheel -r /wheel/requirements.txt && rm -rf /wheel

RUN playwright install --with-deps chromium \
  && rm -rf /var/lib/apt/lists/*

COPY --from=metadata-stage /tmp/VERSION /app/VERSION

COPY . /app/

CMD ["/start.sh"]
