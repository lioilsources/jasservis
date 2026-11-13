(function () {
  'use strict';
  // Remove the temporary message after November in Europe/Prague local time.
  if (Date.now() >= Date.parse('2026-12-01T00:00:00+01:00')) {
    document.querySelectorAll('.site-reconstruction').forEach(function (notice) {
      notice.hidden = true;
    });
  }
}());
