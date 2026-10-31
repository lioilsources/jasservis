#!/usr/bin/env python3
"""Generate only the warning catalogue's three static page bodies from shared evidence.
No runtime translation; no remote requests; no changes to shared header styling.
"""
from pathlib import Path
import json,re,html,os,sys,csv,io
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parent
CAT=json.loads((HERE/'catalog.json').read_text());UI=json.loads((HERE/'locales.json').read_text())
INFO_ROOT=REPO/'source-materials/infotainment-2026-10-31-rev2'
INFO=json.loads((INFO_ROOT/'internal/manifest.json').read_text());INFO_TEXT=json.loads((INFO_ROOT/'translations.json').read_text())
ROUTE='kontrolky-a-vystrazna-hlaseni';LANGS=['cs','en','de'];VERSION='20261031-brand-tiles-v1'
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
def item_anchor(item,brand):
 return 'kontrolka-'+(item['legacy_id'].lower() if item.get('legacy_id') and brand=='volkswagen' else item.get('anchor_id', item['id'])+'-'+brand)
def candidate_link(item,brand,lang):
 # A semantic candidate without this brand's scope has no corresponding card.
 label=esc(item['name'][lang])
 if not any(s['brand']==brand for s in item['scopes']):return label+' <code>'+esc(item['id'])+'</code>'
 return '<a href="./?znacka='+esc(brand)+'#'+esc(item_anchor(item,brand))+'">'+label+'</a>'
def model_label(model,year):return str(model)+(f' · MY {year}' if year else '')
def localized(value,lang,default=''):
 if isinstance(value,dict):return value.get(lang)or value.get('cs')or next((x for x in value.values()if x),default)
 if isinstance(value,list):return ', '.join(str(x)for x in value)
 return default if value is None else str(value)
def audi_photo_occurrences(row):
 occurrences=row.get('occurrences')or[]
 if occurrences:return occurrences
 if row.get('photos'):return [{'photo':x,'position':''}for x in row['photos']]
 if row.get('photo'):return [{'photo':row['photo'],'position':row.get('position')or row.get('position_cs')or''}]
 return []
def audi_photo_title(row,lang):
 return localized(row.get('name'),lang)or localized(row.get('literal_text'),lang)or str(row.get('literal_text_cs')or row.get('observed_text')or row.get('source_caption_cs')or row.get('id')or'')
def audi_photo_candidates(row):return row.get('candidate_catalogue_ids_not_model_verified',row.get('candidate_catalogue_ids',row.get('catalogue_entries',[])))or[]
AUDI_PHOTO_CLASSIFICATIONS={
 'warning-indicator':{'cs':'výstražná kontrolka','en':'warning indicator','de':'Warnleuchte'},'operating-status':{'cs':'provozní stav','en':'operating status','de':'Betriebsstatus'},
 'physical-control':{'cs':'fyzický ovladač','en':'physical control','de':'physisches Bedienelement'},'mmi-control':{'cs':'ovládací prvek MMI','en':'MMI control','de':'MMI-Bedienelement'},
 'control':{'cs':'ovládací prvek','en':'vehicle control','de':'Bedienelement'},'unresolved':{'cs':'neověřený prvek','en':'unresolved element','de':'ungeklärtes Element'},
 'mmi-status':{'cs':'stav MMI','en':'MMI status','de':'MMI-Status'},'driver-message':{'cs':'hlášení pro řidiče','en':'driver message','de':'Fahrermeldung'},
 'vehicle-data':{'cs':'údaje vozidla','en':'vehicle data','de':'Fahrzeugdaten'},'service-reminder':{'cs':'servisní připomínka','en':'service reminder','de':'Servicehinweis'},
 'control-state':{'cs':'stav ovládacího prvku','en':'control state','de':'Bedienstatus'}}
AUDI_PHOTO_STATES={
 'displayed':{'cs':'zobrazeno','en':'displayed in photo','de':'angezeigt'},'control-visible-not-activation-proof':{'cs':'ovladač je viditelný; aktivace není prokázána','en':'control visible; activation not established','de':'Bedienelement sichtbar; Aktivierung nicht belegt'},
 'menu-tile':{'cs':'dlaždice nabídky','en':'menu tile','de':'Menükachel'},'message-displayed':{'cs':'hlášení je zobrazeno','en':'message displayed','de':'Meldung angezeigt'},
 'control-visible':{'cs':'ovladač je viditelný','en':'control visible','de':'Bedienelement sichtbar'},'visible':{'cs':'viditelné','en':'visible in photo','de':'sichtbar'},
 'steady-visible':{'cs':'na snímku trvale viditelné; časový průběh není doložen','en':'steadily visible in the still; timing is not established','de':'im Standbild dauerhaft sichtbar; Zeitverlauf nicht belegt'},
 'visible-state-duration-unknown':{'cs':'stav je viditelný; doba trvání není známá','en':'state visible; duration unknown','de':'Zustand sichtbar; Dauer unbekannt'},
 'visible-state-unknown':{'cs':'prvek je viditelný; přesný stav není ověřen','en':'element visible; exact state unverified','de':'Element sichtbar; genauer Zustand ungeprüft'},
 'control-visible-system-unknown':{'cs':'ovladač je viditelný; systém není určen','en':'control visible; system unknown','de':'Bedienelement sichtbar; System unbekannt'},
 'control-visible-function-unconfirmed':{'cs':'ovladač je viditelný; funkce není potvrzena','en':'control visible; function unconfirmed','de':'Bedienelement sichtbar; Funktion unbestätigt'}}
AUDI_PHOTO_COLOURS={code:{lang:UI[lang]['colors'][code] for lang in LANGS} for code in ['cervena','zluta','zelena','modra','bila','seda']}
AUDI_PHOTO_COLOURS['cervena-bila']={'cs':'Červená a bílá','en':'Red and white','de':'Rot und Weiß'}
AUDI_MEANING_BASES={
 'photo-visible-text-or-graphic':{'cs':'ověřeno z čitelného textu nebo grafiky fotografie; bez modelově přiřazeného návodu','en':'verified from photo-visible text or graphic; no model-assigned manual','de':'anhand lesbaren Textes oder Grafik des Fotos geprüft; keine modellzugeordnete Anleitung'},
 'photo-plus-candidate-manual':{'cs':'fotografie a kandidátní manuálová reference; neurčuje model vozu','en':'photo plus candidate manual reference; does not identify the vehicle model','de':'Foto plus Kandidaten-Anleitungsreferenz; identifiziert nicht das Fahrzeugmodell'},
 'unresolved':{'cs':'význam není uzavřen','en':'meaning unresolved','de':'Bedeutung ungeklärt'}}
AUDI_SOURCE_PAGE_STATUS={'cs':'stránka se nepoužije – zdrojem je fotografie displeje vozidla','en':'page not applicable – source is a vehicle-display photograph','de':'Seite nicht anwendbar – Quelle ist ein Foto der Fahrzeuganzeige'}
AUDI_INVENTORY_STATUS={
 'model':{'cs':'model nedoložen','en':'model not established','de':'Modell unbelegt'},
 'edition':{'cs':'vydání nedoloženo; zdrojem je fotografie vozidla','en':'edition not established; source is a vehicle photograph','de':'Ausgabe unbelegt; Quelle ist ein Fahrzeugfoto'},
 'model_year':{'cs':'modelový rok nedoložen','en':'model year not established','de':'Modelljahr unbelegt'},
 'reviewed':{'cs':'obrazově porovnáno','en':'visually reviewed','de':'visuell verglichen'},
 'pending':{'cs':'přijato; porovnání čeká','en':'received; comparison pending','de':'empfangen; Vergleich ausstehend'}}
AUDI_PHOTO_VIEWS={
 'instrument-cluster':{'cs':'přístrojový štít','en':'instrument cluster','de':'Kombiinstrument'},
 'mmi-dual-display':{'cs':'dvojice displejů MMI','en':'dual MMI display','de':'MMI-Doppeldisplay'},
 'mmi-and-centre-console':{'cs':'MMI a středová konzola','en':'MMI and centre console','de':'MMI und Mittelkonsole'}}
AUDI_PHOTO_ROLES={
 'primary evidence':{'cs':'hlavní obrazový podklad','en':'primary visual evidence','de':'primärer Bildbeleg'},
 'additional supplied view':{'cs':'doplňkový dodaný pohled','en':'additional visual evidence','de':'zusätzlich bereitgestellte Ansicht'}}
AUDI_MANUAL_INVENTORY_STATUS={
 'model':{'cs':'model nedoložen','en':'model not established','de':'Modell unbelegt'},
 'edition':{'cs':'vydání návodu nedoloženo','en':'manual edition not established','de':'Anleitungsausgabe unbelegt'},
 'model_year':{'cs':'modelový rok nedoložen','en':'model year not established','de':'Modelljahr unbelegt'},
 'reviewed':{'cs':'obrazově porovnáno a řádkově přepsáno','en':'visually reviewed and transcribed row by row','de':'visuell geprüft und zeilenweise transkribiert'},
 'page':{'cs':'tištěná strana fotografovaného návodu','en':'printed page of the photographed manual','de':'gedruckte Seite der fotografierten Anleitung'}}
AUDI_MANUAL_PHOTO_ROLES={
 'primary transcription':{'cs':'hlavní podklad přepisu','en':'primary transcription source','de':'primäre Transkriptionsquelle'},
 'primary evidence':{'cs':'hlavní obrazový podklad','en':'primary visual evidence','de':'primärer Bildbeleg'}}
AUDI_MANUAL_SEMANTIC_RESULTS={
 'compatible_candidate':{'cs':'slučitelný významový kandidát','en':'compatible semantic candidate','de':'passender Bedeutungskandidat'},
 'partial_candidate':{'cs':'částečný významový kandidát','en':'partial semantic candidate','de':'teilweiser Bedeutungskandidat'},
 'missing':{'cs':'použitelný kandidát chybí','en':'no usable candidate','de':'kein nutzbarer Kandidat'},
 'rejected_mismatch':{'cs':'kandidát odmítnut pro odlišný význam','en':'candidate rejected as a semantic mismatch','de':'Kandidat wegen abweichender Bedeutung verworfen'},
 'pending_only':{'cs':'pouze čekající kandidát','en':'pending candidate only','de':'nur ausstehender Kandidat'}}
AUDI_MANUAL_GRAPHIC_RESULTS={
 'compatible_unverified':{'cs':'podoba slučitelná, přesná grafika neověřena','en':'appearance compatible; exact graphic unverified','de':'Darstellung passend; genaue Grafik ungeprüft'},
 'mismatch':{'cs':'grafická varianta se neshoduje','en':'graphic variant differs','de':'Grafikvariante weicht ab'},
 'missing':{'cs':'přesná grafická varianta chybí','en':'exact graphic variant missing','de':'genaue Grafikvariante fehlt'},
 'state_unresolved':{'cs':'grafický stav nelze uzavřít z přehledu','en':'graphic state unresolved from the overview','de':'Grafikzustand aus der Übersicht nicht geklärt'},
 'pending':{'cs':'grafika zůstává čekající','en':'graphic remains pending','de':'Grafik bleibt ausstehend'},
 'multiple_distinct':{'cs':'řádek obsahuje více odlišných grafik','en':'row contains multiple distinct graphics','de':'Zeile enthält mehrere unterschiedliche Grafiken'}}
AUDI_MANUAL_MODEL_SCOPE_RESULTS={
 'unknown_source_model_no_exact_scope':{'cs':'model zdroje není znám; přesný modelový rozsah nedoložen','en':'source model unknown; no exact model scope established','de':'Quellmodell unbekannt; kein genauer Modellumfang belegt'}}
AUDI_MANUAL_COLUMNS={
 'main':{'cs':'hlavní sloupec','en':'main column','de':'Hauptspalte'},
 'left':{'cs':'levý sloupec','en':'left column','de':'linke Spalte'},
 'right':{'cs':'pravý sloupec','en':'right column','de':'rechte Spalte'}}
AUDI_MANUAL_SPECIAL_COLOURS={
 'smisena_neurcena':{'cs':'Smíšená / odstín nejistý','en':'Mixed / hue unresolved','de':'Gemischt / Farbton ungeklärt'}}
def audi_photo_classification(row,lang):return AUDI_PHOTO_CLASSIFICATIONS.get(row.get('classification')or row.get('category'),{}).get(lang,{'cs':'neznámý typ','en':'unknown type','de':'unbekannter Typ'}[lang])
def audi_photo_state(row,lang):return AUDI_PHOTO_STATES.get(row.get('signal_state_from_photo'),{}).get(lang,{'cs':'stav není lokalizován','en':'state not localised','de':'Zustand nicht lokalisiert'}[lang])
def audi_photo_colour(row,lang):return AUDI_PHOTO_COLOURS.get(row.get('photo_colour'),{}).get(lang,{'cs':'barva nedoložena','en':'colour not established','de':'Farbe unbelegt'}[lang])
def audi_meaning_basis(row,lang):return AUDI_MEANING_BASES.get(row.get('meaning_verification_basis'),{}).get(lang,AUDI_MEANING_BASES['unresolved'][lang])
def audi_photo_view(photo,lang):return AUDI_PHOTO_VIEWS.get(photo.get('view'),{}).get(lang,{'cs':'nepopsaný pohled','en':'unlabelled view','de':'unbeschriebene Ansicht'}[lang])
def audi_photo_role(photo,lang):return AUDI_PHOTO_ROLES.get(photo.get('role'),{}).get(lang,{'cs':'obrazový podklad','en':'visual evidence','de':'Bildbeleg'}[lang])
def audi_manual_photo_role(photo,lang):return localized(photo.get('role'),lang)if isinstance(photo.get('role'),dict)else AUDI_MANUAL_PHOTO_ROLES.get(photo.get('role'),{}).get(lang,{'cs':'fotografie tištěné strany','en':'printed-page photograph','de':'Foto der gedruckten Seite'}[lang])
def audi_manual_source(evidence):return evidence.get('source',{})
def audi_manual_brand(evidence):return 'Audi'if audi_manual_source(evidence).get('brand')=='audi'else audi_manual_source(evidence).get('brand','')
def audi_manual_photo_id(printed_page):return 'audi-manual-photo-p'+str(printed_page).zfill(2)
def audi_manual_graphic_occurrences(row):
 value=row.get('graphic_occurrence_count')
 return value if isinstance(value,int)and not isinstance(value,bool)else len(row.get('graphic_occurrences')or[])
def audi_manual_result(row,lang):return localized((row.get('text')or{}).get(lang,{}).get('assessment'),lang)
def audi_manual_column(row,lang):return AUDI_MANUAL_COLUMNS.get(row.get('column'),{}).get(lang,row.get('column',''))
def audi_manual_colour(row,lang):
 code=row.get('color','')
 return AUDI_MANUAL_SPECIAL_COLOURS.get(code,{}).get(lang,UI[lang]['colors'].get(code,code))
def audi_manual_references(row,lang):
 result=[]
 for reference in row.get('candidate_manual_references',[]):
  manual_id=reference.get('manual','');manual=CAT.get('manuals',{}).get(manual_id,{})
  result.append({'manual_id':manual_id,'model':manual.get('model',''),'edition':manual.get('edition',''),'part_number':manual.get('part_number',''),'printed_pages':reference.get('printed_pages',[]),'relationship':localized(reference.get('relationship'),lang),'candidate_only':True,'identifies_photographed_vehicle':False,'url':manual.get('url','')})
 return result
def source_label(m,lang):
 names={'cs':{'CS':'čeština','DE':'němčina','EN':'angličtina'},'en':{'CS':'Czech','DE':'German','EN':'English'},'de':{'CS':'Tschechisch','DE':'Deutsch','EN':'Englisch'}}
 label={'cs':'Návod','en':'Manual','de':'Anleitung'}[lang]+' · '+names[lang].get(m['lang'],m['lang'])
 if m.get('host_kind')=='third-party-copy':label+=' · '+{'cs':'kopie vydání výrobce na jiném serveru','en':'manufacturer edition hosted by a third party','de':'von Dritten gehostete Herstellerausgabe'}[lang]
 return label
def options(vals,allText):return '<option value="">'+esc(allText)+'</option>'+''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k,v in vals.items())
DISPLAY_GROUP_BY_GRAPHIC={
 'dpf':'motor',
 'epc':'motor',
 'coolant':'motor',
 'lane-assist':'asistenty',
}
def display_group(item,brand):
 # Identical pictograms use one customer-facing category across all brands.
 # Canonical technical groups remain unchanged in catalog.json.
 return DISPLAY_GROUP_BY_GRAPHIC.get(item['graphic'],item['group'])
