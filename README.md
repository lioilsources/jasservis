# jasservis.cz

Tvůj web. Můžeš ho měnit tím, že napíšeš, co chceš — z telefonu, česky,
bez programování.

## Jak na to

### 1. Řekni, co chceš změnit

V appce **GitHub** otevři tenhle repozitář → **Issues** → **New issue**.
Napiš `@claude` a za to svůj požadavek:

> **Title:** Nová otevírací doba
> **Body:** `@claude V sobotu máme nově otevřeno 8–12. Uprav to na kontaktech i v patičce.`

Odešli. Do minuty ti Claude odpoví, co udělá.

### 2. Podívej se na výsledek

Za pár minut Claude napíše, že je hotovo, a přidá odkaz **Create PR**. Klikni
na něj a potvrď — vznikne **Pull request**, tedy návrh změny. Do minuty se
v něm objeví odkaz **Otevřít náhled**: uvidíš web se změnou, ale ostrý web
`jasservis.cz` je pořád beze změny.

Nelíbí se? Napiš do pull requestu komentář `@claude ještě tohle…` a náhled se
za chvíli obnoví.

### 3. Když se ti to líbí, dej Merge

Tlačítko **Merge** v pull requestu. Za minutu dvě je změna na
`https://jasservis.cz`.

To je celé. Každý další nápad = nové issue.

## Když něco nefunguje

Napiš do issue nebo do komentáře v pull requestu:

> `@claude tohle je špatně, oprav to`

a přilož screenshot — Claude ho umí přečíst.

Když se na ostrý web dostalo něco, co tam být nemá: otevři ten pull request
a dej **Revert** → **Merge**. Web se vrátí do stavu před změnou.

## Na co si dát pozor

- **Jedna věc za issue.** Velké zadání rozděl, půjde to rychleji a líp.
- **Piš konkrétní údaje.** Telefon, cenu, otevírací dobu si Claude nevymyslí —
  napiš je přesně tak, jak mají na webu být.
- **Obrázky** přilož přímo do issue.
- Nastavení domény a nasazování je zamčené — kdyby bylo potřeba sáhnout tam,
  Claude to napíše.

## Co je uvnitř (nemusíš číst)

```
jasservis.cz/   web — tohle se mění (jedna složka = jedna stránka)
.github/        automatika, která web nasazuje a dělá náhledy
backup/         původní kopie starého webu, jen archiv
```

- Ostrý web: GitHub Pages, nasazuje se při každé změně větve `master`.
- Náhledy: Cloudflare Pages, pro každý pull request zvlášť.
