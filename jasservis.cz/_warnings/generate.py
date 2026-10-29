#!/usr/bin/env python3
"""Generate only the warning catalogue's three static page bodies from shared evidence.
No runtime translation; no remote requests; no changes to shared header styling.
"""
from pathlib import Path
import json,re,html,os,sys,csv,io
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
CAT=json.loads((HERE/'catalog.json').read_text());UI=json.loads((HERE/'locales.json').read_text())
ROUTE='kontrolky-a-vystrazna-hlaseni';LANGS=['cs','en','de'];VERSION='20261029-catalog-v5'
def esc(x):return html.escape(str(x),quote=True)
def rel(target,page):return os.path.relpath(ROOT/target,page.parent).replace(os.sep,'/')+('/' if not Path(target).suffix else '')
def locale_root(lang):return '' if lang=='cs' else lang+'/'
def page_path(lang):return ROOT/locale_root(lang)/ROUTE/'index.html'
def switcher(lang,page):
 u=UI[lang];names={'cs':'Čeština','en':'English','de':'Deutsch'};codes={'cs':'CZ','en':'EN','de':'DE'};desktop=[];mobile=[]
 for l in LANGS:
  href=rel(locale_root(l)+ROUTE,page)
  if l==lang:desktop.append(f'<span lang="{l}" aria-current="true">{codes[l]}</span>');mobile.append(f'<li><button type="button" class="language-current" lang="{l}" aria-current="true">{names[l]}</button></li>')
  else:desktop.append(f'<a lang="{l}" hreflang="{l}" href="{href}">{codes[l]}</a>');mobile.append(f'<li><a lang="{l}" hreflang="{l}" href="{href}">{names[l]}</a></li>')
 label={'cs':'Jazyk webu','en':'Website language','de':'Sprache der Website'}[lang]
 return f'<nav class="language-switcher" aria-label="{label}"><div class="language-desktop"><div class="language-codes">'+ '<span aria-hidden="true">|</span>'.join(desktop)+f'</div></div><details class="language-mobile"><summary aria-label="{label}: {names[lang]}">{codes[lang]}</summary><ul class="language-options" aria-label="{label}">'+''.join(mobile)+'</ul></details></nav>'
def modelkey(s):return s.get('manual','generic')
def options(vals,allText):return '<option value="">'+esc(allText)+'</option>'+''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k,v in vals.items())
def card(item,brand,lang,page):
 u=UI[lang];scopes=[s for s in item['scopes'] if s['brand']==brand];i=item;data=[{'model':modelkey(s),'power':s['powertrains']} for s in scopes];sid='kontrolka-'+(i['legacy_id'].lower() if i.get('legacy_id') else i['id']+'-'+brand)
 search=' '.join(i['name'].values())+' '+i['id']+' '+u['brands'][brand]+' '+' '.join(str(s.get('model') or '') for s in scopes)
 out=f'<details class="wl-card" id="{sid}" data-item="{esc(i["id"])}" data-brand="{brand}" data-color="{i["color"]}" data-system="{i["group"]}" data-search="{esc(search)}" data-scopes="{esc(json.dumps(data))}"><summary><span class="wl-symbol"><img src="{rel(i["graphic_path"],page)}" width="96" height="72" alt="{esc(i["alt"][lang])}"></span><span class="wl-name">{esc(i["name"][lang])}</span><span class="wl-status">{esc(u["colors"][i["color"]])} · {esc(u["kinds"][i["kind"]])} · {esc(u["states"][i["state"]])}</span><span class="wl-open">{esc(u["detail"])} <span aria-hidden="true"></span></span></summary><div class="wl-detail">'
 for key,label in [('meaning','meaning'),('action','action'),('note','signal')]:out+=f'<h4>{esc(u[label])}</h4><p>{esc(i[key][lang])}</p>'
 out+=f'<h4>{esc(u["validity"])}</h4><ul class="wl-sources">'
 for s in scopes:
  if s.get('manual'):
   m=CAT['manuals'][s['manual']];pg=', '.join(map(str,s['printed_pages']));pdf=', '.join(map(str,s['pdf_pages']));url=m['url']+'#page='+str(s['pdf_pages'][0]);powers=', '.join(u['powers'][p] for p in s['powertrains'])
   out+=f'<li><strong>{esc(u["brands"][brand])} {esc(s["model"])} · MY {s["model_year"]}</strong><br>{esc(s["edition"])} · {esc(powers)}<br><a href="{esc(url)}" target="_blank" rel="noopener">{esc(u["sourceEN"])}: {esc(u["pages"])} {pg} ({esc(u["pdfPages"])} {pdf})</a></li>'
  else:out+=f'<li><strong>{esc(u["generic"])}</strong><p>{esc(s["scope"][lang])}</p><a href="{esc(s["url"])}" target="_blank" rel="noopener">Volkswagen UK (English)</a></li>'
 out+='</ul><p>'+esc(u['equipment'])+'</p>'
 g=i['graphic_source'];credit=f'<a href="{esc(g["page"])}" target="_blank" rel="noopener">{esc(g["title"].replace("File:",""))}</a>' if g.get('page') else esc(g['title'])
 out+=f'<p class="wl-credit">{esc(u["graphic"])}: {credit} · {esc(g["author"])} · {esc(g["license"])}. <a href="zdroje.html#graphic-{esc(i["graphic"]+"-"+i["color"])}">{esc(u["auditLink"])}</a><br>{esc(u["checked"])}: {i["checked"]}.</p></div></details>'
 return out

