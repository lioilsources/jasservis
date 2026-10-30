# Kontrolky — společná evidence a statické jazyky

`catalog.json` je jediný seznam významových záznamů, jejich grafiky a jednotlivě
uvedených modelových vydání. `locales.json` obsahuje přeložené ovládání.
Každý záznam má vlastní CZ/EN/DE název, vysvětlení, postup, omezení a ALT.
Obrázky jsou společné a jsou uložené pouze jednou v `wp-content/uploads/kontrolky/`.
Barevná varianta je samostatný stav, nikoli jazyková kopie.

```sh
python3 jasservis.cz/_warnings/generate.py
python3 jasservis.cz/_warnings/generate.py --check
```

Generátor přepisuje pouze vlastní obsah přehledu a jeho zdrojový přehled ve
všech třech jazycích. Nemění společné styly záhlaví, ostatní stránky, fotografie,
PDF protokoly ani překlady za běhu stránky. Nový modelový rozsah se musí doložit
v `scopes`; nevzniká automaticky podle platformy nebo příslušnosti ke koncernu.
Přidání/odebrání/přesun záznamu v katalogu se po vygenerování projeví všude.

## Stav tohoto náhledu

**Není kompletní katalog všech evropských vozů od roku 2010.**
Položky jsou podkladem pro následnou odbornou kontrolu. Modelový rok z katalogu
výrobce není totéž jako rok výroby konkrétního vozidla. Generace není doplněná,
pokud nebyla doložená. Žádný interval mezi dvěma vydáními se automaticky nevyplňuje.

- `manuals.status` odlišuje stažení od kontroly vybraných položek. Ani druhý stav
  neznamená kompletní revizi daného návodu nebo vozidla.
- `items` obsahuje zveřejněné významové záznamy; `scopes` jednotlivé doložené
  značky/modely/MY/vydání a stránky tištěného návodu i PDF.
- `verification` u rozšířených rozsahů uvádí způsob porovnání a kontrolní otisky.
- `graphics` obsahuje původ, autora, licenci, změny a SHA-256 sdílené grafiky.
  Grafika má zachovaný významový tvar standardního piktogramu; nejde o fotografii
  konkrétního přístrojového panelu. Neověřený speciální symbol se nenahrazuje.
- `pending_items` a `gaps` uvádějí nevyřešené případy a přístupové překážky.
- Soukromé SSP ani jejich obrázky se nepublikují; jsou doplňujícím technickým
  podkladem, nikoli náhradou pokynů v návodu k obsluze.
- Příručky se celé znovu nepublikují. U každé je uveden jazyk a hostitel;
  kopie vydání výrobce na jiném serveru je výslovně označena. Původní text PDF
  se nevydává za přeložený dokument.

## Rozšíření kontroly 29. 10. 2026

- Počty `distinct_pictogram_shapes`, `graphic_colour_variants`,
  `semantic_variants` a `model_edition_assignments` jsou oddělené, také po
  značkách. Barva ani další přiřazení stejného tvaru není další unikátní symbol.
- Škoda: vybrané položky z Octavia 5E 11.2018 (5E0012715AQ) a Enyaq iV
  11.2020 DE. Jde o výrobcem vydané příručky hostované třetí stranou;
  `host_kind` a `verification.level` tuto skutečnost odlišují. Chybí porovnání
  se souborem na serveru výrobce. Rok vydání se nepřevádí na modelový rok;
  `model_year` proto zůstává `null`.
- Volkswagen Užitkové vozy: samostatně ověřené obecné příklady z oficiálního
  přehledu značky UK; žádný konkrétní model ani ročník z toho neodvozujeme.
- Audi: SSP 668 slouží pouze jako technický doplněk. Nezávislá HTML kopie A4
  2014 nebyla přijata jako ověřené evropské vydání. Zákaznické položky pro Audi
  se nepřidávají odhadem.
- `source_access_log` uvádí konkrétní dokumenty, přístupové chyby a potřebný
  podklad. `review_gaps` obsahuje shodný přeložený seznam mezer CZ/EN/DE.

Před přidáním položky je nutné ověřit grafiku/licenci, význam, barvu, stav,
postup, přesný rozsah a všechny překlady. Odlišná barva nebo blikání se nesmí
převzít jen přebarvením bez doložení příslušného významu. Textové symboly EPC a
AUTO HOLD jsou doložené krátké nápisy; nevkládají proprietární font výrobce.

