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
labels={'cs':'Služby v ceníku','en':'Services in the price list','de':'Leistungen in der Servicepreisliste','uk':'Послуги в прайс-листі','vi':'Dịch vụ trong bảng giá'}
for lang in langs:
 p=base(lang)/'cenik/index.html';s=p.read_text();article=re.search(r'<article class="guide-article price-overview">([\s\S]*?)</article>',s);assert article,p
 intro=re.search(r'<p>[\s\S]*?</p>',article[1])[0];cards=[];toc=[]
 for slug,translations in catalog['services'].items():
  record=translations[lang];content=record['html']
  content=re.sub(r'\{\{([a-z0-9_.-]+)\}\}',lambda m:fmt(values[m[1]]),content)
  assert '{{' not in content
  content=content.replace('<h2','<h3').replace('</h2>','</h3>')
  ident='cena-'+slug.replace('/','-');title=html.escape(record['title']);target='../'+slug+'/'
  toc.append('<li><a href="#'+ident+'">'+title+'</a></li>')
  # The full public price panel preserves VAT, units, inclusions and exclusions.
  cards.append('<section class="price-overview__service" id="'+ident+'" data-price-service="'+slug+'"><h2>'+title+'</h2>'+content+'<p><a href="'+target+'">'+title+'</a></p></section>')
 body='<article class="guide-article price-overview">'+intro+'<details class="article-contents"><summary>'+labels[lang]+'</summary><nav class="price-overview__toc" aria-label="'+labels[lang]+'"><ul>'+''.join(toc)+'</ul></nav></details>'+''.join(cards)+'</article>'
 s=s[:article.start()]+body+s[article.end():]
 s=re.sub(r'<script\b[^>]*src="[^"]*service-prices\.js[^>]*></script>','',s)
 s=s.replace('</head>',runtime(p,values)+'</head>')
 s=s.replace('driver-article-page.css?v=20261110-audit-articles-v2','driver-article-page.css?v=20261112-clear-article-plan-v3');save(p,s)
print(json.dumps({'pages':count,'different':len(changed),'files':changed if args.check else []},ensure_ascii=False))
if args.check and changed:sys.exit(1)
