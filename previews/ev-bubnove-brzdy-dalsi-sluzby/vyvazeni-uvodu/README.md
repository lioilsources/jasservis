# Vyvážení úvodní části a čitelnější popisek – návrh ke schválení

Navazuje na `a2c0ee8`. Mění se výhradně dvě místní CSS pravidla na stránce služby: proporce desktopových sloupců a styl popisku fotografie. Odborné texty, modely, označení T10635, fotografie, všechny čtyři bloky i jejich pořadí jsou zachované. Hlavička, logo, kontakty, navigace, patička, další stránky a společné CSS ani JavaScript nejsou měněny.

## Nové PNG

- [Desktop 1440 px – zavřené bloky](desktop-1440.png)
- [Desktop 1440 px – čtyři otevřené bloky](otevrene-bloky-1440.png)
- [Mobil 390 px – zavřené bloky](mobil-390.png)
- [Mobil 390 px – čtyři otevřené bloky](otevrene-bloky-390.png)
- [Desktopová nabídka](navigace-1440.png)
- [Mobilní nabídka](navigace-390.png)

## Výsledek kontroly

- Desktop od 1200 px: poměr sloupců 60 : 40 pro text a fotografii. Při 1440 px má text šířku 690 px a fotografie 450 × 338 px. Jejich horní okraje jsou zarovnané. Volná výška mezi koncem textového sloupce a spodním okrajem fotografie klesla z 181,3 na 91,3 px. Text nebyl prodloužen.
- Tablet 768 px a mobily 360, 390 a 430 px mají původní proporce sloupců. Při 390 px je fotografie nadále 350 × 263 px. Pořadí zůstává úvod → fotografie → popisek → čtyři odborné bloky.
- Popisek na desktopu i mobilu: 15 px, řádkování 22,5 px, běžná tloušťka 400 a tmavá barva #3d3d3d. Je celý viditelný, jeho text včetně T10635 se nezměnil.
- Chromium při 360, 390, 430, 768 a 1440 px: žádné vodorovné přetékání při zavřených/otevřených blocích ani v rozbalené nabídce. Všechny čtyři bloky otevřeny klávesnicí a zavřeny myší; na třech mobilních šířkách navíc každý otevřen a zavřen simulovaným dotykem. Nejmenší dotyková plocha má 48 px.
- Zařazení v nabídce beze změny: Další služby → Podvozek a brzdy, mezi Opravou brzdových kotoučů a Výměnou uložení nápravnice a ramen. Nabídka a její zavření klávesou Escape fungují.
- Fotografie má správný poměr 4:3 a načtenou variantu WebP. Originál je shodný s dodaným snímkem. Žádné generativní zásahy ani jiné úpravy fotografie.
- Hlavička, patička, obsah článku a strukturovaná data byly strojově porovnány s předchozím commitem: shodné. Nová stránka má jeden H1. Odznak Top firma je v náhledu vykreslen původním SVG ze stejné HTTP 200 URL; pro spolehlivý místní náhled je přesně tento externí soubor předán prohlížeči zachycením jeho síťového požadavku.
- `git diff --check` prošel. Projekt nemá build ani projektovou sadu testů. [Naměřené hodnoty](kontrola.json).

## Změněné soubory tohoto doladění

- `jasservis.cz/servis-zadnich-bubnovych-brzd-elektromobilu/index.html` – dvě místní CSS pravidla.
- `previews/ev-bubnove-brzdy-dalsi-sluzby/vyvazeni-uvodu/` – šest PNG, `kontrola.json` a tento `README.md`.

**Pouze pracovní větev. Žádný merge do master ani produkční nasazení bez výslovného souhlasu majitele.**
