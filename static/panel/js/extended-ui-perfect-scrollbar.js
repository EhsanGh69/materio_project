/**
 * Perfect Scrollbar
 */
'use strict';

document.addEventListener('DOMContentLoaded', function () {
  (function () {
    const verticalSidebar = document.getElementById('vertical-sidebar'),
          verticalCard = document.getElementById('vertical-card'),
      horizontalExample = document.getElementById('horizontal-example'),
      horizVertExample = document.getElementById('both-scrollbars-example');

    // Vertical Example
    // --------------------------------------------------------------------
    if (verticalSidebar) {
      new PerfectScrollbar(verticalSidebar, {
        wheelPropagation: false
      });
    }
    if (verticalCard) {
      new PerfectScrollbar(verticalCard, {
        wheelPropagation: false
      });
    }

    // Horizontal Example
    // --------------------------------------------------------------------
    if (horizontalExample) {
      new PerfectScrollbar(horizontalExample, {
        wheelPropagation: false,
        suppressScrollY: true
      });
    }

    // Both vertical and Horizontal Example
    // --------------------------------------------------------------------
    if (horizVertExample) {
      new PerfectScrollbar(horizVertExample, {
        wheelPropagation: false
      });
    }
  })();
});