def card(items,brand,lang,page):
 u=UI[lang];first=items[0];sid=item_anchor(first,brand);signal_label={'cs':'Rozhodující signalizace','en':'Key indication','de':'Entscheidende Anzeige'}[lang]
 aliases=''.join(f'<span class="wl-card-alias" id="{item_anchor(i,brand)}" tabindex="-1"></span>'for i in items[1:])
 multiple=len(items)>1;title=first['name'][lang]
 if multiple:title+=' · '+{'cs':'více významů stejného symbolu','en':'multiple meanings of the same symbol','de':'mehrere Bedeutungen desselben Symbols'}[lang]
 search=' '.join(i['name'][lang]+' '+i['meaning'][lang]+' '+i['note'][lang] for i in items)
 out=f'<article class="wl-card" id="{sid}" tabindex="-1" data-brand="{brand}" data-search="{esc(search)}">{aliases}<div class="wl-card-head"><span class="wl-symbol"><img src="{rel(first["graphic_path"],page)}" width="112" height="84" alt="{esc(first["alt"][lang])}"></span><h4 class="wl-name">{esc(title)}</h4></div><div class="wl-detail">'
 for i in items:
  scopes=[s for s in i['scopes'] if s['brand']==brand];states=list(dict.fromkeys(sc.get('signal_state',i['state']) for sc in scopes));state_label=' / '.join(u['states'][state] for state in states)
  out+='<section class="wl-meaning-variant">'
  if multiple:out+=f'<h5 class="wl-variant-name">{esc(i["name"][lang])}</h5>'
  out+=f'<p class="wl-status">{esc(u["colors"][i["color"]])} · {esc(u["kinds"][i["kind"]])} · {esc(state_label)}</p>'
  for key,label in [('meaning','meaning'),('action','action')]:out+=f'<h6>{esc(u[label])}</h6><p>{esc(i[key][lang])}</p>'
  out+=f'<h6>{esc(signal_label)}</h6><p>{esc(i["note"][lang])}</p></section>'
 out+='</div></article>'
 return out

INFO_BRANDS={'Volkswagen':'volkswagen','Škoda':'skoda','SEAT':'seat','Volkswagen Užitkové vozy':'volkswagen-uzitkove-vozy'}
INFO_CATEGORY_ORDER=['media','radio','navigation','phone','app-connect','other']
INFO_CATEGORY_LABELS={
 'cs':{'media':'Média','radio':'Rádio','navigation':'Navigace','phone':'Telefon a zprávy','app-connect':'Připojení telefonu a aplikací','other':'Další symboly'},
 'en':{'media':'Media','radio':'Radio','navigation':'Navigation','phone':'Phone and messages','app-connect':'Phone and app connectivity','other':'Other symbols'},
 'de':{'media':'Medien','radio':'Radio','navigation':'Navigation','phone':'Telefon und Nachrichten','app-connect':'Telefon- und App-Verbindung','other':'Weitere Symbole'}}
BRAND_TILE_LABELS={
 'cs':{'volkswagen':'Můj Volkswagen','audi':'Moje Audi','skoda':'Moje Škoda','seat':'Můj SEAT','cupra':'Moje CUPRA','volkswagen-uzitkove-vozy':'Můj užitkový Volkswagen'},
 'en':{'volkswagen':'My Volkswagen','audi':'My Audi','skoda':'My Škoda','seat':'My SEAT','cupra':'My CUPRA','volkswagen-uzitkove-vozy':'My Volkswagen Commercial Vehicle'},
 'de':{'volkswagen':'Mein Volkswagen','audi':'Mein Audi','skoda':'Mein Škoda','seat':'Mein SEAT','cupra':'Mein CUPRA','volkswagen-uzitkove-vozy':'Mein Volkswagen Nutzfahrzeug'}}
def info_category(item):
 raw=str(item.get('category')or'').lower();id=item['id'].lower()
 if raw in ('navigation','navigace'):return'navigation'
 if raw in ('telephone','telefon','phone'):return'phone'
 if raw in ('radio','rádio'):return'radio'
 if raw=='media':return'media'
 if raw=='app-connect':return'app-connect'
 for key,needles in [('navigation',('navigation','navigace')),('radio',('radio-',)),('media',('media-',)),('phone',('phone-','telephone-','telefon-','sms-')),('app-connect',('mirrorlink','smartlink','app-connect','connect-'))]:
  if any(x in id for x in needles):return key
 return'other'
def infotainment_card(items,brand,lang,page):
 first=items[0];sid='infotainment-'+first['id'];aliases=''.join(f'<span class="wl-card-alias" id="infotainment-{i["id"]}" tabindex="-1"></span>'for i in items[1:]);t=INFO_TEXT[first['id']][lang];title=t['name']
 if len(items)>1:title+=' · '+{'cs':'více použití stejného symbolu','en':'multiple uses of the same symbol','de':'mehrere Verwendungen desselben Symbols'}[lang]
 path='wp-content/uploads/infotainment/'+str(Path(first['svg_file']).relative_to('icons')).replace(os.sep,'/')
 search=' '.join(INFO_TEXT[i['id']][lang]['name']+' '+INFO_TEXT[i['id']][lang]['meaning'] for i in items)
 out=f'<article class="wl-card wl-infotainment-card" id="{sid}" tabindex="-1" data-brand="{brand}" data-search="{esc(search)}">{aliases}<div class="wl-card-head"><span class="wl-symbol"><img src="{rel(path,page)}" width="112" height="84" alt="{esc(t["name"])}"></span><h4 class="wl-name">{esc(title)}</h4></div><div class="wl-detail">'
 for i in items:
  text=INFO_TEXT[i['id']][lang];kind={'infotainment-status':{'cs':'Informace o stavu','en':'Status information','de':'Statusinformation'},'infotainment-map-point':{'cs':'Bod nebo údaj mapy','en':'Map point or information','de':'Kartenpunkt oder Information'},'infotainment-traffic-information':{'cs':'Dopravní informace','en':'Traffic information','de':'Verkehrsinformation'}}.get(i.get('kind'),{'cs':'Ovládací symbol','en':'Control symbol','de':'Bediensymbol'})[lang]
  out+='<section class="wl-meaning-variant">'
  if len(items)>1:out+=f'<h5 class="wl-variant-name">{esc(text["name"])}</h5>'
  out+=f'<p class="wl-status">{esc(kind)}</p><h6>'+esc({'cs':'Význam a funkce','en':'Meaning and function','de':'Bedeutung und Funktion'}[lang])+f'</h6><p>{esc(text["meaning"])}</p></section>'
 out+='</div></article>';return out
def infotainment_content(brand,lang,page):
 items=[i for i in INFO['items'] if INFO_BRANDS.get(INFO['scopes'][i['scope_id']]['brand'])==brand]
 if not items:return''
 grouped=[]
 for i in items:
  row=next((x for x in grouped if x[0]['svg_sha256']==i['svg_sha256']),None)
  if row is None:grouped.append([i])
  else:row.append(i)
 out='<div class="wl-infotainment-content">'
 for category in INFO_CATEGORY_ORDER:
  rows=[x for x in grouped if info_category(x[0])==category]
  if rows:out+=f'<details class="wl-info-category"><summary><span>{esc(INFO_CATEGORY_LABELS[lang][category])}</span><span class="wl-group-arrow" aria-hidden="true"></span></summary><div class="wl-grid">'+''.join(infotainment_card(x,brand,lang,page)for x in rows)+'</div></details>'
 return out+'</div>'

def brand_selector_content(lang):
 u=UI[lang]
 prefix={'cs':'Rady pro řidiče','en':'Driver advice','de':'Fahrertipps'}[lang]
 messages={'brands':u['brands'],'advicePrefix':prefix}
 out='<script type="application/json" id="wl-messages">'+json.dumps(messages,ensure_ascii=False).replace('</','<\\/')+'</script><div class="wl-brand-tiles" role="group" aria-label="'+esc(u['brand'])+'">'
 out+=''.join(f'<button type="button" class="wl-brand-tile" data-brand="{brand}" aria-pressed="false" aria-controls="brand-advice">{esc(BRAND_TILE_LABELS[lang][brand])}</button>'for brand in u['brands'])
 return out+'</div>'

def warning_content(lang,page):
 u=UI[lang]
 out='<section id="prehled-kontrolek" class="wl-results">'
 for brand,bname in u['brands'].items():
  entries=[i for i in CAT['items'] if any(s['brand']==brand for s in i['scopes'])]
  if not entries:continue
  brand_grouped=[]
  for i in entries:
   existing=next((row for row in brand_grouped if row[0]['graphic_path']==i['graphic_path']),None)
   if existing is None:brand_grouped.append([i])
   else:existing.append(i)
  out+=f'<section class="wl-brand" data-brand="{brand}" aria-label="{esc(bname)}">'
  for group,gname in u['groups'].items():
   grouped=[items for items in brand_grouped if display_group(items[0],brand)==group]
   if group=='ovladani':
    info_html=infotainment_content(brand,lang,page);gname=({'cs':'Symboly a hlášení MMI','en':'MMI symbols and messages','de':'MMI-Symbole und Meldungen'}if brand=='audi'else{'cs':'Symboly infotainmentu a ovládání','en':'Infotainment and control symbols','de':'Infotainment- und Bediensymbole'})[lang]
    out+=f'<details class="wl-infotainment-section" id="{brand}-ovladani"><summary><span>{esc(gname)}</span><span class="wl-group-arrow" aria-hidden="true"></span></summary><div class="wl-infotainment-body">'
    if grouped:
     existing_label={'cs':'Ovládání a klimatizace','en':'Controls and climate','de':'Bedienung und Klima'}[lang]
     out+=f'<details class="wl-info-category wl-info-existing"><summary><span>{esc(existing_label)}</span><span class="wl-group-arrow" aria-hidden="true"></span></summary><div class="wl-grid">'+''.join(card(items,brand,lang,page) for items in grouped)+'</div></details>'
    out+=info_html+'</div></details>'
    continue
   if grouped:
    if brand=='audi' and group=='motor':out+='<h3 class="wl-audi-section">'+esc({'cs':'Kontrolky vozidla','en':'Vehicle warning lights','de':'Fahrzeug-Kontrollleuchten'}[lang])+'</h3>'
    out+=f'<details class="wl-group" id="{group if brand=='volkswagen' else brand+'-'+group}"><summary><span>{esc(gname)}</span><span class="wl-group-arrow" aria-hidden="true"></span></summary>'
    out+='<div class="wl-grid">'+''.join(card(items,brand,lang,page) for items in grouped)+'</div>'
    out+='</details>'
  out+='</section>'
 out+=f'<section class="wl-contact"><h2>{esc(u["contactTitle"])}</h2><p>{esc(u["contact"])}</p><p><strong>{esc(u["hours"])}</strong></p><p>{esc(u["office"])}: <a href="tel:+420605399448">+420 605 399 448</a><br>{esc(u["workshop"])}: <a href="tel:+420608313437">+420 608 313 437</a></p><a class="tlacitko-akce" href="{rel(locale_root(lang)+"kontakt",page)}" data-booking-panel>{esc(u["contactButton"])}</a><p class="wl-note">{esc(u["notAssistance"])}</p></section></section><noscript><p>'+esc(u['nojs'])+'</p></noscript>'
 return out

