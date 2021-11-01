FROM python:3.8 as requirements-stage

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -o install-poetry.py

RUN python install-poetry.py --yes

ENV PATH="${PATH}:/root/.local/bin"

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8
ENV TZ Asia/Shanghai
ENV DEBIAN_FRONTEND noninteractive

ENV MAX_WORKERS 1
ENV APP_MODULE bot:app
# ENV XVFB_INSTALLED true

# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak &&\
#   echo "deb http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list\
#   && apt-get update && apt-get install -y locales locales-all fonts-noto

RUN apt-get update && apt-get install -y locales locales-all fonts-noto

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN echo "Install playwright headless browser..." \
  && playwright install chromium \
  && apt-get install -y libnss3-dev libxss1 libasound2 libxrandr2\
  libatk1.0-0 libgtk-3-0 libgbm-dev libxshmfence1

# RUN echo "Install wkhtmltox renderer..." \
#   && chmod +x ./scripts/download_wkhtmltox.sh \
#   && ./scripts/download_wkhtmltox.sh buster_amd64 \
#   && apt-get install -y xvfb ./wkhtmltox_*.deb\
#   && rm wkhtmltox_*.deb

COPY ./ /app/
