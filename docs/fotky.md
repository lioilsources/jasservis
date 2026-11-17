# Fotky na web jasservis.cz

Pravidla pro agenta, který vkládá fotky na web. Přesunuto z `CLAUDE.md`.

Fotky z profilu na Firmy.cz a fotky přiložené v zadání ukládej jen skriptem
`.github/scripts/firmy-foto.py`, spouštěným přesně takhle, bez `python3` na začátku
(jinak ho nemáš povolený):

- `seznam` vypíše nabídky s adresou fotky.
- `stahni <url> <nazev-bez-diakritiky>` uloží `<nazev>.jpg` (do 1280 px, fotka na
  stránce služby) a `<nazev>-s.jpg` (600×380, dlaždice na přehledových stránkách)
  a vypíše jejich cestu a rozměry.
- Fotku, kterou majitel přiložil do zadání nebo komentáře, máš stažené ve složce
  `/tmp/github-images/`; ulož ji stejným skriptem:
  `ulozit /tmp/github-images/<soubor> <nazev-bez-diakritiky>` (výsledek je stejný
  jako u `stahni`).

Když fotka zjevně nesedí k textu nebo je nekvalitní, napiš to majiteli, ale vlož ji.
Rozměry pak zapiš i do `width`/`height` a do strukturovaných dat, pokud tam fotka je.
Jinou cestou obrázky z internetu stahovat nemůžeš.