VIN_UI={
 'cs':{
  'whatTitle':'Co je VIN','what':'VIN je jedinečný identifikátor vozidla o délce 17 znaků. První tři znaky VIN tvoří světový kód výrobce (WMI). Znaky VIN na pozicích 4–9 tvoří popisnou část vozidla (VDS) a znaky na pozicích 10–17 identifikační část konkrétního vozidla (VIS). Přesný význam jednotlivých pozic se může lišit podle výrobce a trhu; samotný VIN proto bez odpovídajících podkladů neurčuje úplnou výbavu ani servisní specifikaci.',
  'docsTitle':'Doklady vozidla','docs':'V osvědčení o registraci hledejte položku označenou E nebo textem „identifikační číslo vozidla (VIN)“. Starší a novější doklady i doklady vydané v různých zemích mají odlišné uspořádání, proto nelze uvést jednu polohu údaje platnou pro všechny doklady.',
  'vehicleTitle':'Kde může být VIN na vozidle','vehicle':'Některá provedení mají VIN viditelný zvenku v poli za čelním sklem. VIN je také vyznačen přímo na karoserii; přesné místo se určuje podle modelu, generace a provedení karoserie, nikoli pouze podle značky. Řiďte se návodem konkrétního vozidla a porovnejte údaj s doklady.',
  'labelsTitle':'Štítky a servisní dokumentace','labels':'Pokud jej vozidlo používá, může být datový štítek v zavazadlovém prostoru nebo v servisní dokumentaci. Datový štítek s kódy vozidla není totéž co výrobní štítek s homologačními a výrobními údaji ani VIN vyznačený přímo na karoserii.',
  'wmiTitle':'Příklady úvodních identifikátorů','wmi':'Pro vybranou značku jsou doloženy například tyto počáteční identifikátory WMI: {codes}. Jde o příklady, nikoli úplný seznam. Identifikátor sám neurčuje přesný motor, výbavu ani celé provedení vozidla; rozhoduje celý VIN a odpovídající dokumentace.',
  'keyTitle':'Údaje v klíči','key':'U některých vozidel jsou identifikační a vybrané servisní údaje uloženy také v klíči. Servis s odpovídajícím vybavením je může načíst pomocí specializované čtečky. Dostupnost a rozsah údajů závisí na modelu vozidla a provedení klíče.'},
 'en':{
  'whatTitle':'What a VIN is','what':'A VIN is a unique vehicle identifier made up of 17 VIN characters. Characters 1–3 form the World Manufacturer Identifier (WMI), characters 4–9 the Vehicle Descriptor Section (VDS), and characters 10–17 the Vehicle Identifier Section (VIS). The exact meaning of individual positions can vary by manufacturer and market, so a VIN alone does not establish the complete equipment or service specification without the matching records.',
  'docsTitle':'Vehicle documents','docs':'In a registration certificate, look for field E or wording that identifies the vehicle identification number (VIN). Older and newer certificates, and documents issued in different countries, use different layouts, so one fixed position cannot be stated for every document.',
  'vehicleTitle':'Where the VIN may be found on the vehicle','vehicle':'Some versions display the VIN in a field visible from outside through the windscreen. The VIN is also marked directly on the body; its exact location depends on the model, generation and body version, not only the brand. Follow the manual for the exact vehicle and compare the number with its documents.',
  'labelsTitle':'Labels and service documents','labels':'Where fitted, a vehicle data sticker may be located in the luggage compartment or service documents. A vehicle data sticker containing vehicle codes is different from the manufacturer’s plate carrying approval and production data and from the VIN marked directly on the body.',
  'wmiTitle':'Examples of initial identifiers','wmi':'Documented examples of WMI identifiers for the selected brand include: {codes}. These are examples, not a complete list. The identifier alone does not establish the exact engine, equipment or complete vehicle version; the full VIN and matching documentation are required.',
  'keyTitle':'Data stored in the key','key':'In some vehicles, identification data and selected service information are also stored in the key. A workshop with suitable equipment can read them with a specialised reader. The availability and scope of the data depend on the vehicle model and key version.'},
 'de':{
  'whatTitle':'Was die VIN ist','what':'Die VIN ist eine eindeutige Fahrzeugkennung aus 17 VIN-Zeichen. Die Zeichen 1–3 bilden die Weltherstellerkennung (WMI), die Zeichen 4–9 den beschreibenden Fahrzeugteil (VDS) und die Zeichen 10–17 den individuellen Fahrzeugteil (VIS). Die genaue Bedeutung einzelner Stellen kann je nach Hersteller und Markt abweichen; ohne passende Unterlagen bestimmt die VIN allein daher weder die vollständige Ausstattung noch die Servicespezifikation.',
  'docsTitle':'Fahrzeugdokumente','docs':'Suchen Sie in der Zulassungsbescheinigung das Feld E oder die Bezeichnung der Fahrzeug-Identifizierungsnummer (VIN). Ältere und neuere Dokumente sowie Dokumente verschiedener Länder sind unterschiedlich aufgebaut; deshalb gibt es keine für alle Dokumente gültige feste Position.',
  'vehicleTitle':'Wo die VIN am Fahrzeug stehen kann','vehicle':'Bei manchen Ausführungen ist die VIN von außen in einem Feld hinter der Windschutzscheibe sichtbar. Die VIN ist außerdem direkt an der Karosserie angebracht; die genaue Stelle hängt von Modell, Generation und Karosserieausführung ab, nicht nur von der Marke. Beachten Sie die Anleitung des konkreten Fahrzeugs und vergleichen Sie die Nummer mit den Dokumenten.',
  'labelsTitle':'Aufkleber und Serviceunterlagen','labels':'Falls verwendet, kann sich ein Fahrzeugdatenträger im Gepäckraum oder in den Serviceunterlagen befinden. Ein Datenträger mit Fahrzeugcodes ist nicht dasselbe wie das Herstellerschild mit Genehmigungs- und Produktionsdaten oder die direkt an der Karosserie angebrachte VIN.',
  'wmiTitle':'Beispiele für Herstellerkennungen','wmi':'Für die gewählte Marke sind beispielsweise folgende WMI-Anfangskennungen belegt: {codes}. Dies sind Beispiele und keine vollständige Liste. Die Kennung allein bestimmt weder den genauen Motor noch Ausstattung oder vollständige Fahrzeugausführung; maßgeblich sind die vollständige VIN und die passenden Unterlagen.',
  'keyTitle':'Daten im Schlüssel','key':'Bei einigen Fahrzeugen sind Identifikationsdaten und ausgewählte Serviceinformationen auch im Schlüssel gespeichert. Ein Betrieb mit geeigneter Ausstattung kann sie mit einem spezialisierten Lesegerät auslesen. Verfügbarkeit und Umfang hängen vom Fahrzeugmodell und von der Schlüsselausführung ab.'}
}
VIN_WMI={'volkswagen':['WVW','WVG'],'audi':['WAU'],'skoda':['TMB'],'seat':['VSS'],'cupra':['VSS'],'volkswagen-uzitkove-vozy':['WV1','WV2']}
VIN_PLATE_UI={
 'cs':{'title':'Jak číst datový štítek','note':'Zjednodušené schéma – skutečný vzhled, pořadí a rozsah údajů se liší podle konkrétního vozidla. Nejde o výrobní štítek ani o náhradu VIN vyznačeného na karoserii. Přesnou podobu pro konkrétní Volkswagen lze určit pouze podle odpovídající dokumentace.','optionalLabel':'Údaje uváděné jen na některých datových štítcích','example':'Názorný příklad datového štítku','fields':[('VIN','Celý 17znakový identifikátor vozidla.'),('Typ vozidla','Typové a modelové údaje; podle provedení štítku také výkon motoru a druh převodovky.'),('Motor a převodovka','Identifikační kódy motoru a převodovky.'),('Lak a interiér','Kód barvy laku a kód provedení interiéru, pokud jsou uvedeny.'),('Kódy výbavy','Kódy výrobní výbavy. Jejich význam se ověřuje v dokumentaci pro konkrétní vozidlo.'),('Spotřeba ve městě','Homologační hodnota v l/100 km, pokud je na štítku uvedena.'),('Spotřeba mimo město','Homologační hodnota v l/100 km, pokud je na štítku uvedena.'),('Kombinovaná spotřeba','Kombinovaná homologační hodnota v l/100 km, pokud je uvedena.'),('Kombinované emise CO₂','Kombinovaná homologační hodnota emisí CO₂ v g/km, pokud je uvedena.')]},
 'en':{'title':'How to read a vehicle data sticker','note':'Simplified schematic—the actual appearance, order and scope of data vary by the specific vehicle. This is not the manufacturer’s plate and does not replace the VIN marked on the body. The exact form for a particular Volkswagen can be stated only from the matching documentation.','optionalLabel':'Data stated only on some vehicle data stickers','example':'Illustrative vehicle data sticker','fields':[('VIN','The complete 17-character vehicle identifier.'),('Vehicle type','Type and model information; depending on the sticker version, also engine output and gearbox type.'),('Engine and gearbox','Identification codes for the engine and gearbox.'),('Paint and interior','Paint colour and interior-trim codes, where stated.'),('Equipment codes','Production equipment codes. Their meaning must be checked in documentation for the exact vehicle.'),('Urban consumption','Type-approval value in l/100 km, where stated on the sticker.'),('Extra-urban consumption','Type-approval value in l/100 km, where stated on the sticker.'),('Combined consumption','Combined type-approval value in l/100 km, where stated.'),('Combined CO₂ emissions','Combined type-approval CO₂ value in g/km, where stated.')]},
 'de':{'title':'Fahrzeugdatenträger lesen','note':'Vereinfachtes Schema – Aussehen, Reihenfolge und Umfang der Angaben unterscheiden sich je nach konkretem Fahrzeug. Dies ist kein Herstellerschild und ersetzt nicht die an der Karosserie angebrachte VIN. Die genaue Ausführung für einen bestimmten Volkswagen darf nur anhand der passenden Dokumentation angegeben werden.','optionalLabel':'Angaben, die nur auf bestimmten Fahrzeugdatenträgern stehen','example':'Beispiel eines Fahrzeugdatenträgers','fields':[('VIN','Die vollständige Fahrzeugkennung aus 17 Zeichen.'),('Fahrzeugtyp','Typ- und Modellangaben; je nach Ausführung des Datenträgers auch Motorleistung und Getriebeart.'),('Motor und Getriebe','Identifikationscodes von Motor und Getriebe.'),('Lack und Innenraum','Code der Lackfarbe und der Innenausstattung, sofern angegeben.'),('Ausstattungscodes','Codes der Produktionsausstattung. Ihre Bedeutung ist in den Unterlagen des konkreten Fahrzeugs zu prüfen.'),('Verbrauch innerorts','Typgenehmigungswert in l/100 km, sofern auf dem Datenträger angegeben.'),('Verbrauch außerorts','Typgenehmigungswert in l/100 km, sofern angegeben.'),('Kombinierter Verbrauch','Kombinierter Typgenehmigungswert in l/100 km, sofern angegeben.'),('Kombinierte CO₂-Emissionen','Kombinierter Typgenehmigungswert der CO₂-Emissionen in g/km, sofern angegeben.')]}
}
def vin_plate_content(lang,wmi):
 u=VIN_PLATE_UI[lang];masked=wmi+'•'*14;assert len(masked)==17
 rows=[masked,'MODEL / TYPE','XXXX / XXX','XX / XX','XXX  XXX  XXX','— l/100 km','— l/100 km','— l/100 km','— g/km CO₂']
 plate='<div class="vin-plate-example" role="img" aria-label="'+esc(u['example'])+'">'
 for index,value in enumerate(rows,1):
  if index==6:plate+=f'<div class="vin-plate-optional-label">{esc(u["optionalLabel"])}</div>'
  plate+=f'<div class="vin-plate-row{(" vin-plate-row-optional" if index>=6 else "")}"><span class="vin-plate-number">{index}</span><span>{esc(value)}</span></div>'
 plate+='</div><ol class="vin-plate-legend">'
 for index,(name,meaning) in enumerate(u['fields'],1):
  if index==6:plate+=f'<li class="vin-plate-optional-heading">{esc(u["optionalLabel"])}</li>'
  plate+=f'<li><strong>{esc(name)}</strong><span>{esc(meaning)}</span></li>'
 return f'<figure class="vin-data-plate"><figcaption><strong>{esc(u["title"])}</strong><span class="vin-plate-warning">{esc(u["note"])}</span></figcaption><div class="vin-plate-layout">{plate}</ol></div></figure>'
def vin_content(lang):
 u=VIN_UI[lang];out='<div class="vin-content">'
 for brand,codes in VIN_WMI.items():
  out+=f'<section class="vin-brand-panel" data-vin-panel="{brand}" hidden><div class="vin-intro"><span class="vin-icon" aria-hidden="true"><span>VIN</span></span><div><h2>{esc(u["whatTitle"])}</h2><p>{esc(u["what"])}</p></div></div>'
  for key in ('docs','vehicle','labels'):
   out+=f'<section class="vin-section"><h2>{esc(u[key+"Title"])}</h2><p>{esc(u[key])}</p></section>'
  out+=vin_plate_content(lang,codes[0])
  out+=f'<section class="vin-section vin-wmi"><h2>{esc(u["wmiTitle"])}</h2><p>{esc(u["wmi"].format(codes=", ".join(codes)))}</p></section><section class="vin-section"><h2>{esc(u["keyTitle"])}</h2><p>{esc(u["key"])}</p></section></section>'
 return out+'</div>'

