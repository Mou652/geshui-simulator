(function () {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const id = new URLSearchParams(location.search).get('id') || '';

  function safeUrl(value) {
    const raw = typeof value === 'string' ? value.trim() : '';
    if (!raw || /[\\\u0000-\u001f\u007f-\u009f]/.test(raw)) return '';
    let decoded = raw;
    try {
      for (let index = 0; index < 3; index++) decoded = decodeURIComponent(decoded);
    } catch (_) { return ''; }
    if (/[\\\u0000-\u001f\u007f-\u009f]/.test(decoded) || decoded.startsWith('//')) return '';
    if (/^https?:\/\//i.test(raw)) {
      try {
        const url = new URL(raw);
        return url.hostname && !url.username && !url.password ? url.href : '';
      } catch (_) { return ''; }
    }
    if (/^[a-z][a-z0-9+.-]*:/i.test(decoded) || decoded.split(/[/?#]/).includes('..')) return '';
    return raw.replace(/ /g, '%20');
  }
  function assetUrl(value) {
    return safeUrl(value);
  }
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text == null ? '' : text);
    return node;
  }
  function state(message) {
    $('#detailContent').hidden = true;
    $('#mobileActions').hidden = true;
    const box = $('#detailState');
    box.replaceChildren(element('h1', '', message));
    box.hidden = false;
    const back = element('a', 'button button-outline', '返回产品列表');
    back.href = 'index.html#products';
    box.append(back);
  }
  function renderActions(product) {
    for (const selector of ['#heroActions', '#mobileActions']) {
      const box = $(selector);
      box.replaceChildren();
      const action = element(product.action_type === 'link' ? 'a' : 'button', 'button button-primary', product.action_label);
      if (product.action_type === 'link') action.href = assetUrl(product.action_url);
      else {
        action.type = 'button';
        if (product.action_type === 'activation_notice') action.dataset.downloadNotice = '';
        else action.dataset.contact = '';
      }
      box.append(action);
      const payment = element('button', 'button button-outline', product.price_cny + '元 · 扫码付款');
      payment.type = 'button';
      payment.dataset.payment = String(product.id);
      payment.setAttribute('aria-label', '扫码付款 · ' + product.title);
      box.append(payment);
      if (selector === '#heroActions') {
        const contact = element('button', 'button button-outline', '联系 QQ');
        contact.type = 'button';
        contact.dataset.contact = '';
        box.append(contact);
      }
      if (selector === '#mobileActions') box.hidden = false;
    }
  }
  function renderImage(src, alt, className) {
    const button = element('button', 'detail-image-trigger');
    button.type = 'button';
    button.dataset.imagePreview = '';
    button.setAttribute('aria-label', '查看大图：' + String(alt || '产品界面'));
    button.setAttribute('aria-haspopup', 'dialog');
    const img = element('img', className);
    img.src = src;
    img.alt = String(alt || '产品界面');
    img.loading = 'lazy';
    img.addEventListener('error', () => { button.replaceWith(element('span', 'detail-image-fallback', '图片暂时无法显示')); });
    button.append(img);
    return button;
  }
  let imageTrigger = null;
  let readingOverflow = '';
  function restoreImageView() {
    if (!imageTrigger) return;
    document.body.style.overflow = readingOverflow;
    const trigger = imageTrigger;
    imageTrigger = null;
    $('#imageDialogImage').removeAttribute('src');
    if (trigger.isConnected) trigger.focus({ preventScroll: true });
  }
  function closeImage() {
    const dialog = $('#imageDialog');
    if (dialog.open && typeof dialog.close === 'function') dialog.close();
    else dialog.removeAttribute('open');
    restoreImageView();
  }
  function openImage(trigger) {
    const thumbnail = trigger.querySelector('img');
    if (!thumbnail) return;
    const dialog = $('#imageDialog');
    const image = $('#imageDialogImage');
    const caption = trigger.closest('figure')?.querySelector('figcaption')?.textContent;
    if (imageTrigger) closeImage();
    imageTrigger = trigger;
    readingOverflow = document.body.style.overflow;
    $('#imageDialogTitle').textContent = caption || thumbnail.alt || '产品界面';
    $('#imageDialogStatus').hidden = true;
    image.hidden = false;
    image.alt = thumbnail.alt;
    image.src = thumbnail.getAttribute('src');
    document.body.style.overflow = 'hidden';
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
    $('.detail-image-stage').scrollTop = 0;
    dialog.querySelector('[data-close-image]').focus({ preventScroll: true });
  }
  function renderVisual(product, allowBlob) {
    const src = assetUrl(product.detail_image_url || product.image_url, allowBlob);
    const hero = $('#detailVisual');
    const feature = $('#featureVisual');
    hero.replaceChildren(); feature.replaceChildren();
    if (src) {
      hero.append(renderImage(src, product.title, 'detail-hero-image'));
      feature.append(renderImage(src, product.title, 'detail-feature-image'));
    } else {
      for (const box of [hero, feature]) {
        const phone = element('div', 'detail-phone');
        phone.append(element('span', 'detail-island'));
        const screen = element('div', 'detail-phone-screen');
        screen.append(element('small', '', '9:41'), element('h3', '', product.title || 'App'), element('p', '', product.description || '功能演示'));
        for (const label of ['功能总览', '场景体验', '使用说明']) screen.append(element('div', 'detail-phone-row', label + '　›'));
        phone.append(screen); box.append(phone);
      }
    }
  }
  function align(node, attrs) {
    if (attrs && ['left', 'center', 'right'].includes(attrs.textAlign)) node.style.textAlign = attrs.textAlign;
  }
  function inlineNode(node) {
    if (!node || typeof node !== 'object') return null;
    if (node.type === 'hardBreak') return document.createElement('br');
    if (node.type !== 'text') return null;
    let result = document.createTextNode(typeof node.text === 'string' ? node.text : '');
    const tags = Object.assign(Object.create(null), { bold: 'strong', italic: 'em', underline: 'u', strike: 's' });
    const marks = Array.isArray(node.marks) ? node.marks : [];
    for (const mark of marks) {
      if (!mark || typeof mark !== 'object') continue;
      let wrapper;
      if (mark.type === 'link') {
        const href = assetUrl(mark.attrs && mark.attrs.href, false);
        if (!href) continue;
        wrapper = element('a'); wrapper.href = href;
        wrapper.target = '_blank'; wrapper.rel = 'noopener noreferrer';
      } else if (tags[mark.type]) wrapper = element(tags[mark.type]);
      if (wrapper) { wrapper.append(result); result = wrapper; }
    }
    return result;
  }
  function renderBlock(node, allowBlob, depth, count) {
    if (!node || typeof node !== 'object' || depth > 20 || ++count.value > 2000) return null;
    const attrs = node.attrs && typeof node.attrs === 'object' ? node.attrs : {};
    const tags = Object.assign(Object.create(null), { paragraph: 'p', heading: attrs.level === 3 ? 'h3' : 'h2', bulletList: 'ul', orderedList: 'ol', listItem: 'li', blockquote: 'blockquote', horizontalRule: 'hr' });
    if (node.type === 'image') {
      const src = assetUrl(attrs.src, allowBlob);
      if (!src) return null;
      const figure = element('figure', 'detail-figure');
      const width = attrs.width;
      if (Number.isInteger(width) && width >= 25 && width <= 100) figure.style.width = width + '%';
      align(figure, attrs);
      if (attrs.textAlign === 'right') figure.style.marginLeft = 'auto';
      if (attrs.textAlign === 'center') { figure.style.marginLeft = 'auto'; figure.style.marginRight = 'auto'; }
      figure.append(renderImage(src, attrs.alt || '', 'detail-article-image'));
      if (attrs.caption) figure.append(element('figcaption', '', attrs.caption));
      return figure;
    }
    const tag = tags[node.type];
    if (!tag) return null;
    const output = element(tag);
    if (node.type === 'paragraph' || node.type === 'heading') align(output, attrs);
    if (node.type === 'orderedList' && Number.isInteger(attrs.start) && attrs.start >= 1 && attrs.start <= 9999) output.start = attrs.start;
    const children = Array.isArray(node.content) ? node.content : [];
    for (const child of children) {
      const rendered = node.type === 'paragraph' || node.type === 'heading' ? inlineNode(child) : renderBlock(child, allowBlob, depth + 1, count);
      if (rendered) output.append(rendered);
    }
    return output;
  }
  function renderArticle(product, allowBlob) {
    const article = $('#detailArticle');
    article.replaceChildren();
    if (product.details_doc === null || product.details_doc === undefined) {
      const legacy = String(product.details || product.description || '').trim();
      for (const paragraph of legacy.split(/\n\s*\n/).filter(Boolean)) article.append(element('p', '', paragraph));
    } else if (product.details_doc && product.details_doc.type === 'doc' && Array.isArray(product.details_doc.content)) {
      const count = { value: 0 };
      for (const node of product.details_doc.content) {
        const rendered = renderBlock(node, allowBlob, 1, count);
        if (rendered) article.append(rendered);
      }
    }
    if (!article.childNodes.length) article.append(element('p', 'detail-empty-article', '暂无图文介绍。'));
    const toc = $('#articleToc'); toc.replaceChildren();
    article.querySelectorAll('h2,h3').forEach((heading, index) => {
      heading.id = 'article-heading-' + (index + 1);
      const link = element('a', heading.tagName === 'H3' ? 'toc-sub' : '', heading.textContent || '小节');
      link.href = '#' + heading.id; toc.append(link);
    });
    if (!toc.childNodes.length) {
      const link = element('a', '', '产品介绍'); link.href = '#articleSection'; toc.append(link);
    }
  }
  function render(config) {
    const allowBlob = false;
    if (imageTrigger) closeImage();
    const content = config && config.promo_content;
    const products = content && Array.isArray(content.products) ? content.products : [];
    const product = ['tax', 'leave', 'recording', 'image-editing'].includes(id) ? products.find(item => item && String(item.id) === id) : null;
    if (!product || product.enabled === false || product.enabled === 0) { state('未找到该产品，请返回产品列表选择。'); return; }
    $('#detailState').hidden = true;
    $('#detailContent').hidden = false;
    $('#brandName').textContent = $('#footerBrand').textContent = String(content.brand_name || '灵活就业指导');
    $('#brandTagline').textContent = String(content.brand_tagline || 'CAREER & TOOLS');
    const logo = assetUrl(content.logo_url, allowBlob) || 'assets/promo/logo.svg';
    document.querySelectorAll('.detail-page .brand-logo').forEach(image => { image.src = logo; });
    $('#detailTitle').textContent = $('#crumbProduct').textContent = String(product.title || 'App 产品');
    $('#detailCategory').textContent = product.category + ' · ' + product.platform_label;
    $('#detailDescription').textContent = String(product.description || '');
    $('#detailDescription').hidden = !product.description;
    $('#detailPrice').textContent = '¥ ' + product.price_cny + ' 元';
    $('#detailSummary').textContent = product.details_doc == null ? String(product.details || '') : '';
    $('#featureDescription').textContent = String(product.description || '');
    $('#featureDescription').hidden = !product.description;
    document.title = String(content.brand_name || '灵活就业指导');
    renderVisual(product, allowBlob);
    renderArticle(product, allowBlob);
    renderActions(product, config);
    const steps = product.kind === 'service'
      ? [['沟通需求', '先联系 QQ 2430239942 确认素材与制作需求。'], ['扫码付款', '确认品类后支付 ' + product.price_cny + ' 元。'], ['制作与交付', '发送付款凭证，按沟通结果制作与交付。']]
      : product.id === 'tax'
        ? [['确认安卓设备', '目前仅支持安卓，iOS 版本近日即将更新。'], ['扫码付款', '购买个税 App，付款金额 179 元。'], ['获取激活码', '联系 QQ 2430239942 获取激活码及安装说明。']]
        : [['打开网页工具', '填写示例资料并预览版式。'], ['扫码付款', '购买离职证明，付款金额 79 元。'], ['确认并导出', '按网页说明完成授权与 PDF 保存。']];
    const stepBox = $('.detail-steps');
    stepBox.replaceChildren();
    steps.forEach((step, index) => {
      const block = element('div');
      block.append(element('b', '', String(index + 1).padStart(2, '0')), element('strong', '', step[0]), element('p', '', step[1]));
      stepBox.append(block);
    });
  }
  function load() {
    try {
      render(window.MOU_PROMO_CONFIG || {});
    } catch (_) {
      state('产品资料暂时无法显示，请返回产品列表。');
    }
  }
  document.addEventListener('click', event => {
    const target = event.target.closest('a,button');
    if (!target) return;
    if (target.matches('[data-image-preview]')) { openImage(target); return; }
    if (target.matches('[data-close-image]')) { closeImage(); return; }
  });
  document.querySelectorAll('.detail-page .brand-logo').forEach(image => {
    image.addEventListener('error', () => {
      if (image.getAttribute('src') !== 'assets/promo/logo.svg') image.src = 'assets/promo/logo.svg';
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if ($('#imageDialog').open) { event.preventDefault(); closeImage(); }
    }
    // 兼容没有原生模态弹窗的浏览器，避免 Tab 跳到背景页面。
    if (event.key === 'Tab' && $('#imageDialog').open) {
      event.preventDefault();
      const close = $('#imageDialog [data-close-image]');
      const stage = $('.detail-image-stage');
      (document.activeElement === close ? stage : close).focus({ preventScroll: true });
    }
  });
  $('#imageDialog').addEventListener('click', event => {
    if (event.target === event.currentTarget) closeImage();
  });
  $('#imageDialog').addEventListener('cancel', event => { event.preventDefault(); closeImage(); });
  $('#imageDialog').addEventListener('close', () => { if (!$('#imageDialog').open) restoreImageView(); });
  $('#imageDialogImage').addEventListener('error', () => {
    if (!$('#imageDialog').open) return;
    $('#imageDialogImage').hidden = true;
    $('#imageDialogStatus').hidden = false;
  });
  load();
})();
