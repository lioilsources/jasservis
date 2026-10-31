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
  Datum výroby fotografovaného vozu 03/2026 potvrdil uživatel; modelový rok,
  software, původní názvy a otisky souborů nejsou doložené.
  `terramar-photo-review.json` eviduje 74 pozorování, z toho 69 jednotlivých
  nesouhrnných řádků; nejde o 74 nových unikátních kontrolek ani o úplné
  zdrojové ověření všech šesti fotografií.
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

## Podrobné porovnání fotografií a skutečné doplnění přehledu

- Všech šest fotografií má jednotlivé záznamy s konkrétní polohou, významem,
  postupem řidiče, kategorií, stavem před/po revizi, vydáním/stranou zdroje
  a potřebnou opravou. 69 jednotlivých pozorování není počet unikátních
  kontrolek; opakované výskyty jsou oddělené a souhrnné řádky vyřazené z CSV.
- Nově přímo ve funkčním přehledu Terramar: CLIMA, AUTO klimatizace, TP,
  šedý pasivní Lane Assist a vůz ve smyku s OFF. Devět starších položek
  získalo vlastní doložení Terramar 11.25 (pásy, řízení, brzdy, centrální
  výstraha, Lane Assist, tempomat a Auto Hold). Pásy mají přesné strany 47–48.
- SEAT Leon 11.25 má samostatně doložený šedý pasivní Lane Assist (16/216).
  Golf 5H0 11.2020 má novou žlutou nedostupnost Lane Assist s vykřičníkem
  podle vlastního originálního HTML přehledu a kapitoly řešení problémů.
- Přesné grafiky řady dalších ovladačů dosud chybí; nejsou nahrazovány emoji,
  obecným telefonem, podobným HUD ani jinou barvou bez konkrétního důkazu.
  Oko s vykřičníkem Terramar se nezaměňuje s prostým okem Audi ani šálkem.
  Nepopsaná karta mobilního zařízení není automaticky označena za Telefon.
  Nabídka Audio sama neprokazuje aktivní ztlumení. Neoznačený vůz s oblouky
  a zaškrtnutím byl dohledán u Assistants, Terramar 11.25 strana 39.
- Caddy 2K7 11.2025: pět zdrojových variant Lane Assist má souvislé čáry,
  na rozdíl od Terramar/SEAT. Bez vhodné přesné grafiky nebyly přeneseny.
  Výsledek vlastní kontroly každé značky je v `brand-functional-review.json`
  a přeložených CSV. Jde o vybrané kapitoly, ne všechna modelová vydání.
- Připojený Disk byl prohledán. Soubor „Nový Terramar 2025“ je marketingový
  prospekt, nikoli SSP; neslouží k výkladu kontrolek. Audi SSP 679 je pouze
  technický kontext různých infotainmentových platforem Audi, nikoli důkaz
  shodných ikon Terramar. Soukromé materiály nejsou na webu zveřejněné.
- Zachováno 131 původních záznamů a všechny jejich dosavadní modelové
  rozsahy. Aktuálně 137 významových záznamů, 55 tvarů, 80 barevných variant.
  Počet plně porovnaných celých návodů zůstává 0.
- Všech 18 značkových položek nyní používá název „Kontrolky a ikony…“.
  Nadále jsou za modely a vedou rovnou na předvolenou značku s kotvou.
  V Dalších službách ani u světlometů není přidán žádný odkaz.

## Revize modelů a kapitol 30. 10. 2026

Nově ověřené výtisky Audi A4 DE 07.2024, A8 DE 06.2025 a Q4 e-tron DE 06.2023 nenahrazují chybějící starší vydání. Přidáno pět významových záznamů: LIM AUTO, nedostupnost automatického převzetí limitu, ovládání AUTO a A/C Audi a samostatný nápis ESC OFF. Starší Q4 má vlastní rozsah symbolu šálku, nikoli automaticky oko z 07.2024.

Aktuálně 142 významových záznamů, 58 tvarů a 83 barevných grafik; 44 evidovaných návodů. `chapter-review.json` a přeložené CSV rozlišují 352 oblastí a 11 přesně ohraničených uzavřených porovnání. Deset jejich webových podmnožin je zveřejněno; Caddy čeká na přesné grafiky. Žádný celý návod ani značka není označena jako dokončená.