FUSE_SAFETY={
 'cs':{
  'title':'Pojistka se znovu přepálila? Další výměnu již nezkoušejte.',
  'paragraphs':[
   'Pokud se nová pojistka předepsaného typu a proudové hodnoty znovu přepálí, další již nevkládejte. Nechte příčinu závady zjistit v odborném servisu. Může jít například o zkrat, přetížení elektrického obvodu nebo závadu připojeného zařízení.',
   'Nikdy nepoužívejte „silnější“ pojistku s vyšší hodnotou v ampérech. Pojistky neopravujte ani nepřemosťujte drátem nebo jiným předmětem.',
   'Takový zásah narušuje ochranu elektrického obvodu a může způsobit přehřátí a poškození kabeláže, konektorů či elektronických součástí. V krajním případě hrozí požár vozidla.',
   'Náhradní pojistka musí vždy odpovídat typu, rozměrům a proudové hodnotě předepsaným výrobcem vozidla.']},
 'en':{
  'title':'Has the fuse blown again? Do not try another replacement.',
  'paragraphs':[
   'If a new fuse of the specified type and current rating blows again, do not insert another one. Have the cause of the fault identified by a qualified workshop. Possible causes include a short circuit, an overloaded electrical circuit or a fault in a connected device.',
   'Never use a “stronger” fuse with a higher ampere rating. Do not repair a fuse or bridge it with wire or any other object.',
   'Doing so defeats the protection of the electrical circuit and can cause overheating and damage to wiring, connectors or electronic components. In an extreme case, the vehicle could catch fire.',
   'A replacement fuse must always match the type, dimensions and current rating specified by the vehicle manufacturer.']},
 'de':{
  'title':'Ist die Sicherung erneut durchgebrannt? Versuchen Sie keinen weiteren Austausch.',
  'paragraphs':[
   'Wenn eine neue Sicherung des vorgeschriebenen Typs und Nennstroms erneut durchbrennt, setzen Sie keine weitere ein. Lassen Sie die Störungsursache von einem Fachbetrieb feststellen. Mögliche Ursachen sind zum Beispiel ein Kurzschluss, eine Überlastung des Stromkreises oder ein Fehler eines angeschlossenen Geräts.',
   'Verwenden Sie niemals eine „stärkere“ Sicherung mit höherem Amperewert. Sicherungen dürfen weder repariert noch mit Draht oder einem anderen Gegenstand überbrückt werden.',
   'Ein solcher Eingriff setzt den Schutz des Stromkreises außer Kraft und kann zur Überhitzung sowie zu Schäden an Leitungen, Steckverbindungen oder elektronischen Bauteilen führen. Im Extremfall besteht Fahrzeugbrandgefahr.',
   'Eine Ersatzsicherung muss stets dem vom Fahrzeughersteller vorgeschriebenen Typ, den Abmessungen und dem Nennstrom entsprechen.']}
}
def fuse_safety_content(lang):
 u=FUSE_SAFETY[lang]
 return '<aside class="fuse-safety" role="note"><h2>'+esc(u['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in u['paragraphs'])+'</aside>'

FUSE_COLOUR_UI={
 'cs':{'title':'Barevné označení pojistek','note':'Tento přehled platí pouze pro odpovídající rodinu nožových pojistek. Barva sama nepotvrzuje správný konstrukční typ, rozměr ani umístění ve vozidle. Vždy zkontrolujte hodnotu vyznačenou na pojistce a předpis pro konkrétní vozidlo.','colour':'Barva','rating':'Proudová hodnota','amp':'A','names':['Černá','Šedá','Fialová','Růžová','Světle hnědá','Hnědá','Červená','Světle modrá','Žlutá','Bílá nebo průsvitná','Světle zelená','Modrozelená','Oranžová']},
 'en':{'title':'Fuse colour coding','note':'This table applies only to the corresponding family of blade fuses. Colour alone does not confirm the correct construction type, dimensions or position in the vehicle. Always check the rating marked on the fuse and the specification for the exact vehicle.','colour':'Colour','rating':'Current rating','amp':'A','names':['Black','Grey','Violet','Pink','Light brown','Brown','Red','Light blue','Yellow','White or transparent','Light green','Blue-green','Orange']},
 'de':{'title':'Farbkennzeichnung der Sicherungen','note':'Diese Übersicht gilt nur für die entsprechende Familie von Flachsicherungen. Die Farbe allein bestätigt weder Bauart und Abmessungen noch die Einbauposition im Fahrzeug. Prüfen Sie stets den auf der Sicherung angegebenen Wert und die Vorgabe für das konkrete Fahrzeug.','colour':'Farbe','rating':'Nennstrom','amp':'A','names':['Schwarz','Grau','Violett','Rosa','Hellbraun','Braun','Rot','Hellblau','Gelb','Weiß oder transparent','Hellgrün','Blaugrün','Orange']}
}
FUSE_COLOURS=[('black','1'),('grey','2'),('violet','3'),('pink','4'),('tan','5'),('brown','7,5'),('red','10'),('light-blue','15'),('yellow','20'),('clear','25'),('light-green','30'),('blue-green','35'),('orange','40')]
def fuse_colour_content(lang):
 u=FUSE_COLOUR_UI[lang]
 out=f'<section class="fuse-colour-guide" aria-labelledby="fuse-colour-title-{lang}"><h2 id="fuse-colour-title-{lang}">{esc(u["title"])}</h2><p class="fuse-colour-note">{esc(u["note"])}</p><div class="fuse-table-wrap"><table><thead><tr><th scope="col">{esc(u["colour"])}</th><th scope="col">{esc(u["rating"])}</th></tr></thead><tbody>'
 for (colour,value),name in zip(FUSE_COLOURS,u['names']):out+=f'<tr><th scope="row"><span class="fuse-swatch fuse-swatch-{colour}" aria-hidden="true"></span>{esc(name)}</th><td>{esc(value)} {esc(u["amp"])}</td></tr>'
 return out+'</tbody></table></div></section>'

ONLINE_SERVICES={
 'volkswagen':{'name':'Volkswagen','account':'Volkswagen ID','app':'Volkswagen','account_url':'https://www.myvolkswagen.net/cz/cs/myvolkswagen.html','help_url':'https://www.volkswagen.cz/technologie/konektivita/vw-connect','note':{
  'cs':'Podle provedení může vůz použít naskenování kódu, ověření dvěma klíči nebo zadání aktivačního kódu. Použijte pouze postup zobrazený pro váš vůz a infotainment.',
  'en':'Depending on the vehicle, activation may use a scanned code, verification with two keys or an activation code. Use only the procedure shown for your vehicle and infotainment system.',
  'de':'Je nach Ausführung erfolgt die Aktivierung per Code-Scan, Prüfung mit zwei Schlüsseln oder Eingabe eines Aktivierungscodes. Verwenden Sie nur das für Ihr Fahrzeug und Infotainment angezeigte Verfahren.'}},
 'audi':{'name':'Audi','account':'Audi ID','app':'myAudi','account_url':'https://my.audi.com/','help_url':'https://www.audi.cz/servis-a-prislusenstvi/konektivita-a-technologie/audi-connect/nastaveni-sluzby','note':{
  'cs':'Rozlišujte přihlášení účtem myAudi/Audi ID, propojení s MMI a ověření hlavního uživatele. Postup se liší podle modelu a verze MMI. Použijte návod odpovídající vašemu vozu. Desetimístný kód vozidla není společný všem Audi; myAudi může nejprve nabídnout výběr země nebo regionu.',
  'en':'Keep myAudi/Audi ID sign-in, pairing with MMI and primary-user verification separate. The procedure varies by model and MMI version. Use the instructions for your vehicle. A ten-digit vehicle code does not apply to every Audi; myAudi may first ask for a country or region.',
  'de':'Anmeldung mit myAudi/Audi ID, Verbindung mit dem MMI und Prüfung des Hauptnutzers sind getrennte Schritte. Das Verfahren hängt von Modell und MMI-Version ab. Verwenden Sie die Anleitung für Ihr Fahrzeug. Ein zehnstelliger Fahrzeugcode gilt nicht für alle Audi; myAudi kann zunächst Land oder Region abfragen.'}},
 'skoda':{'name':'Škoda','account':'Škoda ID','app':'MyŠkoda','account_url':'https://skodaid.vwgroup.io/','help_url':'https://www.skoda-auto.cz/konektivita/skoda-connect','app_url':'https://www.skoda-auto.cz/konektivita/myskoda','note':{
  'cs':'Použijte aktuální postup MyŠkoda → Škoda ID → přidání VIN a dokončete kroky podle průvodce. Podrobný způsob ověření závisí na doloženém provedení vozidla.',
  'en':'Use the current MyŠkoda → Škoda ID → add VIN sequence and complete the guided steps. The detailed verification method depends on the documented vehicle version.',
  'de':'Verwenden Sie den aktuellen Ablauf MyŠkoda → Škoda ID → VIN hinzufügen und schließen Sie die geführten Schritte ab. Die genaue Prüfung hängt von der belegten Fahrzeugausführung ab.'}},
 'seat':{'name':'SEAT','account':'SEAT ID','app':'My SEAT','account_url':'https://seatid.vwgroup.io/','help_url':'https://www.seat.cz/servis-a-prislusenstvi/konektivita-a-technologie/seat-connect','note':{
  'cs':'Použijte aktuální aplikaci My SEAT. SEAT ID je účet výrobce; původní webový portál SEAT CONNECT byl ukončen. Dokončete propojení podle aktuálního průvodce.',
  'en':'Use the current My SEAT app. SEAT ID is the manufacturer account; the former SEAT CONNECT web portal has been discontinued. Complete pairing with the current guided procedure.',
  'de':'Verwenden Sie die aktuelle App My SEAT. Die SEAT ID ist das Herstellerkonto; das frühere Webportal SEAT CONNECT wurde eingestellt. Schließen Sie die Verbindung mit dem aktuellen Assistenten ab.'}},
 'cupra':{'name':'CUPRA','account':'CUPRA ID','app':'My CUPRA','account_url':'https://cupraid.vwgroup.io/','help_url':'https://www.cupraofficial.cz/cupra-connect/cupra-connect-gen3','help_url_2':'https://www.cupra.com/en/faqs/cupra-connect/gen-4-general-information','note':{
  'cs':'GEN3 a GEN4 mají odlišné postupy. Potvrzení dvěma klíči neplatí pro všechny modely; odpovídající provedení GEN4 vozů Born a Tavascan používají QR postup.',
  'en':'GEN3 and GEN4 use different procedures. Two-key confirmation does not apply to every model; matching GEN4 versions of the Born and Tavascan use a QR procedure.',
  'de':'GEN3 und GEN4 verwenden unterschiedliche Verfahren. Die Bestätigung mit zwei Schlüsseln gilt nicht für jedes Modell; passende GEN4-Ausführungen von Born und Tavascan verwenden ein QR-Verfahren.'}},
 'volkswagen-uzitkove-vozy':{'name':'Volkswagen Užitkové vozy','account':'Volkswagen ID','app':'Volkswagen','account_url':'https://www.myvolkswagen.net/cz/cs/myvolkswagen.html','help_url':'https://www.vw-uzitkove.cz/digitalni-sluzby-a-aplikace/vw-connect/aktivace','note':{
  'cs':'Volkswagen ID a aplikace Volkswagen jsou společné, ale aktivační postup musí odpovídat konkrétnímu užitkovému modelu, výbavě a infotainmentu.',
  'en':'Volkswagen ID and the Volkswagen app are shared, but the activation procedure must match the exact commercial-vehicle model, equipment and infotainment system.',
  'de':'Volkswagen ID und die Volkswagen App werden gemeinsam verwendet; die Aktivierung muss jedoch zum konkreten Nutzfahrzeugmodell, zur Ausstattung und zum Infotainment passen.'}}
}
ONLINE_UI={
 'cs':{'intro':'Chcete propojit svůj vůz s aplikací výrobce? Vyberte značku. Najdete zde informace k založení účtu, přihlášení a propojení s vozidlem. Přesný postup závisí na modelu, výbavě a systému infotainmentu.','need':'Pro propojení budete potřebovat účet {account} a aplikaci {app}.','start':'Začněte zde','accountButton':'Přihlásit se nebo vytvořit účet {account}','helpButton':'Otevřít návod k propojení vozidla','combinedButton':'Návod k propojení a aplikace {app}','appButton':'Informace a stažení aplikace {app}','steps':[('1. Přihlaste se nebo si vytvořte účet','Pokud už účet máte, přihlaste se. Jinak si jej založte a potvrďte e-mailovou adresu, pokud vás o to výrobce požádá.'),('2. Otevřete aplikaci a přidejte vozidlo','V aplikaci zvolte přidání vozidla a zadejte VIN podle průvodce. VIN je identifikační číslo vozidla. Samotné založení účtu ještě vozidlo s aplikací nepropojí.'),('3. Dokončete propojení ve vozidle','Postupujte podle pokynů v aplikaci a na obrazovce vozidla. Některé služby vyžadují také ověření hlavního uživatele a samostatnou aktivaci.')],'availability':'Dostupnost funkcí závisí na vozidle, výbavě, softwaru, zemi a příslušné smlouvě či licenci. Heslo účtu, bezpečnostní PIN, párovací kód a kód vozidla jsou odlišné údaje. Nezadávejte je na webu J&S SERVIS.','linkNote':'Zapomenuté heslo obnovte pouze přes oficiální přihlašovací stránku výrobce.','gen3':'My CUPRA: návod pro vozy GEN3','gen4':'My CUPRA: návod GEN4 pro odpovídající Born a Tavascan'},
 'en':{'intro':'Would you like to connect your vehicle to the manufacturer’s app? Select a brand for information about creating an account, signing in and pairing the vehicle. The exact procedure depends on the model, equipment and infotainment system.','need':'To connect the vehicle, you will need a {account} account and the {app} app.','start':'Start here','accountButton':'Sign in or create a {account} account','helpButton':'Open the vehicle-pairing instructions','combinedButton':'Pairing instructions and the {app} app','appButton':'Information and download for the {app} app','steps':[('1. Sign in or create an account','If you already have an account, sign in. Otherwise create one and confirm your email address if requested by the manufacturer.'),('2. Open the app and add the vehicle','In the app, select the option to add a vehicle and enter its VIN as instructed. VIN means vehicle identification number. Creating an account alone does not pair the vehicle with the app.'),('3. Complete pairing in the vehicle','Follow the instructions in the app and on the vehicle display. Some services also require primary-user verification and a separate activation.')],'availability':'Function availability depends on the vehicle, equipment, software, country and applicable contract or licence. The account password, security PIN, pairing code and vehicle code are different credentials. Do not enter them on the J&S SERVIS website.','linkNote':'Recover a forgotten password only through the manufacturer’s official sign-in page.','gen3':'My CUPRA: instructions for GEN3 vehicles','gen4':'My CUPRA: GEN4 instructions for matching Born and Tavascan versions'},
 'de':{'intro':'Möchten Sie Ihr Fahrzeug mit der Hersteller-App verbinden? Wählen Sie eine Marke. Hier finden Sie Hinweise zu Kontoerstellung, Anmeldung und Fahrzeugverknüpfung. Der genaue Ablauf hängt von Modell, Ausstattung und Infotainment ab.','need':'Für die Verbindung benötigen Sie ein {account}-Konto und die App {app}.','start':'Hier beginnen','accountButton':'Anmelden oder {account}-Konto erstellen','helpButton':'Anleitung zur Fahrzeugverbindung öffnen','combinedButton':'Verbindungsanleitung und App {app}','appButton':'Informationen und Download der App {app}','steps':[('1. Anmelden oder Konto erstellen','Wenn Sie bereits ein Konto haben, melden Sie sich an. Andernfalls erstellen Sie ein Konto und bestätigen auf Aufforderung des Herstellers Ihre E-Mail-Adresse.'),('2. App öffnen und Fahrzeug hinzufügen','Wählen Sie in der App „Fahrzeug hinzufügen“ und geben Sie die VIN nach Anleitung ein. VIN bedeutet Fahrzeug-Identifizierungsnummer. Die Kontoerstellung allein verbindet das Fahrzeug noch nicht mit der App.'),('3. Verbindung im Fahrzeug abschließen','Folgen Sie den Hinweisen in der App und auf dem Fahrzeugdisplay. Einige Dienste erfordern zusätzlich die Prüfung des Hauptnutzers und eine gesonderte Aktivierung.')],'availability':'Die Verfügbarkeit hängt von Fahrzeug, Ausstattung, Software, Land sowie Vertrag oder Lizenz ab. Kontopasswort, Sicherheits-PIN, Kopplungscode und Fahrzeugcode sind unterschiedliche Daten. Geben Sie diese nicht auf der Website von J&S SERVIS ein.','linkNote':'Ein vergessenes Passwort setzen Sie ausschließlich über die offizielle Anmeldeseite des Herstellers zurück.','gen3':'My CUPRA: Anleitung für GEN3-Fahrzeuge','gen4':'My CUPRA: GEN4-Anleitung für passende Born- und Tavascan-Ausführungen'}
}
def online_services_content(lang):
 u=ONLINE_UI[lang];brand_names=UI[lang]['brands']
 out='<div class="online-services">'
 for brand in brand_names:
  item=ONLINE_SERVICES[brand];app_url=item.get('app_url')
  fmt=lambda key: u[key].format(account=item['account'],app=item['app'])
  out+=f'<section class="online-brand-panel" id="online-panel-{brand}" data-online-panel="{brand}" hidden><h2 tabindex="-1">{esc(brand_names[brand])}</h2><p class="online-requirements">{esc(fmt("need"))}</p><h3 class="online-start">{esc(u["start"])}</h3><div class="online-actions">'
  out+=f'<a class="online-action" href="{esc(item["account_url"])}" target="_blank" rel="noopener noreferrer">{esc(fmt("accountButton"))}</a>'
  if app_url:out+=f'<a class="online-action online-action-secondary" href="{esc(app_url)}" target="_blank" rel="noopener noreferrer">{esc(fmt("appButton"))}</a>'
  if brand=='cupra':
   out+=f'<a class="online-action" href="{esc(item["help_url"])}" target="_blank" rel="noopener noreferrer">{esc(u["gen3"])}</a><a class="online-action" href="{esc(item["help_url_2"])}" target="_blank" rel="noopener noreferrer">{esc(u["gen4"])}</a>'
  else:out+=f'<a class="online-action" href="{esc(item["help_url"])}" target="_blank" rel="noopener noreferrer">{esc(fmt("helpButton" if app_url else "combinedButton"))}</a>'
  out+='</div><ol class="online-steps">'
  for heading,text in u['steps']:out+=f'<li><h3>{esc(heading)}</h3><p>{esc(text)}</p></li>'
  out+=f'</ol><p class="online-brand-note"><strong>{esc(item["note"][lang])}</strong></p><p>{esc(u["availability"])}</p><p class="online-password-note">{esc(u["linkNote"])}</p></section>'
 return out+'</div>'

DRIVER_TOPICS={
 'cs':{
  'page':'Rady pro řidiče','intro':'Praktické přehledy pro správnou reakci na hlášení vozidla a základní kontrolu provozních údajů. Konkrétní údaj vždy ověřte pro přesný model, modelový rok, výbavu a pohon.',
  'titles':['Identifikace mého vozu – VIN','Přihlášení a online služby vozidla','Kontrolky a výstražná hlášení','Pojistky – barvy a hodnoty','Tlak pneumatik','Oleje – viskozita a specifikace','Chladicí kapaliny','Servis a servisní intervaly'],
  'topics':[
   [],[],[],
   [('Typy automobilových pojistek','Před určením náhrady zjistěte konstrukční typ pojistky. Stejná barva u odlišných rodin pojistek sama nepotvrzuje shodné provedení.'),('Barevné značení a proudové hodnoty','Barvu a hodnotu v ampérech posuzujte jen v tabulce pro daný typ pojistky. Přehled neobsahuje obsazení pojistkových skříní ani přiřazení spotřebičů.'),('Jak určit odpovídající pojistku','Rozhoduje návod konkrétního vozidla, poloha ve správné pojistkové skříni, typ pojistky a předepsaná proudová hodnota.'),('Zásady správné náhrady','Vypněte příslušný spotřebič a zapalování podle návodu. Použijte pouze pojistku stejného typu a hodnoty; opakované přepálení vyžaduje diagnostiku.')],
   [('Kde najdu tlakový štítek','Umístění musí být doloženo pro konkrétní model a generaci. Může jít o sloupek nebo rám dveří, vnitřní stranu víčka palivové nádrže či jiné místo uvedené v návodu. Modelově ověřené fotografie a čitelné detaily štítků zatím nejsou zveřejněny.'),('Jak přečtu správné hodnoty','Nejprve porovnejte rozměr pneumatiky a stav zatížení na štítku. Hodnoty pro běžné a plné zatížení ani přední a zadní nápravu nezaměňujte.'),('Kontrola a úprava tlaku','Tlak kontrolujte na studených pneumatikách podle podmínek uvedených výrobcem. Nejdříve skutečný tlak změřte a upravte; samotné zhasnutí kontrolky není cílem.'),('Uložení nebo nastavení systému','Uložení přes infotainment, tlačítko SET nebo jiný postup lze uvést jen pro odpovídající model a systém. Po úpravě tlaku postupujte podle návodu vozidla.')],
   [('Motorové oleje a označení SAE','SAE popisuje viskozitní třídu. Neurčuje samo schválení výrobce ani vhodnost pro konkrétní motor.'),('Normy a schválení Volkswagen Group','Použijte přesné schválení uvedené pro motor a servisní režim. Shodná viskozita neprokazuje zaměnitelnost.'),('Výběr, kontrola hladiny a doplnění','Rozhoduje konkrétní motor, servisní režim a návod. Hladinu kontrolujte předepsaným postupem; nepřeplňujte.'),('Mísení a nouzové doplnění','Možnost mísení nebo nouzového doplnění musí být výslovně doložena pro danou specifikaci. Obecná podobnost názvu nestačí.'),('Převodové a další oleje','Náplně manuálních převodovek, DSG, ostatních automatů, rozvodovek, diferenciálů a spojek pohonu všech kol se posuzují odděleně podle konkrétní konstrukce.')],
   [('Označení a specifikace výrobce','Barva kapaliny není jediným kritériem. Rozhoduje specifikace předepsaná pro konkrétní vozidlo a chladicí okruh.'),('Koncentrát, hotová směs a ředění','Rozlišujte koncentrát a předmíchanou kapalinu. Poměr ředění, požadovanou vodu a ochranu proti zamrznutí přebírejte z příslušného návodu.'),('Mísitelnost a náhrady','Mísitelnost ani náhradu staršího produktu nelze odvodit jen z obchodního názvu. Musí být doložena výrobcem pro daný okruh.'),('Bezpečná kontrola a doplňování','Nikdy neotvírejte horký okruh. Při neznámé náplni, opakovaném úbytku nebo výstraze nejprve zjistěte příčinu; u hybridů a elektromobilů rozlišujte jednotlivé okruhy.')],
   [('Výběr správného servisního plánu','Je nutné určit značku, model a generaci, modelový rok, motor nebo pohon, převodovku a podle potřeby VIN, kódy agregátů a PR kódy.'),('Servisní prohlídky a olejový servis','Inspekční prohlídku, olejový servis a samostatné úkony posuzujte odděleně. Pevný a proměnlivý režim mají rozdílné podmínky.'),('Filtry, svíčky, rozvody a pomocné pohony','První a následující termíny i časové a kilometrové podmínky musí pocházet z odpovídajícího servisního plánu.'),('Převodovka, pohon všech kol, brzdy a kapaliny','Pro DSG, jiné automaty ani pohon 4×4 neexistuje jeden univerzální interval. Rozhoduje konkrétní konstrukce, servisovaný okruh, náplň a případný filtr.'),('Další údržba konkrétní výbavy','Kontrolu, doplnění, pravidelnou výměnu a výměnu podle stavu rozlišujte. Předpis výrobce a preventivní doporučení J&S SERVIS musí být uvedeny samostatně.')]
  ]},
 'en':{
  'page':'Driver advice','intro':'Practical guidance for responding to vehicle messages and checking basic operating information. Always verify a specific value for the exact model, model year, equipment and powertrain.',
  'titles':['Identifying my vehicle – VIN','Sign-in and online vehicle services','Warning lights and driver messages','Fuses – colours and ratings','Tyre pressures','Oils – viscosity and specifications','Coolants','Service and maintenance intervals'],
  'topics':[
   [],[],[],
   [('Automotive fuse types','Identify the fuse construction before selecting a replacement. A matching colour in a different fuse family does not establish the same design.'),('Colour coding and ampere ratings','Use colour and ampere rating only with the table for that fuse type. This section does not reproduce fuse-box positions or consumer assignments.'),('Selecting the correct fuse','Use the exact vehicle manual, the position in the correct fuse box, the fuse type and the specified ampere rating.'),('Safe replacement','Switch off the relevant consumer and ignition as instructed. Use only the same type and rating; repeated failure requires diagnosis.')],
   [('Finding the pressure placard','The location must be documented for the exact model and generation. It may be on a door pillar or frame, inside the fuel flap, or elsewhere stated by the manual. Model-verified location photographs and readable placard details are not yet published.'),('Reading the correct values','Match the tyre size and load condition shown on the placard. Do not interchange normal/full-load or front/rear values.'),('Checking and adjusting pressure','Check cold tyres under the manufacturer’s stated conditions. Measure and correct the real pressure first; merely clearing a warning is not the objective.'),('Storing or setting the system','Infotainment storage, a SET button or another procedure may be assigned only to the matching model and system. Follow the vehicle manual after adjustment.')],
   [('Engine oils and SAE','SAE describes a viscosity grade. It does not by itself establish manufacturer approval or suitability for an engine.'),('Volkswagen Group approvals','Use the exact approval stated for the engine and service regime. Equal viscosity does not prove interchangeability.'),('Selection, level check and topping up','Use the exact engine, service regime and manual. Follow the prescribed level-check procedure and do not overfill.'),('Mixing and emergency top-up','Mixing or emergency top-up must be explicitly documented for the specification; a similar product name is insufficient.'),('Transmission and other oils','Manual transmissions, DSG, other automatics, transfer cases, differentials and all-wheel-drive clutches require separate assessment for the exact construction.')],
   [('Manufacturer designation and specification','Colour is not a sufficient selection criterion. Use the specification for the exact vehicle and cooling circuit.'),('Concentrate, premix and dilution','Distinguish concentrate from premix. Use the manual for dilution, water requirements and frost protection.'),('Mixing and supersession','Do not infer mixing or replacement of an older product from its trade name. Manufacturer evidence for the circuit is required.'),('Safe checking and topping up','Never open a hot circuit. With unknown coolant, repeated loss or a warning, find the cause first; distinguish separate hybrid and EV circuits.')],
   [('Selecting the correct service plan','Identify brand, model and generation, model year, engine or powertrain, transmission and, where necessary, VIN, unit codes and PR codes.'),('Inspections and oil service','Treat inspections, oil service and individual operations separately. Fixed and flexible regimes have different conditions.'),('Filters, plugs, timing and auxiliary drives','First and subsequent due dates and time/mileage conditions must come from the matching service plan.'),('Transmission, all-wheel drive, brakes and fluids','There is no universal DSG, automatic-transmission or 4×4 interval. The exact design, serviced circuit, fluid and filter determine the requirement.'),('Equipment-specific maintenance','Distinguish inspection, topping up, scheduled replacement and condition-based replacement. Manufacturer requirements and J&S SERVIS preventive advice must be separate.')]
  ]},
 'de':{
  'page':'Fahrertipps','intro':'Praktische Hinweise zur richtigen Reaktion auf Fahrzeugmeldungen und zur Kontrolle grundlegender Betriebsangaben. Konkrete Werte immer für Modell, Modelljahr, Ausstattung und Antrieb prüfen.',
  'titles':['Identifikation meines Fahrzeugs – VIN','Anmeldung und Online-Fahrzeugdienste','Kontrollleuchten und Warnmeldungen','Sicherungen – Farben und Werte','Reifendruck','Öle – Viskosität und Spezifikationen','Kühlmittel','Service und Wartungsintervalle'],
  'topics':[
   [],[],[],
   [('Kfz-Sicherungstypen','Vor der Ersatzwahl die Bauform bestimmen. Gleiche Farben in verschiedenen Sicherungsfamilien belegen nicht dieselbe Ausführung.'),('Farbcodierung und Amperewerte','Farbe und Amperewert nur anhand der Tabelle für den jeweiligen Sicherungstyp verwenden. Sicherungskastenbelegung und Verbraucherzuordnung sind nicht Bestandteil.'),('Passende Sicherung bestimmen','Maßgeblich sind die konkrete Fahrzeuganleitung, die Position im richtigen Sicherungskasten, Bauform und vorgeschriebener Amperewert.'),('Sicher ersetzen','Betroffenen Verbraucher und Zündung nach Anleitung ausschalten. Nur gleichen Typ und Wert einsetzen; wiederholtes Auslösen erfordert Diagnose.')],
   [('Reifendruckschild finden','Der Einbauort muss für Modell und Generation belegt sein: Türsäule oder -rahmen, Innenseite der Tankklappe oder ein anderer in der Anleitung genannter Ort. Modellgeprüfte Fotos und lesbare Schilddetails sind noch nicht veröffentlicht.'),('Richtige Werte lesen','Reifengröße und Beladungszustand auf dem Schild abgleichen. Normal-/Volllast- sowie Vorder-/Hinterachswerte nicht vertauschen.'),('Druck prüfen und korrigieren','Kalte Reifen unter den Herstellerbedingungen prüfen. Zuerst den tatsächlichen Druck messen und korrigieren; bloßes Löschen der Warnung ist nicht das Ziel.'),('System speichern oder einstellen','Infotainment-Speicherung, SET-Taste oder andere Verfahren nur dem passenden Modell und System zuordnen. Nach der Korrektur die Fahrzeuganleitung befolgen.')],
   [('Motoröle und SAE','SAE beschreibt die Viskositätsklasse, nicht allein die Herstellerfreigabe oder Motoreignung.'),('Volkswagen-Group-Freigaben','Die genaue Freigabe für Motor und Serviceregime verwenden. Gleiche Viskosität beweist keine Austauschbarkeit.'),('Auswahl, Füllstand und Nachfüllen','Konkreten Motor, Serviceregime und Anleitung beachten. Füllstand vorgeschrieben prüfen und nicht überfüllen.'),('Mischen und Notnachfüllen','Mischung oder Notnachfüllung muss für die Spezifikation ausdrücklich belegt sein; ein ähnlicher Produktname genügt nicht.'),('Getriebe- und weitere Öle','Schaltgetriebe, DSG, andere Automatikgetriebe, Verteilergetriebe, Differentiale und Allradkupplungen getrennt nach genauer Konstruktion beurteilen.')],
   [('Herstellerbezeichnung und Spezifikation','Farbe ist kein ausreichendes Auswahlkriterium. Maßgeblich ist die Spezifikation für Fahrzeug und Kühlkreis.'),('Konzentrat, Fertigmischung und Verdünnung','Konzentrat und Fertigmischung unterscheiden. Verdünnung, Wasseranforderung und Frostschutz aus der Anleitung übernehmen.'),('Mischbarkeit und Ersatz','Mischbarkeit oder Ersatz älterer Produkte nicht aus dem Handelsnamen ableiten. Herstellerbeleg für den Kreis ist erforderlich.'),('Sicher prüfen und nachfüllen','Heißen Kreis nie öffnen. Bei unbekannter Füllung, wiederholtem Verlust oder Warnung zuerst Ursache klären; Hybrid-/EV-Kreise unterscheiden.')],
   [('Passenden Wartungsplan wählen','Marke, Modell und Generation, Modelljahr, Motor/Antrieb, Getriebe sowie bei Bedarf VIN, Aggregat- und PR-Codes bestimmen.'),('Inspektion und Ölservice','Inspektion, Ölservice und Einzelarbeiten getrennt behandeln. Feste und flexible Regime haben unterschiedliche Bedingungen.'),('Filter, Kerzen, Steuer- und Nebenantriebe','Erste und folgende Termine sowie Zeit-/Kilometerbedingungen müssen aus dem passenden Wartungsplan stammen.'),('Getriebe, Allrad, Bremsen und Flüssigkeiten','Kein universelles DSG-, Automatik- oder 4×4-Intervall. Konstruktion, gewarteter Kreis, Öl und Filter entscheiden.'),('Ausstattungsspezifische Wartung','Prüfung, Ergänzung, regelmäßigen und zustandsabhängigen Wechsel unterscheiden. Herstellervorgabe und J&S-Prävention getrennt ausweisen.')]
  ]}
}

def main(lang,page):
 u=UI[lang];d=DRIVER_TOPICS[lang]
 intro={'cs':'Vyberte značku svého vozu a téma, které vás zajímá.','en':'Select your vehicle brand and the topic you are interested in.','de':'Wählen Sie Ihre Fahrzeugmarke und das gewünschte Thema.'}[lang]
 out=f'<main id="warning-lights" class="warning-lights driver-advice" lang="{lang}"><p class="driver-selection-intro">{esc(intro)}</p>{brand_selector_content(lang)}<section id="brand-advice" class="brand-advice" hidden aria-labelledby="brand-advice-title"><h2 id="brand-advice-title" tabindex="-1"></h2><div class="driver-topics" aria-label="{esc(d["page"])}">'
 for index,title in enumerate(d['titles']):
  topic_id=['identifikace-vozu-vin','prihlaseni-online-sluzby','kontrolky','pojistky','tlak-pneumatik','oleje','chladici-kapaliny','servisni-intervaly'][index]
  if index==0:topic_title=f'<span class="driver-topic-title"><span class="driver-vin-icon" aria-hidden="true">VIN</span>{esc(title)}</span>'
  elif index==1:topic_title=f'<span class="driver-topic-title"><span class="driver-profile-icon" aria-hidden="true"></span>{esc(title)}</span>'
  else:topic_title=f'<span>{esc(title)}</span>'
  out+=f'<details class="driver-topic" id="{topic_id}"><summary>{topic_title}<span class="driver-topic-arrow" aria-hidden="true"></span></summary><div class="driver-topic-body">'
  if index==0:out+=vin_content(lang)
  elif index==1:out+=online_services_content(lang)
  elif index==2:out+=warning_content(lang,page)
  else:
   if topic_id=='pojistky':
    out+=fuse_safety_content(lang)+'<div class="fuse-overview-layout"><div class="fuse-overview-copy">'
    for heading,text in d['topics'][index]:out+=f'<section class="driver-subtopic"><h2>{esc(heading)}</h2><p>{esc(text)}</p></section>'
    out+='</div>'+fuse_colour_content(lang)+'</div>'
   else:
    for heading,text in d['topics'][index]:out+=f'<section class="driver-subtopic"><h2>{esc(heading)}</h2><p>{esc(text)}</p></section>'
  out+='</div></details>'
 out+='</div></section></main>'
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
 advice={'cs':'Rady pro řidiče','en':'Driver advice','de':'Fahrertipps'}[lang]
 s=re.sub(r'(<html\b[^>]*\blang=["\'])[^"\']+',r'\g<1>'+lang,s,count=1)
 s=re.sub(r'<main id="warning-lights".*?</main>',lambda m:main(lang,page),s,count=1,flags=re.S)
 s=re.sub(r'<nav class="language-switcher".*?</nav>',lambda m:switcher(lang,page),s,count=1,flags=re.S)
 s=re.sub(r'<title>.*?</title>','<title>'+esc(advice)+' | J&amp;S SERVIS</title>',s,count=1,flags=re.S)
 s=re.sub(r'<meta\b[^>]*(?:name=["\'](?:description|robots)["\']|property=["\'](?:og:title|og:description|og:url|og:locale|article:modified_time)["\'])[^>]*>','',s,flags=re.I)
 s=re.sub(r'<link\b[^>]*(?:rel=["\']canonical["\']|hreflang=)[^>]*>','',s,flags=re.I)
 s=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>','',s,flags=re.S)
 s=re.sub(r'(<h1 class="title-header">).*?(</h1>)',lambda m:m[1]+esc(advice.upper())+m[2],s,count=1,flags=re.S)
 crumb=f'<ul class="breadcrumb breadcrumb__t"><li><a href="{rel(prefix or ".",page)}">{esc(u["home"])}</a></li><li class="divider"></li><li class="active" aria-current="page">{esc(advice)}</li></ul>'
 s=re.sub(r'<ul class="breadcrumb breadcrumb__t">.*?</ul>',lambda m:crumb,s,count=1,flags=re.S)
 # The catalogue belongs only to the separate Driver advice header entry.
 # Clear stale service-menu ancestry inherited from the source template and
 # mark the real catalogue entry as current for assistive technology and CSS.
 s=re.sub(r'(<li id="menu-item-2076" class=")[^"]*(")',r'\1menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children\2',s,count=1)
 s=re.sub(r'<a class="header-driver-advice(?: is-current)?"(?: aria-current="page")?([^>]*)>',r'<a class="header-driver-advice is-current" aria-current="page"\1>',s,count=1)
 s=re.sub(r'(warning-lights\.(?:css|js)\?v=)[^"\']+',r'\g<1>'+VERSION,s)
 s=re.sub(r'(jasservis\.css\?v=)[^"\']+',r'\g<1>20261031-tile-outline-v1',s)
 meta=f'<meta name="robots" content="noindex, nofollow" /><meta name="description" content="{esc(DRIVER_TOPICS[lang]["intro"])}" /><link rel="canonical" href="{url}" /><meta property="og:title" content="{esc(advice)} | J&amp;S SERVIS" /><meta property="og:description" content="{esc(DRIVER_TOPICS[lang]["intro"])}" /><meta property="og:url" content="{url}" /><meta property="og:locale" content="'+{'cs':'cs_CZ','en':'en_GB','de':'de_DE'}[lang]+'" />'
 for l in LANGS:meta+=f'<link rel="alternate" hreflang="{l}" href="https://jasservis.cz/{locale_root(l)}{ROUTE}/" />'
 meta+=f'<link rel="alternate" hreflang="x-default" href="https://jasservis.cz/{ROUTE}/" />'
 schema={'@context':'https://schema.org','@graph':[{'@type':'WebPage','url':url,'name':advice,'inLanguage':lang,'description':DRIVER_TOPICS[lang]['intro']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':u['home'],'item':'https://jasservis.cz/'+prefix},{'@type':'ListItem','position':2,'name':advice,'item':url}]}]}
 meta+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
 s=s.replace('</head>',meta+'</head>');s=re.sub(r'(?m)^[ \t]+$','',s);return page,s

def second_review_page(lang,page):
 a=json.loads((HERE/'attachment-groups.json').read_text());d=json.loads((HERE/'terramar-1125-overview-review.json').read_text());u=UI[lang]
 t={'cs':['Podklady pro nezávislou obsahovou kontrolu','Přehled je rozpracovaný. Úplnost není potvrzená pro celý model, značku ani koncern.','Oddělené skupiny fotografií','Dostupné fotografie','Požadovaný počet','Dokončená revize a přesné mezery','Úplný export textů CZ/EN/DE a použitých sdílených symbolů','Samostatné texty','Použité symboly a licence','Terramar EN 11.25, 578012720AC — celý přehled tištěných stran 11–15 (samostatný zdroj)','Toto samostatné anglické vydání bylo nezávisle zkontrolováno. České úplné vydání 578012715AC a český README 578012815AC jsou evidovány odděleně; README je stručný dokument a nenahrazuje úplný návod.','110 významových buněk není 110 unikátních symbolů. Přehled byl porovnán celý; ne všechny odkazované pokyny a grafiky jsou dokončené.','Řádek a zdroj','Původní popisek EN','Ověření pokynů a barvy','Skutečný stav na webu','Pokyny porovnané','Navazující pokyny nedokončené','Barva displeje nedoložená; neutrální tisk není černá výstraha','V katalogu pro dané vydání','Chybí v katalogu / nedokončené','Porovnání šesti fotografií Terramaru, včetně přesných poloh','Nejasné symboly se neurčují odhadem. Nové fotografie CUPRA a fotografie Audi nejsou nahrazené snímky jiného návodu.'],
 'en':['Materials for independent content review','The overview is in progress. Completeness is not confirmed for a whole model, brand or group.','Separate photograph groups','Available photos','Requested count','Completed comparisons and exact gaps','Full CZ/EN/DE text and shared-symbol export','Separate text files','Used symbols and licences','Terramar EN 11.25, 578012720AC — complete overview on printed pages 11–15 (separate source)','This separate English edition was independently reviewed. The Czech complete edition 578012715AC and Czech README 578012815AC are recorded separately; the README is a condensed document and does not replace the complete manual.','110 meaning cells are not 110 unique symbols. The entire overview was compared; not all referenced instructions and graphics are complete.','Row and source','Original EN caption','Instruction and colour verification','Actual website status','Instructions compared','Referenced instructions unfinished','Display colour unproven; neutral print is not a black warning','In catalogue for this edition','Missing from catalogue / unfinished','Six Terramar photo comparison, including exact positions','Unclear symbols are not guessed. New CUPRA and Audi photographs are not replaced by images of another manual.'],
 'de':['Unterlagen zur unabhängigen Inhaltsprüfung','Die Übersicht ist in Bearbeitung. Vollständigkeit für ein ganzes Modell, eine Marke oder den Konzern ist nicht bestätigt.','Getrennte Fotogruppen','Verfügbare Fotos','Angeforderte Anzahl','Abgeschlossene Vergleiche und genaue Lücken','Vollständiger CZ/EN/DE-Text- und gemeinsamer Symbolexport','Einzelne Textdateien','Verwendete Symbole und Lizenzen','Terramar EN 11.25, 578012720AC — vollständige Übersicht auf den gedruckten Seiten 11–15 (getrennte Quelle)','Diese getrennte englische Ausgabe wurde unabhängig geprüft. Die vollständige tschechische Ausgabe 578012715AC und der tschechische README 578012815AC werden getrennt geführt; der README ist ein Kurzband und ersetzt nicht die vollständige Anleitung.','110 Bedeutungszellen sind nicht 110 einzigartige Symbole. Ganze Übersicht verglichen; nicht alle Folgeanweisungen und Grafiken abgeschlossen.','Zeile und Quelle','Originalbeschriftung EN','Anweisungs-/Farbprüfung','Tatsächlicher Webstand','Anweisungen verglichen','Folgeanweisungen offen','Anzeigefarbe nicht belegt; neutraler Druck ist keine schwarze Warnung','Im Katalog für diese Ausgabe','Fehlt im Katalog / offen','Sechs Terramar-Fotos verglichen, einschließlich genauer Positionen','Unklare Symbole nicht erraten. Neue CUPRA- und Audi-Fotos nicht durch Bilder anderer Anleitung ersetzt.']}[lang]
 style='body{font:18px/1.6 system-ui,sans-serif;color:#222;max-width:1440px;padding:20px;margin:auto;overflow-wrap:anywhere}h1,h2{line-height:1.3}a{color:#111}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #999;padding:10px;text-align:left;vertical-align:top}section{margin-block:28px}a:focus-visible{outline:3px solid #df5300;outline-offset:3px}@media(max-width:900px){table,tbody,tr,td{display:block}thead{display:none}td:before{content:attr(data-label)+": ";font-weight:600}tr{margin-bottom:16px}}'
 out='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+esc(t[0])+' | J&amp;S SERVIS</title><style>'+style+'</style></head><body><a href="./#prehled-kontrolek">'+esc(u['overview'])+'</a> · <a href="revize-kapitol.html#pracovni-fronty">'+t[5]+'</a><h1>'+t[0]+'</h1><p><strong>'+t[1]+'</strong></p><nav>'
 for l in LANGS:out+='<a lang="'+l+'" href="'+rel(locale_root(l)+ROUTE+'/druha-kontrola.html',page)+'">'+l.upper()+'</a> '
 out+='</nav><section id="export"><h2>'+t[6]+'</h2><p><a href="'+rel('_warnings/catalog-review-export.zip',page)+'">ZIP</a></p><p>'+t[7]+': '
 for l in LANGS:out+='<a href="'+rel('_warnings/catalog-texts.'+l+'.csv',page)+'">'+l.upper()+' CSV</a> '
 out+='</p><p><a href="'+rel('_warnings/used-symbols.csv',page)+'">'+t[8]+'</a></p></section>'
 source_reviews=[
  ('terramar-cs-2025-11-review.json',{'cs':'Terramar CS 11.25 — úplný návod a samostatný README','en':'Terramar CS 11.25 — complete manual and separate README','de':'Terramar CS 11.25 — vollständige Anleitung und getrennter README'}[lang]),
  ('tarraco-de-2023-06-2024-01-review.json',{'cs':'Tarraco DE — základ 06.2023 a samostatný dodatek 01.2024','en':'Tarraco DE — 06.2023 base and separate 01.2024 supplement','de':'Tarraco DE — Grundanleitung 06.2023 und getrennter Zusatz 01.2024'}[lang]),
  ('vw-warning-pages-review.json',{'cs':'Volkswagen UK — obecné stránky kontrolek','en':'Volkswagen UK — general warning-light pages','de':'Volkswagen UK — allgemeine Kontrollleuchten-Seiten'}[lang]),
  ('vw-model-lane-review.json',{'cs':'Volkswagen — modelové návody Lane Assist','en':'Volkswagen — model-specific Lane Assist manuals','de':'Volkswagen — modellspezifische Lane-Assist-Anleitungen'}[lang]),
  ('audi-source-access-review.json',{'cs':'Audi — přesný stav přístupu k evropským návodům','en':'Audi — exact European-manual access status','de':'Audi — genauer Zugriffsstand europäischer Anleitungen'}[lang]),
 ]
 source_note={'cs':'Dokumenty Terramar full/README a Tarraco základ/dodatek jsou vedené samostatně. Obecné stránky Volkswagen nenahrazují modelové návody. U Audi byly při dokončeném testu /home/ a /web/config dostupné (HTTP 200); HTTP 403 je doloženo pouze pro /web/models/.','en':'Terramar full/README and Tarraco base/supplement are recorded separately. General Volkswagen pages do not replace model-specific manuals. In the completed Audi test, /home/ and /web/config were available (HTTP 200); HTTP 403 is documented only for /web/models/.','de':'Terramar-Vollanleitung/README und Tarraco-Grundanleitung/Zusatz werden getrennt geführt. Allgemeine Volkswagen-Seiten ersetzen keine modellspezifischen Anleitungen. Beim abgeschlossenen Audi-Test waren /home/ und /web/config verfügbar (HTTP 200); HTTP 403 ist nur für /web/models/ belegt.'}[lang]
 out+='<section id="revize-zdroju"><h2>'+{'cs':'Nové přesně vymezené revize zdrojů','en':'New precisely bounded source reviews','de':'Neue genau abgegrenzte Quellenprüfungen'}[lang]+'</h2><p>'+source_note+'</p><ul>'+''.join('<li><a href="'+rel('_warnings/'+name,page)+'">'+esc(label)+'</a></li>'for name,label in source_reviews)+'</ul></section><section id="prilohy"><h2>'+t[2]+'</h2><p>'+t[22]+'</p>'
 for g in a['groups']:out+='<h3>'+esc(g['id'])+'</h3><p>'+t[3]+': '+str(g['available_in_conversation'])+' / '+t[4]+': '+str(g['expected'])+'</p><p>'+esc(g['status'][lang])+'</p>'
 out+='<p><a href="'+rel('_warnings/attachment-groups.json',page)+'">JSON</a></p></section><section id="fotografie"><h2>'+t[21]+'</h2><p><a href="'+rel('_warnings/all-terramar-photo-occurrences.'+lang+'.csv',page)+'">CSV</a> · <a href="revize.html#fotografie-terramar">'+esc(u['auditLink'])+'</a></p></section><section id="terramar"><h2>'+t[9]+'</h2><p>'+t[10]+'</p><p><strong>'+t[11]+'</strong></p><p><a href="'+rel('_warnings/terramar-1125-overview-review.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/terramar-1125-overview-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in t[12:16])+'</tr></thead><tbody>'
 for r in d['rows']:
  status=(t[16]if r['referenced_instruction_reviewed']else t[17])+'; '+(str(r['actual_display_colour'])if r['actual_display_colour_verified']else t[18]);links=[]
  for id in r['catalogue_entries']:
   item=next(i for i in CAT['items']if i['id']==id);links.append('<a href="./?znacka=cupra#'+esc(item_anchor(item,'cupra'))+'">'+esc(item['name'][lang])+'</a>')
  vals=['<a href="'+esc(r['source_url'])+'">'+esc(r['row_id'])+' · '+str(r['printed_page'])+'</a>',esc(r['source_label']),esc(status),('<strong>'+t[19]+'</strong><br>'+'<br>'.join(links)if links else'<strong>'+t[20]+'</strong>')+'<p>'+esc(r['remaining'][lang])+'</p>']
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+v+'</td>'for label,v in zip(t[12:16],vals))+'</tr>'
 out+='</tbody></table></section>'
 photo_labels={'cs':['Řádek','Doslovný popisek fotografie','Barva a stav','Porovnání s katalogem','Vloženo z této fotografické sady','Ano','Ne','Kandidáti v katalogu'],'en':['Row','Literal photo caption','Colour and state','Catalogue comparison','Added from this photo set','Yes','No','Catalogue candidates'],'de':['Zeile','Wörtliche Fotobeschriftung','Farbe und Zustand','Katalogvergleich','Aus diesem Fotosatz ergänzt','Ja','Nein','Katalogkandidaten']}[lang]
 photo_states={'cs':{'generic':'Způsob svícení nebo blikání není v tomto řádku výslovně uveden.','steady':'Svítí.','flashing':'Bliká.','four':'Svítí čtyři sekundy a následně bliká.'},'en':{'generic':'This row does not explicitly state whether the symbol is steady or flashing.','steady':'Steady.','flashing':'Flashing.','four':'Lit for four seconds, then flashes.'},'de':{'generic':'Diese Zeile nennt nicht ausdrücklich, ob das Symbol leuchtet oder blinkt.','steady':'Leuchtet.','flashing':'Blinkt.','four':'Leuchtet vier Sekunden und blinkt anschließend.'}}[lang]
 enyaq_photo=json.loads((HERE/'enyaq-photo-review.json').read_text())
 out+='<section id="enyaq"><h2>'+{'cs':'Škoda Enyaq — fotografovaný přehled stran 12–17','en':'Škoda Enyaq — photographed overview pp. 12–17','de':'Škoda Enyaq — fotografierte Übersicht S. 12–17'}[lang]+'</h2><p>'+{'cs':'Deset přijatých fotografií pokrývá všech šest unikátních stran 12–17. Překryvy a náhradní záběry nejsou nové řádky. Všech 122 čitelných významových stavů je přepsáno a porovnáno. Z 69 řádků označených jako chybějící vychází 59 redakčních tvarů a 64 kombinací tvaru s barvou; nejde o 69 SVG. U žádného řádku není z fotografie ověřena přesná znovupoužitelná grafika. Vydání, modelový rok a generace fotografované knihy nejsou doložené. Samostatné české a německé návody 11.2020 ji neidentifikují.','en':'Ten received photos cover all six unique pages 12–17. Overlaps and replacement views are not new rows. All 122 readable semantic states are transcribed and compared. The 69 rows classified as missing contain 59 editorial shapes and 64 shape/colour combinations; they are not 69 SVGs. No exact reusable graphic is verified from the photographs. The photographed book’s edition, model year and generation are undocumented. The separate Czech and German 11.2020 manuals do not identify it.','de':'Zehn empfangene Fotos decken alle sechs eindeutigen Seiten 12–17 ab. Überlappungen und Ersatzaufnahmen sind keine neuen Zeilen. Alle 122 lesbaren Bedeutungszustände sind transkribiert und verglichen. Die 69 als fehlend eingestuften Zeilen enthalten 59 redaktionelle Formen und 64 Form-Farb-Kombinationen; es sind keine 69 SVG-Dateien. Aus den Fotos ist keine genaue wiederverwendbare Grafik belegt. Ausgabe, Modelljahr und Generation des fotografierten Buchs sind unbelegt. Die getrennten tschechischen und deutschen Anleitungen 11.2020 identifizieren es nicht.'}[lang]+'</p><p><a href="'+rel('_warnings/enyaq-photo-review.'+lang+'.csv',page)+'">'+{'cs':'Řádkové porovnání','en':'Row comparison','de':'Zeilenvergleich'}[lang]+' CSV</a> · <a href="'+rel('_warnings/enyaq-photo-review.json',page)+'">JSON</a> · <a href="'+rel('_warnings/enyaq-requested-photo-status.'+lang+'.csv',page)+'">'+{'cs':'Inventář fotografií','en':'Photo inventory','de':'Fotoinventar'}[lang]+' CSV</a> · <a href="'+rel('_warnings/enyaq-independent-review.'+lang+'.csv',page)+'">'+{'cs':'Samostatná revize DE 11.2020','en':'Separate DE 11.2020 review','de':'Getrennte Prüfung DE 11.2020'}[lang]+' CSV</a> · <a href="'+rel('_warnings/enyaq-cs-2020-11-review.json',page)+'">'+{'cs':'Samostatná revize CS 11.2020','en':'Separate CS 11.2020 review','de':'Getrennte Prüfung CS 11.2020'}[lang]+'</a></p><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>'for x in photo_labels[:5])+'</tr></thead><tbody>'
 for r in enyaq_photo['rows']:
  candidates=[]
  for id in r['candidate_catalogue_ids']:
   item=next((i for i in CAT['items']if i['id']==id),None)
   if item:candidates.append(candidate_link(item,'skoda',lang))
  comparison=esc(r['catalogue_result_text'][lang])
  if candidates:comparison+='<br>'+esc(photo_labels[7])+': '+'<br>'.join(candidates)
  source_state=r['source_state_text_cs'];state_key='steady'if source_state=='Svítí.'else'flashing'if source_state=='Bliká.'else'four'if source_state.startswith('Svítí čtyři')else'generic'
  vals=[esc(r['id'])+' · p'+str(r['printed_page'])+' · '+esc(r['column'])+str(r['row_from_top']),esc(r['source_caption_cs']),esc(r['photo_colour'])+' · '+esc(photo_states[state_key]),comparison,photo_labels[5]if r['actually_added_from_this_photo_set']else photo_labels[6]]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(photo_labels[:5],vals))+'</tr>'
 out+='</tbody></table></section>'
 multivan_photo=json.loads((HERE/'multivan-photo-review.json').read_text())
 multivan_results={'cs':{'chybí modelově doložená položka':'Chybí modelově doložená položka Multivanu; případný kandidát je pouze významově podobný.','neověřeno':'Přesná drobná grafika není z fotografie bezpečně čitelná.'},'en':{'chybí modelově doložená položka':'A model-documented Multivan item is missing; any candidate is only semantically similar.','neověřeno':'The exact small graphic cannot be read safely from the photo.'},'de':{'chybí modelově doložená položka':'Ein modellbelegter Multivan-Eintrag fehlt; ein Kandidat ist nur bedeutungsähnlich.','neověřeno':'Die genaue kleine Grafik ist auf dem Foto nicht sicher lesbar.'}}[lang]
 out+='<section id="multivan"><h2>'+{'cs':'Volkswagen Užitkové vozy — Multivan, fotografovaný přehled stran16–19','en':'Volkswagen Commercial Vehicles — Multivan, photographed overview pp16–19','de':'Volkswagen Nutzfahrzeuge — Multivan, fotografierte Übersicht S16–19'}[lang]+'</h2><p>'+{'cs':'Pět přijatých fotografií pokrývá čtyři unikátní strany16–19; čitelnější strana16 nahrazuje starší záběr. Všech129 čitelných významových řádků je přepsáno. Třicet sedm má pouze obdobného kandidáta,92 nemá kandidáta a pět drobných grafik je nejasných. Žádná současná položka nemá doložený rozsah Multivan a nic nebylo převzato z Caddy. Vydání, generace a modelový rok nejsou doložené.','en':'Five received photos cover four unique pages16–19; the clearer page16 replaces the earlier view. All129 readable semantic rows are transcribed. Thirty-seven only have a similar candidate,92 have no candidate and five small graphics are unclear. No current item has documented Multivan scope and nothing was inherited from Caddy. Edition, generation and model year are undocumented.','de':'Fünf empfangene Fotos decken vier eindeutige Seiten16–19 ab; die klarere Seite16 ersetzt die frühere Aufnahme. Alle129 lesbaren Bedeutungszeilen sind transkribiert. Siebenunddreißig haben nur einen ähnlichen Kandidaten,92 keinen Kandidaten und fünf kleine Grafiken sind unklar. Kein aktueller Eintrag hat belegten Multivan-Umfang; nichts wurde vom Caddy übernommen. Ausgabe, Generation und Modelljahr sind unbelegt.'}[lang]+'</p><p><a href="'+rel('_warnings/multivan-photo-review.'+lang+'.csv',page)+'">'+{'cs':'Řádkové porovnání','en':'Row comparison','de':'Zeilenvergleich'}[lang]+' CSV</a> · <a href="'+rel('_warnings/multivan-photo-review.json',page)+'">JSON</a> · <a href="'+rel('_warnings/multivan-requested-photo-status.'+lang+'.csv',page)+'">'+{'cs':'Inventář fotografií','en':'Photo inventory','de':'Fotoinventar'}[lang]+' CSV</a></p><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>'for x in photo_labels[:5])+'</tr></thead><tbody>'
 for r in multivan_photo['rows']:
  candidates=[]
  for id in r['candidate_catalogue_ids_not_model_verified']:
   item=next((i for i in CAT['items']if i['id']==id),None)
   if item:candidates.append(esc(item['name'][lang])+' <code>'+esc(id)+'</code>')
  comparison=esc(multivan_results[r['catalogue_result']])
  if candidates:comparison+='<br>'+esc(photo_labels[7])+': '+'<br>'.join(candidates)
  source_state=r['source_state_text'];state_key='steady'if source_state=='Svítí.'else'flashing'if source_state=='Bliká.'else'generic'
  vals=[esc(r['id'])+' · p'+str(r['printed_page'])+' · '+esc(r['column'])+str(r['row_from_top']),esc(r['source_caption_cs']),esc(r['photo_colour'])+' · '+esc(photo_states[state_key]),comparison,photo_labels[6]]
  out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(photo_labels[:5],vals))+'</tr>'
 out+='</tbody></table></section>'
 audi_path=HERE/'audi-photo-review.json'
 if audi_path.exists():
  audi=json.loads(audi_path.read_text())
  al={'cs':['Audi — pět fotografií přístrojového štítu a MMI, model nedoložen','Fotografie a poloha','Viditelný text / symbol','Typ a stav','Porovnání s katalogem','Kandidátní manuálová reference','Význam ověřen','Přesná použitelná grafika ověřena','Vloženo z fotografií','Model, generace, modelový rok a vydání návodu nejsou doložené. Kandidátní manuál slouží jen ke kontrole obdobné funkce a neurčuje model fotografovaného vozu. Dojezd 50 km je hodnota zobrazená na fotografii, nikoli ověřený univerzální práh.','Ano','Ne','Bez modelově doložené shody','Kandidáti','Tištěné strany','Bez kandidátního návodu – zdrojem ověřeného významu je čitelný text nebo grafika fotografie.'],
      'en':['Audi — five instrument-cluster and MMI photos, model undocumented','Photo and position','Visible text / symbol','Type and state','Catalogue comparison','Candidate manual reference','Meaning verified','Exact reusable graphic verified','Added from the photos','Model, generation, model year and manual edition are undocumented. A candidate manual is used only to check a corresponding function and does not identify the photographed vehicle model. The displayed 50 km range is an observed value, not a verified universal threshold.','Yes','No','No model-documented match','Candidates','Printed pages','No candidate manual – the verified meaning comes from readable text or graphics in the photo.'],
      'de':['Audi — fünf Fotos von Kombiinstrument und MMI, Modell unbelegt','Foto und Position','Sichtbarer Text / Symbol','Typ und Zustand','Katalogvergleich','Kandidaten-Anleitungsreferenz','Bedeutung geprüft','Genaue nutzbare Grafik geprüft','Aus den Fotos ergänzt','Modell, Generation, Modelljahr und Anleitungsausgabe sind unbelegt. Eine Kandidaten-Anleitung dient nur zur Prüfung einer entsprechenden Funktion und identifiziert nicht das fotografierte Fahrzeugmodell. Die angezeigten 50 km sind ein beobachteter Wert, keine geprüfte allgemeine Schwelle.','Ja','Nein','Keine modellbelegte Übereinstimmung','Kandidaten','Gedruckte Seiten','Keine Kandidaten-Anleitung – die geprüfte Bedeutung stammt aus lesbarem Text oder Grafik des Fotos.']}[lang]
  out+='<section id="audi-fotografie"><h2>'+al[0]+'</h2><p>'+al[9]+'</p><p><a href="'+rel('_warnings/audi-photo-comparison.'+lang+'.csv',page)+'">'+{'cs':'Položkové porovnání','en':'Item comparison','de':'Einzelvergleich'}[lang]+' CSV</a> · <a href="'+rel('_warnings/audi-photo-inventory.'+lang+'.csv',page)+'">'+{'cs':'Inventář fotografií','en':'Photo inventory','de':'Fotoinventar'}[lang]+' CSV</a> · <a href="'+rel('_warnings/audi-photo-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>'for x in al[1:9])+'</tr></thead><tbody>'
  for row in audi.get('observations',[]):
   occurrences=audi_photo_occurrences(row)
   place='<br>'.join(esc(str(x.get('photo','')))+(': '+esc(localized(x.get('position'),lang))if x.get('position')else'')for x in occurrences)or'—'
   candidates=[str(x)for x in audi_photo_candidates(row)]
   matching=row.get('matching_model_scoped_catalogue_ids',[])or[]
   comparison=esc(localized(row.get('catalogue_result_text'),lang))or(al[12] if not matching else ', '.join(map(esc,matching)))
   if candidates:comparison+='<br>'+al[13]+': '+', '.join('<code>'+esc(x)+'</code>'for x in candidates)
   references=audi_manual_references(row,lang);reference_html=[]
   for reference in references:
    title=esc(reference['manual_id']+' · '+reference['edition']+' · '+reference['part_number']);pages=', '.join(map(str,reference['printed_pages']))
    reference_html.append(('<a href="'+esc(reference['url'])+'">'+title+'</a>'if reference['url']else title)+'<br>'+al[14]+': '+esc(pages)+'<br>'+esc(AUDI_MEANING_BASES['photo-plus-candidate-manual'][lang]))
   reference_text='<br><br>'.join(reference_html)or(al[15]if row.get('meaning_verification_basis')=='photo-visible-text-or-graphic'else esc(AUDI_MEANING_BASES['unresolved'][lang]))
   yes,no=al[10],al[11]
   vals=[place,esc(audi_photo_title(row,lang)),esc(audi_photo_classification(row,lang))+' · '+esc(audi_photo_colour(row,lang))+' · '+esc(audi_photo_state(row,lang)),comparison,reference_text,(yes if row.get('meaning_verified')else no)+'<br>'+esc(audi_meaning_basis(row,lang)),yes if row.get('exact_reusable_graphic_verified')else no,yes if row.get('published_from_this_photo_set')else no]
   out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(al[1:9],vals))+'</tr>'
  out+='</tbody></table></section>'
 audi_manual_path=HERE/'audi-manual-photo-review.json'
 if audi_manual_path.exists():
  audi_manual=json.loads(audi_manual_path.read_text());manual_rows=audi_manual.get('rows',[]);source=audi_manual_source(audi_manual)
  pages=', '.join(map(str,source.get('photographed_printed_pages',[])));missing=', '.join(map(str,source.get('missing_printed_pages',[])))
  graphic_occurrences=sum(audi_manual_graphic_occurrences(row)for row in manual_rows)
  ml={'cs':['Audi — fotografovaný český přehled stran 9–13, model a vydání nedoložené','Fotografie a řádek','Doslovný popisek CS','Odkázané tištěné strany','Grafický popis CS a barva ve zdroji','Významový výsledek','Grafický výsledek','Modelová platnost','Publikováno z fotografií','Řádkové porovnání','Inventář fotografií','Ano','Ne','Kandidáti v katalogu','Čekající kandidáti','Odmítnuté záměny'],
      'en':['Audi — photographed Czech overview pp9–13, model and edition undocumented','Photo and row','Literal CS caption','Referenced printed pages','Graphic description (CS) and source colour','Semantic result','Graphic result','Model scope','Published from the photos','Row comparison','Photo inventory','Yes','No','Catalogue candidates','Pending candidates','Rejected merges'],
      'de':['Audi — fotografierte tschechische Übersicht S9–13, Modell und Ausgabe unbelegt','Foto und Zeile','Wörtliche CS-Beschriftung','Verwiesene Druckseiten','Grafikbeschreibung (CS) und Quellfarbe','Bedeutungsergebnis','Grafikergebnis','Modellgültigkeit','Aus den Fotos veröffentlicht','Zeilenvergleich','Fotoinventar','Ja','Nein','Katalogkandidaten','Ausstehende Kandidaten','Verworfene Zusammenführungen']}[lang]
  summary={'cs':f'{source.get("photo_count",0)} přijaté fotografie pokrývají tištěné strany {pages}; strana {missing or "—"} chybí. Přepsáno je {len(manual_rows)} významových řádků a {graphic_occurrences} grafických výskytů. Značku Audi potvrzuje text viditelný v dokumentu. Model, generace, modelový rok, tiráž a vydání návodu nejsou doložené. Významový výsledek, grafika, modelová platnost a publikování jsou vedené odděleně.',
           'en':f'{source.get("photo_count",0)} received photographs cover printed pages {pages}; page {missing or "—"} is missing. The evidence contains {len(manual_rows)} semantic rows and {graphic_occurrences} graphic occurrences. Text visible in the document confirms the Audi brand. Model, generation, model year, imprint and manual edition are undocumented. Semantic result, graphic result, model scope and publication are recorded separately.',
           'de':f'{source.get("photo_count",0)} empfangene Fotos decken die gedruckten Seiten {pages} ab; Seite {missing or "—"} fehlt. Erfasst sind {len(manual_rows)} Bedeutungszeilen und {graphic_occurrences} Grafikvorkommen. Im Dokument sichtbarer Text bestätigt die Marke Audi. Modell, Generation, Modelljahr, Impressum und Anleitungsausgabe sind unbelegt. Bedeutungsergebnis, Grafikergebnis, Modellgültigkeit und Veröffentlichung werden getrennt geführt.'}[lang]
  legend=localized(source.get('checkmark_legend'),lang)
  out+='<section id="audi-manual-fotografie"><h2>'+ml[0]+'</h2><p>'+esc(summary)+'</p><p><strong>✓:</strong> '+esc(legend)+'</p><p><a href="'+rel('_warnings/audi-manual-photo-review.'+lang+'.csv',page)+'">'+ml[9]+' CSV</a> · <a href="'+rel('_warnings/audi-manual-photo-inventory.'+lang+'.csv',page)+'">'+ml[10]+' CSV</a> · <a href="'+rel('_warnings/audi-manual-photo-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>'for x in ml[1:9])+'</tr></thead><tbody>'
  for row in manual_rows:
   candidates=[]
   for candidate_id in row.get('candidate_ids',[]):
    item=next((item for item in CAT['items']if item['id']==candidate_id),None)
    candidates.append((esc(item['name'][lang])+' 'if item else'')+'<code>'+esc(candidate_id)+'</code>')
   semantic=esc(AUDI_MANUAL_SEMANTIC_RESULTS[row['semantic_result']][lang])+'<br>'+esc(audi_manual_result(row,lang))
   if candidates:semantic+='<br>'+esc(ml[13])+': '+'<br>'.join(candidates)
   if row.get('pending_candidate_ids'):semantic+='<br>'+esc(ml[14])+': '+', '.join('<code>'+esc(x)+'</code>'for x in row['pending_candidate_ids'])
   if row.get('rejected_merge_candidate_ids'):semantic+='<br>'+esc(ml[15])+': '+', '.join('<code>'+esc(x)+'</code>'for x in row['rejected_merge_candidate_ids'])
   graphic='<br>'.join(esc(x.get('visual_description_cs',''))for x in row.get('graphic_occurrences',[]))
   graphic_text=graphic+'<br>'+str(audi_manual_graphic_occurrences(row))+'× · '+esc(audi_manual_colour(row,lang))
   yes,no=ml[11],ml[12]
   graphic_result=esc(AUDI_MANUAL_GRAPHIC_RESULTS[row['graphic_result']][lang])+'<br>'+({'cs':'Přesná použitelná grafika','en':'Exact reusable graphic','de':'Genaue nutzbare Grafik'}[lang])+': '+(yes if row.get('exact_reusable_graphic')else no)
   model_scope=esc(AUDI_MANUAL_MODEL_SCOPE_RESULTS[row['model_scope_result']][lang])
   references=', '.join(map(str,row.get('referenced_printed_pages',[])))or'—'
   position=esc(audi_manual_photo_id(row.get('printed_page')))+' · '+esc(str(row.get('id','')))+' · p'+esc(str(row.get('printed_page','')))+' · '+esc(audi_manual_column(row,lang))+' · '+esc(str(row.get('position_in_column','')))
   vals=[position,esc(row.get('description_cs_verbatim','')),esc(references),graphic_text,semantic,graphic_result,model_scope,yes if row.get('published')else no]
   out+='<tr>'+''.join('<td data-label="'+esc(label)+'">'+value+'</td>'for label,value in zip(ml[1:9],vals))+'</tr>'
  out+='</tbody></table></section>'
 out+='<section id="audi-q4-climate"><h2>'+{'cs':'Audi Q4 07.2024 — porovnání funkcí klimatizace','en':'Audi Q4 07.2024 — climate-function comparison','de':'Audi Q4 07.2024 — Vergleich der Klimafunktionen'}[lang]+'</h2><p><a href="'+rel('_warnings/q4-climate-function-review.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/q4-climate-function-review.json',page)+'">JSON</a></p></section><p><a href="revize-kapitol.html#pracovni-fronty">'+t[5]+'</a></p></body></html>';return out

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
   source=rel(r['source_file'],page)if r.get('source_file')else r['source_url']
   out+='<p>'+esc(r['remaining'][lang])+'</p><p><a href="'+esc(source)+'">'+labels[5]+'</a></p>'
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
    item=next(i for i in CAT['items']if i['id']==id);out+='<a href="./?znacka='+m['brand']+'#'+esc(item_anchor(item,m['brand']))+'">'+esc(item['name'][lang])+'</a> '
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
 t={'cs':['Položková revize návodů','Kompletně porovnané návody: žádné.','Tabulka rozlišuje ověření vybraných položek od dokončení celého návodu. Automatická inventura znaků textové vrstvy není vizuální kontrola ani důkaz úplnosti. Rastrové obrázky, kresby bez textového znaku a některé ovládací nápisy vyžadují další kontrolu.','Značka a model','Vydání','Přístrojový panel','Asistenti','Infotainment','Komfortní ovládání','Celý návod','Vybrané položky porovnané','Neporovnáno celé','Nedokončeno','Šest fotografií CUPRA Terramar','Bylo dodáno a vizuálně zkontrolováno všech šest fotografií: čtyři obrazovky Control Centra a dva odlišné snímky přístrojového panelu. Uživatel potvrdil datum výroby fotografovaného vozu 03/2026. Modelový rok a verze softwaru nejsou doložené; neověřené významy a grafiky nejsou doplněné odhadem.','Ovládací ikony Terramar MAX a REAR jsou samostatně porovnané podle návodů 09.24, strana 146, a 11.25, strana 148. To nenahrazuje kontrolu fotografií ani všech ostatních ovládacích ikon.','Nově doplněné významy','Zbývající konkrétní mezery','Úplná evidence JSON','Tabulka návodů CSV','Pracovní index zdrojových znaků CSV','Zdrojové kódy znaků nejsou univerzální identifikátory symbolů a nezakládají ověřený výklad. Neověřené kandidáty nepřidáváme do zákaznického přehledu.'],
 'en':['Item-by-item manual review','Completely compared manuals: none.','The table separates review of selected entries from completion of an entire manual. Automated text-layer character indexing is not visual review or proof of completeness. Raster images, outline-only drawings and some functional inscriptions require further review.','Brand and model','Edition','Instrument panel','Assistants','Infotainment','Comfort controls','Whole manual','Selected entries compared','Not fully compared','Incomplete','Six CUPRA Terramar photographs','All six photographs were supplied and visually reviewed: four Control Centre screens and two distinct instrument-cluster views. The user confirmed the photographed vehicle’s manufacture date as 03/2026. Its model year and software version are undocumented; unverified meanings and graphics are not guessed.','Terramar MAX and REAR controls are independently compared with manuals 09.24, page 146, and 11.25, page 148. This does not replace review of the photographs or all other control icons.','Newly added meanings','Specific remaining gaps','Full JSON register','Manual table CSV','Working source-character index CSV','Source character codes are not universal symbol identifiers and do not establish a verified interpretation. Unverified candidates are not added to the customer overview.'],
 'de':['Einzelprüfung der Anleitungen','Vollständig verglichene Anleitungen: keine.','Die Tabelle trennt ausgewählte geprüfte Einträge vom Abschluss einer ganzen Anleitung. Automatische Textzeichen-Inventur ist keine Sichtprüfung und kein Vollständigkeitsnachweis. Rasterbilder, reine Umrisszeichnungen und manche Bedienaufschriften benötigen weitere Prüfung.','Marke und Modell','Ausgabe','Kombiinstrument','Assistenten','Infotainment','Komfortbedienung','Ganze Anleitung','Ausgewählte Einträge verglichen','Nicht vollständig verglichen','Unvollständig','Sechs CUPRA-Terramar-Fotografien','Alle sechs Fotos wurden bereitgestellt und visuell geprüft: vier Control-Centre-Ansichten und zwei unterschiedliche Kombiinstrument-Aufnahmen. Der Nutzer bestätigte das Produktionsdatum des fotografierten Fahrzeugs mit 03/2026. Modelljahr und Softwarestand sind nicht belegt; ungeprüfte Bedeutungen und Grafiken werden nicht geraten.','Die Terramar-Bedienzeichen MAX und REAR sind unabhängig anhand der Anleitungen 09.24, Seite 146, und 11.25, Seite 148, verglichen. Das ersetzt weder die Fotoprüfung noch die Prüfung aller weiteren Bedienzeichen.','Neu ergänzte Bedeutungen','Konkrete verbleibende Lücken','Vollständige JSON-Dokumentation','Anleitungstabelle CSV','Arbeitsindex der Quellzeichen CSV','Quellzeichencodes sind keine universellen Symbolkennungen und belegen keine geprüfte Bedeutung. Ungeprüfte Kandidaten werden nicht in die Kundenübersicht übernommen.']}[lang]
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
 out+='<section id="fotografie-terramar"><h2>'+labels[0]+'</h2><p>'+esc(photos['important_limitations'][lang])+'</p><p>'+{'cs':'Ovládací zkratka, její funkce, přesná grafika a signalizační stav jsou kontrolovány odděleně. Chybějící grafika není nahrazena podobnou ikonou. Datum výroby fotografovaného vozu 03/2026 potvrdil uživatel. Rozsah návodu ani modelový rok z něj nejsou automaticky odvozeny.','en':'A control shortcut, its function, exact artwork and signalling state are checked separately. Missing artwork is not replaced with a similar icon. The user confirmed the photographed vehicle’s manufacture date as 03/2026. Manual applicability and model year are not inferred from that date.','de':'Bedienverknüpfung, Funktion, genaue Grafik und Signalzustand werden getrennt geprüft. Fehlende Grafiken werden nicht durch ähnliche Symbole ersetzt. Der Nutzer bestätigte das Produktionsdatum des fotografierten Fahrzeugs mit 03/2026. Anleitungsgültigkeit und Modelljahr werden daraus nicht abgeleitet.'}[lang]+'</p><p><a href="'+rel('_warnings/terramar-photo-comparison.'+lang+'.csv',page)+'">CSV</a> · <a href="'+rel('_warnings/terramar-photo-review.json',page)+'">JSON</a></p><table><thead><tr>'+''.join('<th>'+x+'</th>'for x in labels[1:7])+'</tr></thead><tbody>'
 for row in photos['observations']:
  if row.get('aggregate_only'):continue
  locations='<br>'.join(esc(x['photo'].rsplit('-',1)[1])+': '+esc(x['position'][lang])for x in row['occurrences'])
  links=[]
  for id in row['catalogue_entries']:
   it=next((i for i in CAT['items']if i['id']==id),None)
   if it and any(sc.get('manual')=='cupra-terramar-2026-11-25'for sc in it['scopes']):links.append('<a href="./?znacka=cupra#'+esc(item_anchor(it,'cupra'))+'">'+esc(it['name'][lang])+'</a>')
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
 statuses={'cs':{'selected-symbols-and-instructions-reviewed-not-complete':'Vybrané položky zkontrolované; celé vydání není hotové.','downloaded-not-yet-item-reviewed':'Staženo; kontrola všech symbolů nedokončená.','overview-reviewed-not-complete':'Stručný přehled zkontrolovaný; nejde o úplný návod.','complete-supplement-reviewed-base-link-not-proven':'Celý dodatek zkontrolovaný; výslovná vazba na konkrétní základní návod není doložená.'},'en':{'selected-symbols-and-instructions-reviewed-not-complete':'Selected entries checked; full edition not complete.','downloaded-not-yet-item-reviewed':'Downloaded; symbol-by-symbol review incomplete.','overview-reviewed-not-complete':'Condensed overview reviewed; this is not a complete manual.','complete-supplement-reviewed-base-link-not-proven':'Entire supplement reviewed; an explicit link to a specific base manual is not established.'},'de':{'selected-symbols-and-instructions-reviewed-not-complete':'Ausgewählte Einträge geprüft; vollständige Ausgabe nicht abgeschlossen.','downloaded-not-yet-item-reviewed':'Heruntergeladen; symbolweise Prüfung nicht abgeschlossen.','overview-reviewed-not-complete':'Kurzübersicht geprüft; keine vollständige Anleitung.','complete-supplement-reviewed-base-link-not-proven':'Gesamter Zusatz geprüft; ausdrückliche Zuordnung zu einer bestimmten Grundanleitung nicht belegt.'}}[lang]
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
  writer.writerow([item['id'],item['name']['cs'],item['name']['en'],item['name']['de'],scope['brand'],scope.get('model') or 'Not documented',scope.get('model_year') or 'Not documented',scope.get('edition') or '',','.join(map(str,scope.get('printed_pages',[]))),','.join(map(str,scope.get('pdf_pages',[]))),','.join(scope['powertrains']),scope.get('signal_state',item['state']),item['color'],source,item['graphic_path'],item['graphic_source'].get('page',''),item['graphic_source']['license'],item['checked']])
