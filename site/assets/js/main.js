/**
 * 拓达昇官网 - 主脚本
 * 职责：平滑滚动锚点、通用交互
 */

(function () {
  'use strict';

  /* 平滑滚动（锚点链接） */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
