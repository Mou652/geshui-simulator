(function () {
  'use strict';
  const QQ = '2430239942';
  const config = window.MOU_PROMO_CONFIG || {};
  const products = (config.promo_content?.products || []).filter(product => product.enabled !== false);
  const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const scriptBase = new URL('.', document.currentScript.src);
  const qrUrl = new URL('payment-qr.png', scriptBase).href;
  const dialog = document.createElement('dialog');
  dialog.className = 'mou-dialog';
  dialog.tabIndex = -1;
  dialog.setAttribute('aria-labelledby', 'mouDialogTitle');
  dialog.innerHTML = '<div class="dialog-shell"><button class="dialog-close" type="button" data-close-mou aria-label="关闭弹窗">×</button><div id="mouDialogBody"></div></div>';
  const toast = document.createElement('p');
  toast.className = 'toast';
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');
  toast.hidden = true;
  document.body.append(dialog, toast);
  let trigger = null;
  let previousOverflow = '';
  let toastTimer;

  function menu(open) {
    const button = document.querySelector('#menuToggle');
    if (!button) return;
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? '关闭导航菜单' : '打开导航菜单');
    document.querySelector('#mainNav')?.classList.toggle('is-open', open);
  }

  function open(markup, imageMode) {
    menu(false);
    if (!dialog.open) {
      trigger = document.activeElement;
      previousOverflow = document.body.style.overflow;
    }
    dialog.querySelector('#mouDialogBody').innerHTML = markup;
    dialog.classList.toggle('image-dialog', Boolean(imageMode));
    if (!dialog.open) dialog.showModal();
    document.body.style.overflow = 'hidden';
    dialog.focus({ preventScroll: true });
  }

  function openContact() {
    open('<p class="eyebrow">LET’S TALK</p><h2 id="mouDialogTitle">联系灵活就业指导</h2><p class="dialog-description">产品、激活码、录屏与图片处理需求，都可以联系我。</p><p class="contact-value">' + QQ + '</p><div class="dialog-actions"><button class="button button-primary" type="button" data-copy-qq>复制 QQ 号码 <span aria-hidden="true">→</span></button><a class="button button-outline" href="https://wpa.qq.com/msgrd?v=3&amp;uin=' + QQ + '&amp;site=qq&amp;menu=yes" target="_blank" rel="noopener noreferrer">打开 QQ ↗</a></div>');
  }

  function openActivationNotice() {
    open('<p class="eyebrow">ACTIVATION</p><h2 id="mouDialogTitle">本应用需激活码使用</h2><p class="dialog-description activation-description">本应用需激活码激活后使用，<strong>不支持试用</strong>。激活码及安装说明请联系 QQ 获取。</p><p class="activation-case-note">担心上当受骗，可先<a class="activation-case-link" href="customer-cases.html" target="_blank" rel="noopener noreferrer">查看客户案例 <span aria-hidden="true">↗</span></a>，再决定是否购买。</p><p class="platform-notice">目前仅支持安卓，暂不支持 iOS；iOS 版本近日即将更新。</p><p class="contact-value">' + QQ + '</p><div class="dialog-actions"><button class="button button-primary" type="button" data-copy-qq>复制 QQ 号码</button><button class="button button-outline" type="button" data-contact>联系 QQ</button></div>');
  }

  function paymentMarkup(product, pageMode) {
    const heading = pageMode ? 'h1 id="paymentTitle"' : 'h2 id="mouDialogTitle"';
    const closingHeading = pageMode ? 'h1' : 'h2';
    const choices = products.map(item => '<button type="button" data-payment-choice="' + escape(item.id) + '" aria-pressed="' + (item.id === product.id) + '"><span>' + escape(item.title) + '</span><strong>' + item.price_cny + ' 元</strong></button>').join('');
    return '<div class="payment-content" data-selected-product="' + escape(product.id) + '"><p class="eyebrow">ALIPAY · 扫码付款</p><' + heading + '>选择品类，扫码付款</' + closingHeading + '><div class="payment-choices" role="group" aria-label="选择付款品类">' + choices + '</div><div class="payment-summary"><span>' + escape(product.title) + '</span><strong><small>¥</small>' + product.price_cny + '<small>元</small></strong></div><p class="payment-methods"><span>支持信用卡</span><i aria-hidden="true"></i><span>花呗付款</span></p><figure class="payment-code"><img class="payment-qr" src="' + qrUrl + '" width="688" height="688" alt="' + escape(product.title) + '收款二维码，付款金额 ' + product.price_cny + ' 元"><figcaption>长按保存收款码 · 打开支付宝扫一扫</figcaption></figure><p class="payment-followup"><strong>付款后联系 QQ ' + QQ + '<br>发送付款截图</strong></p><p class="payment-product-note ' + (product.id === 'tax' ? 'is-platform-note' : '') + '">' + escape(product.payment_note) + '</p><div class="payment-actions"><a class="button button-primary" href="' + qrUrl + '" download="灵活就业指导-支付宝收款码.png">保存收款码 ↓</a><button class="button button-outline" type="button" data-contact>联系 QQ</button></div><p class="payment-note">请核对所选品类，并按上方金额付款</p></div>';
  }

  function selectedProduct(id) {
    return products.find(product => product.id === id) || products[0];
  }

  function openPayment(id) {
    const product = selectedProduct(id);
    if (product) open(paymentMarkup(product, false));
  }

  function openImage(src, title) {
    const container = document.createElement('div');
    const heading = document.createElement('h2');
    heading.id = 'mouDialogTitle';
    heading.textContent = title;
    const image = document.createElement('img');
    image.className = 'dialog-image';
    image.src = src;
    image.alt = title;
    const hint = document.createElement('p');
    hint.className = 'image-hint';
    hint.textContent = '点击图片放大，再次点击还原；放大后可滑动查看';
    const stage = document.createElement('button');
    stage.type = 'button';
    stage.className = 'image-stage';
    stage.dataset.zoomImage = '';
    stage.setAttribute('aria-label', '放大图片');
    stage.setAttribute('aria-pressed', 'false');
    stage.append(image);
    container.append(heading, hint, stage);
    open(container.innerHTML, true);
  }

  function setupHeader() {
    const header = document.querySelector('.site-header');
    if (!header) return;
    const syncHeaderHeight = () => document.documentElement.style.setProperty('--site-header-height', header.offsetHeight + 'px');
    new ResizeObserver(syncHeaderHeight).observe(header);
    syncHeaderHeight();
  }

  function notify(message) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 3200);
  }

  async function copyQQ() {
    try {
      await navigator.clipboard.writeText(QQ);
      notify('QQ 号码已复制');
    } catch (_) {
      notify('QQ：' + QQ + '，可选中号码手动复制');
    }
  }

  document.addEventListener('click', event => {
    const target = event.target.closest('a,button');
    if (!target) return;
    if (target.matches('[data-contact]')) { event.preventDefault(); openContact(); }
    else if (target.matches('[data-payment]')) { event.preventDefault(); openPayment(target.dataset.payment); }
    else if (target.matches('[data-activation-notice]')) { event.preventDefault(); openActivationNotice(); }
    else if (target.matches('[data-payment-choice]')) {
      const product = selectedProduct(target.dataset.paymentChoice);
      const page = target.closest('#paymentPageContent');
      if (page) page.innerHTML = paymentMarkup(product, true);
      else openPayment(product.id);
      const scope = page || dialog;
      [...scope.querySelectorAll('[data-payment-choice]')].find(button => button.dataset.paymentChoice === product.id)?.focus({ preventScroll: true });
    }
    else if (target.matches('[data-copy-qq]')) { event.preventDefault(); copyQQ(); }
    else if (target.matches('[data-zoom-image]')) {
      const zoomed = target.classList.toggle('is-zoomed');
      target.setAttribute('aria-pressed', String(zoomed));
      target.setAttribute('aria-label', zoomed ? '还原图片' : '放大图片');
    }
    else if (target.matches('[data-close-mou]')) dialog.close();
    else if (target.id === 'menuToggle') menu(target.getAttribute('aria-expanded') !== 'true');
    else if (target.closest('#mainNav') && target.tagName === 'A') menu(false);
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') menu(false);
  });
  setupHeader();
  const paymentPage = document.querySelector('#paymentPageContent');
  if (paymentPage && products.length) paymentPage.innerHTML = paymentMarkup(selectedProduct(new URLSearchParams(location.search).get('product')), true);
  window.MouSite = { openPayment, openContact, openImage, openActivationNotice };
}());
