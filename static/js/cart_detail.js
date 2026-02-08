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

// ③ プロモーションコード適用を fetch 化
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

    const isApplyForm = target.classList.contains("promotion-apply-form");
    const isRemoveForm = target.classList.contains("promotion-remove-form");
    if (!isApplyForm && !isRemoveForm) {
      return;
    }

    const url = target.getAttribute("action");
    if (!url) {
      return;
    }

    event.preventDefault();

    const formData = new FormData(target);
    if (!formData.get("csrfmiddlewaretoken")) {
      formData.append("csrfmiddlewaretoken", csrfToken);
    }

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
      if (!data.html) {
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

// ④ 郵便番号入力フォームに自動補完機能を追加
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

// ⑤ チェックアウトフォームのフロントバリデーション
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("checkout-form");
  if (!form) {
    return;
  }

  const fields = {
    name: document.getElementById("id_name"),
    phone: document.getElementById("id_phone"),
    email: document.getElementById("id_email"),
    postalCode: document.getElementById("id_postal_code"),
    prefecture: document.getElementById("id_prefecture"),
    city: document.getElementById("id_city"),
    street: document.getElementById("id_street"),
    building: document.getElementById("id_building"),
    cardNumber: document.getElementById("cc-number"),
    cardExpire: document.getElementById("cc-expiration"),
    cardCvv: document.getElementById("cc-cvv"),
    cardHolder: document.getElementById("cc-name"),
  };

  const maxLengthRules = new Map([
    [fields.name, 100],
    [fields.city, 50],
    [fields.street, 50],
    [fields.building, 100],
    [fields.cardHolder, 100],
  ]);

  const fieldLabels = new Map([
    [fields.name, "お名前"],
    [fields.phone, "電話番号"],
    [fields.email, "メールアドレス"],
    [fields.postalCode, "郵便番号"],
    [fields.prefecture, "都道府県"],
    [fields.city, "市区町村"],
    [fields.street, "丁目・番地・号"],
    [fields.building, "建物名／会社名・部屋番号"],
    [fields.cardNumber, "カード番号"],
    [fields.cardExpire, "有効期限"],
    [fields.cardCvv, "セキュリティコード"],
    [fields.cardHolder, "カード名義人"],
  ]);

  const requiredTargets = [
    fields.name,
    fields.phone,
    fields.email,
    fields.postalCode,
    fields.prefecture,
    fields.city,
    fields.street,
    fields.cardNumber,
    fields.cardExpire,
    fields.cardCvv,
    fields.cardHolder,
  ].filter(Boolean);

  function isBlank(value) {
    return !value || value.trim() === "";
  }

  function getServerFeedback(field) {
    const parent = field.parentElement;
    if (!parent) {
      return null;
    }
    const feedbacks = parent.querySelectorAll(".invalid-feedback");
    for (const feedback of feedbacks) {
      if (!feedback.dataset.clientError) {
        return feedback;
      }
    }
    return null;
  }

  function getClientFeedback(field) {
    const parent = field.parentElement;
    if (!parent) {
      return null;
    }
    return parent.querySelector(".invalid-feedback[data-client-error='1']");
  }

  function createClientFeedback(field) {
    const feedback = document.createElement("div");
    feedback.className = "invalid-feedback";
    feedback.dataset.clientError = "1";
    field.insertAdjacentElement("afterend", feedback);
    return feedback;
  }

  function setClientError(field, message) {
    if (!field) {
      return;
    }
    field.classList.add("is-invalid");
    field.dataset.clientError = "1";

    const existingClientFeedback = getClientFeedback(field);
    if (existingClientFeedback) {
      existingClientFeedback.textContent = message;
      return;
    }

    const serverFeedback = getServerFeedback(field);
    if (serverFeedback) {
      return;
    }

    const feedback = createClientFeedback(field);
    feedback.textContent = message;
  }

  function clearClientError(field) {
    if (!field) {
      return;
    }
    if (field.dataset.clientError) {
      field.classList.remove("is-invalid");
      delete field.dataset.clientError;
    }
    const feedback = getClientFeedback(field);
    if (feedback) {
      feedback.remove();
    }
  }

  function clearAllClientErrors() {
    const targets = Object.values(fields).filter(Boolean);
    for (const field of targets) {
      clearClientError(field);
    }
  }

  function validateRequired(field, label) {
    if (!field) {
      return true;
    }
    if (isBlank(field.value)) {
      setClientError(field, `${label}を入力してください。`);
      return false;
    }
    return true;
  }

  function validateMaxLength(field, label, max) {
    if (!field) {
      return true;
    }
    if (field.value.trim().length > max) {
      setClientError(field, `${label}は${max}文字以内で入力してください。`);
      return false;
    }
    return true;
  }

  function validateEmail(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    if (field.validity && field.validity.typeMismatch) {
      setClientError(field, "メールアドレスの形式が正しくありません。");
      return false;
    }
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(field.value.trim())) {
      setClientError(field, "メールアドレスの形式が正しくありません。");
      return false;
    }
    return true;
  }

  function validatePostalCode(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    const pattern = /^\d{3}-?\d{4}$/;
    if (!pattern.test(field.value.trim())) {
      setClientError(field, "郵便番号は000-0000の形式で入力してください。");
      return false;
    }
    return true;
  }

  function validatePhone(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    const value = field.value.trim();
    if (!/^[0-9-]+$/.test(value)) {
      setClientError(field, "電話番号は数字とハイフンのみで入力してください。");
      return false;
    }
    const digits = extractDigits(value);
    if (digits.length < 10 || digits.length > 11) {
      setClientError(field, "電話番号は10〜11桁で入力してください。");
      return false;
    }
    return true;
  }

  function validateCardNumber(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    const value = field.value.trim();
    if (!/^[0-9 -]+$/.test(value)) {
      setClientError(field, "カード番号は数字・空白・ハイフンで入力してください。");
      return false;
    }
    const digits = extractDigits(value);
    if (digits.length < 13 || digits.length > 19) {
      setClientError(field, "カード番号は13〜19桁で入力してください。");
      return false;
    }
    return true;
  }

  function validateCardExpire(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    const value = field.value.trim();
    const pattern = /^(0[1-9]|1[0-2])\/\d{2}$/;
    if (!pattern.test(value)) {
      setClientError(field, "有効期限はMM/YY形式で入力してください。");
      return false;
    }
    return true;
  }

  function validateCardCvv(field) {
    if (!field || isBlank(field.value)) {
      return true;
    }
    const pattern = /^\d{3,4}$/;
    if (!pattern.test(field.value.trim())) {
      setClientError(field, "セキュリティコードは3〜4桁で入力してください。");
      return false;
    }
    return true;
  }

  form.addEventListener("submit", (event) => {
    clearAllClientErrors();

    let isValid = true;

    for (const field of requiredTargets) {
      const label = fieldLabels.get(field) || "必須項目";
      if (!validateRequired(field, label)) {
        isValid = false;
      }
    }

    for (const [field, max] of maxLengthRules) {
      if (!field) {
        continue;
      }
      const label = fieldLabels.get(field) || "入力項目";
      if (!validateMaxLength(field, label, max)) {
        isValid = false;
      }
    }

    if (!validateEmail(fields.email)) {
      isValid = false;
    }
    if (!validatePostalCode(fields.postalCode)) {
      isValid = false;
    }
    if (!validatePhone(fields.phone)) {
      isValid = false;
    }
    if (!validateCardNumber(fields.cardNumber)) {
      isValid = false;
    }
    if (!validateCardExpire(fields.cardExpire)) {
      isValid = false;
    }
    if (!validateCardCvv(fields.cardCvv)) {
      isValid = false;
    }

    if (!isValid) {
      event.preventDefault();
      const firstInvalid = form.querySelector(".is-invalid");
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
        if (typeof firstInvalid.focus === "function") {
          firstInvalid.focus();
        }
      }
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