outputs=[(HERE/'coverage.csv','\ufeff'+csv_stream.getvalue())]
review_register=json.loads((HERE/'review-register.json').read_text())
stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
w.writerow(['id','brand','model','edition','part_number','whole_manual_comparison','reviewed_printed_pages','reviewed_html_sections','verified_item_ids','source_url'])
for row in review_register['manuals']:
 w.writerow([row['id'],row['brand'],row['model'],row['edition'],row.get('part_number')or'',row['whole_manual_comparison'],', '.join(map(str,row['reviewed_printed_pages'])),' / '.join(row['reviewed_html_sections']),', '.join(row['verified_item_ids']),row['source_url']])
outputs.append((HERE/'manual-review.csv','\ufeff'+stream.getvalue()))
brand_review=json.loads((HERE/'brand-functional-review.json').read_text())
for lang in LANGS:
 stream=io.StringIO();w=csv.writer(stream,lineterminator='\n')
 w.writerow(['brand','model','edition','printed_pages_or_sections','reviewed','remaining','source'])
 for row in brand_review['rows']:
  location=','.join(map(str,row['printed_pages'])) if row['printed_pages'] else ' / '.join(row['source_sections'])
  w.writerow([row['brand'],row['model'],row['edition'],location,row['reviewed'][lang],row['remaining'][lang],row['source_url']])
 outputs.append((HERE/f'brand-functional-review.{lang}.csv',stream.getvalue()))
