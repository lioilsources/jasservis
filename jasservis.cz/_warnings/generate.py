#!/usr/bin/env python3
"""Generate only the warning catalogue's three static page bodies from shared evidence.
No runtime translation; no remote requests; no changes to shared header styling.
"""
from pathlib import Path
import json,re,html,os,sys,csv,io
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
CAT=json.loads((HERE/'catalog.json').read_text());UI=json.loads((HERE/'locales.json').read_text())
ROUTE='kontrolky-a-vystrazna-hlaseni';LANGS=['cs','en','de'];VERSION='20261030-review-v6'
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
def model_label(model,year):return str(model)+(f' · MY {year}' if year else '')
def source_label(m,lang):
 names={'cs':{'CS':'čeština','DE':'němčina','EN':'angličtina'},'en':{'CS':'Czech','DE':'German','EN':'English'},'de':{'CS':'Tschechisch','DE':'Deutsch','EN':'Englisch'}}
 label={'cs':'Návod','en':'Manual','de':'Anleitung'}[lang]+' · '+names[lang].get(m['lang'],m['lang'])
 if m.get('host_kind')=='third-party-copy':label+=' · '+{'cs':'kopie vydání výrobce na jiném serveru','en':'manufacturer edition hosted by a third party','de':'von Dritten gehostete Herstellerausgabe'}[lang]
 return label
def options(vals,allText):return '<option value="">'+esc(allText)+'</option>'+''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k,v in vals.items())
def card(item,brand,lang,page):
 u=UI[lang];scopes=[s for s in item['scopes'] if s['brand']==brand];i=item;data=[{'model':modelkey(s),'power':s['powertrains']} for s in scopes];sid='kontrolka-'+(i['legacy_id'].lower() if i.get('legacy_id') and brand=='volkswagen' else i['id']+'-'+brand)
 search=' '.join(i['name'].values())+' '+i['id']+' '+u['brands'][brand]+' '+' '.join(str(s.get('model') or '') for s in scopes)
 out=f'<details class="wl-card" id="{sid}" data-item="{esc(i["id"])}" data-brand="{brand}" data-color="{i["color"]}" data-system="{i["group"]}" data-search="{esc(search)}" data-scopes="{esc(json.dumps(data))}"><summary><span class="wl-symbol"><img src="{rel(i["graphic_path"],page)}" width="96" height="72" alt="{esc(i["alt"][lang])}"></span><span class="wl-name">{esc(i["name"][lang])}</span><span class="wl-status">{esc(u["colors"][i["color"]])} · {esc(u["kinds"][i["kind"]])} · {esc(u["states"][i["state"]])}</span><span class="wl-open">{esc(u["detail"])} <span aria-hidden="true"></span></span></summary><div class="wl-detail">'
 if not any(sc.get('manual')for sc in scopes):out=out.replace('<span class="wl-open">','<span class="wl-status">'+esc(u['generic'])+'</span><span class="wl-open">',1)
 for key,label in [('meaning','meaning'),('action','action'),('note','signal')]:out+=f'<h4>{esc(u[label])}</h4><p>{esc(i[key][lang])}</p>'
 out+=f'<h4>{esc(u["validity"])}</h4><ul class="wl-sources">'
 for s in scopes:
  if s.get('manual'):
   m=CAT['manuals'][s['manual']];powers=', '.join(u['powers'][p] for p in s['powertrains'])
   if m.get('document_type')=='html':
    url=m['url'];location=' · '.join(s['source_sections'])
   else:
    pg=', '.join(map(str,s['printed_pages']));pdf=', '.join(map(str,s['pdf_pages']));url=m['url']+'#page='+str(s['pdf_pages'][0]);location=f'{u["pages"]} {pg} ({u["pdfPages"]} {pdf})'
   out+=f'<li><strong>{esc(u["brands"][brand])} {esc(model_label(s["model"],s["model_year"]))}</strong><br>{esc(s["edition"])} · {esc(powers)}<br><a href="{esc(url)}" target="_blank" rel="noopener">{esc(source_label(m,lang))}: {esc(location)}</a>'
   if m.get('viewer_url'):
    alternate=m['viewer_url'].replace('{page}',str(s['pdf_pages'][0]));out+='<br><a href="'+esc(alternate)+'" target="_blank" rel="noopener">'+{'cs':'Alternativní prohlížeč stejného vydání','en':'Alternative viewer for the same edition','de':'Alternativer Betrachter derselben Ausgabe'}[lang]+'</a>'
   if s.get('model_note'):out+='<p>'+esc(s['model_note'][lang])+'</p>'
   out+='</li>'
  else:out+=f'<li><strong>{esc(u["generic"])}</strong><p>{esc(s["scope"][lang])}</p><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s.get("source_label", "Volkswagen UK (English)"))}</a></li>'
 out+='</ul><p>'+esc(u['equipment'])+'</p>'
 for sc in scopes:
  if sc.get('manual') and CAT['manuals'][sc['manual']].get('model_year_note'):out+='<p>'+esc(CAT['manuals'][sc['manual']]['model_year_note'][lang])+'</p>'
 g=i['graphic_source'];credit=f'<a href="{esc(g["page"])}" target="_blank" rel="noopener">{esc(g["title"].replace("File:",""))}</a>' if g.get('page') else esc(g['title'])
 out+=f'<p class="wl-credit">{esc(u["graphic"])}: {credit} · {esc(g["author"])} · {esc(g["license"])}. <a href="zdroje.html#graphic-{esc(i["graphic"]+"-"+i["color"])}">{esc(u["auditLink"])}</a><br>{esc(u["checked"])}: {i["checked"]}.</p></div></details>'
 return out

