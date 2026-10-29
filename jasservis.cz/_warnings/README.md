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
- Návody a grafika nejsou znovu publikované jako celé příručky. Odkazy vedou na
  oficiální dokumenty; jejich původní anglický text se nevydává za přeložený PDF.

Před přidáním položky je nutné ověřit grafiku/licenci, význam, barvu, stav,
postup, přesný rozsah a všechny překlady. Odlišná barva nebo blikání se nesmí
převzít jen přebarvením bez doložení příslušného významu. Textové symboly EPC a
AUTO HOLD jsou doložené krátké nápisy; nevkládají proprietární font výrobce.

Všechny tři nové stránky i jejich zdrojové přehledy mají `noindex, nofollow`.
Zbývající ochranu celého náhledu přidává stávající preview workflow.
