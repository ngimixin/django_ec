-- ============================
-- ECサイト用スキーマ定義
-- products / carts / cart_items / orders / order_items
-- ============================

-- products
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
  id           BIGSERIAL PRIMARY KEY,
  sku          VARCHAR(100) NOT NULL,
  name         VARCHAR(255) NOT NULL,
  description  TEXT NULL,
  price        INTEGER NOT NULL,                    -- 価格（円）
  stock        INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0), -- 在庫数（0以上）
  image        VARCHAR NULL,                        -- Django ImageField が保存する画像ファイルのパス
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,       -- 掲載フラグ
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (sku)
);

-- carts（セッションごとのカート）
DROP TABLE IF EXISTS carts CASCADE;
CREATE TABLE carts (
  id           BIGSERIAL PRIMARY KEY,
  session_key  VARCHAR(64) NOT NULL,                -- Djangoセッションキー想定
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (session_key)
);

-- cart_items（カート内の商品）
DROP TABLE IF EXISTS cart_items CASCADE;
CREATE TABLE cart_items (
  id          BIGSERIAL PRIMARY KEY,
  cart_id     BIGINT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
  product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (cart_id, product_id)
);

-- orders（注文ヘッダ）
DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
  id           BIGSERIAL PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,           -- 購入者氏名
  
-- 後から追加したカラムのため、既存レコード対応として NULL 許可
  phone        VARCHAR(20) NULL,                -- 購入者電話番号

  email        VARCHAR NOT NULL,                -- 購入者メール

-- 後から追加したカラムのため、既存レコード対応として NULL 許可
  postal_code  VARCHAR(8) NULL,                 -- 配送先郵便番号
  
  address      TEXT NOT NULL,                   -- 配送先住所
  total_amount INTEGER NOT NULL,                -- 合計金額（円）

-- チェックアウト時のクレジットカード情報（学習用）
-- 後から追加したカラムのため、既存レコード対応として NULL 許可
-- ※ 実サービスではDBに保存しない
  card_number  VARCHAR(20) NULL,                -- カード番号
  card_expire  VARCHAR(7) NULL,                 -- 有効期限（MM/YY）
  card_cvv     VARCHAR(4) NULL,                 -- セキュリティコード
  card_holder  VARCHAR(100) NULL,               -- カード名義人

  status       VARCHAR(20) NOT NULL DEFAULT 'pending',   -- 'pending' | 'paid' | 'shipped' など想定
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- order_items（注文明細）
DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
  id          BIGSERIAL PRIMARY KEY,
  order_id    BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  price       INTEGER NOT NULL,                     -- 注文時点の単価（円）
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
