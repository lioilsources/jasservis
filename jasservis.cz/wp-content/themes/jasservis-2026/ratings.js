/* Reuse the existing public rating service. Never publish stale or mismatched data. */
(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-review-source]')];
  if (!cards.length) return;
  const locale = (document.documentElement.lang || 'cs').split('-')[0];
  const words = {
    cs:['recenzí','Aktualizováno','Živé hodnocení J&S SERVIS na Firmy.cz'],
    en:['reviews','Updated','Live rating of J&S SERVIS on Firmy.cz'],
    de:['Bewertungen','Aktualisiert','Aktuelle Bewertung von J&S SERVIS auf Firmy.cz'],
    uk:['відгуків','Оновлено','Актуальна оцінка J&S SERVIS на Firmy.cz'],
    vi:['lượt đánh giá','Cập nhật','Đánh giá hiện tại của J&S SERVIS trên Firmy.cz']
  }[locale] || ['reviews','Updated','J&S SERVIS on Firmy.cz'];
  const googleProfile = 'https://maps.google.com/maps?cid=14113684367371719453';
  const snapshotUrl = new URL('google-rating-snapshot.json', document.currentScript.src).href;
  const maxAge = 48 * 60 * 60 * 1000;
  let loaded = false;
  let expiry;
  function fallback(card) {
    card.querySelector('.review-source-fallback').hidden = false;
    card.querySelector('.review-value')?.remove();
  }
  async function load() {
    if (loaded) return;
    loaded = true;
    const firmy = cards.find(card => card.dataset.reviewSource === 'firmy');
    if (firmy && !firmy.querySelector('.review-source-preview img')) {
      const badge = document.createElement('img');
      badge.width = 249; badge.height = 56; badge.alt = words[2];
      badge.hidden = true; badge.decoding = 'async';
      badge.addEventListener('load', () => {
        badge.hidden = false;
        firmy.querySelector('.review-source-fallback').hidden = true;
      });
      badge.addEventListener('error', () => {
        badge.hidden = true;
        firmy.querySelector('.review-source-fallback').hidden = false;
      });
      firmy.querySelector('.review-source-preview').append(badge);
      badge.src = 'https://www.firmy.cz/img-stars/light-12996882.svg';
    }
    const google = cards.find(card => card.dataset.reviewSource === 'google');
    if (!google || !window.fetch) return;
    google.dataset.ratingState = 'loading';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      let response;
      try {
        response = await fetch('https://jasservis-google-hodnoceni.sleek-bass-5878.chatgpt.site/rating.json', {
          credentials:'omit', cache:'no-store', signal:controller.signal
        });
        if (!response.ok) throw new Error('Rating service unavailable');
      } catch {
        // A dated, verified snapshot remains subject to the same 48-hour limit.
        response = await fetch(snapshotUrl, {credentials:'omit',cache:'no-store'});
      }
      if (!response.ok) throw new Error('Rating unavailable');
      const data = await response.json();
      const timestamp = Date.parse(data.updatedAt);
      const age = Date.now() - timestamp;
      if (data.source !== 'Google' || data.profileUrl !== googleProfile ||
          typeof data.rating !== 'number' || !Number.isFinite(data.rating) || data.rating < 1 || data.rating > 5 ||
          !Number.isSafeInteger(data.count) || data.count < 1 || !Number.isFinite(age) || age < -300000 || age >= maxAge) {
        throw new Error('Invalid rating');
      }
      const value = document.createElement('span'); value.className = 'review-value';
      const rating = document.createElement('strong');
      rating.textContent = new Intl.NumberFormat(locale,{minimumFractionDigits:1,maximumFractionDigits:1}).format(data.rating) + ' / 5';
      const stars = document.createElement('span'); stars.className = 'review-stars review-stars-fill';
      stars.setAttribute('aria-hidden','true'); stars.textContent = '★★★★★';
      const fill = document.createElement('span'); fill.textContent = '★★★★★';
      fill.style.width = (data.rating / 5 * 100) + '%'; stars.append(fill);
      const count = document.createElement('span');
      count.textContent = new Intl.NumberFormat(locale).format(data.count) + ' ' + words[0];
      const updated = document.createElement('small');
      updated.textContent = words[1] + ' ' + new Intl.DateTimeFormat(locale,{dateStyle:'short',timeZone:'Europe/Prague'}).format(new Date(timestamp));
      value.append(rating, stars, count, updated);
      google.querySelector('.review-source-preview').append(value);
      google.querySelector('.review-source-fallback').hidden = true;
      google.dataset.ratingState = 'ready';
      expiry = setTimeout(() => fallback(google), Math.max(1,maxAge - age));
    } catch {
      fallback(google);
      google.dataset.ratingState = 'unavailable';
    } finally {
      clearTimeout(timeout);
    }
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { observer.disconnect(); load(); }
    }, {rootMargin:'180px'});
    cards.forEach(card => observer.observe(card));
  } else load();
  window.addEventListener('pagehide', () => clearTimeout(expiry), {once:true});
  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const google = cards.find(card => card.dataset.reviewSource === 'google');
      if (google) { fallback(google); loaded = false; load(); }
    }
  });
})();
