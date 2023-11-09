# 準備
## Dockerのインストール
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

## Gitリポジトリのクローン
UbuntuもしくはMacのターミナル上で以下のコマンドを実行する。
```shell
$ git clone https://github.com/Ktomoya912/g-13-documents.git
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
### GitHubに公開鍵を登録
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

### configファイルの作成
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
  ProxyCommand ssh -q -W %h:%p
```
</details>

これでリポジトリがクローンされる。

```shell
$ docker-compose build
```

# 1. 必要ライブラリのインストール
```shell
$ docker-compose run --entrypoint "poetry install --no-root" demo-app
```

# 2. APIの立ち上げ
```shell
$ docker-compose up
```
# 参考
## [FastAPI入門](https://zenn.dev/sh0nk/books/537bb028709ab9)
基本はここに書かれているのでここを参照すると作業が捗る。