def main(lang,page):
 u=UI[lang];models={s['manual']:f'{u["brands"][s["brand"]]} {model_label(s["model"],s["model_year"])} · {s["edition"]}' for i in CAT['items'] for s in i['scopes'] if s.get('manual')}
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
 out+=f'<details class="wl-review"><summary>{esc(u["audit"])}</summary><p>{esc(u["counts"].format(items=len(CAT["items"]),graphics=CAT["counts"]["shared_graphic_colour_variants"],shapes=CAT["counts"]["distinct_pictogram_shapes"]))}</p><p>{esc(u["auditNote"])}</p><p><a href="zdroje.html">{esc(u["auditLink"])}</a> · <a href="{rel("_warnings/catalog.json",page)}">JSON</a></p></details></main>'
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
 crumb=f'<ul class="breadcrumb breadcrumb__t"><li><a href="{rel(prefix or ".",page)}">{esc(u["home"])}</a></li><li class="divider"></li><li><a href="{rel(prefix+"autoservis",page)}">{esc(u["services"])}</a></li><li class="divider"></li><li class="active" aria-current="page">{esc(u["title"])}</li></ul>'
 s=re.sub(r'<ul class="breadcrumb breadcrumb__t">.*?</ul>',lambda m:crumb,s,count=1,flags=re.S)
 s=re.sub(r'(warning-lights\.(?:css|js)\?v=)[^"\']+',r'\g<1>'+VERSION,s)
 meta=f'<meta name="robots" content="noindex, nofollow" /><meta name="description" content="{esc(u["intro3"])}" /><link rel="canonical" href="{url}" /><meta property="og:title" content="{esc(u["title"])} | J&amp;S SERVIS" /><meta property="og:description" content="{esc(u["scopeTitle"])}" /><meta property="og:url" content="{url}" /><meta property="og:locale" content="'+{'cs':'cs_CZ','en':'en_GB','de':'de_DE'}[lang]+'" />'
 for l in LANGS:meta+=f'<link rel="alternate" hreflang="{l}" href="https://jasservis.cz/{locale_root(l)}{ROUTE}/" />'
 meta+=f'<link rel="alternate" hreflang="x-default" href="https://jasservis.cz/{ROUTE}/" />'
 schema={'@context':'https://schema.org','@graph':[{'@type':'WebPage','url':url,'name':u['title'],'inLanguage':lang,'description':u['scopeTitle']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':u['home'],'item':'https://jasservis.cz/'+prefix},{'@type':'ListItem','position':2,'name':u['services'],'item':'https://jasservis.cz/'+prefix+'autoservis/'},{'@type':'ListItem','position':3,'name':u['title'],'item':url}]}]}
 meta+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
 s=s.replace('</head>',meta+'</head>');s=re.sub(r'(?m)^[ \t]+$','',s);return page,s

def second_review_page(lang,page):
 a=json.loads((HERE/'attachment-groups.json').read_text());d=json.loads((HERE/'terramar-1125-overview-review.json').read_text());u=UI[lang]
 t={'cs':['Podklady pro nezávislou obsahovou kontrolu','Přehled je rozpracovaný. Úplnost není potvrzená pro celý model, značku ani koncern.','Oddělené skupiny fotografií','Dostupné fotografie','Požadovaný počet','Dokončená revize a přesné mezery','Úplný export textů CZ/EN/DE a použitých sdílených symbolů','Samostatné texty','Použité symboly a licence','Terramar 11.2025 — celé vstupní tabulky, strany 11–15','Toto je nezávisle ověřené vydání 578012720AC. Nejde o identifikaci chybějících nových fotografií návodu na stranách 7–10.','110 významových buněk není 110 unikátních symbolů. Přehled byl porovnán celý; ne všechny odkazované pokyny a grafiky jsou dokončené.','Řádek a zdroj','Původní popisek EN','Ověření pokynů a barvy','Skutečný stav na webu','Pokyny porovnané','Navazující pokyny nedokončené','Barva displeje nedoložená; neutrální tisk není černá výstraha','V katalogu pro dané vydání','Chybí v katalogu / nedokončené','Porovnání šesti fotografií Terramaru, včetně přesných poloh','Nejasné symboly se neurčují odhadem. Nové fotografie CUPRA a fotografie Audi nejsou nahrazené snímky jiného návodu.'],
 'en':['Materials for independent content review','The overview is in progress. Completeness is not confirmed for a whole model, brand or group.','Separate photograph groups','Available photos','Requested count','Completed comparisons and exact gaps','Full CZ/EN/DE text and shared-symbol export','Separate text files','Used symbols and licences','Terramar 11.2025 — complete opening tables, pages 11–15','This independently verified edition is 578012720AC. It does not identify the missing new manual photographs on pages 7–10.','110 meaning cells are not 110 unique symbols. The entire overview was compared; not all referenced instructions and graphics are complete.','Row and source','Original EN caption','Instruction and colour verification','Actual website status','Instructions compared','Referenced instructions unfinished','Display colour unproven; neutral print is not a black warning','In catalogue for this edition','Missing from catalogue / unfinished','Six Terramar photo comparison, including exact positions','Unclear symbols are not guessed. New CUPRA and Audi photographs are not replaced by images of another manual.'],
 'de':['Unterlagen zur unabhängigen Inhaltsprüfung','Die Übersicht ist in Bearbeitung. Vollständigkeit für ein ganzes Modell, eine Marke oder den Konzern ist nicht bestätigt.','Getrennte Fotogruppen','Verfügbare Fotos','Angeforderte Anzahl','Abgeschlossene Vergleiche und genaue Lücken','Vollständiger CZ/EN/DE-Text- und gemeinsamer Symbolexport','Einzelne Textdateien','Verwendete Symbole und Lizenzen','Terramar 11.2025 — vollständige Eingangstabellen, Seiten 11–15','Diese eigenständig geprüfte Ausgabe ist 578012720AC. Sie identifiziert nicht die fehlenden neuen Anleitungsfotos auf Seiten 7–10.','110 Bedeutungszellen sind nicht 110 einzigartige Symbole. Ganze Übersicht verglichen; nicht alle Folgeanweisungen und Grafiken abgeschlossen.','Zeile und Quelle','Originalbeschriftung EN','Anweisungs-/Farbprüfung','Tatsächlicher Webstand','Anweisungen verglichen','Folgeanweisungen offen','Anzeigefarbe nicht belegt; neutraler Druck ist keine schwarze Warnung','Im Katalog für diese Ausgabe','Fehlt im Katalog / offen','Sechs Terramar-Fotos verglichen, einschließlich genauer Positionen','Unklare Symbole nicht erraten. Neue CUPRA- und Audi-Fotos nicht durch Bilder anderer Anleitung ersetzt.']}[lang]
 style='body{font:18px/1.6 system-ui,sans-serif;color:#222;max-width:1440px;padding:20px;margin:auto;overflow-wrap:anywhere}h1,h2{line-height:1.3}a{color:#111}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #999;padding:10px;text-align:left;vertical-align:top}section{margin-block:28px}a:focus-visible{outline:3px solid #df5300;outline-offset:3px}@media(max-width:900px){table,tbody,tr,td{display:block}thead{display:none}td:before{content:attr(data-label)+": ";font-weight:600}tr{margin-bottom:16px}}'
 out='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+esc(t[0])+' | J&amp;S SERVIS</title><style>'+style+'</style></head><body><a href="./#prehled-kontrolek">'+esc(u['overview'])+'</a> · <a href="revize-kapitol.html#pracovni-fronty">'+t[5]+'</a><h1>'+t[0]+'</h1><p><strong>'+t[1]+'</strong></p><nav>'
 for l in LANGS:out+='<a lang="'+l+'" href="'+rel(locale_root(l)+ROUTE+'/druha-kontrola.html',page)+'">'+l.upper()+'</a> '
 out+='</nav><section id="export"><h2>'+t[6]+'</h2><p><a href="'+rel('_warnings/catalog-review-export.zip',page)+'">ZIP</a></p><p>'+t[7]+': '
 for l in LANGS:out+='<a href="'+rel('_warnings/catalog-texts.'+l+'.csv',page)+'">'+l.upper()+' CSV</a> '
 out+='</p><p><a href="'+rel('_warnings/used-symbols.csv',page)+'">'+t[8]+'</a></p></section><section id="prilohy"><h2>'+t[2]+'</h2><p>'+t[22]+'</p>'
 for g in a['groups']:out+='<h3>'+esc(g['id'])+'</h3><p>'+t[3]+': '+str(g['available_in_conversation'])+' / '+t[4]+': '+str(g['expected'])+'</p><p>'+esc(g['status'][lang])+'</p>'
 out+='<p><a href="'+rel('_warnings/attachment-groups.json',page)+'">JSON</a></p></section><section id="fotografie"><h2>'+t[21]+'</h2><p><a href="'+rel('_warnings/all-terramar-photo-occurrences.'+lang+'.csv',page)+'">CSV</a> · <a href="revize.html#fotografie-terramar">'+esc(u['auditLink'])+'</a></p></section><section id="terramar"><h2>'+t[9]+'</h2><p>'+t[10]+'</p><p><strong>'+t[11]+'</strong></p><p><a href="'+rel('_warnings/terramar-1125-overview-review.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/terramar-1125-overview-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in t[12:16])+'</tr></thead><tbody>'
 for r in d['rows']:
  status=(t[16]if r['referenced_instruction_reviewed']else t[17])+'; '+(str(r['actual_display_colour'])if r['actual_display_colour_verified']else t[18]);links=[]
  for id in r['catalogue_entries']:
   item=next(i for i in CAT['items']if i['id']==id);links.append('<a href="./?znacka=cupra#kontrolka-'+id+'-cupra">'+esc(item['name'][lang])+'</a>')
  vals=['<a href="'+esc(r['source_url'])+'">'+esc(r['row_id'])+' · '+str(r['printed_page'])+'</a>',esc(r['source_label']),esc(status),('<strong>'+t[19]+'</strong><br>'+'<br>'.join(links)if links else'<strong>'+t[20]+'</strong>')+'<p>'+esc(r['remaining'][lang])+'</p>']
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+v+'</td>'for label,v in zip(t[12:16],vals))+'</tr>'
 out+='</tbody></table></section><section id="enyaq"><h2>'+{'cs':'Škoda Enyaq — požadované fotografie a nezávislá revize','en':'Škoda Enyaq — requested photos and independent review','de':'Škoda Enyaq — angeforderte Fotos und eigenständige Prüfung'}[lang]+'</h2><p>'+{'cs':'Pět fotografií stran 12–17 není v dostupných přílohách. Tabulka jejich řádků proto není hotová a vydání ani modelový rok nejsou určené. Následující samostatná revize návodu DE 11.2020 není identifikací fotografovaného návodu.','en':'Five photos of pages12–17 are absent from available attachments. Their row comparison is therefore unfinished and edition/model year unidentified. The following separate DE11.2020 manual review does not identify the photographed manual.','de':'Fünf Fotos der Seiten12–17 fehlen in verfügbaren Anhängen. Zeilenvergleich daher offen und Ausgabe/Modelljahr unbestimmt. Folgende getrennte Prüfung DE11.2020 identifiziert nicht fotografierte Anleitung.'}[lang]+'</p><p><a href="'+rel('_warnings/enyaq-requested-photo-status.'+lang+'.csv',page)+'">'+{'cs':'Stav pěti fotografií','en':'Five-photo status','de':'Stand der fünf Fotos'}[lang]+' CSV</a> · <a href="'+rel('_warnings/enyaq-independent-review.'+lang+'.csv',page)+'">'+{'cs':'Nezávislé porovnání 11.2020','en':'Independent11.2020 comparison','de':'Eigenständiger Vergleich11.2020'}[lang]+' CSV</a> · <a href="'+rel('_warnings/enyaq-independent-review.json',page)+'">JSON</a></p></section><section id="audi-q4-climate"><h2>'+{'cs':'Audi Q4 07.2024 — porovnání funkcí klimatizace','en':'Audi Q4 07.2024 — climate-function comparison','de':'Audi Q4 07.2024 — Vergleich der Klimafunktionen'}[lang]+'</h2><p><a href="'+rel('_warnings/q4-climate-function-review.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/q4-climate-function-review.json',page)+'">JSON</a></p></section><p><a href="revize-kapitol.html#pracovni-fronty">'+t[5]+'</a></p></body></html>';return out

def work_queue_section(lang,page):
 q=json.loads((HERE/'work-queues.json').read_text());u=UI[lang]
 labels={'cs':['Zbývající práce ve čtyřech oddělených skupinách','Tato evidence odlišuje dostupnou nedokončenou práci, konkrétní chybějící dokumenty, neověřené významy a grafiky a nevyřešené použití ověřených grafik. Žádný celý návod není dokončený.','Model a vydání','Ověřené části / grafiky','Zbývající práce','Zdroj','Význam ověřen','Přesná zdrojová grafika ověřena','Vloženo do náhledu','Ano','Ne'], 'en':['Remaining work in four separate queues','This register separates available unfinished work, specific missing sources, unverified meanings and graphics, and unresolved reuse of verified graphics. No whole manual is complete.','Model and edition','Compared sections / graphics','Remaining work','Source','Meaning verified','Exact source graphic verified','Published in preview','Yes','No'],'de':['Offene Arbeit in vier getrennten Gruppen','Dieses Register trennt verfügbare offene Arbeit, konkrete fehlende Quellen, ungeprüfte Bedeutungen und Grafiken sowie ungeklärte Nutzung geprüfter Grafiken. Keine ganze Anleitung ist abgeschlossen.','Modell und Ausgabe','Geprüfte Abschnitte / Grafiken','Offene Arbeit','Quelle','Bedeutung geprüft','Genaue Quellgrafik geprüft','In Vorschau eingefügt','Ja','Nein']}[lang]
 out='<section id="pracovni-fronty"><h2>'+labels[0]+'</h2><p>'+labels[1]+'</p><p><a href="'+rel('_warnings/work-queues.json',page)+'">JSON</a> · <a href="'+rel('_warnings/work-queues.'+lang+'.csv',page)+'">CSV</a></p>'
 for group in q['groups']:
  out+='<h3>'+esc(group['title'][lang])+'</h3>'
  for r in group['rows']:
   brand=u['brands'].get(r['brand'],r['brand']);out+='<details><summary>'+esc(brand+' · '+str(r.get('model')or'—')+' · '+r['edition'])+'</summary><div>'
   for state,label in [('meaning_verified',labels[6]),('exact_source_graphic_verified',labels[7]),('published',labels[8])]:
    if state in r:out+='<p><strong>'+label+': '+(labels[9]if r[state]else labels[10])+'</strong></p>'
   refs=r.get('closed_comparisons',r.get('graphic_references',[]))
   if refs:out+='<p>'+labels[3]+': '+esc(', '.join(refs))+'</p>'
   out+='<p>'+esc(r['remaining'][lang])+'</p><p><a href="'+esc(r['source_url'])+'">'+labels[5]+'</a></p>'
   if r.get('conditions_source'):out+='<p><a href="'+esc(r['conditions_source'])+'">'+esc(r['conditions_edition']+' · '+r['conditions_clause'])+'</a></p>'
   out+='</div></details>'
 out+='</section>';return out

def chapter_page(lang,page):
 u=UI[lang];d=json.loads((HERE/'chapter-review.json').read_text());photos=json.loads((HERE/'terramar-photo-review.json').read_text())
 t={'cs':['Revize po modelech, vydáních a kapitolách','Žádný celý návod ani celá značka zatím nejsou označené jako dokončené. Uzavřené níže uvedené úzké oddíly nejsou dokončením ostatních kapitol.','Fotografie Terramar – identifikace souborů a záběrů','Pracovní označení','Původní název souboru','Záběr','Nepředán u vloženého obrázku','Uzavřená porovnání přesně vymezených oddílů','Porovnání uzavřeno; položky na webu doplněné','Porovnání uzavřeno; doplnění do webu není hotové','Postup podle jednotlivých vydání','Oblast','Stav','Porovnané stránky / části','Konkrétní položky na webu','Co zbývá','Zbývající přesné podklady','Technické testy jsou vedené odděleně a nedokládají obsahovou úplnost.','Vybrané položky porovnány; zbytek kapitoly otevřený','Zatím neporovnáno','Některé přesně vymezené oddíly uzavřené; zbytek otevřený','Funkce porovnány, přesné grafiky chybějí'],
 'en':['Review by model, edition and chapter','No entire manual or brand is marked complete. The closed narrow subsections below do not complete the remaining chapters.','Terramar photos – file and view identification','Working reference','Original filename','View','Not supplied with the inline image','Closed comparisons of precisely bounded subsections','Comparison closed; corresponding website entries present','Comparison closed; website publication incomplete','Progress by individual edition','Area','Status','Compared pages / sections','Specific website entries','Remaining work','Exact outstanding sources','Technical tests are recorded separately and do not establish content completeness.','Selected entries compared; rest of chapter open','Not yet compared','Some bounded subsections closed; rest open','Functions compared; exact graphics missing'],
 'de':['Prüfung nach Modell, Ausgabe und Kapitel','Keine vollständige Anleitung oder Marke ist abgeschlossen. Die unten abgeschlossenen engen Teilabschnitte schließen andere Kapitel nicht ab.','Terramar-Fotos – Datei- und Bildidentifikation','Arbeitskennung','Originaldateiname','Ansicht','Mit eingebettetem Bild nicht mitgeteilt','Abgeschlossene Vergleiche genau begrenzter Teilabschnitte','Vergleich abgeschlossen; Webeinträge vorhanden','Vergleich abgeschlossen; Veröffentlichung unvollständig','Fortschritt nach einzelner Ausgabe','Bereich','Status','Verglichene Seiten / Abschnitte','Konkrete Webeinträge','Offene Arbeit','Genaue fehlende Quellen','Technische Tests werden getrennt geführt und belegen keine inhaltliche Vollständigkeit.','Ausgewählte Einträge verglichen; restliches Kapitel offen','Noch nicht verglichen','Einige begrenzte Abschnitte abgeschlossen; Rest offen','Funktionen verglichen; genaue Grafiken fehlen']}[lang]
 style='body{font:18px/1.6 system-ui,sans-serif;color:#222;max-width:1440px;padding:20px;margin:auto;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:#111}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #999;padding:9px;text-align:left;vertical-align:top}details{border:1px solid #999;margin-block:12px}summary{cursor:pointer;padding:14px;font-weight:600;background:#f4f4f4}details>div{padding:14px}summary:focus-visible,a:focus-visible{outline:3px solid #df5300;outline-offset:3px}@media(max-width:900px){table,tbody,tr,td{display:block}thead{display:none}td:before{content:attr(data-label)+": ";font-weight:600}tr{margin-bottom:16px}}'
 out='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+esc(t[0])+' | J&amp;S SERVIS</title><style>'+style+'</style></head><body><a href="./#prehled-kontrolek">'+esc(u['overview'])+'</a> · <a href="revize.html#fotografie-terramar">'+esc(u['auditLink'])+'</a><h1>'+t[0]+'</h1><p><strong>'+t[1]+'</strong></p><nav>'
 for l in LANGS:out+='<a lang="'+l+'" href="'+rel(locale_root(l)+ROUTE+'/revize-kapitol.html',page)+'">'+l.upper()+'</a> '
 out+='</nav><p><a href="druha-kontrola.html">'+{'cs':'Podklady pro druhou kontrolu: fotografie, celý přehled Terramar a export','en':'Second-review materials: photographs, entire Terramar overview and export','de':'Unterlagen zur Zweitprüfung: Fotos, ganze Terramar-Übersicht und Export'}[lang]+'</a></p>'+work_queue_section(lang,page)+'<section id="fotografie"><h2>'+t[2]+'</h2><p>'+esc(photos['photo_inventory_status']['clarification'][lang])+'</p><p><a href="'+rel('_warnings/terramar-photo-inventory.'+lang+'.csv',page)+'">CSV</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in t[3:6])+'</tr></thead><tbody>'
 for ph in photos['photos']:
  vals=[ph['working_reference'],ph.get('original_filename')or t[6],ph['identifying_description'][lang]]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+esc(value)+'</td>'for label,value in zip(t[3:6],vals))+'</tr>'
 out+='</tbody></table></section><section id="hotove-oddily"><h2>'+t[7]+'</h2>'
 for row in d['completed_bounded_subsections']:
  m=CAT['manuals'][row['manual']];where=', '.join(map(str,row['printed_pages']))or' / '.join(row['source_sections']);ref=m['url']+('#page='+str(row['printed_pages'][0]+2)if row['printed_pages']else'')
  out+='<details><summary>'+esc(u['brands'][m['brand']]+' '+m['model']+' · '+m['edition']+' · '+row['title'][lang])+'</summary><div><p><strong>'+(t[8]if row['website_complete']else t[9])+'</strong></p><p><a href="'+esc(ref)+'">'+esc(u['pages'])+': '+esc(where)+'</a></p><p>'+esc(row['precise_boundary_i18n'][lang])+'</p><ul>'
  for state in row['source_rows']:
   out+='<li>'+esc(state['source_state'][lang])+': '
   for id in state['catalogue_ids']:
    item=next(i for i in CAT['items']if i['id']==id);out+='<a href="./?znacka='+m['brand']+'#kontrolka-'+(item['legacy_id'].lower()if item.get('legacy_id')and m['brand']=='volkswagen'else id+'-'+m['brand'])+'">'+esc(item['name'][lang])+'</a> '
   if not state['catalogue_ids']:out+=esc(t[9])
   out+='</li>'
  out+='</ul><p>'+esc(row['remaining'][lang])+'</p>'
  if row.get('evidence_file'):
   out+='<p><a href="'+rel('_warnings/'+row['evidence_file'],page)+'">JSON</a> · <a href="'+rel('_warnings/'+row['evidence_file'].replace('.json','.'+lang+'.csv'),page)+'">CSV</a></p>'
  out+='</div></details>'
 out+='</section><section id="navody"><h2>'+t[10]+'</h2><p><a href="'+rel('_warnings/chapter-review.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/chapter-review.json',page)+'">JSON</a></p>'
 status=dict(zip(['selected-items-compared-not-full-chapter','not-yet-compared','bounded-subsections-compared-rest-open','functions-compared-exact-graphics-pending'],t[18:22]))
 for m in d['manuals']:
  out+='<details><summary>'+esc(u['brands'][m['brand']]+' '+m['model']+' · '+m['edition'])+'</summary><div><p><a href="'+esc(m['source_url'])+'">'+esc(m.get('part_number')or m['edition'])+'</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in t[11:16])+'</tr></thead><tbody>'
  for row in m['areas']:
   loc=', '.join(map(str,row['reviewed_printed_pages']))or' / '.join(row['reviewed_html_sections']);vals=[row['title'][lang],status[row['status']],loc,', '.join(row['verified_catalogue_ids']),row['remaining'][lang]]
   out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+esc(value)+'</td>'for label,value in zip(t[11:16],vals))+'</tr>'
  out+='</tbody></table></div></details>'
 out+='</section><section id="grafiky-caddy"><h2>'+{'cs':'Caddy 11.2025 – kontrola přesných zdrojových grafik','en':'Caddy 11.2025 – exact source-graphic comparison','de':'Caddy 11.2025 – Vergleich genauer Quellgrafiken'}[lang]+'</h2><p>'+{'cs':'Pět přesných originálních SVG bylo porovnáno: OFF, nedostupnost s vykřičníkem a žlutý, zelený a šedý provozní stav. Obecné podmínky Volkswagen, Wolfsburg červen 2026, bod 2, uvádějí ochranu obrázků a neposkytují licenci samotným přístupem. Pro tato konkrétní SVG nebyla nalezena samostatná licence ani vyřešen jiný použitelný právní základ. Žádost o svolení nebyla odeslána; nejde tedy o čekání na odpověď ani o odmítnuté svolení. Toto zjištění samo nerozhoduje o autorskoprávní ochraně každého jednoduchého piktogramu. Originální soubory nejsou vložené do zákaznického přehledu a nejsou nahrazené podobnými pruhy jiného modelu. Dostupné texty Caddy jsou zpracovávány nezávisle na této otázce.',
'en':'Five exact original SVGs were compared: OFF, exclamation-mark unavailability and amber, green and grey operating states. Volkswagen general terms, Wolfsburg June 2026, clause 2, reserve image rights and grant no licence merely through access. No separate licence for these specific SVGs or other applicable legal basis has been established. No permission request was sent, so no reply is awaited and no permission was refused. This finding does not itself determine copyright eligibility of each simple pictogram. Original files are not inserted into the customer overview or replaced by similar lanes from another model. Available Caddy text is processed independently of this issue.',
'de':'Fünf genaue Original-SVGs wurden verglichen: OFF, Nichtverfügbarkeit mit Ausrufezeichen sowie gelber, grüner und grauer Betriebszustand. Die allgemeinen Volkswagen-Nutzungsbedingungen, Wolfsburg Juni 2026, Ziffer 2, behalten Bildrechte vor; bloßer Abruf gewährt keine Lizenz. Für diese konkreten SVGs wurde weder eine gesonderte Lizenz gefunden noch eine andere anwendbare Rechtsgrundlage geklärt. Keine Erlaubnisanfrage versandt, daher weder ausstehende Antwort noch verweigerte Erlaubnis. Dies entscheidet nicht über die Schutzfähigkeit jedes einfachen Piktogramms. Originaldateien sind nicht in die Kundenübersicht eingefügt und nicht durch ähnliche Spuren anderer Modelle ersetzt. Verfügbare Caddy-Texte werden unabhängig davon bearbeitet.'}[lang]+'</p><a href="'+rel('_warnings/caddy-source-graphic-review.json',page)+'">'+{'cs':'Zdrojové adresy, kontrolní otisky a výsledek porovnání','en':'Source URLs, checksums and comparison result','de':'Quelladressen, Prüfsummen und Vergleichsergebnis'}[lang]+'</a></section><section id="chybejici-podklady"><h2>'+t[16]+'</h2><ul>'
 for msg in CAT['review_gaps'][lang]:out+='<li>'+esc(msg)+'</li>'
 out+='</ul></section><p>'+t[17]+' <a href="'+rel('_warnings/verification.json',page)+'">JSON</a></p></body></html>';return out

def history_table(lang):
 u=UI[lang];h=next(x for x in CAT.get('change_history',[]) if x['id']=='73-to-86')
 labels={'cs':['Vysvětlení změny 73 → 86','Původních 73 významových záznamů zůstalo zachováno včetně textů a modelových přiřazení. Přibylo 13 nových záznamů: 7 pro Škodu a 6 pro užitkové vozy. Nic nebylo sloučeno, nahrazeno ani odstraněno.','Škoda: 43 položek = 36 nových přiřazení stávajících záznamů + 7 nových záznamů. Volkswagen Užitkové vozy: 24 položek = 18 přiřazení stávajících záznamů + 6 nových záznamů. Počet karet podle značek se změnil ze 107 na 174, nikoli počet unikátních významů o 67.','Nové významové záznamy','Přiřazené stávající záznamy','Zachované položky SEAT a CUPRA','Tento rozpis porovnává konkrétně verze db2c200 a 279c4c9. Další rozšíření se vykazují samostatně.'],
 'en':['Explaining the change from 73 to 86','All 73 original semantic records were retained, including their texts and model assignments. Thirteen new records were added: seven for Škoda and six for commercial vehicles. None were merged, replaced or removed.','Škoda: 43 brand entries = 36 assignments of existing records + 7 new records. Volkswagen Commercial Vehicles: 24 brand entries = 18 assignments of existing records + 6 new records. Brand-card count rose from 107 to 174; this does not mean 67 new unique meanings.','New semantic records','Assignments of existing records','Retained SEAT and CUPRA entries','This reconciliation specifically compares versions db2c200 and 279c4c9. Subsequent expansions are reported separately.'],
 'de':['Erklärung der Änderung von 73 auf 86','Alle 73 ursprünglichen Bedeutungseinträge einschließlich Texten und Modellzuordnungen blieben erhalten. Hinzu kamen 13 neue Einträge: sieben für Škoda und sechs für Nutzfahrzeuge. Nichts wurde zusammengeführt, ersetzt oder entfernt.','Škoda: 43 Markeneinträge = 36 Zuordnungen vorhandener Einträge + 7 neue Einträge. Volkswagen Nutzfahrzeuge: 24 Markeneinträge = 18 Zuordnungen vorhandener Einträge + 6 neue Einträge. Die Zahl der Markenkarten stieg von 107 auf 174; dies bedeutet nicht 67 neue einzigartige Bedeutungen.','Neue Bedeutungseinträge','Zuordnungen vorhandener Einträge','Erhaltene SEAT- und CUPRA-Einträge','Dieser Abgleich vergleicht ausdrücklich die Versionen db2c200 und 279c4c9. Weitere Ergänzungen werden gesondert ausgewiesen.']}[lang]
 out='<section id="zmeny-73-86"><h2>'+labels[0]+'</h2><p>'+labels[1]+'</p><p>'+labels[2]+'</p><p>'+labels[6]+'</p><h3>'+labels[3]+'</h3><ul>'
 for row in h['added']:out+='<li><code>'+esc(row['id'])+'</code> — '+esc(row['name'][lang])+'</li>'
 out+='</ul><h3>'+labels[4]+'</h3>'
 for brand,row in h['brand_additions'].items():
  ids=set(row['existing_records_assigned']);out+='<details><summary>'+esc(u['brands'][brand])+' · '+str(len(ids))+'</summary><ul>'
  for item in CAT['items']:
   if item['id'] in ids:out+='<li><code>'+esc(item['id'])+'</code> — '+esc(item['name'][lang])+'</li>'
  out+='</ul></details>'
 out+='<h3>'+labels[5]+'</h3><p>SEAT: 43 → 43. CUPRA: 49 → 49.</p></section>'
 return out

def latest_history(lang):
 u=UI[lang];event=next(x for x in CAT['change_history'] if x['id']=='86-to-88')
 t={'cs':['Nové ověření: 86 → 88 významových záznamů','Přibyly dva samostatné významy stejného nového tvaru: bílá výzva k převzetí řízení a červená naléhavá výzva. Celkem nyní 35 tvarů a 47 barevných variant. Přibylo 48 modelových přiřazení; 30 z nich nahrazuje obecné rozsahy (13 Volkswagen, 17 užitkové vozy). Původní obecné zdroje zůstávají uložené v evidenci. Žádný původní záznam ani modelové přiřazení SEAT/CUPRA/Škoda nebylo odstraněno.','Nahrazené obecné rozsahy','Nově doložená modelová přiřazení'],
 'en':['New verification: 86 → 88 semantic records','Two distinct meanings of one new pictogram shape were added: a white steering take-over request and a red urgent request. There are now 35 shapes and 47 colour variants. Forty-eight model assignments were added; 30 replace general scopes (13 Volkswagen, 17 commercial vehicles). Previous general sources remain in the evidence. No original SEAT/CUPRA/Škoda record or model assignment was removed.','Replaced general scopes','Newly supported model assignments'],
 'de':['Neue Prüfung: 86 → 88 Bedeutungseinträge','Zwei Bedeutungen einer neuen Piktogrammform kamen hinzu: weiße Aufforderung zur Lenkungsübernahme und rote dringende Aufforderung. Insgesamt jetzt 35 Formen und 47 Farbvarianten. 48 Modellzuordnungen kamen hinzu; 30 ersetzen allgemeine Geltungsbereiche (13 Volkswagen, 17 Nutzfahrzeuge). Bisherige allgemeine Quellen bleiben dokumentiert. Kein ursprünglicher SEAT/CUPRA/Škoda-Eintrag oder Modellnachweis wurde entfernt.','Ersetzte allgemeine Geltungsbereiche','Neu belegte Modellzuordnungen']}[lang]
 out='<section id="zmeny-86-88"><h2>'+t[0]+'</h2><p>'+t[1]+'</p>'
 for key,title in [('replaced_general_scopes',t[2]),('added_model_assignments',t[3])]:
  out+='<details><summary>'+title+'</summary><ul>'
  for row in event[key]:
   m=CAT['manuals'][row['manual']];out+='<li><code>'+esc(row['id'])+'</code> · '+esc(u['brands'][row['brand']])+' · '+esc(m['model'])+' · '+esc(m['edition'])+'</li>'
  out+='</ul></details>'
 return out+'</section>'

def coverage_table(lang):
 u=UI[lang]
 labels={'cs':['Rozsah po značkách','Značka','Tvary symbolů','Barevné varianty','Významové varianty','Modelová přiřazení','Obecné příklady','Přesné chybějící podklady a přístup','Zdroj'],
 'en':['Coverage by brand','Brand','Pictogram shapes','Colour variants','Semantic variants','Model assignments','General examples','Specific missing documents and access','Source'],
 'de':['Umfang nach Marke','Marke','Piktogrammformen','Farbvarianten','Bedeutungsvarianten','Modellzuordnungen','Allgemeine Beispiele','Konkret fehlende Unterlagen und Zugriff','Quelle']}[lang]
 text='<h2>'+labels[0]+'</h2><p>'+esc(CAT['counting_method'][lang])+'</p><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in labels[1:7])+'</tr></thead><tbody>'
 for brand,n in CAT['counts']['by_brand'].items():
  text+='<tr><td>'+esc(u['brands'][brand])+'</td>'+''.join('<td>'+str(n[k])+'</td>' for k in ['distinct_pictogram_shapes','graphic_colour_variants','semantic_variants','model_edition_assignments','generic_brand_assignments'])+'</tr>'
 text+='</tbody></table>'
 for brand,n in CAT['counts']['by_brand'].items():
  text+='<section id="rozsah-'+brand+'"><h3>'+esc(u['brands'][brand])+'</h3><ul>'
  keys=sorted({s['manual'] for i in CAT['items'] for s in i['scopes'] if s['brand']==brand and s.get('manual')})
  for key in keys:
   m=CAT['manuals'][key];text+='<li>'+esc(model_label(m['model'],m['year']))+' · '+esc(m['edition'])+' · '+esc(source_label(m,lang))+'</li>'
  text+='</ul>'
  for gap in CAT['gaps']:
   if gap['brand']==brand:text+='<p>'+esc(gap['description'][lang])+'</p>'
  generic=[i for i in CAT['items'] if any(s['brand']==brand and not s.get('manual') for s in i['scopes'])]
  if generic:text+='<p>'+esc(labels[6])+': '+', '.join('<code>'+esc(i['id'])+'</code>' for i in generic)+'.</p>'
  text+='</section>'
 text+='<h2>'+labels[7]+'</h2><ul>'
 for entry in CAT['source_access_log']:text+='<li><strong>'+esc(u['brands'][entry['brand']])+'</strong>: '+esc(entry['summary'][lang])+' <a href="'+esc(entry['url'])+'" target="_blank" rel="noopener">'+labels[8]+'</a></li>'
 return text+'</ul>'

def current_expansion(lang):
 labels={'cs':['Další rozšíření: 88 → 116 významových záznamů','Přibylo 28 nových významových záznamů a 57 modelových přiřazení. Audi Q3 11.2024 má 45 položek: 22 přiřazení dosavadních záznamů a 23 nových významů. Dalších pět nových významů rozlišuje elektrický pohon Born, Enyaq, Mii electric a ID.4. Žádný původní záznam ani modelové přiřazení Škoda, SEAT a CUPRA nebylo odstraněno.','Golf VII 11.2019 nově dokládá původní spirálu žhavení i blikající závadu řízení dieselu. Modelově doloženo je 14 z původních 15 položek Volkswagen; konkrétní modelový doklad pro vw-range nadále chybí.','Přidané významové záznamy'],
 'en':['Further expansion: 88 → 116 semantic records','Twenty-eight new semantic records and 57 model assignments were added. Audi Q3 11.2024 has 45 entries: 22 assignments of existing records and 23 new meanings. Five further new meanings distinguish the electric drive of Born, Enyaq, Mii electric and ID.4. No original Škoda, SEAT or CUPRA record or model assignment was removed.','Golf VII 11.2019 now documents the original preheating coil and flashing diesel engine-management fault. Fourteen of the original 15 Volkswagen entries have model evidence; specific model evidence for vw-range remains missing.','Added semantic records'],
 'de':['Weitere Ergänzung: 88 → 116 Bedeutungseinträge','28 neue Bedeutungseinträge und 57 Modellzuordnungen kamen hinzu. Audi Q3 11.2024 hat 45 Einträge: 22 Zuordnungen bestehender Einträge und 23 neue Bedeutungen. Fünf weitere neue Bedeutungen unterscheiden den Elektroantrieb von Born, Enyaq, Mii electric und ID.4. Kein ursprünglicher Škoda-, SEAT- oder CUPRA-Eintrag oder Modellnachweis wurde entfernt.','Golf VII 11.2019 belegt jetzt die ursprüngliche Vorglühspirale und die blinkende Diesel-Motorsteuerungsstörung. Für 14 der ursprünglichen 15 Volkswagen-Einträge liegt ein Modellnachweis vor; der konkrete Modellnachweis für vw-range fehlt weiterhin.','Hinzugefügte Bedeutungseinträge']}[lang]
 events=[e for e in CAT['change_history'] if e['id'] in ['88-to-audi-ev','113-to-115-model-evidence','115-to-116-traffic-sign']]
 ids={id for event in events for id in event['added_record_ids']}
 out='<section id="zmeny-audi-ev"><h2>'+labels[0]+'</h2><p>'+labels[1]+'</p><p>'+labels[2]+'</p><h3>'+labels[3]+'</h3><ul>'
 for item in CAT['items']:
  if item['id'] in ids:out+='<li><code>'+esc(item['id'])+'</code> — '+esc(item['name'][lang])+'</li>'
 return out+'</ul></section>'

def review_page(lang,page):
 u=UI[lang];r=json.loads((HERE/'review-register.json').read_text())
 t={'cs':['Položková revize návodů','Kompletně porovnané návody: žádné.','Tabulka rozlišuje ověření vybraných položek od dokončení celého návodu. Automatická inventura znaků textové vrstvy není vizuální kontrola ani důkaz úplnosti. Rastrové obrázky, kresby bez textového znaku a některé ovládací nápisy vyžadují další kontrolu.','Značka a model','Vydání','Přístrojový panel','Asistenti','Infotainment','Komfortní ovládání','Celý návod','Vybrané položky porovnané','Neporovnáno celé','Nedokončeno','Šest fotografií CUPRA Terramar','Nyní bylo dodáno a vizuálně zkontrolováno pět fotografií: čtyři obrazovky Control Centra a jeden přístrojový panel. Šestý snímek chybí. Kontrola všech šesti se nepotvrzuje. Rok a verze softwaru fotografovaného vozu nejsou doložené; neověřené významy a grafiky nejsou doplněné odhadem.','Ovládací ikony Terramar MAX a REAR jsou samostatně porovnané podle návodů 09.24, strana 146, a 11.25, strana 148. To nenahrazuje kontrolu fotografií ani všech ostatních ovládacích ikon.','Nově doplněné významy','Zbývající konkrétní mezery','Úplná evidence JSON','Tabulka návodů CSV','Pracovní index zdrojových znaků CSV','Zdrojové kódy znaků nejsou univerzální identifikátory symbolů a nezakládají ověřený výklad. Neověřené kandidáty nepřidáváme do zákaznického přehledu.'],
 'en':['Item-by-item manual review','Completely compared manuals: none.','The table separates review of selected entries from completion of an entire manual. Automated text-layer character indexing is not visual review or proof of completeness. Raster images, outline-only drawings and some functional inscriptions require further review.','Brand and model','Edition','Instrument panel','Assistants','Infotainment','Comfort controls','Whole manual','Selected entries compared','Not fully compared','Incomplete','Six CUPRA Terramar photographs','Five photographs have now been supplied and visually reviewed: four Control Centre screens and one instrument cluster. The sixth is missing. Review of all six is not confirmed. The photographed vehicle’s year and software version are not documented; unverified meanings and graphics are not guessed.','Terramar MAX and REAR controls are independently compared with manuals 09.24, page 146, and 11.25, page 148. This does not replace review of the photographs or all other control icons.','Newly added meanings','Specific remaining gaps','Full JSON register','Manual table CSV','Working source-character index CSV','Source character codes are not universal symbol identifiers and do not establish a verified interpretation. Unverified candidates are not added to the customer overview.'],
 'de':['Einzelprüfung der Anleitungen','Vollständig verglichene Anleitungen: keine.','Die Tabelle trennt ausgewählte geprüfte Einträge vom Abschluss einer ganzen Anleitung. Automatische Textzeichen-Inventur ist keine Sichtprüfung und kein Vollständigkeitsnachweis. Rasterbilder, reine Umrisszeichnungen und manche Bedienaufschriften benötigen weitere Prüfung.','Marke und Modell','Ausgabe','Kombiinstrument','Assistenten','Infotainment','Komfortbedienung','Ganze Anleitung','Ausgewählte Einträge verglichen','Nicht vollständig verglichen','Unvollständig','Sechs CUPRA-Terramar-Fotografien','Fünf Fotos wurden jetzt bereitgestellt und visuell geprüft: vier Control-Centre-Ansichten und ein Kombiinstrument. Das sechste fehlt. Die Prüfung aller sechs wird nicht bestätigt. Baujahr und Softwarestand sind nicht belegt; ungeprüfte Bedeutungen und Grafiken werden nicht geraten.','Die Terramar-Bedienzeichen MAX und REAR sind unabhängig anhand der Anleitungen 09.24, Seite 146, und 11.25, Seite 148, verglichen. Das ersetzt weder die Fotoprüfung noch die Prüfung aller weiteren Bedienzeichen.','Neu ergänzte Bedeutungen','Konkrete verbleibende Lücken','Vollständige JSON-Dokumentation','Anleitungstabelle CSV','Arbeitsindex der Quellzeichen CSV','Quellzeichencodes sind keine universellen Symbolkennungen und belegen keine geprüfte Bedeutung. Ungeprüfte Kandidaten werden nicht in die Kundenübersicht übernommen.']}[lang]
 out='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+t[0]+' | J&amp;S SERVIS</title><style>body{font:18px/1.6 system-ui,sans-serif;color:#222;max-width:1440px;padding:20px;margin:auto;overflow-wrap:anywhere}h1,h2{line-height:1.3}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #999;padding:9px;text-align:left;vertical-align:top}a{color:#111}section{margin-block:24px}@media(max-width:900px){table,tbody,tr,td{display:block}thead{display:none}td:before{content:attr(data-label)": ";font-weight:600}tr{margin-bottom:16px}}</style></head><body><a href="./#prehled-kontrolek">'+esc(u['overview'])+'</a> · <a href="zdroje.html">'+esc(u['auditLink'])+'</a><h1>'+t[0]+'</h1><p><strong>'+t[1]+'</strong></p><p>'+t[2]+'</p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in t[3:10])+'</tr></thead><tbody>'
 for m in r['manuals']:
  vals=[u['brands'][m['brand']]+' '+str(m['model']),m['edition']]+[t[10]if m['sections'][k]=='selected-entries-reviewed'else t[11]for k in ['instrument-panel','driver-assistance','infotainment-and-control-icons','comfort-controls']]+[t[12]]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+esc(value)+'</td>'for label,value in zip(t[3:10],vals))+'</tr>'
 out+='</tbody></table><p><a href="revize-kapitol.html">'+{'cs':'Revize po modelech, vydáních a kapitolách; identifikace fotografií','en':'Review by model, edition and chapter; photo identification','de':'Prüfung nach Modell, Ausgabe und Kapitel; Fotoidentifikation'}[lang]+'</a></p><h2>'+t[13]+'</h2><p>'+t[14]+'</p><p>'+t[15]+'</p><h2>'+t[16]+'</h2><ul>'
 events=[e for e in CAT['change_history']if e['id']in ['116-q4-and-control-icons','129-to-131-terramar-user-photos','terramar-functional-photo-comparison','independent-seat-vw-lane-review','audi-editions-and-chapter-states','q4-2023-cup-edition','audi-start-stop-and-direct-tyres','a8-documented-climate-text-controls','a4-a8-climate-context-variants','a4-residual-heat-context','enyaq-tarraco-independent-function-review','golf-white-assistant-independent-review','caddy-braking-support-independent-review','terramar-own-overview-and-driver-sections','q4-own-climate-auto-assignment','enyaq-independent-2020-electric-review']];event={'added_record_ids':[id for e in events for id in e['added_record_ids']]}
 for i in CAT['items']:
  if i['id']in event['added_record_ids']:out+='<li><code>'+esc(i['id'])+'</code> — '+esc(i['name'][lang])+'</li>'
 out+='</ul><h2>'+t[17]+'</h2><ul>'+''.join('<li>'+esc(x)+'</li>'for x in CAT['review_gaps'][lang])+'</ul><p>'+t[21]+'</p><ul>'
 for file,label in [('review-register.json',t[18]),('manual-review.csv',t[19]),('source-character-review.csv',t[20])]:out+='<li><a href="'+rel('_warnings/'+file,page)+'">'+label+'</a></li>'
 out+='</ul><h2>'+{'cs':'Q4 e-tron 07/2024: řádkové porovnání obrazového přehledu','en':'Q4 e-tron 07/2024: row-by-row overview comparison','de':'Q4 e-tron 07/2024: zeilenweiser Vergleich der Symbolübersicht'}[lang]+'</h2><p>'+{'cs':'Zdrojové názvy v následující tabulce jsou německy tak, aby šly dohledat v originálu. Uvedené záznamy pokrývají jen jednotlivě ověřené stavy; ani přiřazený řádek neznamená úplné zpracování všech významů a souvisejících kapitol. Nezařazené obrázky se v zákaznickém přehledu nenahrazují.','en':'The following source labels remain in German to make them traceable in the original. Listed entries cover only individually reviewed states; a mapped row does not mean every meaning or related chapter is complete. Unmatched graphics are not replaced in the customer overview.','de':'Die Quellbezeichnungen bleiben zur Nachvollziehbarkeit im Original deutsch. Zugeordnete Einträge erfassen nur einzeln geprüfte Zustände; auch eine zugeordnete Zeile bedeutet keinen vollständigen Abschluss aller Bedeutungen oder Kapitel. Nicht zugeordnete Grafiken werden in der Kundenübersicht nicht ersetzt.'}[lang]+'</p><table><thead><tr><th>ID</th><th>'+u['pages']+'</th><th>Original DE</th><th>'+{'cs':'Jednotlivě doložené záznamy','en':'Individually documented records','de':'Einzeln belegte Einträge'}[lang]+'</th></tr></thead><tbody>'
 q=json.loads((HERE/'q4-overview-review.json').read_text())
 for row in q['rows']:
  matched=', '.join(row['catalogue_entries']) or {'cs':'Nezařazeno / další ověření a přesná grafika chybí','en':'Unmatched / further review and exact graphic outstanding','de':'Nicht zugeordnet / weitere Prüfung und genaue Grafik fehlen'}[lang]
  out+='<tr><td data-label="ID">'+esc(row['row_id'])+'</td><td data-label="'+esc(u['pages'])+'">'+str(row['printed_page'])+'</td><td data-label="Original DE">'+esc(row['source_label_de'])+'</td><td data-label="Status">'+esc(matched)+'</td></tr>'
 out+='</tbody></table><p><a href="'+rel('_warnings/q4-overview-review.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/q4-overview-review.json',page)+'">JSON</a></p>'
 photos=json.loads((HERE/'terramar-photo-review.json').read_text())
 labels={'cs':['Porovnání šesti fotografií Terramar se skutečným přehledem','Fotografie a poloha','Symbol / název','Typ','Význam a postup','Stav na webu / potřebná změna','Zdroj a rozsah','Výstraha nebo stav – rozhoduje hlášení','Provozní stav','Ovládací ikona','Nejasný symbol','V přehledu s modelovým doložením','Přesná obrazová položka chybí','Přesná varianta fotografie nevyřešena','Význam této zkratky neověřen'],
 'en':['Comparison of six Terramar photographs with the actual overview','Photo and position','Symbol / name','Type','Meaning and action','Website status / required change','Source and applicability','Warning or state – message decisive','Operating state','Control icon','Unresolved symbol','In the overview with model evidence','Exact pictorial entry missing','Exact photo variant unresolved','Meaning of this shortcut unverified'],
 'de':['Vergleich der sechs Terramar-Fotos mit der tatsächlichen Übersicht','Foto und Position','Symbol / Name','Typ','Bedeutung und Vorgehen','Webstatus / erforderliche Änderung','Quelle und Geltungsbereich','Warnung oder Zustand – Meldung maßgeblich','Betriebszustand','Bedienzeichen','Ungeklärtes Symbol','Mit Modellnachweis in der Übersicht','Genauer Bildeintrag fehlt','Genaue Fotovariante ungeklärt','Bedeutung dieser Verknüpfung ungeprüft']}[lang]
 cats=dict(zip(['warning-or-operating-state-needs-message','operating-state','control-icon','unresolved'],labels[7:11]));statuses=dict(zip(['model-scoped-entry-present','missing-exact-model-scoped-graphic-entry','exact-photo-variant-unresolved','meaning-not-established-for-this-shortcut'],labels[11:15]))
 out+='<section id="fotografie-terramar"><h2>'+labels[0]+'</h2><p>'+esc(photos['important_limitations'][lang])+'</p><p>'+{'cs':'Ovládací zkratka, její funkce, přesná grafika a signalizační stav jsou kontrolovány odděleně. Chybějící grafika není nahrazena podobnou ikonou. Rozsah návodu není automaticky přenesen na neznámý rok fotografovaného vozu.','en':'A control shortcut, its function, exact artwork and signalling state are checked separately. Missing artwork is not replaced with a similar icon. Manual applicability is not automatically transferred to the photographed vehicle’s unknown year.','de':'Bedienverknüpfung, Funktion, genaue Grafik und Signalzustand werden getrennt geprüft. Fehlende Grafiken werden nicht durch ähnliche Symbole ersetzt. Die Anleitungsgültigkeit wird nicht automatisch auf das unbekannte Baujahr des fotografierten Fahrzeugs übertragen.'}[lang]+'</p><p><a href="'+rel('_warnings/terramar-photo-comparison.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/terramar-photo-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in labels[1:7])+'</tr></thead><tbody>'
 for row in photos['observations']:
  if row.get('aggregate_only'):continue
  locations='<br>'.join(esc(x['photo'].rsplit('-',1)[1])+': '+esc(x['position'][lang])for x in row['occurrences'])
  links=[]
  for id in row['catalogue_entries']:
   it=next((i for i in CAT['items']if i['id']==id),None)
   if it and any(sc.get('manual')=='cupra-terramar-2026-11-25'for sc in it['scopes']):links.append('<a href="./?znacka=cupra#kontrolka-'+esc(id)+'-cupra">'+esc(it['name'][lang])+'</a>')
  before=row.get('website_comparison',{});before_text={'cs':'Před touto revizí: ','en':'Before this revision: ','de':'Vor dieser Revision: '}[lang]+({'cs':'modelově doložená položka již existovala','en':'model-scoped entry already existed','de':'modellbelegter Eintrag bereits vorhanden'}[lang]if before.get('before_record_ids')else{'cs':'odpovídající modelová položka chyběla','en':'corresponding model-scoped entry was missing','de':'entsprechender modellbelegter Eintrag fehlte'}[lang]);web=esc(before_text)+'<br>'+esc(statuses.get(row['web_result'],row['web_result']))+'<br>'+('<br>'.join(links))+'<p>'+esc(row['required_change'][lang])+'</p>'
  source=row['source_review'];m=CAT['manuals'][source['manual']];pages=', '.join(map(str,source['printed_pages']));ref='<a href="'+esc(source['url']+'#page='+str(source['pdf_pages'][0]))+'">Terramar '+esc(source['edition'])+' · '+esc(u['pages'])+' '+pages+'</a><p>'+esc(source['scope_note'][lang])+'</p>'
  values=[locations,'<code>'+esc(row['id'])+'</code><br>'+esc(row['name'][lang]),esc(cats.get(row['category'],row['category'])),esc(row['meaning'][lang])+'<p><strong>'+esc(u['action'])+'</strong>: '+esc(row['driver_action'][lang])+'</p><p>'+esc(row['note'][lang])+'</p>',web,ref]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(labels[1:7],values))+'</tr>'
 out+='</tbody></table></section>'
 b=json.loads((HERE/'brand-functional-review.json').read_text());bl={'cs':['Samostatná kontrola podle značek v této revizi','Model a vydání','Kontrolované kapitoly / stránky','Skutečně porovnáno','Konkrétní zbývající mezery'],'en':['Independent own-brand checks in this revision','Model and edition','Checked chapters / pages','Actually compared','Specific remaining gaps'],'de':['Unabhängige markeneigene Prüfung dieser Revision','Modell und Ausgabe','Geprüfte Kapitel / Seiten','Tatsächlich verglichen','Konkrete verbleibende Lücken']}[lang]
 out+='<section id="revize-znacek"><h2>'+bl[0]+'</h2><p>'+{'cs':'Následující řádky vymezují vybrané kontroly konkrétních zdrojů. Nejde o úplnou revizi všech modelů, vydání ani všech kapitol. Počet položek není důkazem úplnosti.','en':'The following rows define selected checks of specific sources. They are not a complete review of all models, editions or chapters. Entry counts do not prove completeness.','de':'Die folgenden Zeilen begrenzen ausgewählte Prüfungen konkreter Quellen. Keine vollständige Revision aller Modelle, Ausgaben oder Kapitel. Eintragszahlen belegen keine Vollständigkeit.'}[lang]+'</p><p><a href="'+rel('_warnings/brand-functional-review.'+lang+'.csv',page)+'">CSV</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in bl[1:])+'</tr></thead><tbody>'
 for row in b['rows']:
  ref='<a href="'+esc(row['source_url'])+'">'+esc(u['brands'][row['brand']]+' '+row['model']+' · '+row['edition'])+'</a>'
  location=', '.join(map(str,row['printed_pages']))if row['printed_pages']else' / '.join(row['source_sections'])
  vals=[ref,esc(location),esc(row['reviewed'][lang]),esc(row['remaining'][lang])]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(bl[1:],vals))+'</tr>'
 out+='</tbody></table></section>'
 return out+'</body></html>'


