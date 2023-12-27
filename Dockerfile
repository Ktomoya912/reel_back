FROM python:3.11-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /src
COPY . /src

RUN apk --update add \
    curl \
    gcc \
    musl-dev \
    linux-headers \
    build-base \
    libffi-dev \
    bash

# pipを使ってpoetryをインストール
RUN pip install --upgrade pip
RUN pip install poetry

# poetryの定義ファイルをコピー (存在する場合)
COPY pyproject.toml* poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# uvicornのサーバーを立ち上げる
ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:create_app", "--host", "0.0.0.0", "--reload"]
