import { readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

// Run with node jasservis.cz/_warnings/generate-warning-search.mjs.
// Add --check to verify that all public indexes match their source pages.
const site = fileURLToPath(new URL('../', import.meta.url));
const locales = ['', 'de', 'en', 'uk', 'vi'];
const brands = ['volkswagen', 'audi', 'skoda', 'seat', 'cupra', 'volkswagen-uzitkove-vozy'];
const check = process.argv.includes('--check');
const entities = { amp: '&', apos: "'", gt: '>', lt: '<', nbsp: ' ', quot: '"' };

function textContent(html) {
  return html.replace(/<[^>]*>/g, '').replace(/&(#x[\da-f]+|#\d+|[a-z]+);/gi, (entity, name) => {
    if (name.startsWith('#x')) return String.fromCodePoint(Number.parseInt(name.slice(2), 16));
    if (name.startsWith('#')) return String.fromCodePoint(Number.parseInt(name.slice(1), 10));
    if (!Object.hasOwn(entities, name)) throw new Error(`Unsupported HTML entity ${entity}`);
    return entities[name];
  }).replace(/\s+/g, ' ').trim();
}

function attributes(tag) {
  return Object.fromEntries(
    Array.from(tag.matchAll(/\s+([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g),
      ([, name, doubleQuoted, singleQuoted]) => [name.toLowerCase(), doubleQuoted ?? singleQuoted]),
  );
}

function imagePath(markup, file) {
  const image = markup.match(/<img\b(?:[^"'<>]|"[^"]*"|'[^']*')*>/i);
  if (!image) return undefined;

  const src = attributes(image[0]).src;
  if (!src || !/^(?:\.\.\/)+wp-content\/uploads\/kontrolky\/[\w./-]+\.(?:svg|png|jpe?g|webp|avif)$/i.test(src)) {
    throw new Error(`Unexpected warning image in ${file}: ${src}`);
  }
  const asset = resolve(dirname(file), src);
  const path = relative(site, asset).split(sep).join('/');
  if (!path.startsWith('wp-content/uploads/kontrolky/') || !statSync(asset).isFile()) {
    throw new Error(`Missing warning image in ${file}: ${path}`);
  }
  return path;
}

function readCard(markup, brand, id, file) {
  const fields = { 'wl-name': [], 'wl-variant-name': [], 'wl-status': [] };
  const labelTags = /<(h3|h4|p)\b((?:[^"'<>]|"[^"]*"|'[^']*')*)>([\s\S]*?)<\/\1>/gi;
  for (const [, , tag, html] of markup.matchAll(labelTags)) {
    const className = attributes(tag).class;
    if (Object.hasOwn(fields, className)) fields[className].push(textContent(html));
  }
  const [title] = fields['wl-name'];
  const statuses = [...new Set(fields['wl-status'])];
  if (fields['wl-name'].length !== 1 || !title || !statuses.length || statuses.includes('')) {
    throw new Error(`Incomplete warning card ${id} in ${file}`);
  }
  return {
    brand,
    id,
    title,
    statuses,
    keywords: [...new Set(fields['wl-variant-name'])].filter(keyword => keyword && keyword !== title),
    image: imagePath(markup, file),
  };
}

function readCatalogue(locale, brand) {
  const file = resolve(site, locale, 'rady-pro-ridice', `kontrolky-${brand}`, 'index.html');
  const html = readFileSync(file, 'utf8');
  const tags = /<(\/?)\s*(section|article)\b((?:[^"'<>]|"[^"]*"|'[^']*')*)>/gi;
  const cards = [];
  const ids = new Set();
  let warningsDepth = 0;
  let openCard;
  for (const tag of html.matchAll(tags)) {
    const [markup, closing, rawName, source] = tag;
    const name = rawName.toLowerCase();
    if (name === 'section' && closing) {
      if (warningsDepth) warningsDepth--;
      continue;
    }
    if (name === 'section') {
      if (warningsDepth || attributes(source).id === 'prehled-kontrolek') warningsDepth++;
      continue;
    }
    if (!warningsDepth) continue;
    if (closing) {
      if (openCard) {
        cards.push(readCard(html.slice(openCard.start, tag.index), brand, openCard.id, file));
        openCard = undefined;
      }
      continue;
    }
    const { class: className, id, 'data-brand': cardBrand } = attributes(source);
    const classes = (className ?? '').split(/\s+/);
    if (!classes.includes('wl-card') || classes.includes('wl-infotainment-card')) continue;
    if (cardBrand !== brand || !/^kontrolka-[a-z\d-]+$/.test(id) || ids.has(id) || openCard) {
      throw new Error(`Unexpected warning card ${id} in ${file}`);
    }
    ids.add(id);
    openCard = { id, start: tag.index + markup.length };
  }
  if (openCard || warningsDepth || !cards.length) throw new Error(`Incomplete warning catalogue ${file}`);
  return cards;
}

// Identify aliases from the displayed warning and its known Czech fragment.
// Dashboard markings with a different meaning keep their own search family.
const familyRules = [
  ['oil_pressure', /^(?:a|oil-pressure|vwcv-oil-pressure-flashing)$/, /tlak motorového oleje/i],
  ['oil_level', /^toledo-oil-level$/, /hladina oleje/i],
  ['battery', /^(?:j|audi-12v-system-red|ev-12v-red|ev-12v-yellow-connection|ev-12v-yellow-replace|enyaq-12v-charge-fault|vwcv-battery-charge-fault)$/, /akumulátor|dobíjení|elektrická soustava|12v/i],
  ['coolant', /^(?:c|vw-c|enyaq-coolant|toledo-coolant-cold|toledo-coolant-red|ev-coolant)$/, /chlad|chlaz|motor ještě není zahřátý/i],
  ['brakes', /^(?:d|e|brake-fault|brake-fluid|pads-worn|parking-applied|brake-servo|caddy-brake-servo-yellow-restricted|mii-foot-brake)$/, /brzd/i],
  ['parking_brake', /^parking-applied$/, /parkovací brzda/i],
  ['engine', /^(?:f|mil-steady)$/, /emisní systém|řízení motoru/i],
  ['tyre', /^(?:i|tpms-low|audi-tpms-fault)$/, /pneumatik|tpms/i],
  ['abs', /^(?:abs|abs-fault)$/, /\bABS\b/i],
  ['airbag', /^(?:airbag|airbag-fault|airbag-diagnostic-off)$/, /airbag/i],
  ['steering', /^(?:steering-red|steering-yellow|vwcv-steering-red|vwcv-steering-yellow)$/, /řízení/i],
  ['epc', /^epc$/, /\bEPC\b/i],
  ['dpf', /^(?:h|vw-h)$/, /filtr pevných částic|\bDPF\b/i],
  ['adblue', /^adblue(?:-|$)/, /\bAdBlue\b/i],
  ['glow', /^(?:glow-preheat|glow-fault)$/, /žhavení|spirála/i],
];

function families(card) {
  const key = card.id.slice('kontrolka-'.length);
  const suffix = `-${card.brand}`;
  const symbol = key.endsWith(suffix) ? key.slice(0, -suffix.length) : key;
  const result = familyRules.filter(([, id]) => id.test(symbol)).map(([family, , title]) => {
    if (!title.test(card.title)) throw new Error(`Verify ${family} classification for ${card.id}`);
    return family;
  });
  if (result.includes('brakes') && /\/brake-(?:cervena|zluta)\.svg$/.test(card.image ?? '')) {
    result.push('circle_exclamation');
  }
  return result;
}

const key = ({ brand, id }) => `${brand}#${id}`;
const czech = brands.flatMap(brand => readCatalogue('', brand));
const catalogueKeys = new Set(czech.map(key));
const controlLabel = 'Ovládací znak (nikoli výstraha)';
const searchableCzech = czech.filter(({ statuses }) =>
  !statuses.every(status => status.split(' · ').at(-1) === controlLabel),
);
const czechFamilies = new Map(searchableCzech.map(card => [key(card), families(card)]));
const outputs = locales.map(locale => {
  const cards = locale ? brands.flatMap(brand => readCatalogue(locale, brand)) : czech;
  if (cards.length !== catalogueKeys.size || cards.some(card => !catalogueKeys.has(key(card)))) {
    throw new Error(`Catalogue fragments disagree in ${locale || 'cs'}`);
  }
  const indexed = cards.filter(card => czechFamilies.has(key(card))).map(card => {
    const { brand, id, title, statuses, keywords, image } = card;
    return { brand, id, title, signal: statuses.join(' / '), keywords, image, family: czechFamilies.get(key(card)) };
  });
  const json = `{"cards":[\n${indexed.map(card => `  ${JSON.stringify(card)}`).join(',\n')}\n]}\n`;
  return [resolve(site, locale, 'kontrolky-a-vystrazna-hlaseni', 'warning-search.json'), json];
});

for (const [file, json] of outputs) {
  if (check) {
    if (readFileSync(file, 'utf8') !== json) throw new Error(`Outdated warning search index: ${file}`);
  } else {
    writeFileSync(file, json);
  }
}
console.log(`${czechFamilies.size} warning cards × ${locales.length} languages`);
