(function () {
  'use strict';
  const config = window.MOU_PROMO_CONFIG;
  const content = config.promo_content;
  const products = content.products;
  const grid = document.querySelector('#productGrid');
  const filters = document.querySelector('#productFilters');
  const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));

  function visual(product) {
    const src = escape(product.image_url);
    const title = escape(product.title);
    if (product.kind === 'tax' || product.kind === 'service') return '<div class="phone" aria-hidden="true"><div class="phone-screen"><img class="custom-screen" src="' + src + '" alt="' + title + '高清预览"></div><span class="island"></span></div>';
    return '<img class="product-cover ' + (product.kind === 'document' ? 'is-document' : 'is-service') + '" src="' + src + '" alt="' + title + '高清展示图" loading="lazy">';
  }

  function primaryAction(product) {
    if (product.action_type === 'activation_notice') return '<button type="button" data-download-notice>' + escape(product.action_label) + ' <span aria-hidden="true">↗</span></button>';
    if (product.action_type === 'link') return '<a href="' + escape(product.action_url) + '">' + escape(product.action_label) + ' <span aria-hidden="true">↗</span></a>';
    return '<button type="button" data-contact>' + escape(product.action_label) + ' <span aria-hidden="true">↗</span></button>';
  }

  function renderProducts(category) {
    const categories = ['', ...new Set(products.map(product => product.category))];
    filters.innerHTML = categories.map(item => '<button type="button" data-category="' + escape(item) + '" aria-pressed="' + (category === item) + '">' + escape(item || '全部品类') + '</button>').join('');
    grid.innerHTML = products.filter(product => !category || category === product.category).map(product => {
      const title = escape(product.title);
      const detail = 'promo-detail.html?id=' + encodeURIComponent(product.id);
      const description = product.description ? '<p>' + escape(product.description) + '</p>' : '';
      const anchor = product.id === 'leave' ? ' id="leave-certificate"' : '';
      return '<article class="product-card"' + anchor + ' data-product-id="' + escape(product.id) + '"><a class="product-visual" href="' + detail + '" aria-label="了解' + title + '"><span class="product-visual-label">' + (product.kind === 'service' ? 'CREATIVE SERVICE' : 'PRODUCT PREVIEW') + '</span>' + visual(product) + '</a><div class="product-heading"><h3>' + title + '</h3><strong class="product-price"><small>¥</small>' + product.price_cny + '<small>元</small></strong></div><span class="product-platform">' + escape(product.platform_label) + '</span>' + description + '<div class="product-actions"><a href="' + detail + '">查看详情 <span aria-hidden="true">→</span></a><i aria-hidden="true"></i>' + primaryAction(product) + '<button type="button" class="purchase-link" data-payment="' + escape(product.id) + '">' + product.price_cny + '元 · 扫码付款 <span aria-hidden="true">↗</span></button></div></article>';
    }).join('');
    grid.classList.toggle('is-filtered', Boolean(category));
  }

  document.querySelectorAll('[data-text]').forEach(node => {
    node.textContent = String(content[node.dataset.text] || '');
  });
  document.querySelector('#year').textContent = new Date().getFullYear();
  document.querySelector('#contactLabel').textContent = '联系咨询';
  document.querySelector('#screenshots').hidden = false;
  document.querySelector('#screenshotGrid').innerHTML = config.phone_images.map((shot, index) => '<button type="button" class="screenshot-tile" data-image="' + index + '" aria-label="放大' + escape(shot.title) + '"><img src="' + escape(shot.image_url) + '" alt="' + escape(shot.title) + '" loading="lazy"><strong>' + escape(shot.title) + '</strong>' + (shot.description ? '<p>' + escape(shot.description) + '</p>' : '') + '</button>').join('');
  document.querySelector('#faqList').innerHTML = content.faqs.map((item, index) => '<details' + (index === 0 ? ' open class="faq-notice"' : '') + '><summary>' + escape(item.question) + '</summary>' + (item.points ? '<ul class="faq-points">' + item.points.map(point => '<li>' + escape(point) + '</li>').join('') + '</ul>' : '<p>' + escape(item.answer) + '</p>') + '</details>').join('');
  renderProducts('');

  document.addEventListener('click', event => {
    const target = event.target.closest('button');
    if (!target) return;
    if (target.matches('[data-category]')) {
      const category = target.dataset.category;
      renderProducts(category);
      [...filters.children].find(item => item.dataset.category === category)?.focus({ preventScroll: true });
    } else if (target.matches('[data-image]')) {
      const image = config.phone_images[Number(target.dataset.image)];
      window.MouSite.openImage(image.image_url, image.title);
    }
  });
}());
