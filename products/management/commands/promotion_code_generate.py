"""事前にDBへプロモーションコードを生成する管理コマンド。

使い方:
    python manage.py promotion_code_generate          # 10件生成（デフォルト）
    python manage.py promotion_code_generate --count 20  # 20件生成
"""

import random
import string

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from products.models import PromotionCode


class Command(BaseCommand):
    help = "7桁の英数字からなるプロモーションコードを10個生成します（割引額：100〜1000円）。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="生成するプロモーションコードの数（デフォルト: 10）",
        )

    def handle(self, *args, **options):
        count: int = options["count"]

        if count <= 0:
            self.stderr.write(self.style.ERROR("--count は1以上で指定してください。"))
            return

        created: list[PromotionCode] = []

        # 7桁英数字の候補文字
        # 見分けづらい文字（O/0, I/1）を除外する
        excluded = {"O", "0", "I", "1"}
        chars = "".join(
            ch for ch in (string.ascii_uppercase + string.digits) if ch not in excluded
        )

        # 重複や同時実行を考慮し、保存時にコケたらリトライする（無限ループ防止）
        max_attempts = count * 20
        attempts = 0

        while len(created) < count and attempts < max_attempts:
            attempts += 1

            code = "".join(random.choice(chars) for _ in range(7))
            discount_amount = random.randrange(100, 1001, 100)

            try:
                with transaction.atomic():
                    promotion = PromotionCode.objects.create(
                        code=code,
                        discount_amount=discount_amount,
                        is_used=False,
                        used_at=None,
                    )
                created.append(promotion)
            except IntegrityError:
                # code に unique 制約があるため、偶然の重複でここに来たとき再試行する
                continue

        if len(created) < count:
            self.stderr.write(
                self.style.ERROR(
                    f"プロモーションコードを必要数生成できませんでした（生成数: {len(created)}/{count}）"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"プロモーションコード生成結果（CSV形式、{count}件）：")
        )
        self.stdout.write("コード,割引額")
        for p in created:
            self.stdout.write(f"{p.code},{p.discount_amount}")

        self.stdout.write("")
        self.stdout.write("プロモーションコード生成結果（PR貼り付け用）：")
        for p in created:
            self.stdout.write(f"- `{p.code}` : {p.discount_amount}円OFF")
