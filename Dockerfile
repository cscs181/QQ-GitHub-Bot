FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with deploy

FROM python:3.10-slim

WORKDIR /app

ENV TZ Asia/Shanghai
ENV DEBIAN_FRONTEND noninteractive

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

ENV PYTHONPATH=/app

EXPOSE 8086

ENV APP_MODULE bot:app

# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak &&\
#   echo "deb http://mirrors.aliyun.com/debian/ buster main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main" >> /etc/apt/sources.list\
#   && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main" >> /etc/apt/sources.list

RUN apt-get update \
  && apt-get install -y curl p7zip-full fontconfig fonts-noto-color-emoji \
  && curl -sSL https://github.com/be5invis/Sarasa-Gothic/releases/download/v0.37.4/sarasa-gothic-ttf-0.37.4.7z -o /tmp/sarasa.7z \
  && 7z x /tmp/sarasa.7z -o/tmp/sarasa \
  && install -d /usr/share/fonts/sarasa-gothic \
  && install -m644 /tmp/sarasa/sarasa-ui-*.ttf /usr/share/fonts/sarasa-gothic \
  && install -m644 /tmp/sarasa/sarasa-mono-*.ttf /usr/share/fonts/sarasa-gothic \
  && fc-cache -fv \
  && apt-get remove -y curl p7zip-full \
  && rm -rf /tmp/sarasa/ /tmp/sarasa.7z

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN playwright install --with-deps chromium

COPY . /app/

CMD ["/start.sh"]