audi_path=HERE/'audi-photo-review.json'
if audi_path.exists():
 audi=json.loads(audi_path.read_text())
 for lang in LANGS:
  stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
  w.writerow(['observation_id','photo','position','literal_text_CS','name','classification_code','classification','photo_colour_code','photo_colour','signal_state_from_photo_code','signal_state_from_photo','meaning','meaning_verification_basis_code','meaning_verification_basis','candidate_catalogue_ids_not_model_verified','matching_model_scoped_catalogue_ids','catalogue_result','catalogue_result_text','candidate_manual_references_json','candidate_manual_ids','candidate_manual_editions','candidate_manual_part_numbers','candidate_manual_printed_pages','candidate_manual_reference_status','meaning_verified','exact_reusable_graphic_verified','published_from_this_photo_set','source_type','brand','model','model_status','manual_edition','manual_edition_status','model_year','model_year_status','source_page','source_page_status_code','source_page_status','notes'])
  for row in audi.get('observations',[]):
   occurrences=audi_photo_occurrences(row)or[{'photo':'','position':''}]
   for occurrence in occurrences:
    references=audi_manual_references(row,lang);basis=row.get('meaning_verification_basis','unresolved')
    w.writerow([row.get('id',''),occurrence.get('photo',''),localized(occurrence.get('position'),lang),row.get('literal_text_cs')or localized(row.get('literal_text'),'cs'),audi_photo_title(row,lang),row.get('classification')or row.get('category',''),audi_photo_classification(row,lang),row.get('photo_colour',''),audi_photo_colour(row,lang),row.get('signal_state_from_photo',''),audi_photo_state(row,lang),localized(row.get('meaning'),lang),basis,audi_meaning_basis(row,lang),','.join(map(str,audi_photo_candidates(row))),','.join(map(str,row.get('matching_model_scoped_catalogue_ids',[])or[])),row.get('catalogue_result',''),localized(row.get('catalogue_result_text'),lang),json.dumps(references,ensure_ascii=False), '|'.join(x['manual_id']for x in references),'|'.join(x['edition']for x in references),'|'.join(x['part_number']for x in references),'|'.join(x['manual_id']+':'+','.join(map(str,x['printed_pages']))for x in references),audi_meaning_basis(row,lang),row.get('meaning_verified',''),row.get('exact_reusable_graphic_verified',''),row.get('published_from_this_photo_set',''),audi.get('source_type',''),audi.get('brand_confirmed_by_user')or audi.get('brand_id',''),audi.get('model_confirmed_by_user')or'',AUDI_INVENTORY_STATUS['model'][lang],row.get('manual_edition',audi.get('manual_edition'))or'',AUDI_INVENTORY_STATUS['edition'][lang],row.get('model_year',audi.get('model_year'))or'',AUDI_INVENTORY_STATUS['model_year'][lang],row.get('source_page')if row.get('source_page')is not None else'',row.get('source_page_status',''),AUDI_SOURCE_PAGE_STATUS[lang],localized(row.get('notes'),lang)])
  outputs.append((HERE/f'audi-photo-comparison.{lang}.csv','\ufeff'+stream.getvalue()))
  stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
  w.writerow(['working_photo_reference','description','view','role','brand','brand_confirmation_basis','model','model_status','manual_edition','edition_status','printed_page','page_status_code','page_status','original_filename','comparison_status'])
  basis=localized(audi.get('brand_confirmation_basis'),lang)
  for photo in audi.get('photos',[]):
   reviewed=bool(photo.get('visual_review'))or audi.get('photos_visually_inspected',0)>=len(audi.get('photos',[]))
   w.writerow([photo.get('id',''),localized(photo.get('description')or photo.get('name'),lang),audi_photo_view(photo,lang),audi_photo_role(photo,lang),audi.get('brand_confirmed_by_user')or audi.get('brand_id',''),basis,audi.get('model_confirmed_by_user')or'',localized(audi.get('model_status'),lang,AUDI_INVENTORY_STATUS['model'][lang]),audi.get('manual_edition')or'',localized(audi.get('edition_status'),lang,AUDI_INVENTORY_STATUS['edition'][lang]),photo.get('printed_page')or'',photo.get('page_status',''),AUDI_SOURCE_PAGE_STATUS[lang],photo.get('original_filename')or'',localized(photo.get('comparison_status'),lang,AUDI_INVENTORY_STATUS['reviewed'if reviewed else'pending'][lang])])
  outputs.append((HERE/f'audi-photo-inventory.{lang}.csv','\ufeff'+stream.getvalue()))
