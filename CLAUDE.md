# CLAUDE.md — pravidla pro web jasservis.cz

## Kdo ti píše

Majitel tohohle webu **není vývojář**. Píše ti z telefonu, česky, krátce a často
nepřesně. Popisuje, co chce na webu vidět, ne jak se to má udělat.

- **Neptej se, když se rozhodnout dá.** Když je zadání nejednoznačné, zvol rozumnou
  variantu, udělej ji a v odpovědi napiš jednou větou, co jsi zvolil a proč. Ptej se
  jen tehdy, když by špatná volba znamenala vyhozenou práci.
- **Nepiš technicky.** Žádné názvy souborů, tříd ani značek v komunikaci s majitelem.
  „Změnil jsem telefon v patičce na všech stránkách", ne „upravil jsem `<footer>`
  ve 21 souborech `index.html`".
- **Jeden požadavek = jeden PR.** Když je zadání velké, udělej první krok a v komentáři
  navrhni pořadí zbytku.
- **Nevymýšlej si fakta.** Ceny, otevírací doba, telefony, adresy, jména a nabízené
  služby piš jen tak, jak je zadal majitel nebo jak už na webu jsou. Když údaj chybí,
  zeptej se. Tohle je web skutečné firmy.

Výjimka: když pracuješ lokálně v terminálu se správcem repa (`@lioilsources`),
komunikuj normálně technicky. Pravidla o chráněných cestách tam neplatí.

## Co je tohle za web

Statická kopie původního WordPress webu autoservisu. Žádný build, žádný generátor:
co je v `jasservis.cz/`, to se nahraje na ostrý web.

```
jasservis.cz/                 ← TOHLE je web; měň jen tady
├── index.html                úvodní stránka
├── <stranka>/index.html      jedna složka = jedna stránka (kontakt, servis-skoda, …)
└── wp-content/themes/, uploads/   styly a skripty vzhledu, obrázky
backup/                       původní stažená kopie — NIKDY neměnit
*.py                          jednorázové skripty z migrace — neměnit
```

Tři věci, které tu nejsou vidět na první pohled (podrobně v `docs/web.md`, přečti
si ho před první změnou):

1. **Hlavička, menu a patička jsou zkopírované v každé stránce.** Změna v nich se dělá
   **ve všech** `jasservis.cz/**/index.html` stejně.
2. **Cesty jsou relativní k umístění stránky** (`wp-content/…`, `../wp-content/…`,
   `../kontakt/`). Nikdy nezačínej `/` ani `https://jasservis.cz/…`.
3. **HTML je strojově vygenerované** z WordPressu. Neuklízej ho, měň jen, o co majitel žádá.

**Fotky** (z Firmy.cz nebo přiložené v zadání): před vložením si přečti
`docs/fotky.md`. Jinou cestou obrázky z internetu stahovat nemůžeš.

## Odpověď a Pull Request

- **Název** lidsky, česky: „Nový telefon v patičce", ne „fix(footer): update phone number".
- **Popis** má dvě části: **Co se změnilo** (z pohledu člověka, který se dívá na web)
  a **Jak to ověřit** (na které stránce a kde). Odkaz na náhled se do PR přidá
  automaticky, zmiň ho.
- Když jsi něco zvolil za majitele (formulace, barva, velikost, umístění), napiš to
  a nabídni, že to změníš.

## Co nesmíš měnit

- `.github/**` (automatika, která web nasazuje), `docs/**`
- `.claude/**`, `CLAUDE.md` a `AGENTS.md`: tvoje oprávnění a pravidla (i pro jiné
  agenty, např. ChatGPT Codex)
- `CNAME` a `jasservis.cz/CNAME`: na těch visí doména
- `backup/**` a `*.py`: archiv a nástroje z migrace

Když jde požadavek splnit **jen** změnou v těchhle souborech, neobcházej to. Napiš
do issue, co by bylo potřeba, a označ `@lioilsources`.

## Kvalita — než pushneš

Build ani testy tu nejsou, kontrola je na tobě:

- Změna hlavičky, menu nebo patičky je ve **všech** stránkách.
- Každý nový nebo změněný odkaz a obrázek vede na soubor, který v repu opravdu
  existuje (ověř Globem), se správným počtem `../`.
- Neporušil jsi párování značek. Změněné místo si po úpravě přečti znovu.
- Při změně názvu firmy, telefonu, adresy nebo otevírací doby uprav i strukturovaná
  data (`<script type="application/ld+json">`), `<title>` a `<meta name="description">`.
- Nepřidávej externí skripty, sledovací kódy ani fonty z cizích serverů, pokud o to
  majitel výslovně nepožádal.
