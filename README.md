# VELO STATION（Django ECサイト / ポートフォリオ）

Djangoで作成したECサイトです。  
商品一覧 → カート → チェックアウト → 注文確定までの購入フローを一通り実装しています。

- デモURL：[https://django-ec-staging-005009c332da.herokuapp.com/](https://django-ec-staging-005009c332da.herokuapp.com/)
- ローカル起動：Docker対応（下に手順あり）
- 作者：nagai（GitHub: ngimixin）

---

## できること（実装済み）

### お客様向け
- 商品一覧 / 商品詳細
- カート追加（一覧は +1、詳細は指定数量を追加）
- カート内の数量表示 / 削除
- チェックアウト（購入フォーム入力 → 注文確定）
- 購入後：購入完了画面にてフラッシュメッセージを表示
- 注文完了メール送信（購入明細を含む）
- セッション単位でカートを分離（ブラウザが違えば別カート）

### 管理者向け（/admin とは別に独自実装）
- 管理者用 商品管理ページ（`/manage/products`）
  - 商品一覧 / 作成 / 編集 / 削除（一覧から削除可能）
- 管理者用 注文一覧（`/manage/orders/`）
  - 注文詳細
  - 購入者は閲覧不可
- 管理者向けページは Basic認証で保護

### データの整合性
- 商品情報を更新・削除しても、購入明細は「購入時点の情報」を保持

---

## 工夫した点

- 購入フローの一連を実装（カート → チェックアウト → 注文作成 → 注文明細作成 → メール送信）
- セッション単位でカートを分離し、複数ユーザー同時利用でも混ざらない設計
- 購入明細はスナップショットとして保持し、商品が削除されても注文情報が壊れないように実装
- Django標準 admin に頼らず管理画面を独自実装し、Basic認証で保護
- カートの数量変更は非同期で処理し、チェックアウト画面の入力内容が保持されるように実装
- 商品一覧・カートの数量選択はプルダウン式にし、DBの在庫数を上限として反映
- 郵便番号から住所を自動入力し、購入時の入力負担を軽減
- 注文確定時は行ロックで在庫をチェックし、不整合があれば注文を確定せずカートへ戻す

---

## 現在対応中

- プロモーションコード機能（適用・割引・1回のみ利用）
  - 実装中のため、完了後に機能一覧へ追記予定

---

## ローカル環境での起動方法


### .envを作成し、以下を記載

SECRET_KEYは自身で生成する

[【Django】settings.pyのSECRET_KEYを再発行(リジェネレート)する](https://noauto-nolife.com/post/django-secret-key-regenerate/)

```.env
DATABASE_URL="postgres://postgres:postgres@db:5432/django_develop"
SECRET_KEY=<自身で生成したものを使う>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### dockerを立ち上げる

```
docker-compose up
```

※ 以降の `docker-compose exec` は、上記でコンテナ起動中であることが前提です。

### 初期データ（シード）を投入

※ ローカル環境で商品を表示する場合は、初期データ（シード）を登録してください。

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata products/fixtures/products.json
```

### 画面イメージ
ブラウザで以下にアクセスし、商品一覧画面が表示されれば起動完了です。

[localhost:3000/](http://localhost:3000/)
![商品一覧画面](docs/screenshots/top.png)
![チェックアウト画面](docs/screenshots/checkout.png)