Přijato všech šest odlišných fotografií Terramaru; datum výroby fotografovaného vozu 03/2026 potvrdil uživatel. Modelový rok a software zůstávají nedoložené. Původní názvy souborů nebyly předány a pracovní identifikátory nejsou názvy originálů. Inventář obsahují `terramar-photo-inventory.*.csv`.

Technicky úspěšných 36 testů modelů a revizních stránek a 36 návazností značek v CZ/EN/DE, Chromium 154 a WebKit 26 na Linuxu. Kontrola 83 grafik v obou jádrech. Rozměry 360×800, 390×844, 844×390, 768×1024, 1366×768 a 1920×1080; nejde o skutečný iPhone ani Android. Tyto testy nedokládají obsahovou úplnost.

## Pokračování obsahové revize 30. 10. 2026

Porovnány celé samostatné oddíly Klimaanlage: Audi A4 07.2024 str. 104–109 před Lenkradheizung a Audi A8 06.2025 str. 113–118 před Lenkradheizung. Nejde o celé Warm und kalt ani celé knihy. Evidence `audi-climate-source-comparison.json` a tři CSV zachycují jednotlivé funkční rodiny i doložené odlišné stavy a chybějící obrazové položky. Zveřejnění celého obrazového obsahu hotové není. Dále porovnány celé oddíly přímého Reifendruck-Kontrollsystem a Start-Stop-System v obou těchto vydáních.

V náhledu je 17 nových významových položek oproti 0bf6bba. Přímé měření tlaku má samostatné nízké/kritické hlášení a výměnu kol, běžný neprovedený stop není porucha. A4 A/C OFF není celkové OFF, SET REAR není A8 REAR. Zbytkové teplo má vlastní ovládání AUTO pro A4 a podržení MAX pro A8. Funkční nápisy jsou samostatně sázené krátké ovládací značky, nikoli nové výrobní piktogramy.

Nesprávná náhrada Audi A OFF nebyla zveřejněna: Audi má OFF vedle A, licencovaná Terramar varianta pod A. Přesných pět původních SVG Caddy bylo vizuálně porovnáno včetně původních barev; soubory zatím nejsou převzaty do webu bez potvrzeného oprávnění použití. Zdrojové adresy a otisky uvádí `caddy-source-graphic-review.json`. Žádné podobné náhradní obrázky.

Fotografie Terramar: všech šest zachováno v evidenci, nově rozpoznán Full Link podle přesné kresby na str. 287 vydání 11.25. P v horní liště má doloženou roli oblasti aktivních funkcí, ale konkrétní význam této zkratky zůstává otevřený. Malé znaky přístrojového panelu a některé ovládací varianty nejsou násilně určeny. Fotografie při 0 ot/min nedokládá závadu.

Technicky: 42 kombinací rozměru/jazyka/prohlížeče, šest dotykových a modelových scénářů včetně otočení, 36 značkových vstupů a 92 grafik v Chromium 154 / WebKit 26 na Linuxu. Bez skutečného iPhonu či Androidu. Všech 142 původních záznamů i rozsahů zůstalo zachováno; čtyři související textové opravy jsou doložené novým zdrojem. Všech 90 záhlaví a patiček beze změny, společná média 28 skupin / 76 položek konzistentní. Počty zahrnují i funkční nápisy a neprokazují úplnost.

## Dostupné podklady a oddělené pracovní fronty – navazující revize

