/**
 * app.js — 共通初期化
 */
(function () {
  "use strict";

  // サイドバートグル
  const toggle = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // フラッシュアラート自動消去（5秒後）
  document.querySelectorAll("#alert-area .alert").forEach((el) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });
})();
