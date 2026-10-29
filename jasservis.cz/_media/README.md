# Společná správa fotografií CZ / EN / DE

Autoritativní seznam je `catalog.json`. Web zůstává statický: `manage.py`
vytvoří současně české, anglické a německé HTML. Fotografie se při načítání
stránky nepřekládají ani neskládají JavaScriptem. Vše funguje i bez JavaScriptu.

- `pages` obsahuje jednu společnou pozici a pořadí médií každé stránky.
- `photos` obsahuje společné soubory, rozměry a případné responzivní varianty.
- `locales.cs/en/de` obsahují samostatné alternativní texty, popisky a další
  lokalizované texty, včetně stávajících ovládacích popisků.
- Obrázkové soubory zůstávají na původních místech; nejsou kopírovány do EN/DE.
- HTML uvnitř komentářů `shared-media` je výstup. Neupravovat fotografie
  samostatně ve třech stránkách. Texty mimo tyto oblasti zůstávají nezávislé.

Příkazy spouštět z kořene repozitáře (Python 3.9+, bez dalších balíčků):

```sh
python3 jasservis.cz/_media/manage.py list
python3 jasservis.cz/_media/manage.py check
python3 jasservis.cz/_media/manage.py sync
```

`check` odhalí chybějící soubory, chybějící jazykovou variantu, opakované ID,
nesoulad výstupu i fotografii přidanou mimo společný seznam. `sync` promítne
úpravu katalogu do všech tří jazyků. Před zápisem se ověří všechny výstupy;
při chybě validace se nezapíše žádná stránka. Tento krok je nutný před odesláním
změn do náhledu. Stávající automatiku nasazování není potřeba měnit.

## Výměna

```sh
python3 jasservis.cz/_media/manage.py replace ID wp-content/uploads/fotografie.jpg --width 1280 --height 960
```

Rozměry musí odpovídat skutečnému souboru. Současně se aktualizují odkazy na
zvětšení, miniatury a případné kopie téže fotografie pro mobil/desktop dané
stránky ve všech jazycích. Původní `srcset` se zruší, aby prohlížeč nezobrazoval
staré varianty. Odkaz na PDF se nemění. Aktualizují se rovněž obrazové odkazy
v metadatech této stránky. Přeložené popisky se při prosté výměně souboru nemění;
pokud fotografie zachycuje jiný obsah, upravit také `locales` v katalogu a spustit `sync`.

## Pořadí a odstranění

```sh
python3 jasservis.cz/_media/manage.py move ID --position 1
python3 jasservis.cz/_media/manage.py remove ID
```

Pořadí je číslované od 1 uvnitř galerie. Při přesunu mezi bloky použít také
`--group gallery-02`, případně `--page specializovana-diagnostika/index.html`.
Nezaměňovat fotografie různých metod bez věcného důvodu. Odstranění odebere
fotografii z příslušné stránky ve všech třech jazycích; fyzický soubor nemaže,
protože jej mohou používat jiné stránky.

## Přidání

Připravit skutečný obrázek a JSON s doloženými popisky:

```json
{
  "cs": {"alt": "Český alternativní text", "caption": "Český popisek"},
  "en": {"alt": "English alternative text", "caption": "English caption"},
  "de": {"alt": "Deutscher Alternativtext", "caption": "Deutsche Bildunterschrift"}
}
```

```sh
python3 jasservis.cz/_media/manage.py add nove-id wp-content/uploads/fotografie.jpg --page specializovana-diagnostika --group gallery-02 --width 1280 --height 960 --translations /tmp/popisky.json
```

Nová položka dostane existující jednoduché rozložení obrázku s popiskem a
odkazem na plnou velikost. Chybějící EN/DE text se nepřebírá z češtiny a
nevymýšlí se: příkaz skončí chybou. Pro zvláštní existující typy médií lze
připravit položku přímo v katalogu podle odpovídajícího stávajícího vzoru.

Loga, ocenění a dekorativní ikony jsou mimo seznam fotografií. Nadále používají
jediné původní společné soubory. Fotografie pozadí v CSS jsou již společné pro
všechny jazyky; snímky slideru a obrázková pozadí v HTML jsou v katalogu.

Po každé úpravě zkontrolovat `check`, místní odkazy, popisky a zobrazení na
mobilu a počítači. Samotný tento nástroj nic nepublikuje.
