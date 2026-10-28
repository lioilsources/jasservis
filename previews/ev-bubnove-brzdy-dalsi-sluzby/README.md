# Servis zadních bubnových brzd elektromobilů – návrh ke schválení

Umístění: **Další služby → Podvozek a brzdy**, bezprostředně za Opravou brzdových kotoučů a před Výměnou uložení nápravnice a ramen.

Služba má stejně jako sousední služby vlastní stránku a kartu v přehledu. Podrobnosti používají čtyři stávající rozbalovací komponenty. Text není vložen na stránce Autoservis a na webu není druhý výskyt článku. Původní návrh v Autoservisu nebyl součástí master, proto není potřeba na master odstraňovat článek.

## Náhledy z prohlížeče

- [Desktop – zavřené bloky](sluzba-1440-zavreno.png)
- [Desktop – otevřené bloky](sluzba-1440-otevreno.png)
- [Mobil – zavřené bloky](sluzba-390-zavreno.png)
- [Mobil – otevřené bloky](sluzba-390-otevreno.png)
- [Nabídka na desktopu](nabidka-1440.png)
- [Nabídka na mobilu](nabidka-390.png)
- [Karta mezi sousedními službami – desktop](prehled-1440.png)
- [Karta služby – mobil](prehled-390.png)

## Ověření

- Prohlížeč Chromium při 1440, 768, 360, 390 a 430 px: žádné vodorovné přetékání nové stránky; funkční rozbalení klávesnicí, nabídka i odkazy z karty.
- Správné pořadí položky ověřeno ve všech 29 navigacích včetně nové stránky.
- Fotografie má na stránce poměr 4:3, WebP a záložní JPEG. Náhledová karta používá přiměřený ořez téže fotografie. Originál je bajtově shodný s dodaným snímkem; žádná generativní úprava.
- Nová stránka má jeden H1, popis fotografie a ALT. Relativní cesty obrázků a nových odkazů existují. Strukturovaná data jsou platný JSON.
- Původní stránky byly porovnány s master: po odečtení nového odkazu v nabídce a karty v Dalších službách jsou bajtově shodné. Původní metadata, texty, hlavička mimo přidaný odkaz, patička, fotografie a styly se nemění.
- V projektu není build ani projektová sada testů. Proběhly cílené kontroly zdrojů, prohlížeče a `git diff --check`.
- Na snímcích je také původní nenačtený odznak Top firma v hlavičce; není součástí této změny.

[Úplný seznam změněných a přidaných souborů](zmenene-soubory.txt). Z původních souborů se mění 28 stránek kvůli zkopírovanému menu; jen přehled Dalších služeb má navíc novou kartu. Přidává se jedna stránka služby, originál a tři webové varianty fotografie, snímky a tento přehled kontroly. Společné CSS ani JavaScript se nemění.

**Návrh není schválen k nasazení. Neslučovat do master bez výslovného souhlasu majitele.**
