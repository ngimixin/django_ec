// カート数量変更（右ペイン）
// 数量セレクト変更時に、そのフォームだけ submit する
// → チェックアウト用 submit 処理とは完全に独立
document.addEventListener("DOMContentLoaded", () => {
  const selects = document.querySelectorAll(".cart-quantity-select");

  selects.forEach((select) => {
    select.addEventListener("change", () => {
      if (select.form) {
        select.form.submit();
      }
    });
  });
});

// 共通ユーティリティ
// 数字だけを抽出（ハイフン・スペース等を除去）
function extractDigits(value) {
  return (value || "").replace(/\D/g, "");
}

// 住所（入力内容 → hidden）
function syncAddressHidden() {
  const pref = document.getElementById("prefecture")?.value.trim() || "";
  const city = document.getElementById("city")?.value.trim() || "";
  const street = document.getElementById("street")?.value.trim() || "";
  const building = document.getElementById("building")?.value.trim() || "";

  // 空要素は除外して、スペース区切りで結合
  const address = [pref, city, street, building].filter(Boolean).join(" ");

  const hidden = document.getElementById("id_address");
  if (hidden) {
    hidden.value = address;
  }

  return address;
}

// ZipCloud で郵便番号 → 都道府県/市区町村の自動補完（失敗しても手入力で続行）
async function autofillByZip(zip) {
  if (!zip) return;

  try {
    const url = `https://zipcloud.ibsnet.co.jp/api/search?zipcode=${encodeURIComponent(
      zip
    )}`;
    const res = await fetch(url);
    if (!res.ok) return;

    const data = await res.json();
    if (data.status !== 200 || !data.results?.length) return;

    const r = data.results[0];

    const prefSelect = document.getElementById("prefecture");
    if (prefSelect) {
      prefSelect.value = r.address1;
      prefSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const cityInput = document.getElementById("city");
    if (cityInput) {
      cityInput.value = `${r.address2}${r.address3}`;
      cityInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
  } catch (err) {
    console.warn("ZipCloud autofill failed:", err);
  }
}

const addressInputIds = new Set([
  "id_postal_code",
  "city",
  "street",
  "building",
]);

// チェックアウトフォームだけを対象に hidden を同期（右ペインには影響しない）
document.addEventListener("DOMContentLoaded", () => {
  const checkoutForm = document.getElementById("checkout-form");
  if (!checkoutForm) {
    return;
  }

  const zipInput = document.getElementById("id_postal_code");
  if (!zipInput) {
    return;
  }

  checkoutForm.addEventListener("input", (e) => {
    const el = e.target;
    if (!(el instanceof HTMLInputElement)) {
      return;
    }

    if (!addressInputIds.has(el.id)) {
      return;
    }
    syncAddressHidden();
  });

  checkoutForm.addEventListener("change", (e) => {
    const el = e.target;
    if (!(el instanceof HTMLSelectElement)) {
      return;
    }
    if (el.id !== "prefecture") {
      return;
    }
    syncAddressHidden();
  });

  zipInput.addEventListener("input", async () => {
    const zip7 = extractDigits(zipInput.value);
    if (zip7.length !== 7) {
      return;
    }
    await autofillByZip(zip7);
  });

  // 購入ボタン押下「直前」に必ず hidden を最新化
  checkoutForm.addEventListener("submit", () => {
    syncAddressHidden();
  });
});
