# REEL Project Backend
## 目次
- [APIの仕様書](document.md)
- [概要](#概要)
- [環境構築](#環境構築)
  - [Dockerのインストール](#dockerのインストール)
  - [Gitリポジトリのクローン](#gitリポジトリのクローン)
  - [SSHの鍵の作成](#sshの鍵の作成)
    - [GitHubに公開鍵を登録](#githubに公開鍵を登録)
    - [configファイルの作成](#configファイルの作成)
    - [リポジトリのクローン](#リポジトリのクローン)
  - [必要ライブラリのインストール](#必要ライブラリのインストール)
- [コンテナの起動と操作](#コンテナの起動と操作)
  - [実行](#実行)
  - [データベースのマイグレーション](#データベースのマイグレーション)
  - [MySQLの操作](#mysqlの操作)
  - [APIのテスト](#apiのテスト)
- [参考](#参考)
## 概要
REELプロジェクトのバックエンドのリポジトリ。

## 環境構築
### Dockerのインストール
初めに[Docker Desktop](https://www.docker.com/products/docker-desktop/)のインストールを行う。  
Windowsの場合は追加で[wsl2](https://learn.microsoft.com/ja-jp/windows/wsl/install)のインストールが必要になる。
<details><summary>WSL2のインストール</summary>

```PowerShell
# 以下のコマンドでWSL2のインストールを行う
> wsl --install -d Ubuntu
# 以下のコマンドでUbuntuのバージョンを確認する
> wsl -l -v
```
ターミナル上でwslと入力するか、Ubuntuを直接起動するとUbuntuのターミナルが立ち上がる。Ubuntuのターミナルが起動すると初回起動時にユーザー名とパスワードの入力を求められるので入力する。  
以上でWSL2のインストールは完了する。
</details>

### Gitリポジトリのクローン
UbuntuもしくはMacのターミナル上で以下のコマンドを実行する。
```shell
$ git clone github:Ktomoya912/reel_back.git
```
<details><summary>失敗した場合</summary>
認証失敗のエラーが出た場合、SSHでクローンを行うようにする。
初めにSSHの鍵を作成する。

### SSHの鍵の作成

```shell
$ mkdir .ssh
$ cd .ssh
$ ssh-keygen -t rsa
```

```shell
Enter file in which to save the key (/home/ユーザー名/.ssh/id_rsa): github
Enter passphrase (empty for no passphrase): そのままEnter
Enter same passphrase again: そのままEnter
```

以上で鍵の作成が終了する。
続いて作成した鍵をGitHubに登録する。
#### GitHubに公開鍵を登録
windowsのwsl2上で行っている場合は以下のコマンドを実行する。

```shell
$ cat github.pub | clip.exe
```

macの場合は以下のコマンドを実行する。

```shell
$ cat github.pub | pbcopy
```

以上でクリップボードに公開鍵がコピーされるので、GitHubの[SSH and GPG keys](
    https://github.com/settings/keys)にアクセスし、New SSH keyをクリックする。
![New SSH key](./documents/SSHCONFIG.png)
titleは任意の名前を入力する。keyにはクリップボードにコピーした公開鍵を貼り付ける。
これでGitHubに公開鍵が登録される。

#### configファイルの作成
configファイルを作成することで、GitHubにSSHでアクセスする際に公開鍵を使用するようにする。

```shell
vi ~/.ssh/config
```
以下の内容を記述する。
```shell
Host github
  HostName github.com
  User git
  IdentityFile ~/.ssh/github
  Port 22
  # もし学内で優先接続を行う場合は以下の行を追加する
  ProxyCommand nc -X connect -x proxy.noc.kochi-tech.ac.jp:3128 %h %p
```

#### リポジトリのクローン

```shell
$ git clone github:Ktomoya912/reel_back.git
```

</details>

これでリポジトリがクローンされる。

続いてクローンしたリポジトリに移動し、Dockerイメージのビルドを行う。

```shell
$ cd reel_back
$ docker compose build
```

<details><summary>学内の有線の場合</summary>
Proxyの関係でビルドが失敗する場合がある。その場合は~/.bashrcに以下の内容を追記し、ターミナルを再起動する。

```shell
export http_proxy=http://proxy.noc.kochi-tech.ac.jp:3128
export https_proxy=http://proxy.noc.kochi-tech.ac.jp:3128
```
これで再度試してほしい。
</details>

### 必要ライブラリのインストール
このコマンドを実行することで、pyproject.tomlに記述されている必要なライブラリがインストールされる。
```shell
$ docker compose run --entrypoint "poetry install --no-root" demo-app
```

## コンテナの起動と操作
### 実行
以下のコマンドを実行することでAPIが立ち上がる。
実際にlocalhost:8000/docsにアクセスするとAPIのドキュメントが表示される。
```shell
$ docker compose up
```
この際に`ModuleNotFoundError`が出た場合には、コンテナを起動した状態で以下のコマンドを入力する。
```shell
$ docker compose exec demo-app poetry lock
$ docker compose exec demo-app poetry install --no-root
```
上記の内容を行い、`ERROR: Error loading ASGI app. Attribute "app" not found in module "api.main".`というエラーが出た場合はDockerのイメージを再ビルドする必要がある。そのため、Dockerのコンテナを終了し、以下のコマンドを入力する。
```shell
$ docker compose build --no-cache
```

### データベースのマイグレーション
コンテナが立ち上がった状態で以下のコマンドを実行することでデータベースのマイグレーションが行われる。
```shell
$ docker compose exec demo-app poetry run python -m api.migrate_db
```

マイグレーションを行った際に、`TypeError`などと出力された場合は`.env`ファイルに、
それぞれ必要となるデータを宣言する必要がある。

`.env`ファイルに記述された内容が環境変数に読み込まれる。
```python
os.getenv("SAMPLE")
```
上のような記述であれば、
```plain
SAMPLE="sample"
```
"sample"として読み取られる。
`.env`ファイルを保存するときに権限エラーが出ると思われるがその時は以下のコマンドを打つことによって解決することができる。
```bash
$ sudo chown -R [username]:[username] ./
```

### MySQLの操作
以下のコマンドを実行することでMySQLのコンテナに入ることができる。
```shell
$ docker compose exec db bash -c "mysql"
```

### APIのテスト
以下のコマンドを実行することでテストが実行される。
```shell
$ docker compose run --entrypoint "poetry run pytest" demo-app
```

## デプロイ
デプロイはAWSのEC2を使用して行う。
EC2上で、このリポジトリをクローンし、以下のコマンドを実行することでデプロイが行われる。
```shell
docker build -t reel-back:latest --platform linux/amd64 -f Dockerfile.cloud .
```
docker image が作成されたら、以下のコマンドを実行することでコンテナが立ち上がる。
```shell
docker run -d -p 8000:8000 --name reel-back reel-back:latest
```
ここでエラーが出る場合は、```.env```ファイルを作成していない、もしくは、必要になる環境変数が設定されていない可能性があるので、確認すること。

以上でデプロイは完了する。

## 参考
- [FastAPI入門](https://zenn.dev/sh0nk/books/537bb028709ab9)  
    基本はここに書かれているのでここを参照すると作業が捗る。
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/ja/tutorial/)  
    ちょっと難しいけど、ここに書かれていることを理解するとより深くFastAPIを使いこなせるようになる。
- [SQLAlchemyとFastAPIのリレーション](https://qiita.com/shimi7o/items/c009014b864c4412884a)  
    SQLAlchemyでのリレーションの書き方がわからない場合はここを参照すると良い。

## その他
### 詰まったこと
 ```fastapi.exceptions.ResponseValidationError: <exception str() failed>```というエラーが出た場合、モデルインスタンスを用いる前に(return objなど)
```python
await db.reflesh(obj)
```
を行うことで解決する。