def main(lang,page):
 u=UI[lang];models={s['manual']:f'{u["brands"][s["brand"]]} {s["model"]} · MY {s["model_year"]} · {s["edition"]}' for i in CAT['items'] for s in i['scopes'] if s.get('manual')}
 models['generic']=u['generic']
 out=f'<main id="warning-lights" class="warning-lights" lang="{lang}"><script type="application/json" id="wl-messages">'+json.dumps({k:u[k] for k in ['brands','overview','count','empty','missingBrand','preset']},ensure_ascii=False).replace('</','<\\/')+'</script>'
 out+='<div class="wl-intro">'+''.join('<p>'+esc(u[k])+'</p>' for k in ['intro1','intro2','intro3'])+'</div>'
 out+=f'<aside class="wl-stop" aria-labelledby="wl-stop-title"><h2 id="wl-stop-title">{esc(u["stopTitle"])}</h2><p>{esc(u["stop"])}</p></aside>'
 out+=f'<aside class="wl-scope"><strong>{esc(u["scopeTitle"])}</strong><p>{esc(u["scope"])}</p><p>{esc(u["yearNote"])}</p><a href="zdroje.html">{esc(u["auditLink"])}</a></aside><noscript><p>{esc(u["nojs"])}</p></noscript>'
 out+='<form class="wl-filters" role="search" aria-label="'+esc(u['search'])+'" hidden><label>'+esc(u['search'])+'<input type="search" id="wl-search" autocomplete="off"></label>'
 for key,vals,al in [('brand',u['brands'],'allBrands'),('model',models,'allModels'),('color',u['colors'],'allColors'),('system',u['groups'],'allSystems'),('power',u['powers'],'allPowers')]:out+=f'<label>{esc(u[key])}<select id="wl-{key}">'+options(vals,u[al])+'</select></label>'
 out+=f'<button type="reset">{esc(u["reset"])}</button></form><section id="prehled-kontrolek" class="wl-results" aria-labelledby="wl-results-title"><h2 id="wl-results-title" tabindex="-1">{esc(u["overview"])}</h2><p id="wl-brand-context" class="wl-brand-context" hidden></p><div class="wl-countline"><p id="wl-count" role="status" aria-live="polite"></p><a href="./#prehled-kontrolek">{esc(u["all"])}</a></div><p id="wl-empty" role="status" hidden>{esc(u["empty"])}</p>'
 for brand,bname in u['brands'].items():
  entries=[i for i in CAT['items'] if any(s['brand']==brand for s in i['scopes'])]
  if not entries:continue
  out+=f'<section class="wl-brand" data-brand="{brand}" aria-labelledby="brand-{brand}"><h2 id="brand-{brand}">{esc(bname)}</h2>'
  for group,gname in u['groups'].items():
   groupitems=[i for i in entries if i['group']==group]
   if groupitems:out+=f'<section class="wl-group" id="{group if brand=='volkswagen' else brand+'-'+group}"><h3>{esc(gname)}</h3><div class="wl-grid">'+''.join(card(i,brand,lang,page) for i in groupitems)+'</div></section>'
  out+='</section>'
 out+='</section>'
 out+=f'<section class="wl-contact"><h2>{esc(u["contactTitle"])}</h2><p>{esc(u["contact"])}</p><p><strong>{esc(u["hours"])}</strong></p><p>{esc(u["office"])}: <a href="tel:+420605399448">+420 605 399 448</a><br>{esc(u["workshop"])}: <a href="tel:+420608313437">+420 608 313 437</a></p><a class="tlacitko-akce" href="{rel(locale_root(lang)+"kontakt",page)}" data-booking-panel>{esc(u["contactButton"])}</a><p class="wl-note">{esc(u["notAssistance"])}</p></section>'
 out+=f'<details class="wl-review"><summary>{esc(u["audit"])}</summary><p>{esc(u["counts"].format(items=len(CAT["items"]),graphics=len(CAT["graphics"])))}</p><p>{esc(u["auditNote"])}</p><p><a href="zdroje.html">{esc(u["auditLink"])}</a> · <a href="{rel("_warnings/catalog.json",page)}">JSON</a></p></details></main>'
 return out

