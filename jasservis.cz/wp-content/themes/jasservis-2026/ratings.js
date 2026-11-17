/* Each provider is verified independently; stale or mismatched values stay hidden. */
(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-review-source]')];
  if (!cards.length || !window.fetch) return;
  const locale = (document.documentElement.lang || 'cs').split('-')[0];
  const words = {
    cs:['recenzí','hodnocení','Ověřeno'],
    en:['reviews','reviews','Verified'],
    de:['Bewertungen','Bewertungen','Geprüft'],
    uk:['відгуків','відгуків','Перевірено'],
    vi:['lượt đánh giá','lượt đánh giá','Đã xác minh']
  }[locale] || ['reviews','reviews','Verified'];
  const scriptUrl = document.currentScript.src;
  const service = 'https://jasservis-google-hodnoceni.sleek-bass-5878.chatgpt.site/';
  const sources = [
    {id:'google', source:'Google', profile:'https://maps.google.com/maps?cid=14113684367371719453', snapshot:'google-rating-snapshot.json', endpoint:'rating.json', countWord:words[0]},
    {id:'firmy', source:'Firmy.cz', profile:'https://www.firmy.cz/detail/12996882-j-s-servis-jaroslav-mateju-statenice-cerny-vul.html', snapshot:'firmy-rating-snapshot.json', endpoint:'firmy-rating.json', countWord:words[1]}
  ];
  const maxAge = 48 * 60 * 60 * 1000;
  const expiry = new Map();
  let generation = 0;
  function fallback(card) {
    clearTimeout(expiry.get(card));
    expiry.delete(card);
    card.querySelector('.review-source-fallback').hidden = false;
    card.querySelector('.review-value')?.remove();
    card.dataset.ratingState = 'unavailable';
  }
  function validate(data, source) {
    const timestamp = Date.parse(data && data.updatedAt);
    const age = Date.now() - timestamp;
    if (!data || data.source !== source.source || data.profileUrl !== source.profile ||
        typeof data.rating !== 'number' || !Number.isFinite(data.rating) || data.rating < 1 || data.rating > 5 ||
        !Number.isSafeInteger(data.count) || data.count < 1 || !Number.isFinite(age) || age < -300000 || age >= maxAge) {
      throw new Error('Invalid rating');
    }
    return timestamp;
  }
  async function readRating(url, source) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(url, {credentials:'omit', cache:'no-store', signal:controller.signal});
      if (!response.ok) throw new Error('Rating unavailable');
      const data = await response.json();
      return {data, timestamp:validate(data, source)};
    } finally { clearTimeout(timeout); }
  }
  function render(card, source, data, timestamp) {
    const value = document.createElement('span'); value.className = 'review-value';
    const rating = document.createElement('strong');
    rating.textContent = new Intl.NumberFormat(locale,{minimumFractionDigits:1,maximumFractionDigits:1}).format(data.rating) + ' / 5';
    const stars = document.createElement('span'); stars.className = 'review-stars review-stars-fill';
    stars.setAttribute('aria-hidden','true'); stars.textContent = '★★★★★';
    const fill = document.createElement('span'); fill.textContent = '★★★★★';
    fill.style.width = (data.rating / 5 * 100) + '%'; stars.append(fill);
    const count = document.createElement('span');
    count.textContent = new Intl.NumberFormat(locale).format(data.count) + ' ' + source.countWord;
    const updated = document.createElement('small');
    updated.textContent = words[2] + ' ' + new Intl.DateTimeFormat(locale,{dateStyle:'short',timeZone:'Europe/Prague'}).format(new Date(timestamp));
    value.append(rating, stars, count, updated);
    card.querySelector('.review-value')?.remove();
    card.querySelector('.review-source-preview').append(value);
    card.querySelector('.review-source-fallback').hidden = true;
    card.dataset.ratingState = 'ready';
    clearTimeout(expiry.get(card));
    expiry.set(card, setTimeout(() => fallback(card), Math.max(1, timestamp + maxAge - Date.now())));
  }
  async function loadSource(source, request) {
    const card = cards.find(card => card.dataset.reviewSource === source.id);
    if (!card) return;
    card.dataset.ratingState = 'loading';
    let latestTimestamp = -Infinity;
    let shown = false;
    const urls = [new URL(source.snapshot,scriptUrl).href, service + source.endpoint];
    await Promise.allSettled(urls.map(async url => {
      const {data, timestamp} = await readRating(url, source);
      if (request !== generation || timestamp < latestTimestamp) return;
      latestTimestamp = timestamp;
      render(card, source, data, timestamp);
      shown = true;
    }));
    if (!shown && request === generation) fallback(card);
  }
  function load() {
    const request = ++generation;
    sources.forEach(source => { loadSource(source, request); });
  }
  load();
  window.addEventListener('pagehide', () => {
    expiry.forEach(timer => clearTimeout(timer)); expiry.clear(); generation++;
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted) { cards.forEach(fallback); load(); }
  });
})();