- `work-queues.json` a tři jazykové CSV oddělují 45 dostupných neuzavřených dokumentů, 10 konkrétních přístupových/modelových mezer a tři skupiny přesně porovnaných grafik s nevyřešeným použitím. Nejde o 10 nedostupných celých návodů: Caddy má nepřístupná konkrétní nová témata, zatímco uložené oddíly zůstávají dostupné.
- `function-review-current.json` a CSV dokládají 13 nových vymezených porovnání pro Golf 11.2020, Octavia 5E 11.2018, Enyaq 11.2020, Born 08.2021, Tarraco 06.2023, Caddy 11.2025 a Q4 e-tron 07.2024. Význam, přesná zdrojová varianta a vložení do webu jsou samostatné stavy. Porovnání oddílů se mohou překrývat; nejde o počet unikátních hotových kapitol.
- Do skutečných tří jazykových stránek přibylo sedm významových záznamů: bílé A Golf; blikající parkovací brzda na prudkém svahu a Dynamic Light Assist Enyaq; zelené kruhové P Auto Hold a vlastní modré A Tarraco; omezený žlutý posilovač a ruční ASR OFF Caddy. Opraven modrý Light Assist Enyaq/Born; neslučuje se s Tarracem. Q4 CO₂ doplněno o oddělení normálního textového omezení klimatizace při ochraně HV akumulátoru.
- Nově stažený celý oficiální Tarraco 06.2023, 5FJ012720BR, 408 stran PDF, je samostatné vydání. Není bez důkazu označen jako základ doplňku 01.2024.
- Pět přesných SVG Caddy zůstává nezveřejněno: obecné podmínky Volkswagen, Wolfsburg červen 2026, bod 2, samotným přístupem licenci neudělují; specifický použitelný právní základ nebyl doložen. Žádná žádost o svolení nebyla odeslána, žádná odpověď se neočekává a žádné odmítnutí se netvrdí. Samotná tato evidence nerozhoduje o ochraně každého jednoduchého symbolu. Přesné původní URL, barvy a otisky jsou v `caddy-source-graphic-review.json`.
- Celkem nyní 166 významových záznamů, 94 barevných grafik a 67 tvarových identit; barva ani modelové přiřazení nejsou další unikátní tvar. Všech 159 předchozích záznamů a jejich modelová přiřazení zůstala zachována. Celé návody kompletně porovnané: **0**. Zbývající dostupná práce není přístupovou překážkou.
- `verification-queue-round.json` odděluje obsah od technických testů: Chromium a WebKit v Linuxu, 36 cílených modelových scénářů v CZ/EN/DE, 1366×768, 390×844 a 844×390. Nejde o skutečný iPhone/Android. Hlavičky a patičky 90 stránek beze změny; přístup zůstává pouze z jednotlivých značek.

## Sjednocené zadání a druhá kontrola – fotografie, Terramar a Q4

