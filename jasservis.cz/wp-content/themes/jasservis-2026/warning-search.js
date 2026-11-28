(() => {
  const panel = document.getElementById('warning-search');
  if (!panel) return;

  const form = panel.querySelector('form');
  const input = panel.querySelector('input');
  const brand = panel.querySelector('select');
  const status = panel.querySelector('[role="status"]');
  const results = panel.querySelector('ul');
  const { ui, aliases, colours, guides, colour_prefixes: colourPrefixes = [], detail_terms: detailTerms = [] } =
    JSON.parse(panel.querySelector('script[type="application/json"]').textContent);
  const catalogueLinks = panel.closest('details').querySelectorAll('nav[aria-labelledby="warning-catalogues-title"] a');
  const brandLinks = new Map();
  const guidesByName = new Map();

  function fold(value) {
    return value.normalize('NFD').toLowerCase().replace(/\p{M}/gu, '').replace(/đ/g, 'd')
      .replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  }

  for (const link of catalogueLinks) {
    const slug = new URL(link.href).searchParams.get('znacka');
    const name = link.textContent.trim();
    if (!slug) continue;
    brandLinks.set(slug, { name, href: link.getAttribute('href') });
    brand.add(new Option(name, slug));
  }
  for (const [name, selector] of Object.entries(guides)) {
    const link = document.querySelector(selector);
    if (link) guidesByName.set(fold(name), link);
  }

  const colourWords = new Map(Object.entries(colours).flatMap(([key, words]) => words.map(word => [fold(word), key])));
  const prefixes = new Set(colourPrefixes.map(fold));
  const vagueWords = new Set(['stop', ...detailTerms.map(fold)]);
  const phrases = Object.entries(aliases).flatMap(([family, entries]) =>
    entries.map(entry => ({ family, phrase: fold(entry) }))
  ).sort((a, b) => b.phrase.length - a.phrase.length);

  let catalogue;
  let timer;
  let revision = 0;

  function loadCatalogue() {
    if (!catalogue) {
      catalogue = fetch(panel.dataset.index)
        .then(response => {
          if (!response.ok) throw new Error('Warning cards are unavailable');
          return response.json();
        })
        .then(({ cards }) => {
          if (!Array.isArray(cards)) throw new Error('Warning cards are invalid');
          return cards
            .filter(card => brandLinks.has(card.brand) && /^[a-z0-9-]+$/i.test(card.id))
            .map(card => ({
              ...card,
              name: fold(card.title),
              text: fold([card.title, card.signal, ...card.keywords].join(' ')),
              colour: new Set(fold(card.signal).split(' ').map(word => colourWords.get(word)).filter(Boolean)),
            }));
        })
        .catch(error => {
          catalogue = undefined;
          throw error;
        });
    }
    return catalogue;
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function matchFamilies(query) {
    const padded = ' ' + query + ' ';
    const exact = phrases.filter(({ phrase }) => phrase === query);
    const embedded = exact.length ? exact : phrases.filter(({ phrase }) => phrase.includes(' ') && padded.includes(' ' + phrase + ' '));
    const longest = embedded[0]?.phrase.length;
    return new Set(embedded.filter(({ phrase }) => phrase.length === longest).map(({ family }) => family));
  }

  function rank(card, query, words, families, requestedColours) {
    const named = words.every(word => card.name.includes(word));
    const described = words.every(word => card.text.includes(word));
    const recognised = card.family.some(family => families.has(family));
    if (!described && !recognised) return 0;

    let score = card.name === query ? 120 : named ? 90 : described ? 50 : 0;
    if (recognised) score += 65;
    if (requestedColours.some(colour => card.colour.has(colour))) score += 22;
    return score;
  }

  function resultLink(href, title, description, image) {
    const item = document.createElement('li');
    const link = document.createElement('a');
    const label = document.createElement('span');
    const name = document.createElement('strong');
    const meta = document.createElement('small');
    link.setAttribute('href', href);
    name.textContent = title;
    meta.textContent = description;
    if (image && /^wp-content\/uploads\/[a-z0-9/_-]+\.(?:svg|png|webp|jpe?g)$/i.test(image)) {
      const icon = new Image(48, 36);
      icon.src = panel.dataset.site + image;
      icon.alt = '';
      icon.loading = 'lazy';
      link.append(icon);
    }
    label.append(name, meta);
    link.append(label);
    item.append(link);
    return item;
  }

  async function search(query, selectedBrand, requestedRevision) {
    const words = query.split(' ');
    const requestedColours = words.map(word => colourWords.get(word)).filter(Boolean);
    const terms = words.filter(word => !colourWords.has(word) && (!requestedColours.length || !prefixes.has(word)));
    if (terms.every(word => vagueWords.has(word))) {
      setStatus(ui.more_detail);
      return;
    }

    setStatus(ui.loading);
    try {
      const cards = await loadCatalogue();
      if (revision !== requestedRevision) return;

      const text = terms.join(' ');
      const families = matchFamilies(text);
      const ranked = cards
        .filter(card => !selectedBrand || selectedBrand === card.brand)
        .map(card => ({ card, score: rank(card, text, terms, families, requestedColours) }))
        .filter(({ score }) => score > 0)
        .sort((a, b) => b.score - a.score);

      const direct = guidesByName.get(query) ?? guidesByName.get(text);
      const total = ranked.length + Number(Boolean(direct));
      const limit = 10;
      const displayed = [];
      if (direct) displayed.push(resultLink(direct.getAttribute('href'), direct.textContent.trim(), ui.guide));
      for (const { card } of ranked.slice(0, limit - displayed.length)) {
        const source = brandLinks.get(card.brand);
        const href = source.href + '#' + encodeURIComponent(card.id);
        const description = [source.name, card.signal].filter(Boolean).join(' · ');
        displayed.push(resultLink(href, card.title, description, card.image));
      }
      results.replaceChildren(...displayed);
      results.hidden = !displayed.length;
      setStatus(total ? ui.count.replace('{shown}', String(displayed.length)).replace('{total}', String(total)) : ui.zero);
    } catch {
      if (revision === requestedRevision) setStatus(ui.error);
    }
  }

  function refresh(delay) {
    clearTimeout(timer);
    const requestedRevision = ++revision;
    const query = fold(input.value);
    results.replaceChildren();
    results.hidden = true;
    setStatus('');
    if (query.length < 2) return;

    timer = setTimeout(() => search(query, brand.value, requestedRevision), delay);
  }

  input.addEventListener('input', () => refresh(180));
  brand.addEventListener('change', () => refresh(0));
  form.addEventListener('submit', event => {
    event.preventDefault();
    refresh(0);
  });
  panel.hidden = false;
})();
