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

## Přesné vydání Q4, ovládací ikony a kontrolní tabulky

- Získán celý Q4 e-tron DE 07.2024, 89A012705AM, 338 stran. SHA-256:
  `597a12fce2d3a5e749ae0c70754d649c218c6a735638a6dd6e8d3b394abdcf9e`.
  Běžný veřejný prohlížeč PDF umožnil načtení přesného souboru; nešlo
  o obejití přihlášení nebo záměnu za jiné vydání. Hostitel je třetí strana.
- Nové stavy zahrnují červenou želvu Q4 s omezením na manévrování, samostatné
  funkční nápisy HOLD a LIM (aktivní, neaktivní, blikající překročení, chyba),
  bílý neaktivní tempomat a červené/žluté hlášení A/C o CO₂ v kabině.
  Levá a pravá směrovka Q4 mají oddělenou grafiku; žlutá zadní mlhovka nebyla
  na Q4 přenesena bez vlastního barevného důkazu. Staré rozsahy zůstaly.
- Terramar 09.24 / 11.25: ovládací MAX a REAR byly individuálně porovnané
  na tištěných stranách 146 / 148. Jde o samostatnou skupinu ovládacích ikon,
  jejichž bílá schematická barva neznamená závadu ani univerzální aktivaci.
- Následně dodáno a vizuálně porovnáno **šest** fotografií Terramar: čtyři
  obrazovky Control Centre a dva odlišné snímky přístrojového panelu.
  Modelový rok, software, původní názvy a otisky souborů nejsou doložené.
  `terramar-photo-review.json` eviduje 54 pozorování; nejde o 54 nových
  unikátních kontrolek ani o úplné zdrojové ověření všech šesti fotografií.
- `review-register.json` a `manual-review.csv` oddělují vybrané ověřené položky
  od kompletního porovnání celého vydání. **Kompletně porovnaná vydání: 0.**
  `source-character-review.csv` je pouze automatický pracovní index znaků
  textové vrstvy všech dostupných PDF, nikoli důkaz grafické nebo obsahové
  úplnosti. Rastrové obrázky ani některé ovládací nápisy jím nejsou pokryté.
- `q4-overview-review.json/.csv` evidují jednotlivé řádky obrazového přehledu
  Q4 na stranách 10–14: samostatně přiřazené ověřené stavy a dosud nezařazené
  varianty. Přiřazení řádku nepotvrzuje všechny významy jeho obrázku.
- `revize.html` je přeložená kontrolní tabulka CZ/EN/DE. Ani počet dokumentů,
  přiřazení, znaků, tvarů, barev nebo testů se nevydává za důkaz úplnosti.
- Z veřejných nabídek Další služby a úvodního přehledu byl odkaz kontrolek
  odstraněn ve všech stránkách a jazycích. Přístup přes šest konkrétních značek
  v Autoservisu zůstává. Existující URL přehledu se nemění; drobečková úroveň
  nyní odpovídá Autoservisu. Záhlaví se jinak nepřestavuje.

## Doplnění po pěti fotografiích Terramar

- Samostatně doloženy bílé ovládací zkratky Lane Assist a A OFF v návodu
  Terramar 11.25. A OFF není poruchová kontrolka a jeho rozsah nezahrnuje PHEV.
- Zelený pokyn sešlápnout brzdu není zaměněn s Auto Hold. Červená parkovací
  brzda je samostatná; žlutý symbol motoru na fotografii při 0 ot/min není
  důkazem závady bez hlášení a provozního kontextu.
- Neoznačené ikony bez doloženého významu nejsou odhadovány. Ovládací
  fotografie se nevydávají za nezávislý důkaz všech signalizačních stavů.
- Aktuálně 131 významových záznamů, 50 tvarů, 74 barevných variant,
  446 modelových přiřazení. Plně porovnané návody stále **0**.
- Dalších 24 funkčních kontrol ve třech jazycích, Chromium a WebKit,
  rozměry 390×844, 844×390, 768×1024 a 1366×768. Skutečná mobilní zařízení
  nebyla testována. Funkční zkoušky nepotvrzují úplnost odborného obsahu.

## Šestý uživatelský snímek

Druhý odlišný přístrojový panel doplněn do evidence; nyní 6/6 vizuálně
zkontrolovaných fotografií, nikoli 6/6 kompletně zdrojově ověřených sad ikon.
Návod Terramar 11.25, strany 11–14 a 16/178, porovnán pro viditelné podoby,
kontrolu zapalování a samostatnou polohu voliče P. Drobné nečitelné stavové
varianty nejsou odhadovány; nedošlo k navýšení katalogu 131 záznamů.
