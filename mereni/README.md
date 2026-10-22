# Měření viditelnosti v AI asistentech

Fáze 4 plánu viditelnosti: jednou za čas položit stejných 10 dotazů stejným
asistentům a zapsat, jestli zmíní J&S servis, jestli citují jasservis.cz a jestli
uvádějí správná fakta. Složka `mereni/` leží mimo `jasservis.cz/`, na web se
nenasazuje.

## Výsledky

| Datum | Soubor | Kontext |
|---|---|---|
| 14. 10. 2026 | [2026-10-14-vychozi-stav.md](2026-10-14-vychozi-stav.md) | výchozí stav, na produkci fáze 1, před PR #4 |

Nové měření = nový soubor `RRRR-MM-DD-<popis>.md` se stejnou tabulkou a řádek sem.
Surové odpovědi asistentů patří do `mereni/surova-data/RRRR-MM-DD/`, která se
necommituje (repo je veřejné a odpovědi obsahují recenze a údaje o konkurenci).

## Dotazy

Vždy přesně v tomhle znění, každý v novém chatu:

1. autoservis Statenice
2. nezávislý servis Škoda Praha-západ
3. kde opravit Volkswagen Horoměřice okolí
4. kolik stojí diagnostika auta u Prahy
5. servis převodovky DSG Praha západ
6. geometrie kol Statenice
7. kalibrace jízdních asistentů Praha
8. J&S servis Statenice recenze
9. servis CUPRA Praha 6 okolí
10. příprava na STK Praha západ

## Asistenti a postup

Měří se z Chrome na Macu správce, přihlášeného do Googlu a claude.ai. Výsledky
ovlivňuje poloha i účet, proto vždy ze stejného prohlížeče.

| Asistent | Jak položit dotaz |
|---|---|
| Google AI Mode | `https://www.google.com/search?q=<dotaz>&udm=50&hl=cs`, počkat ~15 s |
| Gemini | `https://gemini.google.com/app`, dotaz vložit do pole a odeslat, počkat ~40 s |
| Claude | `https://claude.ai/new?q=<dotaz>`, kliknout na odeslat, počkat ~40 s |
| ChatGPT | 14. 10. 2026 neměřen, bez přihlášení blokuje ověření proti robotům |
| Perplexity | 14. 10. 2026 neměřena, vyžaduje přihlášení |

Měření jde zadat i Claude Code s Claude in Chrome: „Zopakuj měření podle
mereni/README.md a porovnej s posledním výsledkem.“ (Gemini: text s diakritikou
vkládat přes stránku, ne psaním na klávesnici; odpověď se vykreslí až po
zobrazení záložky.)

## Co zapsat

Pro každý dotaz a asistenta:

- **Zmíněn:** ano / ne, případně pořadí nebo „okrajově“.
- **Web jako zdroj:** jasservis.cz v seznamu zdrojů odpovědi. Odkaz jen z karty
  firmy (Mapy Google) zapsat zvlášť.
- **Chyby:** každý nesprávný údaj o J&S (adresa, telefon, „autorizovaný“,
  „Praha“, služby, ceny) doslovně.

Cíl z plánu na 3 měsíce: zmíněn aspoň u 5 z 10 dotazů ve dvou asistentech, web
citován aspoň u 3, žádná chybná fakta.
