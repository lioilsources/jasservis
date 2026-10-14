# Výchozí měření viditelnosti v AI asistentech, 14. 10. 2026

Stav před nasazením PR #4 (sjednocení s Firmy.cz). Na produkci je fáze 1 (PR #3).

Podmínky: Chrome na Macu, přihlášený Google účet správce (Google AI Mode, Gemini),
claude.ai (Fable 5.1). Výsledky jsou ovlivněné polohou a účtem, pro srovnání
příště měřit stejně. ChatGPT neměřen (bez přihlášení spadl na ověření proti
robotům), Perplexity neměřena (vyžaduje přihlášení).

Legenda: **ano** = J&S servis zmíněn, **web** = jasservis.cz uveden jako zdroj
odpovědi, **chyba** = nesprávný údaj o J&S.

| # | Dotaz | Google AI Mode | Gemini | Claude |
|---|---|---|---|---|
| 1 | autoservis Statenice | ano, 1. místo | ano | ano |
| 2 | nezávislý servis Škoda Praha-západ | ano, 1. místo, **web** (starý titulek, chyba) | ano, 1. místo | ano, 1. místo (chyba: „Horoměřice“) |
| 3 | kde opravit Volkswagen Horoměřice okolí | ano, 1. místo | ano | ano, až v „kousek dál“ |
| 4 | kolik stojí diagnostika auta u Prahy | ne | ne | ne |
| 5 | servis převodovky DSG Praha západ | ne | ne | ne |
| 6 | geometrie kol Statenice | ano, 1. místo (Firmy.cz, 2 420 Kč) | ano, 1. místo (Beissbarth) | ano, ale „geometrii nikdo neuvádí“ |
| 7 | kalibrace jízdních asistentů Praha | ne | ne | ne |
| 8 | J&S servis Statenice recenze | ano | ano | ano |
| 9 | servis CUPRA Praha 6 okolí | ano, jako nezávislá alternativa | ne | ne |
| 10 | příprava na STK Praha západ | ne | ano („příprava a realizace STK“) | ne |
| | **Zmíněn** | **6/10** | **6/10** | **5/10** (č. 3 a 6 slabě) |
| | **Web jako zdroj** | 1/10 (+ odkaz z karty firmy u 1, 3, 8, 9) | 0/10 | 0/10 |

Zdroje, ze kterých asistenti o J&S čerpají: profil v Mapách Google (Claude a
Gemini výhradně), Firmy.cz, Mapy.com (recenze), jasservis.cz jen u Google AI
Mode.

## Chybná nebo zavádějící fakta

- **Starý titulek webu:** Google AI Mode u dotazu 2 cituje jasservis.cz/servis-skoda/
  jako „Značkový autoservis Škoda v Praze“ a „Černý Vůl, 252 64 Praha - západ“.
  To je dnešní produkce; PR #4 titulek i PSČ opravuje.
- **Adresa „Statenice-Horoměřice“** (Gemini 1, 2, 3; Google AI Mode 9; Claude 2
  dokonce „J&S servis, Horoměřice“). Pravděpodobně zápis v profilu Google, ověřit.
- **Telefon 605 399 448 (kancelář)** jako hlavní číslo u Gemini i Claude, tedy
  z profilu Google. Pro objednání servisu je na webu 608 313 437.
- **Claude, dotaz 6:** „Google u žádného výslovně neuvádí geometrii“ a doporučuje
  jiné servisy. Profil Google služby neuvádí.
- **Claude, dotaz 3:** naznačuje, že ODIS má jen autorizovaný servis; o ODIS u J&S neví.
- **Gemini, dotaz 6:** „v areálu čerpací stanice“, neověřeno.
- **Google AI Mode, dotaz 9:** „posílá fotky a videa z průběhu opravy“, neověřeno.

## Kde J&S chybí, i když službu nabízí

Diagnostika s cenou (4), DSG (5), kalibrace ADAS (7), CUPRA (9, Gemini a Claude),
STK (10, Google a Claude). Stránky DSG a CUPRA na produkci nejsou, přidává je
PR #4. Diagnostika, kalibrace a STK na produkci jsou, ale bez cen a se starými
titulky; ceny přidává PR #4.

## Příští měření

Stejné dotazy, stejní asistenti, 4 až 6 týdnů po nasazení PR #4 a po úpravě
profilu Google (adresa, telefon servisu, služby).
