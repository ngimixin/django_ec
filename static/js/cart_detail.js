// カート数量変更（右ペイン）を fetch 化して、右ペインだけ更新
document.addEventListener("DOMContentLoaded", () => {
  // ① 右ペイン：カート数量変更フォームを fetch 化
  const summary = document.getElementById("cart-summary");
  if (!summary) {
    return;
  }

  const csrfToken = document.querySelector(
    'input[name="csrfmiddlewaretoken"]',
  )?.value;
  if (!csrfToken) {
    return;
  }

  summary.addEventListener("change", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLSelectElement)) {
      return;
    }

    if (!target.classList.contains("cart-quantity-select")) {
      return;
    }

    const form = target.closest("form");
    if (!form) {
      return;
    }

    const url = form.getAttribute("action");
    if (!url) {
      return;
    }

    const formData = new FormData();
    formData.append("quantity", target.value);
    formData.append("csrfmiddlewaretoken", csrfToken);

    try {
      const res = await fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!res.ok) {
        window.location.reload();
        return;
      }

      const data = await res.json();
      if (!data.ok || !data.html) {
        window.location.reload();
        return;
      }

      summary.innerHTML = data.html;

      // ナビゲーションバーのカートバッジを更新
      const cartBadge = document.getElementById("cart-badge");
      if (cartBadge && typeof data.total_quantity !== "undefined") {
        cartBadge.textContent = data.total_quantity;
      }
    } catch (e) {
      window.location.reload();
    }
  });
});

// ② 右ペイン：削除ボタンを fetch 化
document.addEventListener("DOMContentLoaded", () => {
  const summary = document.getElementById("cart-summary");
  if (!summary) {
    return;
  }

  const csrfToken = document.querySelector(
    'input[name="csrfmiddlewaretoken"]',
  )?.value;
  if (!csrfToken) {
    return;
  }

  summary.addEventListener("submit", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLFormElement)) {
      return;
    }

    if (!target.classList.contains("cart-item-delete-form")) {
      return;
    }

    const url = target.getAttribute("action");
    if (!url) {
      return;
    }

    event.preventDefault();

    const formData = new FormData();
    formData.append("csrfmiddlewaretoken", csrfToken);

    try {
      const res = await fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!res.ok) {
        window.location.reload();
        return;
      }

      const data = await res.json();
      if (!data.ok || !data.html) {
        window.location.reload();
        return;
      }

      summary.innerHTML = data.html;

      const cartBadge = document.getElementById("cart-badge");
      if (cartBadge && typeof data.total_quantity !== "undefined") {
        cartBadge.textContent = data.total_quantity;
      }
    } catch (e) {
      window.location.reload();
    }
  });
});

// ③ 郵便番号入力フォームに自動補完機能を追加
document.addEventListener("DOMContentLoaded", () => {
  const zipInput = document.getElementById("id_postal_code");
  if (!zipInput) {
    return;
  }

  zipInput.addEventListener("input", async () => {
    // ハイフンを含んでもOKなように数字だけ抽出
    const zip = extractDigits(zipInput.value);

    // 7桁になったら ZipCloud を呼ぶ
    if (zip.length === 7) {
      await autofillByZip(zip);
    }
  });
});

// 共通ユーティリティ
// 数字だけを抽出（ハイフン・スペース等を除去）
function extractDigits(value) {
  return (value || "").replace(/\D/g, "");
}

// ZipCloud で郵便番号 → 都道府県/市区町村の自動補完（失敗しても手入力で続行）
async function autofillByZip(zip) {
  if (!zip) {
    return;
  }

  try {
    const url = `https://zipcloud.ibsnet.co.jp/api/search?zipcode=${encodeURIComponent(
      zip,
    )}`;
    const res = await fetch(url);
    if (!res.ok) {
      return;
    }

    const data = await res.json();
    if (data.status !== 200 || !data.results?.length) {
      return;
    }

    const r = data.results[0];

    const prefSelect = document.getElementById("id_prefecture");
    if (prefSelect) {
      prefSelect.value = r.address1;
      prefSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }

    const cityInput = document.getElementById("id_city");
    if (cityInput) {
      cityInput.value = `${r.address2}${r.address3}`;
      cityInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
  } catch (err) {
    console.warn("ZipCloud autofill failed:", err);
  }
}
