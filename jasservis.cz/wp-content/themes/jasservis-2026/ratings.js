/* Prefer verified same-origin data. Never publish stale or mismatched ratings. */
(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-review-source]')];
  if (!cards.length) return;
  const locale = (document.documentElement.lang || 'cs').split('-')[0];
  const words = {
    cs:['recenzí','Ověřeno','Živé hodnocení J&S SERVIS na Firmy.cz'],
    en:['reviews','Verified','Live rating of J&S SERVIS on Firmy.cz'],
    de:['Bewertungen','Geprüft','Aktuelle Bewertung von J&S SERVIS auf Firmy.cz'],
    uk:['відгуків','Перевірено','Актуальна оцінка J&S SERVIS на Firmy.cz'],
    vi:['lượt đánh giá','Đã xác minh','Đánh giá hiện tại của J&S SERVIS trên Firmy.cz']
  }[locale] || ['reviews','Verified','J&S SERVIS on Firmy.cz'];
  const googleProfile = 'https://maps.google.com/maps?cid=14113684367371719453';
  const firmyProfile = 'https://www.firmy.cz/detail/12996882-j-s-servis-jaroslav-mateju-statenice-cerny-vul.html';
  const snapshotUrl = new URL('google-rating-snapshot.json', document.currentScript.src).href;
  const firmySnapshotUrl = new URL('firmy-rating-snapshot.json', document.currentScript.src).href;
  const maxAge = 48 * 60 * 60 * 1000;
  let loaded = false;
  let expiry;
  let firmyExpiry;
  let generation = 0;
  function fallback(card) {
    card.querySelector('.review-source-fallback').hidden = false;
    card.querySelector('.review-value')?.remove();
    card.dataset.ratingState = 'unavailable';
  }
  function validate(data, source = 'Google', profile = googleProfile) {
    const timestamp = Date.parse(data.updatedAt);
    const age = Date.now() - timestamp;
    if (data.source !== source || data.profileUrl !== profile ||
        typeof data.rating !== 'number' || !Number.isFinite(data.rating) || data.rating < 1 || data.rating > 5 ||
        !Number.isSafeInteger(data.count) || data.count < 1 || !Number.isFinite(age) || age < -300000 || age >= maxAge) {
      throw new Error('Invalid rating');
    }
    return {timestamp, age};
  }
  async function readRating(url, source = 'Google', profile = googleProfile) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(url, {credentials:'omit', cache:'no-store', signal:controller.signal});
      if (!response.ok) throw new Error('Rating unavailable');
      const data = await response.json();
      return {data, ...validate(data, source, profile)};
    } finally {
      clearTimeout(timeout);
    }
  }
  async function loadFirmyCount(card, request) {
    let latestTimestamp = -Infinity;
    await Promise.allSettled([firmySnapshotUrl, 'https://jasservis-google-hodnoceni.sleek-bass-5878.chatgpt.site/firmy-rating.json'].map(async url => {
      const {data, timestamp, age} = await readRating(url, 'Firmy.cz', firmyProfile);
      if (request !== generation || timestamp < latestTimestamp) return;
      latestTimestamp = timestamp;
      const value = document.createElement('span');
      value.className = 'review-value review-firmy-value';
      const count = document.createElement('span');
      count.textContent = new Intl.NumberFormat(locale).format(data.count) + ' ' + words[0];
      const updated = document.createElement('small');
      updated.textContent = words[1] + ' ' + new Intl.DateTimeFormat(locale,{dateStyle:'short',timeZone:'Europe/Prague'}).format(new Date(timestamp));
      value.append(count, updated);
      card.querySelector('.review-firmy-value')?.remove();
      card.querySelector('.review-source-preview').append(value);
      card.dataset.ratingState = 'ready';
      card.dataset.countSource = url === firmySnapshotUrl ? 'snapshot' : 'live';
      clearTimeout(firmyExpiry);
      firmyExpiry = setTimeout(() => {
        card.querySelector('.review-firmy-value')?.remove();
        card.dataset.ratingState = 'unavailable';
      }, Math.max(1,maxAge - age));
    }));
  }
  async function load() {
    if (loaded) return;
    loaded = true;
    const request = ++generation;
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
    if (firmy) loadFirmyCount(firmy, request);
    const google = cards.find(card => card.dataset.reviewSource === 'google');
    if (!google || !window.fetch) return;
    google.dataset.ratingState = 'loading';
    let latestTimestamp = -Infinity;
    let shown = false;
    await Promise.allSettled([snapshotUrl, 'https://jasservis-google-hodnoceni.sleek-bass-5878.chatgpt.site/rating.json'].map(async url => {
      const {data, timestamp, age} = await readRating(url);
      if (request !== generation || timestamp < latestTimestamp) return;
      latestTimestamp = timestamp;
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
      google.querySelector('.review-value')?.remove();
      google.querySelector('.review-source-preview').append(value);
      google.querySelector('.review-source-fallback').hidden = true;
      google.dataset.ratingState = 'ready';
      clearTimeout(expiry);
      expiry = setTimeout(() => fallback(google), Math.max(1,maxAge - age));
      shown = true;
    }));
    if (!shown && request === generation) fallback(google);
  }
  load();
  window.addEventListener('pagehide', () => { clearTimeout(expiry); clearTimeout(firmyExpiry); generation++; });
  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const google = cards.find(card => card.dataset.reviewSource === 'google');
      if (google) { fallback(google); loaded = false; load(); }
    }
  });
})();
