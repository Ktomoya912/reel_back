# REEL API documentation
## 概要
REEL Projectで使用するAPIの仕様書です。
例文はSwagger UIで確認できるため、ここでは省略します。
## ベースURL
`https://{awsのURL}/api/v1`
## 認証
### ログイン
#### リクエスト
`POST /auth/login`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| username | ○ | string | ユーザー名 |
| password | ○ | string | パスワード |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| token | string | アクセストークン |
| user | object | ユーザー情報 |
### ログアウト
#### リクエスト
`POST /auth/logout`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |
### ユーザー登録
#### リクエスト
`POST /auth/register`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| username | ○ | string | ユーザー名 |
| email | ○ | string | メールアドレス |
| password | ○ | string | パスワード |
| sex | ○ | string | 性別 |
| birthday | ○ | string | 誕生日 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| token | string | アクセストークン |
| user | object | ユーザー情報 |
### ユーザー情報取得
#### リクエスト
`GET /auth/user`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| user | object | ユーザー情報 |
### ユーザー情報更新
#### リクエスト
`PUT /auth/user`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| username | ○ | string | ユーザー名 |
| password | ○ | string | パスワード |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| user | object | ユーザー情報 |
### ユーザー削除
#### リクエスト
`DELETE /auth/user`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |


## ユーザー
### ユーザー一覧取得
#### リクエスト
`GET /users`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| users | array | ユーザー情報 |
### ユーザー情報取得
#### リクエスト
`GET /users/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| id | ○ | string | ユーザーID |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| user | object | ユーザー情報 |
### ユーザー情報更新
#### リクエスト
`PUT /users/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| id | ○ | string | ユーザーID |
| username | ○ | string | ユーザー名 |
| password | ○ | string | パスワード |
| email | ○ | string | メールアドレス |
| sex | ○ | string | 性別 |
| birthday | ○ | string | 誕生日 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| user | object | ユーザー情報 |
### ユーザー削除
#### リクエスト
`DELETE /users/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| id | ○ | string | ユーザーID |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |
## 通知取得
### 通知一覧取得
#### リクエスト
`GET /notifications`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| notifications | array | 通知情報 |
## イベント情報
### イベント一覧取得
#### リクエスト
`GET /events`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
| keyword | ○ | string | キーワード |
| event_tag | | array | イベントタグ |
| event_time | | array | イベント時間 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| events | array | イベント情報 |
### イベント情報登録
#### リクエスト
`POST /events`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| title | ○ | string | タイトル |
| postal_code | ○ | string | 郵便番号 |
| prefecture | ○ | string | 都道府県 |
| city | ○ | string | 市区町村 |
| address | ○ | string | 住所 |
| phone_number | ○ | string | 電話番号 |
| email | ○ | string | メールアドレス |
| homepage | ○ | string | ホームページ |
| event_description | ○ | string | イベント説明 |
| participation_fee |  | string | 参加費 |
| capacity |  | string | 定員 |
| event_time | 〇 | array | イベント時間 |
| event_tag | 〇 | array | イベントタグ |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| event | object | イベント情報
### イベント情報取得
#### リクエスト
`GET /events/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | イベントID |
| token | | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| event | object | イベント情報 |
### イベント情報更新
#### リクエスト
`PUT /events/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | イベントID |
| token | ○ | string | アクセストークン |
| title | ○ | string | タイトル |
| postal_code | ○ | string | 郵便番号 |
| prefecture | ○ | string | 都道府県 |
| city | ○ | string | 市区町村 |
| address | ○ | string | 住所 |
| phone_number | ○ | string | 電話番号 |
| email | ○ | string | メールアドレス |
| homepage | ○ | string | ホームページ |
| event_description | ○ | string | イベント説明 |
| participation_fee |  | string | 参加費 |
| capacity |  | string | 定員 |
| event_time | 〇 | array | イベント時間 |
| event_tag | 〇 | array | イベントタグ |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| event | object | イベント情報 |
### イベント削除
#### リクエスト
`DELETE /events/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | イベントID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |


## 求人情報
### 求人一覧取得
#### リクエスト
`GET /jobs`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
| keyword | | string | キーワード |
| job_tag | | array | 求人タグ |
| job_time | | array | 求人時間 |
| is_one_day | | array | 求人タイプ |
| salary | | array | 給与 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| jobs | array | 求人情報 |
### 求人情報登録
#### リクエスト
`POST /jobs`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| title | ○ | string | タイトル |
| postal_code | ○ | string | 郵便番号 |
| prefecture | ○ | string | 都道府県 |
| city | ○ | string | 市区町村 |
| address | ○ | string | 住所 |
| phone_number | ○ | string | 電話番号 |
| email | ○ | string | メールアドレス |
| homepage | ○ | string | ホームページ |
| job_description | ○ | string | 求人説明 |
| is_one_day | ○ | string | 求人タイプ |
| salary | ○ | string | 給与 |
| job_time | 〇 | array | 求人時間 |
| job_tag | 〇 | array | 求人タグ |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| job | object | 求人情報
### 求人情報取得
#### リクエスト
`GET /jobs/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| job | object | 求人情報 |
### 求人情報更新
#### リクエスト
`PUT /jobs/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | ○ | string | アクセストークン |
| title | ○ | string | タイトル |
| postal_code | ○ | string | 郵便番号 |
| prefecture | ○ | string | 都道府県 |
| city | ○ | string | 市区町村 |
| address | ○ | string | 住所 |
| phone_number | ○ | string | 電話番号 |
| email | ○ | string | メールアドレス |
| homepage | ○ | string | ホームページ |
| job_description | ○ | string | 求人説明 |
| is_one_day | ○ | string | 求人タイプ |
| salary | ○ | string | 給与 |
| job_time | 〇 | array | 求人時間 |
| job_tag | 〇 | array | 求人タグ |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| job | object | 求人情報 |
### 求人削除
#### リクエスト
`DELETE /jobs/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |
### 求人応募
#### リクエスト
`POST /jobs/{id}/apply`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| job | object | 求人情報 |

## 求人応募履歴
### 求人応募履歴一覧取得(ユーザー側)
#### リクエスト
`GET /jobs/apply_histories`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| apply_histories | array | 求人応募履歴情報(求人情報) |
### 求人応募履歴一覧取得(企業側)
#### リクエスト
`GET /jobs/{id}/apply_histories`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| apply_histories | array | 求人応募履歴情報(ユーザー情報) |

## お気に入り情報
### お気に入り登録(求人)
#### リクエスト
`POST /favorites/jobs/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| job | object | 求人情報 |
### お気に入り削除(求人)
#### リクエスト
`DELETE /favorites/jobs/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | 求人ID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |
## お気に入り一覧取得(求人)
#### リクエスト
`GET /favorites/jobs`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| jobs | array | 求人情報 |
### お気に入り登録(イベント)
#### リクエスト
`POST /favorites/events/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | イベントID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| event | object | イベント情報 |
### お気に入り削除(イベント)
#### リクエスト
`DELETE /favorites/events/{id}`
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | イベントID |
| token | ○ | string | アクセストークン |
### お気に入り一覧取得(イベント)
#### リクエスト
`GET /favorites/events`
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | ○ | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
| sort | | string | ソート順 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| events | array | イベント情報 |



## プラン情報
### プラン一覧取得
#### リクエスト
`GET /plans`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| plans | array | プラン情報 |
### プラン情報登録
#### リクエスト
`POST /plans`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| name | ○ | string | プラン名 |
| price | ○ | string | 価格 |
| period | ○ | string | 期間 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| plan | object | プラン情報
### プラン情報取得
#### リクエスト
`GET /plans/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | プランID |
| token | | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| plan | object | プラン情報 |
### プラン情報更新
#### リクエスト
`PUT /plans/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | プランID |
| token | ○ | string | アクセストークン |
| name | ○ | string | プラン名 |
| price | ○ | string | 価格 |
| period | ○ | string | 期間 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| plan | object | プラン情報 |
### プラン削除
#### リクエスト
`DELETE /plans/{id}`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | プランID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| message | string | メッセージ |
## プラン購入
### プラン購入
#### リクエスト
`POST /plans/{id}/purchase`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| id | ○ | string | プランID |
| token | ○ | string | アクセストークン |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| plan | object | プラン情報 |
## プラン購入履歴
### プラン購入履歴一覧取得
#### リクエスト
`GET /plans/purchase_histories`
#### パラメータ
| パラメータ名 | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| token | | string | アクセストークン |
| limit | | int | 取得件数 |
| offset | | int | 取得開始位置 |
#### レスポンス
| パラメータ名 | 型 | 説明 |
| --- | --- | --- |
| purchase_histories | array | プラン購入履歴情報 |