def audit(lang,page):
 u=UI[lang];heading={'cs':'Stav systematické kontroly','en':'Systematic review status','de':'Stand der systematischen Prüfung'}[lang]
 text=f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(u["audit"])}</title><style>body{{font:18px/1.6 system-ui,sans-serif;max-width:1100px;padding:20px;margin:auto;color:#222;overflow-wrap:anywhere}}h1,h2{{line-height:1.3}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #777;padding:10px;text-align:left;vertical-align:top}}a{{color:#111}}section{{margin-block:28px}}@media(max-width:650px){{table,tbody,tr,td{{display:block}}thead{{display:none}}td{{border-bottom:0}}tr{{margin-bottom:16px;border-bottom:1px solid #777}}}}</style></head><body><a href="./#prehled-kontrolek">{esc(u["overview"])}</a><h1>{esc(u["audit"])}</h1><p><strong>{esc(u["scopeTitle"])}</strong></p><p>{esc(u["scope"])}</p><p>{esc(u["counts"].format(items=len(CAT["items"]),graphics=CAT["counts"]["shared_graphic_colour_variants"],shapes=CAT["counts"]["distinct_pictogram_shapes"]))}</p><p>{esc(u["yearNote"])}</p><p>{esc(u["auditNote"])}</p><h2>{heading}</h2>'
 statuses={'cs':{'selected-symbols-and-instructions-reviewed-not-complete':'Vybrané položky zkontrolované; celé vydání není hotové.','downloaded-not-yet-item-reviewed':'Staženo; kontrola všech symbolů nedokončená.'},'en':{'selected-symbols-and-instructions-reviewed-not-complete':'Selected entries checked; full edition not complete.','downloaded-not-yet-item-reviewed':'Downloaded; symbol-by-symbol review incomplete.'},'de':{'selected-symbols-and-instructions-reviewed-not-complete':'Ausgewählte Einträge geprüft; vollständige Ausgabe nicht abgeschlossen.','downloaded-not-yet-item-reviewed':'Heruntergeladen; symbolweise Prüfung nicht abgeschlossen.'}}[lang]
 text+='<table><thead><tr><th>Model · MY</th><th>'+esc(u['edition'])+'</th><th>'+{'cs':'Počet doložených záznamů','en':'Documented records','de':'Belegte Einträge'}[lang]+'</th><th>Status</th></tr></thead><tbody>'
 for k,m in sorted(CAT['manuals'].items()):text+=f'<tr><td>{esc(u["brands"][m["brand"]])} {esc(model_label(m["model"],m["year"]))}</td><td><a href="{esc(m["url"])}">{esc(m["edition"])} · {esc(source_label(m,lang))}</a></td><td>{sum(any(sc.get("manual")==k for sc in it["scopes"]) for it in CAT["items"])}</td><td>{esc(statuses[m["status"]])}</td></tr>'
 text+='</tbody></table>'
 # Localised, explicit brand access gaps. No private Drive URLs or documents are published.
 gap=CAT['review_gaps'][lang]
 text+='<ul>'+''.join('<li>'+esc(x)+'</li>' for x in gap)+'</ul>'
 text+=history_table(lang)+latest_history(lang)+current_expansion(lang)+coverage_table(lang)
 text+='<h2>'+{'cs':'Položková kontrola celých návodů','en':'Item-by-item review of whole manuals','de':'Einzelprüfung ganzer Anleitungen'}[lang]+'</h2><p><a href="revize.html">'+{'cs':'Otevřít kontrolní tabulky a stav šesti fotografií Terramar','en':'Open review tables and the status of six Terramar photographs','de':'Prüftabellen und Stand der sechs Terramar-Fotos öffnen'}[lang]+'</a></p>'
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
 page,body=create_page(lang);outputs.append((page,body));outputs.append((page.parent/'zdroje.html',audit(lang,page)));outputs.append((page.parent/'revize.html',review_page(lang,page)));outputs.append((page.parent/'revize-kapitol.html',chapter_page(lang,page)));outputs.append((page.parent/'druha-kontrola.html',second_review_page(lang,page)));outputs.append((page.parent/'evidence.json',json.dumps({'canonical_catalog':rel('_warnings/catalog.json',page),'review_status':'incomplete-preview','checked':CAT['checked'],**CAT['counts']},indent=2)+'\n'))
from export_review import review_export_outputs
outputs+=review_export_outputs(ROOT,HERE,CAT)
# Validate all translations and assets before touching output files.
assert len({x['id'] for x in CAT['items']})==len(CAT['items'])
for item in CAT['items']:
 for field in ['name','meaning','action','note','alt']:
  assert all(item[field].get(l) for l in LANGS),(item['id'],field)
 assert (ROOT/item['graphic_path']).is_file(),item['graphic_path']
for p,s in outputs:
 if '--check' in sys.argv:
  assert p.exists() and (p.read_bytes()if isinstance(s,bytes)else p.read_text())==s, 'Out of sync: '+str(p)
 else:
  if isinstance(s,bytes):p.write_bytes(s)
  else:p.write_text(s)
print(('Checked' if '--check' in sys.argv else 'Generated')+': 3 static locales, '+str(len(CAT['items']))+' semantic entries; shared images only.')
