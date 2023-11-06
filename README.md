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
# 参考
## [FastAPI入門](https://zenn.dev/sh0nk/books/537bb028709ab9)
基本はここに書かれているのでここを参照すると作業が捗る。
