# 準備
```{shell}
$ docker-compose build
```

# 1. FastAPIのインストール
```{shell}
$ docker-compose run --entrypoint "poetry install --no-root" demo-app
```

# 2. APIの立ち上げ
```{shell}
$ docker-compose up
```
