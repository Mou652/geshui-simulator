(() => {
  const qq = '2430239942';

  document.querySelectorAll('[data-copy-qq]').forEach((button) => {
    button.addEventListener('click', async () => {
      const status = button.closest('.qq-bar').querySelector('.qq-copy-status');

      try {
        await navigator.clipboard.writeText(qq);
        button.textContent = '已复制 QQ';
        status.textContent = `QQ ${qq} 已复制`;
      } catch {
        button.textContent = '长按号码复制';
        status.textContent = `请长按 QQ 号码 ${qq} 复制`;
      }
    });
  });
})();
