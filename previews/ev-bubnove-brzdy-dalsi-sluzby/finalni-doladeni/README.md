# Finální vizuální doladění – návrh ke schválení

Navazuje na typografické úpravy `f2cafcc`. Aktuální stránka má úvod zarovnaný k hornímu okraji fotografie, původní dvousloupcové rozložení i velikost obrázku. Drobečková navigace má poslední položku „Bubnové brzdy elektromobilů“, na desktopu se vejde do jednoho řádku. Mobilní drobečky ukazují pouze Úvod a Další služby; neopakují nadpis stránky.

## Nové skutečné PNG

- [Desktop 1440 px](desktop-1440.png)
- [Mobil 390 px](mobil-390.png)
- [Desktop – otevřené bloky](otevrene-bloky-1440.png)
- [Mobil – otevřené bloky](otevrene-bloky-390.png)
- [Desktop – rozbalená navigace](navigace-1440.png)
- [Mobil – rozbalená navigace](navigace-390.png)

## Kontroly

Chromium při 360, 390, 430, 768 a 1440 px: bez vodorovného přetékání při zavřených i otevřených blocích a nabídce. Všechny čtyři bloky lze otevřít klávesnicí Enter a zavřít myší; dotykové plochy mají nejméně 48 px. Nabídka funguje, Escape ji zavře a služba je mezi Opravou brzdových kotoučů a Výměnou uložení nápravnice a ramen.

Úvod má zachovaný font Ubuntu a velikosti 20/17 px na desktopu, 19/16 px na mobilu. Popisek má 14 px a řádkování 21 px. Fotografie je bez deformace ve formátu 4:3; desktop 570 × 428 px, mobil 390 px: 350 × 263 px. Na desktopu i tabletu je rozdíl horních okrajů úvodu a fotografie 0 px.

Odznak Top firma: původní URL https://www.firmy.cz/top-firma/2025.svg vrací HTTP 200 a správné SVG. Příčinou předchozího chybějícího obrázku bylo blokování externích obrázků v automatizaci náhledu, nikoli vadná cesta webu. Pro nové snímky byla původní nezměněná data SVG načtena z této URL a předána prohlížeči přes zachycení síťového požadavku. Odznak byl vykreslen a jeho načtení ověřeno na všech pěti šířkách. Hlavička ani její grafika se nemění.

Porovnání se zdrojovou verzí před tímto doladěním: odborný obsah všech čtyř bloků, celý obsah článku, hlavička, patička, strukturovaná data i fotografie jsou shodné. Nová stránka má nadále jeden H1. Ostatní stránky, nabídky a společné styly ani JavaScript nejsou v tomto doladění měněny. `git diff --check` prošel; projekt nemá build ani projektovou sadu testů. [Naměřené hodnoty a kontrolní součet stránky](kontrola.json).

## Změněné soubory v tomto doladění

- `jasservis.cz/servis-zadnich-bubnovych-brzd-elektromobilu/index.html` – pouze místní styly, třídy titulku a drobečkové navigace.
- `previews/ev-bubnove-brzdy-dalsi-sluzby/finalni-doladeni/` – šest PNG, `kontrola.json` a tento přehled.

Žádné nevyřešené problémy v kontrolovaném rozsahu. Dostupnost odznaku v produkci nebyla měněna; snímky používají originální SVG z ověřené URL.

**Pouze pracovní větev. Nic neslučovat do master ani nenasazovat do produkce bez výslovného souhlasu majitele.**
