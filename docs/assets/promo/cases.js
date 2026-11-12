(function () {
  'use strict';
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-case-image]');
    if (button) window.MouSite.openImage(button.dataset.caseImage, button.dataset.caseTitle);
  });
}());
