"""Render and verify the five service price lists from the shared numeric source.

Run from any directory: python3 jasservis.cz/_media/tools/sync-prices.py
Use --check before publication. This authoring tool is excluded from the public artifact.
"""
from pathlib import Path
import argparse, html, json, os, re, sys

parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--root',type=Path)
args=parser.parse_args();root=(args.root or Path(__file__).resolve().parents[2]).resolve()
theme=root/'wp-content/themes/theme53985'
source=json.loads((theme/'price-values.json').read_text());catalog=json.loads((theme/'service-prices.json').read_text())
layout=json.loads((Path(__file__).parent/'service-price-table.json').read_text())
assert source['schemaVersion']==1 and source['currency']=='CZK'
values=source['values'];assert all(type(n) is int and n>0 for n in values.values())
langs=['cs','en','de','uk','vi'];changed=[];count=0
def fmt(n):return f'{n:,}'.replace(',','\u00a0')
def base(l):return root if l=='cs' else root/l
def runtime(p,keys):
 path=os.path.relpath(theme/'js/service-prices.js',p.parent).replace(os.sep,'/')
 data=html.escape(json.dumps({k:values[k] for k in keys},separators=(',',':')),quote=True)
 return '<script defer src="'+path+'?v=20261112-shared-prices-v1" data-price-values="'+data+'"></script>'
def save(p,s):
 global count
 count+=1
 if p.read_text()!=s:
  changed.append(str(p.relative_to(root)))
  if not args.check:p.write_text(s)
# Prices are displayed only in /cenik/; service pages link to their section there.
# Do not restore the old price panels or their runtime on individual service pages.
for p in root.rglob('index.html'):
 if p.parent.name!='cenik':
  s=p.read_text()
  assert not re.search(r'Kč|CZK|data-price=|data-price-values=|service-prices\.js',s),p
labels=layout['labels'];groups=layout['groups']
assert layout['schemaVersion']==1
assert {slug for group in groups for slug in group['services']}==set(catalog['services'])
assert {r[k] for group in groups for r in group['rows'] for k in ('net','gross') if k in r}==set(values)
def esc(s):return html.escape(s,quote=True)
def paragraph(text,cls='price-table-note'):return '<p class="'+cls+'">'+esc(text)+'</p>'
def price_cell(record,kind,lang):
 key=record.get(kind)
 # Missing published prices deliberately stay empty: no zero, dash, estimate,
 # photo amount or implicit VAT calculation may be substituted here.
 if not key:return '<td class="service-price-table__price" data-price-status="unpublished"></td>'
 prefix=esc(labels['from'][lang])+' ' if record.get('from') else ''
 return '<td class="service-price-table__price">'+prefix+'<span class="price-table-amount"><span data-price="'+esc(key)+'">'+fmt(values[key])+'</span> Kč</span></td>'
for lang in langs:
 p=base(lang)/'cenik/index.html';s=p.read_text();article=re.search(r'<article class="guide-article price-overview">([\s\S]*?)</article>',s);assert article,p
 sections=[];toc=[]
 for group in groups:
  ident='cenik-'+group['id'];title=esc(group['title'][lang]);rows=[]
  toc.append('<li><a href="#'+ident+'">'+title+'</a></li>')
  for record in group['rows']:
   text=esc(record['label'][lang])
   for kind in ('unit','note'):
    if kind in record:text+='<small class="service-price-table__'+kind+'">'+esc(record[kind][lang])+'</small>'
   rows.append('<tr id="polozka-'+record['id']+'"><th scope="row">'+text+'</th>'+price_cell(record,'net',lang)+price_cell(record,'gross',lang)+'</tr>')
  anchors=''.join('<span class="price-table-anchor" id="cena-'+slug.replace('/','-')+'"></span>' for slug in group['services'])
  table='<table class="service-price-table"><caption class="price-table-sr-only">'+title+'</caption><colgroup><col class="service-price-table__item-col"><col class="service-price-table__price-col"><col class="service-price-table__price-col"></colgroup><thead><tr>'+''.join('<th scope="col">'+esc(labels[k][lang])+'</th>' for k in ('item','net','gross'))+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
  notes=''.join(paragraph(note[lang]) for note in group['notes'])
  links=''.join('<li><a href="../'+slug+'/">'+esc(catalog['services'][slug][lang]['title'])+'</a></li>' for slug in group['services'])
  if links:notes+='<details class="price-table-details"><summary>'+esc(labels['detail'][lang])+'</summary><ul>'+links+'</ul></details>'
  sections.append('<section class="price-table-section" id="'+ident+'">'+anchors+'<h2>'+title+'</h2>'+table+notes+'</section>')
 body='<article class="guide-article price-overview">'+paragraph(labels['intro'][lang],'price-table-intro')+paragraph(labels['blank'][lang],'price-table-key')+'<nav class="price-table-nav" aria-label="'+esc(labels['nav'][lang])+'"><ul>'+''.join(toc)+'</ul></nav>'+''.join(sections)+'</article>'
 s=s[:article.start()]+body+s[article.end():]
 s=re.sub(r'<script\b[^>]*src="[^"]*service-prices\.js[^>]*></script>','',s)
 s=s.replace('</head>',runtime(p,values)+'</head>')
 stylesheet=os.path.relpath(theme/'service-price-table.css',p.parent).replace(os.sep,'/')+'?v=20261113-table-v2'
 s=re.sub(r'<link\b[^>]*href="[^"]*service-price-table\.css[^>]*>','',s)
 s=s.replace('</head>','<link rel="stylesheet" href="'+stylesheet+'"></head>')
 s=s.replace('driver-article-page.css?v=20261110-audit-articles-v2','driver-article-page.css?v=20261112-clear-article-plan-v3');save(p,s)
print(json.dumps({'pages':count,'different':len(changed),'files':changed if args.check else []},ensure_ascii=False))
if args.check and changed:sys.exit(1)