audi_manual_path=HERE/'audi-manual-photo-review.json'
if audi_manual_path.exists():
 audi_manual=json.loads(audi_manual_path.read_text());source=audi_manual_source(audi_manual)
 for lang in LANGS:
  stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
  w.writerow(['row_id','photo','printed_page','column','position_in_column','literal_caption_CS','label','source_checkmark_legend','graphic_occurrence_count','graphic_occurrences_CS_json','photo_colour_code','photo_colour','referenced_printed_pages','candidate_ids_not_model_verified','pending_candidate_ids','rejected_merge_candidate_ids','semantic_result_code','semantic_result','semantic_assessment','graphic_result_code','graphic_result','model_scope_result_code','model_scope_result','published','published_exact_match','exact_reusable_graphic','brand','brand_confirmation_basis','model','model_status','manual_edition','manual_edition_status','model_year','model_year_status','source_page_status_code','source_page_status','review_note'])
  for row in audi_manual.get('rows',[]):
   row_text=(row.get('text')or{}).get(lang,{})
   w.writerow([row.get('id',''),audi_manual_photo_id(row.get('printed_page')),row.get('printed_page',''),row.get('column',''),row.get('position_in_column',''),row.get('description_cs_verbatim',''),row_text.get('label',''),localized(source.get('checkmark_legend'),lang),audi_manual_graphic_occurrences(row),json.dumps(row.get('graphic_occurrences',[]),ensure_ascii=False),row.get('color',''),audi_manual_colour(row,lang),','.join(map(str,row.get('referenced_printed_pages',[]))),','.join(map(str,row.get('candidate_ids',[]))),','.join(map(str,row.get('pending_candidate_ids',[]))),','.join(map(str,row.get('rejected_merge_candidate_ids',[]))),row.get('semantic_result',''),AUDI_MANUAL_SEMANTIC_RESULTS[row['semantic_result']][lang],row_text.get('assessment',''),row.get('graphic_result',''),AUDI_MANUAL_GRAPHIC_RESULTS[row['graphic_result']][lang],row.get('model_scope_result',''),AUDI_MANUAL_MODEL_SCOPE_RESULTS[row['model_scope_result']][lang],row.get('published',''),row.get('published_exact_match',''),row.get('exact_reusable_graphic',''),audi_manual_brand(audi_manual),localized(source.get('brand_evidence'),lang),source.get('model')or'',AUDI_MANUAL_INVENTORY_STATUS['model'][lang],source.get('edition')or'',AUDI_MANUAL_INVENTORY_STATUS['edition'][lang],source.get('model_year')or'',AUDI_MANUAL_INVENTORY_STATUS['model_year'][lang],'photographed-manual-page',AUDI_MANUAL_INVENTORY_STATUS['page'][lang],localized(row.get('review_note'),lang)])
  outputs.append((HERE/f'audi-manual-photo-review.{lang}.csv','\ufeff'+stream.getvalue()))
  stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
  w.writerow(['working_photo_reference','description','role','brand','brand_confirmation_basis','model','model_status','manual_edition','edition_status','model_year','model_year_status','printed_page','row_count','graphic_occurrence_count','page_status_code','page_status','original_filename','comparison_status'])
  basis=localized(source.get('brand_evidence'),lang)
  for photo in (photo for photo in audi_manual.get('photos',[])if photo.get('status')=='supplied'):
   printed_page=photo.get('printed_page')
   description={'cs':'Fotografie tištěné strany ','en':'Photograph of printed page ','de':'Foto der gedruckten Seite '}[lang]+str(printed_page or'')
   w.writerow([audi_manual_photo_id(printed_page),description,audi_manual_photo_role(photo,lang),audi_manual_brand(audi_manual),basis,source.get('model')or'',AUDI_MANUAL_INVENTORY_STATUS['model'][lang],source.get('edition')or'',AUDI_MANUAL_INVENTORY_STATUS['edition'][lang],source.get('model_year')or'',AUDI_MANUAL_INVENTORY_STATUS['model_year'][lang],printed_page or'',photo.get('row_count',''),photo.get('graphic_occurrence_count',''),'photographed-manual-page',AUDI_MANUAL_INVENTORY_STATUS['page'][lang],'',AUDI_MANUAL_INVENTORY_STATUS['reviewed'][lang]])
  outputs.append((HERE/f'audi-manual-photo-inventory.{lang}.csv','\ufeff'+stream.getvalue()))