Všechny tři nové stránky i jejich zdrojové přehledy mají `noindex, nofollow`.
Zbývající ochranu celého náhledu přidává stávající preview workflow.

## Modelové doložení 30. 10. 2026

- Oficiální veřejný německý DIMA portál umožnil zvolit model a vydání bez VIN.
  Nově jsou samostatně doloženy Golf 5H0, 11.2020 (5H0012769AD), a Caddy 2K7,
  11.2025 (2K7012767AM). Nejde o návod přizpůsobený konkrétnímu VIN.
- HTML příručky mají `document_type: html`, `source_sections` a
  `source_topic_ids`; nevymýšlejí se čísla stránek PDF. Původní veřejná URL
  výběru návodu neobsahuje soukromý token.
- `change_history` dokládá přesný přechod 73 → 86 i další přechod 86 → 88.
  Původních 73 záznamů zůstalo zachováno. Rozšíření Škoda 43 = 36 přiřazení
  starých záznamů + 7 nových; užitkové vozy 24 = 18 přiřazení + 6 nových.
- Nová modelová kontrola přidala 48 přiřazení a dva významové stavy jednoho
  nového tvaru (ruce na volantu, bílá/červená). Třicet obecných rozsahů bylo
  nahrazeno modelem; starý zdroj zůstává v `previous_general_scopes`.
- Žádný starší záznam ani modelový rozsah Škoda/SEAT/CUPRA nebyl odstraněn.
- Nelze přebírat rozdílné tvary: Caddy má jiná provedení jízdních pruhů,
  některých asistentů, volantu a DPF. Nepotvrzené varianty zůstávají oddělené.
- Kompletní revize Audi, všech modelů/let a všech ADAS/EV symbolů stále chybí.
  Přehled proto musí zůstat označený jako nekompletní a pouze v náhledu.

## Audi a elektrické pohony, další kontrola 30. 10. 2026

- Audi Q3: 45 doložených významových položek z německé příručky 11.2024,
  83B012705AA. Úplný dokument AUDI AG je veřejně hostovaný autoškolou;
  není vydáván za soubor stažený z Audi a jeho vydání není modelový rok.
  Přesné stránky, otisk dokumentu a porovnání grafiky jsou v každém rozsahu.
- Rozlišeny jsou mimo jiné oko pro únavu, bílé/žluté stavy nedostupnosti
  asistentů, výzvy k převzetí řízení, nápis TPMS a AUTO u dálkových světel.
  Rozpoznaná značka 120 je doložený příklad z obr. 100, nikoli poruchová
  kontrolka nebo zde platný rychlostní limit; dodatkové tabulky se neimplikují.
- Elektrické pohony: želva v kruhu má samostatně doložené významy pro Born,
  Enyaq, Mii electric a ID.4. Omezený výkon, příliš studený akumulátor a hrozící
  vypnutí při vybití se neslučují. ID.4 11.2021 má také nezávisle ověřené
  rozsahy e-Sound, Lane Assist a výzev k převzetí řízení.
- Golf VII 11.2019 dokládá původní položku `vw-g` včetně blikající závady
  řízení dieselu. Modelové doložení původních položek Volkswagen je 14/15.
  Pro `vw-range` chybí odpovídající modelový podklad; kontrola přehledů
  a závad osvětlení Golf VII a Touareg 11.2019 požadovaný symbol nepotvrdila.
  Podklad Audi Q3 se na Volkswagen nepřenáší.
- Celkem 116 významových záznamů, 42 tvarů a 64 barevných grafických variant.
  Není to 116 unikátních obrázků ani kompletní katalog všech vozů od roku 2010.
  Přibylo 28 záznamů a 57 modelových přiřazení oproti verzi s 88 záznamy.
  Všech 88 původních záznamů a jejich texty i všechny dosavadní modelové
  rozsahy SEAT/CUPRA/Škoda zůstaly zachované.
- Audi A4 8W 01.2016 (8W0012705AC), A8 4N 2018 a Q4 e-tron 2022 mají stále
  nedostupné evropské návody (portál /models a zveřejněné odkazy: 403).
  Není stanovena zástupná platnost Q3 pro tyto modely. SSP je pouze doplněk.
- Přesné složené a vícebarevné grafiky Travel Assist, další dopravní značky
  a jejich stavy, některá parkovací/Front Assist/AdBlue/HV upozornění nejsou
  nahrazována podobnými obrázky. Jejich chybějící grafické podklady a modelový
  rozsah jsou výslovně uvedené v přeložené evidenci.
