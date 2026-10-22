# AGENTS.md — pravidla pro web jasservis.cz (ChatGPT Codex a jiní agenti)

**Než cokoli změníš, přečti si celý `CLAUDE.md`.** Pravidla v něm platí
i pro tebe, i když je psaný pro Clauda: kdo ti píše a jak s ním mluvit, jak je
web postavený, jak psát PR, co nesmíš měnit a co zkontrolovat před pushem.
Tady jsou jen věci, které se pro tebe liší nebo které nejčastěji pokazíš.

## Nejdůležitější pravidla v kostce

- **Měň jen `jasservis.cz/`.** Nikdy neměň `.github/**`, `.claude/**`,
  `CLAUDE.md`, `AGENTS.md`, `CNAME`, `jasservis.cz/CNAME`, `backup/**`
  ani `*.py` v kořeni. Když to jinak nejde, napiš to majiteli a označ
  `@lioilsources`.
- **Hlavička, menu a patička jsou zkopírované v každé stránce.** Změna v nich
  se musí udělat ve **všech** `jasservis.cz/**/index.html` stejně.
- **Cesty jsou relativní** k umístění stránky (`../kontakt/`,
  `../wp-content/…`). Nikdy nezačínej cestu `/` ani `https://jasservis.cz/`
  u obrázků, stylů, skriptů a odkazů mezi stránkami. Rozbilo by to náhled.
- **Nevymýšlej si fakta.** Ceny, telefony, adresy, otevírací dobu a služby
  piš jen tak, jak je zadal majitel nebo jak už na webu jsou.
- **Nepřidávej externí skripty, měřicí kódy (Google Analytics apod.),
  cookies ani fonty z cizích serverů**, pokud o to majitel výslovně nepožádal.
  Když požádá o měření návštěvnosti, nejdřív mu napiš, že měření s cookies
  vyžaduje souhlasovou lištu, a označ `@lioilsources`.
- **HTML je strojově vygenerované z WordPressu.** Neuklízej ho a nepřepisuj.
  Měň jen to, o co majitel žádá.

## Čím se lišíš od Clauda

- **Jedna rozpracovaná změna na stránku.** Než začneš, podívej se na otevřené
  PR (větve `claude/…` i tvoje). Když některé mění stejnou stránku, upozorni
  majitele, že vzniknou konflikty, a navrhni nejdřív to otevřené schválit
  nebo zavřít.
- **Fotky z Firmy.cz** stahuj jen skriptem
  `python3 .github/scripts/firmy-foto.py` (popis je v `CLAUDE.md`; potřebuje
  Pillow a přístup na firmy.cz). Když ho spustit nemůžeš, obrázky z internetu
  nestahuj jinak. Napiš majiteli, ať fotku přiloží nebo o ni požádá Clauda
  v issue.
- **Náhled:** ke každému PR se automaticky přidá komentář s odkazem na náhled.
  V popisu PR na něj odkaž, majitel změnu kontroluje v telefonu.

## Než pushneš

Není tu build ani testy, kontrola je na tobě:

- Každý nový nebo změněný odkaz a obrázek vede na soubor, který v repu
  existuje, se správným počtem `../`.
- Změna hlavičky, menu nebo patičky je ve všech stránkách a starý text už
  nikde nezůstal (ověř hledáním napříč `jasservis.cz/`).
- Značky jsou správně spárované. Změněné místo si po úpravě přečti znovu.
- Při změně názvu firmy, telefonu, adresy nebo otevírací doby uprav i
  strukturovaná data (`application/ld+json`), `<title>` a
  `<meta name="description">`.
- PR pojmenuj lidsky česky a v popisu napiš **Co se změnilo** a **Jak to
  ověřit** (na které stránce a kde).