queues=json.loads((HERE/'work-queues.json').read_text())
for lang in LANGS:
 stream=io.StringIO();w=csv.writer(stream,delimiter=';',lineterminator='\n')
 w.writerow(['queue','brand','model','edition','document_kind','meaning_verified','exact_graphic_verified','published','remaining','source_url','source_file'])
 for group in queues['groups']:
  for row in group['rows']:
   w.writerow([group['id'],row['brand'],row.get('model',''),row['edition'],row.get('document_kind',row.get('source_kind','owner-manual'if row.get('manual')else'')),row.get('meaning_verified',''),row.get('exact_source_graphic_verified',''),row.get('published',''),row['remaining'][lang],row.get('source_url')or'',row.get('source_file')or''])
 outputs.append((HERE/f'work-queues.{lang}.csv','\ufeff'+stream.getvalue()))
for lang in LANGS:
 page,body=create_page(lang);outputs.append((page,body));outputs.append((page.parent/'zdroje.html',audit(lang,page)));outputs.append((page.parent/'revize.html',review_page(lang,page)));outputs.append((page.parent/'revize-kapitol.html',chapter_page(lang,page)));outputs.append((page.parent/'druha-kontrola.html',second_review_page(lang,page)));outputs.append((page.parent/'evidence.json',json.dumps({'canonical_catalog':rel('_warnings/catalog.json',page),'review_status':'incomplete-preview','checked':CAT['checked'],**CAT['counts']},indent=2)+'\n'))
from export_review import review_export_outputs
outputs+=review_export_outputs(ROOT,HERE,CAT,outputs)
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
print(('Checked' if '--check' in sys.argv else 'Generated')+': 3 static locales, '+str(len(CAT['items']))+' warning-light entries and '+str(len(INFO['items']))+' infotainment entries; shared images only.')
