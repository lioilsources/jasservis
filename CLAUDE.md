# CLAUDE.md — pravidla pro web jasservis.cz

## Kdo ti píše

Majitel tohohle webu **není vývojář**. Píše ti z telefonu, česky, krátce
a často nepřesně. Popisuje, co chce na webu vidět — ne, jak se to má udělat.

Z toho plyne:

- **Neptej se, když se rozhodnout dá.** Když je zadání nejednoznačné, zvol
  rozumnou variantu, udělej ji, a v odpovědi napiš jednou větou, co jsi zvolil
  a proč. Ptej se jen tehdy, když by špatná volba znamenala vyhozenou práci.
- **Nepiš technicky.** Žádné názvy souborů, tříd ani značek v komunikaci
  s majitelem. „Změnil jsem telefon v patičce na všech stránkách" — ne
  „upravil jsem `<footer>` ve 21 souborech `index.html`".
- **Jeden požadavek = jeden PR.** Když je zadání velké, udělej první krok
  a v komentáři navrhni pořadí zbytku.
- **Nevymýšlej si fakta.** Ceny, otevírací doba, telefony, adresy, jména
  a nabízené služby piš jen tak, jak je zadal majitel nebo jak už na webu jsou.
  Když údaj chybí, zeptej se — tohle je web skutečné firmy.

Výjimka: když pracuješ lokálně v terminálu se správcem repa (`@lioilsources`),
komunikuj normálně technicky. Pravidla o chráněných cestách tam neplatí.

## Co je tohle za web

Statická kopie původního WordPress webu autoservisu. Žádný build, žádný
generátor — co je v `jasservis.cz/`, to se nahraje na ostrý web.

```
jasservis.cz/                 ← TOHLE je web; měň jen tady
├── index.html                úvodní stránka
├── <stranka>/index.html      jedna složka = jedna stránka (kontakt, servis-skoda, …)
└── wp-content/
    ├── themes/               styly a skripty vzhledu
    └── uploads/              obrázky
backup/                       původní stažená kopie — NIKDY neměnit
*.py                          jednorázové skripty z migrace — neměnit
```

Tři věci, které tu nejsou vidět na první pohled:

1. **Hlavička, menu a patička jsou zkopírované v každé stránce.** Neexistuje
   společná šablona. Změna v menu, logu, telefonu v hlavičce nebo v patičce
   se musí udělat **ve všech** `jasservis.cz/**/index.html` stejně. Než
   pushneš, ověř si Grepem, že starý text už nikde nezůstal.
2. **Cesty jsou relativní k umístění stránky.** Úvodní stránka odkazuje na
   `wp-content/…`, stránka v podsložce na `../wp-content/…`. Odkazy mezi
   stránkami stejně (`../kontakt/`). Nepoužívej cesty začínající `/` ani
   `https://jasservis.cz/…` pro obrázky, styly a skripty — rozbilo by to náhled.
3. **HTML je strojově vygenerované** (WordPress, CherryFramework). Je ukecané
   a plné tříd, které vypadají zbytečně. Nepřepisuj ho ani „neuklízej" — měň
   jen to, o co majitel žádá, a drž se stylu okolního kódu.

Nová stránka = nová složka `jasservis.cz/<nazev-bez-diakritiky>/index.html`,
vzniklá kopií podobné existující stránky, plus odkaz v menu na všech stránkách
(pokud ji tam majitel chce). Nový obrázek patří do
`jasservis.cz/wp-content/uploads/`.

## Odpověď a Pull Request

- **Název** lidsky, česky: „Nový telefon v patičce", ne
  „fix(footer): update phone number".
- **Popis** má dvě části:
  1. **Co se změnilo** — z pohledu člověka, který se dívá na web.
  2. **Jak to ověřit** — na které stránce a kde má změnu vidět. Odkaz na
     náhled se do PR přidá automaticky, zmiň ho.
- Když jsi něco zvolil za majitele (formulace, barva, velikost, umístění),
  napiš to a nabídni, že to změníš.

## Co nesmíš měnit

- `.github/**` — automatika, která web nasazuje
- `.claude/**` a `CLAUDE.md` — tvoje vlastní oprávnění a pravidla
- `CNAME` a `jasservis.cz/CNAME` — na těch visí doména
- `backup/**` a `*.py` — archiv a nástroje z migrace

Když si myslíš, že požadavek jde splnit **jen** změnou v těchhle souborech,
neobcházej to. Napiš do issue, co by bylo potřeba, a označ `@lioilsources`.

## Kvalita — než pushneš

Není tu žádný build ani testy, takže kontrola je na tobě:

- Změna, která se týká hlavičky/menu/patičky, je ve **všech** stránkách.
- Každý nový nebo změněný odkaz a obrázek vede na soubor, který v repu
  opravdu existuje (ověř Globem), se správným počtem `../`.
- Neporušil jsi párování značek — po úpravě si změněné místo přečti znovu.
- Když měníš název firmy, telefon, adresu nebo otevírací dobu, změň je i ve
  strukturovaných datech (`<script type="application/ld+json">`) a v `<title>`
  / `<meta name="description">`, pokud tam jsou.
- Nepřidávej externí skripty, sledovací kódy ani fonty z cizích serverů, pokud
  o to majitel výslovně nepožádal.