def create_page(lang):
 page=page_path(lang);page.parent.mkdir(parents=True,exist_ok=True)
 if page.exists():s=page.read_text()
 else:
  # Same-depth localized header and footer from the current project, never from production/history.
  s=page_path('cs').read_text();s=re.sub(r'((?:href|src)=["\'])\.\./',r'\1../../',s)
  template=(ROOT/lang/'serizeni-svetlometu/index.html').read_text()
  s=re.sub(r'<header\b.*?</header>',lambda m:re.search(r'<header\b.*?</header>',template,re.S)[0],s,count=1,flags=re.S)
  s=s[:s.index('<footer')]+template[template.index('<footer'):]
  s=s.replace('/js/service-navigation.js?','/js/service-navigation.'+lang+'.js?').replace('/js/contact-actions.js?','/js/contact-actions.'+lang+'.js?')
  s=s.replace('</head>',f'<link rel="stylesheet" href="../../wp-content/themes/theme53985/languages.css?v=20261029-i18n" /></head>')
 u=UI[lang];prefix=locale_root(lang);url='https://jasservis.cz/'+prefix+ROUTE+'/'
 s=re.sub(r'(<html\b[^>]*\blang=["\'])[^"\']+',r'\g<1>'+lang,s,count=1)
 s=re.sub(r'<main id="warning-lights".*?</main>',lambda m:main(lang,page),s,count=1,flags=re.S)
 s=re.sub(r'<nav class="language-switcher".*?</nav>',lambda m:switcher(lang,page),s,count=1,flags=re.S)
 s=re.sub(r'<title>.*?</title>','<title>'+esc(u['title'])+' | J&amp;S SERVIS</title>',s,count=1,flags=re.S)
 s=re.sub(r'<meta\b[^>]*(?:name=["\'](?:description|robots)["\']|property=["\'](?:og:title|og:description|og:url|og:locale|article:modified_time)["\'])[^>]*>','',s,flags=re.I)
 s=re.sub(r'<link\b[^>]*(?:rel=["\']canonical["\']|hreflang=)[^>]*>','',s,flags=re.I)
 s=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>','',s,flags=re.S)
 s=re.sub(r'(<h1 class="title-header">).*?(</h1>)',lambda m:m[1]+esc(u['title'].upper())+m[2],s,count=1,flags=re.S)
 crumb=f'<ul class="breadcrumb breadcrumb__t"><li><a href="{rel(prefix or ".",page)}">{esc(u["home"])}</a></li><li class="divider"></li><li><a href="{rel(prefix+"dalsi-sluzby",page)}">{esc(u["services"])}</a></li><li class="divider"></li><li class="active" aria-current="page">{esc(u["title"])}</li></ul>'
 s=re.sub(r'<ul class="breadcrumb breadcrumb__t">.*?</ul>',lambda m:crumb,s,count=1,flags=re.S)
 s=re.sub(r'(warning-lights\.(?:css|js)\?v=)[^"\']+',r'\g<1>'+VERSION,s)
 meta=f'<meta name="robots" content="noindex, nofollow" /><meta name="description" content="{esc(u["intro3"])}" /><link rel="canonical" href="{url}" /><meta property="og:title" content="{esc(u["title"])} | J&amp;S SERVIS" /><meta property="og:description" content="{esc(u["scopeTitle"])}" /><meta property="og:url" content="{url}" /><meta property="og:locale" content="'+{'cs':'cs_CZ','en':'en_GB','de':'de_DE'}[lang]+'" />'
 for l in LANGS:meta+=f'<link rel="alternate" hreflang="{l}" href="https://jasservis.cz/{locale_root(l)}{ROUTE}/" />'
 meta+=f'<link rel="alternate" hreflang="x-default" href="https://jasservis.cz/{ROUTE}/" />'
 schema={'@context':'https://schema.org','@graph':[{'@type':'WebPage','url':url,'name':u['title'],'inLanguage':lang,'description':u['scopeTitle']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':u['home'],'item':'https://jasservis.cz/'+prefix},{'@type':'ListItem','position':2,'name':u['services'],'item':'https://jasservis.cz/'+prefix+'dalsi-sluzby/'},{'@type':'ListItem','position':3,'name':u['title'],'item':url}]}]}
 meta+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
 s=s.replace('</head>',meta+'</head>');s=re.sub(r'(?m)^[ \t]+$','',s);return page,s

def audit(lang,page):
 u=UI[lang];heading={'cs':'Stav systematické kontroly','en':'Systematic review status','de':'Stand der systematischen Prüfung'}[lang]
 text=f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(u["audit"])}</title><style>body{{font:18px/1.6 system-ui,sans-serif;max-width:1100px;padding:20px;margin:auto;color:#222;overflow-wrap:anywhere}}h1,h2{{line-height:1.3}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #777;padding:10px;text-align:left;vertical-align:top}}a{{color:#111}}section{{margin-block:28px}}@media(max-width:650px){{table,tbody,tr,td{{display:block}}thead{{display:none}}td{{border-bottom:0}}tr{{margin-bottom:16px;border-bottom:1px solid #777}}}}</style></head><body><a href="./#prehled-kontrolek">{esc(u["overview"])}</a><h1>{esc(u["audit"])}</h1><p><strong>{esc(u["scopeTitle"])}</strong></p><p>{esc(u["scope"])}</p><p>{esc(u["counts"].format(items=len(CAT["items"]),graphics=len(CAT["graphics"])))}</p><p>{esc(u["yearNote"])}</p><p>{esc(u["auditNote"])}</p><h2>{heading}</h2>'
 statuses={'cs':{'selected-symbols-and-instructions-reviewed-not-complete':'Vybrané položky zkontrolované; celé vydání není hotové.','downloaded-not-yet-item-reviewed':'Staženo; kontrola všech symbolů nedokončená.'},'en':{'selected-symbols-and-instructions-reviewed-not-complete':'Selected entries checked; full edition not complete.','downloaded-not-yet-item-reviewed':'Downloaded; symbol-by-symbol review incomplete.'},'de':{'selected-symbols-and-instructions-reviewed-not-complete':'Ausgewählte Einträge geprüft; vollständige Ausgabe nicht abgeschlossen.','downloaded-not-yet-item-reviewed':'Heruntergeladen; symbolweise Prüfung nicht abgeschlossen.'}}[lang]
 text+='<table><thead><tr><th>Model · MY</th><th>'+esc(u['edition'])+'</th><th>'+{'cs':'Počet doložených záznamů','en':'Documented records','de':'Belegte Einträge'}[lang]+'</th><th>Status</th></tr></thead><tbody>'
 for k,m in sorted(CAT['manuals'].items()):text+=f'<tr><td>{esc(u["brands"][m["brand"]])} {esc(m["model"])} · MY {esc(m["year"])}</td><td><a href="{esc(m["url"])}">{esc(m["edition"])} (English)</a></td><td>{sum(any(sc.get("manual")==k for sc in it["scopes"]) for it in CAT["items"])}</td><td>{esc(statuses[m["status"]])}</td></tr>'
 text+='</tbody></table>'
 # Localised, explicit brand access gaps. No private Drive URLs or documents are published.
 gap={
 'cs':['Volkswagen: všechny modely a roky od 2010 zůstávají bez úplného modelového ověření. Veřejný digitální návod vyžaduje skutečný VIN; původních 15 příkladů UK neuvádí modelové roky. Potřebné jsou evropské modelové návody nebo přístup k jejich složce.','Audi: žádný evropský model ani rok od 2010 není zatím obrazově pokrytý. Veřejný seznam modelů v tomto prostředí vrací 403. SSP 667 není náhradou návodu k obsluze. Potřebné jsou evropské návody podle modelu a roku.','Škoda: žádný model ani rok od 2010 není zatím obrazově pokrytý. Zdroj veřejné aplikace je nedostupný (403), starší oficiální služba vrací 503. Potřebné jsou dostupné evropské návody.','Volkswagen Užitkové vozy: žádný model ani rok od 2010 není zatím obrazově pokrytý. Digitální návody vyžadují VIN. Potřebné jsou evropské modelové návody.','SEAT a CUPRA: platnost je zatím ověřena pouze pro jednotlivé položky ve výslovně uvedených modelových vydáních uvedených v kartách. Ostatní dostupné návody jsou v tabulce označené jako nedokončené. Žádná mezera mezi vydáními není automaticky vyplněná.','Chybějí zejména přesně ověřené grafické varianty a úplná revize Travel Assist, Front Assist, rozpoznání značek, parkovacích asistentů, AdBlue/SCR a vysokonapěťových výstrah. Varianty bez doložené grafiky nebo barvy nejsou publikované s náhradním symbolem.','Nápis READY (Mii electric MY2020) a bílá varianta Light Assist (Leon MY2021 / Formentor MY2021) zatím nejsou v zákaznickém přehledu: v prohlédnutých stranách nebyla potvrzena jejich barva. Modrá varianta Light Assist Born je doložena zvlášť.'],
 'en':['Volkswagen: all models and years from 2010 still lack complete model-specific verification. Public digital manuals require a real VIN; the 15 original UK examples do not specify model years. European model manuals or access to their folder are needed.','Audi: no European model or year from 2010 is yet covered by illustrated entries. The public model list returns 403 in this environment. SSP 667 does not replace an owner’s manual. European manuals by model and year are needed.','Škoda: no model or year from 2010 is yet covered by illustrated entries. The public application source is unavailable (403); the older official service returns 503. Accessible European manuals are needed.','Volkswagen Commercial Vehicles: no model or year from 2010 is yet covered by illustrated entries. Digital manuals require a VIN. European model manuals are needed.','SEAT and CUPRA: applicability is currently verified only for individual entries in the explicitly listed model editions identified on the cards. Other available manuals are marked incomplete in the table. No gap between editions is filled automatically.','In particular, accurately verified graphic variants and a full review of Travel Assist, Front Assist, traffic sign recognition, parking assistants, AdBlue/SCR and high-voltage warnings remain missing. Variants without documented graphics or colours are not published with substitute symbols.','The READY inscription (Mii electric MY2020) and white Light Assist version (Leon MY2021 / Formentor MY2021) are not yet in the customer overview: their colour was not confirmed on the reviewed pages. The Born blue Light Assist version is documented separately.'],
 'de':['Volkswagen: Für alle Modelle und Jahre ab 2010 fehlt weiterhin eine vollständige modellbezogene Prüfung. Öffentliche digitale Anleitungen benötigen eine echte FIN; die 15 ursprünglichen UK-Beispiele nennen keine Modelljahre. Benötigt werden europäische Modellanleitungen oder Zugang zu deren Ordner.','Audi: Noch kein europäisches Modell oder Jahr ab 2010 ist durch bebilderte Einträge abgedeckt. Die öffentliche Modellliste liefert in dieser Umgebung 403. SSP 667 ersetzt keine Betriebsanleitung. Benötigt werden europäische Anleitungen nach Modell und Jahr.','Škoda: Noch kein Modell oder Jahr ab 2010 ist durch bebilderte Einträge abgedeckt. Die Quelle der öffentlichen Anwendung ist nicht verfügbar (403); der ältere offizielle Dienst liefert 503. Zugängliche europäische Anleitungen werden benötigt.','Volkswagen Nutzfahrzeuge: Noch kein Modell oder Jahr ab 2010 ist durch bebilderte Einträge abgedeckt. Digitale Anleitungen benötigen eine FIN. Europäische Modellanleitungen werden benötigt.','SEAT und CUPRA: Die Gültigkeit ist bisher nur für einzelne Einträge in den ausdrücklich auf den Karten genannten Modellausgaben geprüft. Weitere verfügbare Anleitungen sind in der Tabelle als unvollständig gekennzeichnet. Lücken zwischen Ausgaben werden nicht automatisch ergänzt.','Insbesondere fehlen genau geprüfte Grafikvarianten und die vollständige Prüfung von Travel Assist, Front Assist, Verkehrszeichenerkennung, Parkassistenten, AdBlue/SCR und Hochvoltwarnungen. Varianten ohne belegte Grafik oder Farbe werden nicht mit Ersatzsymbolen veröffentlicht.','Der Schriftzug READY (Mii electric MY2020) und die weiße Light-Assist-Variante (Leon MY2021 / Formentor MY2021) fehlen noch in der Kundenübersicht: Ihre Farbe wurde auf den geprüften Seiten nicht bestätigt. Die blaue Light-Assist-Variante des Born ist separat belegt.']}[lang]
 text+='<ul>'+''.join('<li>'+esc(x)+'</li>' for x in gap)+'</ul>'
 text+='<h2>'+{'cs':'Křížová kontrola návodů','en':'Manual cross-check','de':'Abgleich der Anleitungen'}[lang]+'</h2>'
 for flag in CAT.get('cross_checks',[]):
  text+='<p><strong>'+esc(flag['model'])+' · MY '+str(flag['model_year'])+'</strong>: '+esc(flag['note'][lang])+'</p><ul>'
  for src in flag['sources']:text+='<li><a href="'+esc(src['url'])+'#page='+str(src['pdf_pages'][0])+'">'+esc(src['language'].upper())+' · '+esc(u['pages'])+' '+', '.join(map(str,src['printed_pages']))+'</a></li>'
  text+='</ul>'
 text+='<h2>'+esc(u['graphic'])+'</h2>'
 for k,g in CAT['graphics'].items():text+=f'<section id="graphic-{esc(k)}"><h3>{esc(k)}</h3><p>{esc(g["title"])} · {esc(g["author"])} · {esc(g["license"])}</p>'+ (f'<p><a href="{esc(g["page"])}">{esc(g["page"])}</a></p>' if g.get('page') else '') +(f'<p><a href="{esc(g["license_url"])}">License</a></p>' if g.get('license_url') else '')+f'<code>SHA-256: {g["sha256"]}</code></section>'
 text+='<h2>SSP</h2><p>'+esc(u['auditNote'])+'</p><ul>'+''.join('<li>'+esc(x['title'])+'</li>' for x in CAT['supplementary_sources'])+'</ul><p><a href="'+rel('_warnings/catalog.json',page)+'">JSON</a> · <a href="'+rel('_warnings/coverage.csv',page)+'">CSV</a></p></body></html>'
 return text

csv_stream=io.StringIO();writer=csv.writer(csv_stream,delimiter=';',lineterminator='\n')
writer.writerow(['ID','Název CZ','Name EN','Name DE','Brand','Model','Model year','Edition','Printed pages','PDF pages','Powertrains','State','Colour','Source','Graphic','Graphic source','Licence','Checked'])
for item in CAT['items']:
 for scope in item['scopes']:
  source=CAT['manuals'][scope['manual']]['url'] if scope.get('manual') else scope['url']
  writer.writerow([item['id'],item['name']['cs'],item['name']['en'],item['name']['de'],scope['brand'],scope.get('model') or 'Not documented',scope.get('model_year') or 'Not documented',scope.get('edition') or '',','.join(map(str,scope.get('printed_pages',[]))),','.join(map(str,scope.get('pdf_pages',[]))),','.join(scope['powertrains']),item['state'],item['color'],source,item['graphic_path'],item['graphic_source'].get('page',''),item['graphic_source']['license'],item['checked']])
outputs=[(HERE/'coverage.csv','\ufeff'+csv_stream.getvalue())]
for lang in LANGS:
 page,body=create_page(lang);outputs.append((page,body));outputs.append((page.parent/'zdroje.html',audit(lang,page)));outputs.append((page.parent/'evidence.json',json.dumps({'canonical_catalog':rel('_warnings/catalog.json',page),'review_status':'incomplete-preview','checked':CAT['checked'],**CAT['counts']},indent=2)+'\n'))
# Validate all translations and assets before touching output files.
assert len({x['id'] for x in CAT['items']})==len(CAT['items'])
for item in CAT['items']:
 for field in ['name','meaning','action','note','alt']:
  assert all(item[field].get(l) for l in LANGS),(item['id'],field)
 assert (ROOT/item['graphic_path']).is_file(),item['graphic_path']
for p,s in outputs:
 if '--check' in sys.argv:
  assert p.exists() and p.read_text()==s, 'Out of sync: '+str(p)
 else:p.write_text(s)
print(('Checked' if '--check' in sys.argv else 'Generated')+': 3 static locales, '+str(len(CAT['items']))+' semantic entries; shared images only.')
