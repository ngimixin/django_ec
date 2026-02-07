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

-- promotion_codes（プロモーションコード）
DROP TABLE IF EXISTS promotion_codes CASCADE;
CREATE TABLE promotion_codes (
  id              BIGSERIAL PRIMARY KEY,
  code            VARCHAR(7) NOT NULL,
  discount_amount INTEGER NOT NULL CHECK (discount_amount BETWEEN 100 AND 1000),
  is_used         BOOLEAN NOT NULL DEFAULT FALSE,
  used_at         TIMESTAMP NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (code)
);

-- orders（注文ヘッダ）
DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
  id           BIGSERIAL PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,           -- 購入者氏名
  phone        VARCHAR(20) NOT NULL,            -- 購入者電話番号
  email        VARCHAR NOT NULL,                -- 購入者メール
  postal_code  VARCHAR(8) NOT NULL,             -- 配送先郵便番号
  address      TEXT NOT NULL,                   -- 配送先住所
  total_amount INTEGER NOT NULL,                -- 支払合計（円）

-- チェックアウト時のクレジットカード情報（学習用）
-- ※ 実サービスではDBに保存しないが、本課題では理解のため保持する
  card_number  VARCHAR(20) NOT NULL,            -- カード番号
  card_expire  VARCHAR(7) NOT NULL,             -- 有効期限（MM/YY）
  card_cvv     VARCHAR(4) NOT NULL,             -- セキュリティコード
  card_holder  VARCHAR(100) NOT NULL,           -- カード名義人

  status       VARCHAR(20) NOT NULL DEFAULT 'pending',   -- 'pending' | 'paid' | 'shipped' など想定

  promotion_code_id BIGINT NULL REFERENCES promotion_codes(id) ON DELETE SET NULL,
  promotion_discount_amount INTEGER NULL CHECK (promotion_discount_amount BETWEEN 0 AND 1000),

  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- order_items（注文明細）
DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
  id          BIGSERIAL PRIMARY KEY,
  order_id    BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  product_name VARCHAR(255) NOT NULL,           -- 注文時点の商品名
  price       INTEGER NOT NULL,                 -- 注文時点の単価（円）
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
