# Jak je postavený web jasservis.cz

Podrobnosti ke struktuře webu pro agenta. Přesunuto z `CLAUDE.md`, kde zůstalo shrnutí.

Tři věci, které tu nejsou vidět na první pohled:

1. **Hlavička, menu a patička jsou zkopírované v každé stránce.** Společná šablona
   neexistuje. Změna v menu, logu, telefonu v hlavičce nebo v patičce se musí udělat
   **ve všech** `jasservis.cz/**/index.html` stejně. Před pushem ověř Grepem, že
   starý text už nikde nezůstal.
2. **Cesty jsou relativní k umístění stránky.** Úvodní stránka odkazuje na
   `wp-content/…`, stránka v podsložce na `../wp-content/…`, odkazy mezi stránkami
   stejně (`../kontakt/`). Nepoužívej cesty začínající `/` ani `https://jasservis.cz/…`
   pro obrázky, styly a skripty, rozbilo by to náhled.
3. **HTML je strojově vygenerované** (WordPress, CherryFramework). Je ukecané a plné
   tříd, které vypadají zbytečně. Nepřepisuj ho ani „neuklízej", měň jen to, o co
   majitel žádá, a drž se stylu okolního kódu.

Nová stránka = nová složka `jasservis.cz/<nazev-bez-diakritiky>/index.html`, kopie
podobné existující stránky, plus odkaz v menu na všech stránkách (pokud ho tam
majitel chce). Nový obrázek patří do `jasservis.cz/wp-content/uploads/`.
