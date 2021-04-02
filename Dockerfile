FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple

RUN python3 -m pip install poetry && poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export --without-hashes -f requirements.txt \
    | poetry run pip install -r /dev/stdin \
    && echo "Install playwright headless browser..." \
    && poetry run playwright install \
    && poetry install --no-dev

COPY ./scripts/download_wkhtmltox.sh /app/

RUN echo "deb http://mirrors.aliyun.com/debian/ buster main contrib non-free" >> /etc/apt/sources.list\
    && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list\
    && apt-get update

RUN echo "Install wkhtmltox renderer..." \
    && chmod +x ./download_wkhtmltox.sh \
    && ./download_wkhtmltox.sh buster_amd64 \
    && apt-get install -y xvfb ./wkhtmltox_*.deb\
    && rm wkhtmltox_*.deb download_wkhtmltox.sh