- `attachment-groups.json` rozlišuje šest sad: šest dostupných fotografií Terramaru; tři dosud nedostupné fotografie návodu CUPRA7–10; čtyři nedostupné fotografie vozu Audi; tři nedostupné starší fotografie návodu9–13 s neověřeným dřívějším označením Audi; deset přijatých fotografií Enyaqu pokrývajících strany12–17 a pět přijatých fotografií Multivanu pokrývajících strany16–19. Opakované a náhradní záběry nejsou nové řádky. Neznámá vydání ani modelové roky nejsou odhadnuté.
- Doložený celý Terramar EN 11.25, 578012720AC, má na stranách 7–10 pohledy na vozidlo; tabulky jsou 11–15. `terramar-1125-overview-review.json` a tři CSV evidují všech 110 významových buněk těchto tabulek. Není to 110 unikátních piktogramů ani identifikace nových chybějících fotografií. Zvlášť je přímo uvedeno ověření navazujících pokynů a skutečné vložení na web.
- Vloženy dvě nové významové varianty: žlutá závada parkovací brzdy Terramar a žluté blikání řízení podle str.186. Přibylo 17 modelových přiřazení pro Terramar a jedno pro Q4. Modelová přiřazení nejsou nové unikátní symboly. Celkem 168 významových záznamů, 94 sdílených barevných grafik a 67 tvarových identit; žádný nový obrázkový soubor nevznikl.
- Doplněné nezávislé rozsahy Terramar zahrnují mj. nízkou brzdovou kapalinu, červený/žlutý posilovač, obložení, tlak oleje, zadní mlhovku, vnější osvětlení, řízení, centrální výstrahu, dálková světla, modré A, směrovky, tempomat a nepřímé sledování tlaku. Str.387–389 rozlišují ztrátu tlaku, přibližně minutové blikání při závadě a krátké potvrzení kalibrace. Opraven přehled aktivní parkovací brzdy z chybné str.12 na str.11.
- Přesná grafika velmi nízké hladiny oleje se neslučuje s tlakem oleje. Odlišná obrysová grafika vnějšího zvuku PHEV není nahrazená jinou siluetou auta/reproduktoru. Prediktivní, SOS, Travel/Front/Emergency Assist a další nepokryté varianty jsou v řádkové evidenci výslovně nepublikované. Neutrální černý tisk není automaticky černá kontrolka; smíšená varianta nevykládá provozní barvy bez příslušného oddílu.
- Q4 e-tron DE 07.2024,89A012705AM: celý samostatný oddíl Klimaanlage str.88–92 před Lenkradheizung porovnán ve 21 funkčních bodech (`q4-climate-function-review.json` + CSV). Nejde o celý Warm und kalt. Vložen AUTO s vlastními modelovými podmínkami; další ovladače nejsou převzaté automaticky z A4/A8.
- `druha-kontrola.html` v každém jazyce nabízí oddělené přílohy, přesné polohy dosavadních pozorování Terramaru, celé zdrojové tabulky a export. `catalog-review-export.zip` obsahuje všechny texty CZ/EN/DE, zdrojovou evidenci a 94 skutečně používaných sdílených licencovaných SVG pouze jednou. Neobsahuje originální návody, soukromé SSP ani původní grafiky výrobce.
- Pracovní fronty jsou nyní čtyři: dostupná nehotová práce; konkrétní chybějící dokumenty; neověřené významy/grafické varianty; ověřené grafiky s nevyřešeným použitím. Pět originálních Caddy SVG zůstává v poslední skupině bez tvrzení, že byla odeslána nebo odmítnuta žádost o svolení.
- Všech 18 značkových tlačítek používá odpovídající překlad „ZOBRAZIT KONTROLKY A IKONY“ za Servisovanými modely značky, se značkou v URL a kotvou přehledu. Další služby zůstávají bez odkazu. Aktuální náhled navíc připravuje společný vstup „RADY PRO ŘIDIČE“ v horní liště; jde o druhý vstup do stejného katalogu, nikoli o další katalog.
- `verification-unified-round.json` odděluje techniku od obsahu: Chromium154/WebKit26 v Linuxu, telefon/tablet v obou orientacích a notebook; delší německá tlačítka také ve WebKitu360×800/800×360. Žádný skutečný iPhone, Android ani tablet nebyl testován. Hlavičky/patičky90 stránek shodné s výchozí verzí. Všech166 předchozích významových záznamů i jejich modelové rozsahy zachované. Celé návody kompletně porovnané: **0**.

## Fotografovaný přehled Enyaqu12–17 a nezávislá kontrola11.2020

- Přijato deset fotografií Enyaqu. Po odečtení překryvů a náhradních záběrů pokrývají celý fotografovaný přehled stran12–17. `enyaq-photo-review.json` a tři CSV evidují všech122 čitelných významových řádků:38 odpovídá již existujícím modelovým záznamům,2 mají význam na webu bez celé kombinované grafiky,5 má pouze obecného kandidáta bez rozsahu tohoto Enyaqu,8 vyžaduje podrobnou kapitolu a69 přesných variant v katalogu chybí. Jde o významové stavy, nikoli122 unikátních piktogramů.
- Značku a model Škoda Enyaq potvrzuje uživatel. Vydání, modelový rok a generace fotografovaného českého návodu zůstávají nedoložené; chybí tiráž. Přepis a porovnání tabulky jsou hotové, ale podrobné pokyny a právně použitelné grafiky nových variant nikoli. Z fotografické sady proto nebyla neověřená položka přidána do zákaznického katalogu.
- Dostupná výrobní příručka DE11.2020, hostovaná třetí stranou, je jiný nezávisle vedený podklad. Str.12–16 neobsahují dané tabulky, vlastní přehled je17–21. Zdroj se nevydává za identifikaci fotografovaného vydání. Rok vydání není převeden na modelový rok.
- Z této samostatné příručky doplněna červená želva nedostatečného výkonu, str.17 a100–101. Odlišena žlutá omezená výkonnost; nevnáší se Q4 omezení na manévrování ani univerzální STOP ke všem červeným symbolům. Použita existující licencovaná červená grafika po nezávislém porovnání původní červené varianty, bez přebarvování.
- EPC už bylo správně vedeno pro elektrický Enyaq; ověřeno podle původního piktogramu a vlastního oddílu str.201, neduplikováno a nevysvětleno jako benzinová škrticí klapka.
- Upřesněny modelové poznámky nabíjení12V, závady12V, nízkého nabití, opotřebení a chladicí soustavy. Podmínka společného zobrazení s trojúhelníkem je výslovná. Pro přesné celé kombinace není tvrzeno dokončené obrazové zveřejnění. Rekuperace s ABS a přehřátí elektrického systému s teploměrem zůstávají samostatně ověřené významy bez náhradního odhadnutého obrázku.
- `enyaq-independent-review.json` a tři CSV jsou skutečná vymezená kontrola dostupného staršího dokumentu; samostatný fotografický přepis je v `enyaq-photo-review.json` a třech CSV. Neověřené CO₂/požární/Traction a další varianty se na vydání11.2020 nepřenášejí.
- Celkem169 významových záznamů; původních168 zachováno. Stále94 barevných grafik a67 tvarových identit. Technické testy jsou v `verification-enyaq-addendum.json` oddělené od obsahu: Chromium/WebKit Linux, CZ/EN/DE,390×844/844×390,820×1180/1180×820,1366×768; žádné skutečné zařízení. Hlavičky a patičky90 stránek,18 značkových vstupů a ostatní obsah zachované.

## Fotografovaný přehled Multivanu16–19

- Přijato pět fotografií, přičemž novější záběr strany16 nahrazuje starší. Čtyři unikátní strany16–19 jsou přepsané po všech129 čitelných významových řádcích. `multivan-photo-review.json` a tři CSV drží stránku, sloupec, polohu, doslovný popisek, barvu, výslovný STOP a oddělený stav grafiky, významu a publikování.
- Třicet sedm řádků má pouze podobného významového kandidáta v současném katalogu,92 nemá ani kandidáta. Žádná položka zatím nemá doložený rozsah Multivan a žádná nebyla převzata z Caddy nebo jiné značky. Pět drobných grafik zůstává obrazově nejasných.
- Model Multivan potvrdil uživatel; generace, modelový rok a vydání návodu jsou nedoložené. Pro přiřazení a pokyny řidiči chybí tiráž a odkazované podrobné kapitoly. Samotný veřejný seznam vydání7T0 neurčuje vydání fotografované knihy.


## Opravy po auditu 30. 10. 2026

- Pracovní fronty fotografovaných příruček Enyaqu a Multivanu odkazují na vlastní JSON evidenci. Identita vydání zůstává nedoložená; nepřebírá se příručka Octavie ani jiné modelové vydání.
- Aktuální fotografický souhrn je odvozený z výslovně vymezených skupin Enyaq a Multivan: 15 přijatých fotografií vůči 9 původně požadovaným; překryvy a náhradní záběry nejsou nové řádky. Ostatní chybějící skupiny a Terramar jsou vedené samostatně.
- Kandidát bez rozsahu příslušné značky se v revizní tabulce vypisuje bez odkazu na neexistující kartu. Nevzniká nové modelové přiřazení.
- Generátor obnovuje také work-queues.*.csv. ZIP doplňuje coverage.csv, manual-review.csv, tři pracovní CSV a export-manifest.json s otisky všech ostatních položek archivu. Soukromé originály fotografií ani celé návody nepřidává.
- validate.py ověřuje počty, datové vazby, překlady, grafiky, CSV, vymezenou dostupnost fotografií, vztah fotopřehledu a modelu i kotvy 15 katalogových/revizních HTML stránek. Kontrola generátoru zůstává samostatná. Úspěch obou kontrol není odborným potvrzením všech pokynů ani úplnosti celého katalogu.

```sh
python3 jasservis.cz/_warnings/validate.py
python3 jasservis.cz/_warnings/generate.py --check
```
