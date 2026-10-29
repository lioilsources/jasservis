#!/usr/bin/env python3
"""One media catalogue -> three static editions. No browser-side dependency."""
from pathlib import Path
from dom import DOM
import argparse,copy,html,json,os,posixpath,re,tempfile,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
CATALOG=Path(__file__).with_name('catalog.json')
LANGS=('cs','en','de')
IMAGE_SUFFIXES={'.jpg','.jpeg','.png','.webp','.gif','.avif','.svg'}
TOKEN=re.compile(r'\{\{(file|label|dimension|srcset):([^{}]+)\}\}|\{\{caption\}\}')
def local_file(value):
 u=urllib.parse.urlsplit(value)
 if u.scheme or u.netloc:raise ValueError('Media must use a local file: '+value)
 p=(ROOT/urllib.parse.unquote(u.path)).resolve()
 if not p.is_relative_to(ROOT) or not p.is_file():raise ValueError('Missing local media: '+value)
 return p

def media_url(value,page):
 u=urllib.parse.urlsplit(value);relative=posixpath.relpath(u.path,posixpath.dirname(page))
 return urllib.parse.urlunsplit(('', '',urllib.parse.quote(relative,safe='/@:-._~'),u.query,u.fragment))

def render(item,lang,page,pid):
 locale=item['locales'][lang]
 def replace(m):
  if m[0]=='{{caption}}':return locale.get('caption_html','')
  kind,key=m[1],m[2]
  if kind=='file':return html.escape(media_url(item['files'][key],page),quote=True)
  if kind=='label':return html.escape(locale['labels'][key],quote=True)
  if kind=='dimension':return str(item['dimensions'][key])
  if kind=='srcset':return ', '.join(html.escape(media_url(item['files'][part['file']],page),quote=True)+(' '+part['descriptor'] if part['descriptor'] else '') for part in item['srcsets'][key])
  raise ValueError('Unknown media token')
 result=TOKEN.sub(replace,locale['template'])
 if '{{' in result:raise ValueError('Unresolved token '+pid)
 return result

def validate(c):
 if c.get('version')!=1:raise ValueError('Unknown catalogue version')
 used=set()
 for page,entry in c['pages'].items():
  if page.startswith(('en/','de/')) or not page.endswith('index.html'):raise ValueError('Invalid Czech page key')
  local_file(page)
  for group,ids in entry['groups'].items():
   if not re.fullmatch(r'gallery-\d+',group):raise ValueError('Invalid gallery key')
   if len(ids)!=len(set(ids)):raise ValueError('Duplicate item in '+page+' '+group)
   for pid in ids:
    if pid in used:raise ValueError('Media ID must have one shared position: '+pid)
    used.add(pid);item=c['photos'][pid]
    if set(item['locales'])!=set(LANGS):raise ValueError('Supply CS, EN and DE translations for '+pid)
    if item['main_file'] not in item['files']:raise ValueError('Missing main file')
    for value in item['files'].values():local_file(value)
    for lang in LANGS:
     render(item,lang,('' if lang=='cs' else lang+'/')+page,pid)
 return used

def outputs(c):
 used=validate(c);plans={}
 for page,entry in c['pages'].items():
  for lang in LANGS:
   file=('' if lang=='cs' else lang+'/')+page;p=ROOT/file;before=local_file(file).read_text();after=before
   for group,ids in entry['groups'].items():
    start='<!-- shared-media:'+group+':start -->';end='<!-- shared-media:'+group+':end -->'
    if after.count(start)!=1 or after.count(end)!=1:raise ValueError('Missing/duplicate gallery boundaries in '+file+' '+group)
    a=after.index(start)+len(start);z=after.index(end,a)
    content=entry.get('separators',{}).get(group,'\n').join(render(c['photos'][pid],lang,file,pid) for pid in ids)
    after=after[:a]+content+after[z:]
   expected=[pid for ids in entry['groups'].values() for pid in ids]
   actual=[n.attrs.get('data-media-id') for n in DOM(after).units()]
   if actual!=expected:raise ValueError('Unmanaged, duplicated or misplaced media in '+file)
   # Keep Open Graph and structured image references in the same page in sync.
   for old,replacement in entry.get('image_replacements',{}).items():
    target=replacement['file'];head,tail=after.split('</head>',1)
    for a,b in [(media_url(old,file),media_url(target,file)),('https://jasservis.cz/'+old,'https://jasservis.cz/'+target)]:head=head.replace(a,b)
    def schema_image(m):
     try:obj=json.loads(m[2])
     except ValueError:return m[0]
     def walk(o):
      if isinstance(o,dict):
       if o.get('@type')=='ImageObject' and o.get('url')=='https://jasservis.cz/'+target:
        o.update(width=replacement['width'],height=replacement['height'])
       for v in o.values():walk(v)
      elif isinstance(o,list):
       for v in o:walk(v)
     walk(obj)
     return m[1]+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+m[3]
    head=re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',schema_image,head,flags=re.S)
    after=head+'</head>'+tail
   plans[p]=(before,after)
 return plans

def write_all(c,save_catalog=False):
 plans=outputs(c)
 if save_catalog:plans[CATALOG]=(CATALOG.read_text(),json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 changed={p:v for p,v in plans.items() if v[0]!=v[1]};written=[]
 try:
  for p,(before,after) in changed.items():
   temporary=p.with_name(p.name+'.media-tmp');temporary.write_text(after);os.replace(temporary,p);written.append(p)
 except BaseException:
  for p in written:p.write_text(changed[p][0])
  raise
 return len(changed)

def find_position(c,pid):
 for page,p in c['pages'].items():
  for group,ids in p['groups'].items():
   if pid in ids:return page,group,ids,ids.index(pid)
 raise ValueError('Item not in any gallery: '+pid)

def add_item(c,page,group,pid,source,width,height,translations,position):
 if pid in c['photos']:raise ValueError('ID already exists')
 if set(translations)!=set(LANGS):raise ValueError('Three translated descriptions are required')
 item={'files':{'file-1':source},'main_file':'file-1','dimensions':{'width':width,'height':height},'srcsets':{},'locales':{}}
 for lang,t in translations.items():
  if not t.get('alt','').strip():raise ValueError('Translated alt text is required for '+lang)
  caption=t.get('caption','')
  item['locales'][lang]={'labels':{'alt-1':t['alt']},'caption_html':html.escape(caption),'template':'<figure data-media-id="'+pid+'"><a href="{{file:file-1}}"><img src="{{file:file-1}}" width="{{dimension:width}}" height="{{dimension:height}}" alt="{{label:alt-1}}" loading="lazy" decoding="async" /></a>'+('<figcaption>{{caption}}</figcaption>' if caption else '')+'</figure>'}
 c['photos'][pid]=item
 ids=c['pages'][page]['groups'][group]
 if position is not None and not 1<=position<=len(ids)+1:raise ValueError('Invalid position')
 ids.insert(len(ids) if position is None else position-1,pid)

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
 sub.add_parser('check');sub.add_parser('sync');sub.add_parser('list')
 a=sub.add_parser('replace');a.add_argument('id');a.add_argument('source');a.add_argument('--width',type=int,required=True);a.add_argument('--height',type=int,required=True)
 a=sub.add_parser('remove');a.add_argument('id')
 a=sub.add_parser('move');a.add_argument('id');a.add_argument('--position',type=int,required=True);a.add_argument('--group');a.add_argument('--page')
 a=sub.add_parser('add');a.add_argument('id');a.add_argument('source');a.add_argument('--page',required=True);a.add_argument('--group',required=True);a.add_argument('--translations',type=Path,required=True);a.add_argument('--width',type=int,required=True);a.add_argument('--height',type=int,required=True);a.add_argument('--position',type=int)
 args=p.parse_args();c=json.loads(CATALOG.read_text())
 if args.action=='list':
  for page,entry in c['pages'].items():
   for group,ids in entry['groups'].items():print(page,group,', '.join(ids))
  return
 if args.action=='check':
  plans=outputs(c);drift=[str(p.relative_to(ROOT)) for p,(a,b) in plans.items() if a!=b]
  if drift:raise ValueError('Generated media differ from shared catalogue: '+', '.join(drift))
  print('PASS:',len(c['pages']),'page groups,',len(validate(c)),'media items, CS/EN/DE consistent');return
 if args.action=='replace':
  if min(args.width,args.height)<=0:raise ValueError('Positive dimensions required')
  if local_file(args.source).suffix.lower() not in IMAGE_SUFFIXES:raise ValueError('An image file is required')
  page,group,ids,index=find_position(c,args.id)
  olditem=c['photos'][args.id];oldsource=olditem['files'][olditem['main_file']]
  # Mobile/desktop copies of the same photo on a page share the replacement.
  for photo_id in [pid for rows in c['pages'][page]['groups'].values() for pid in rows]:
   item=c['photos'][photo_id]
   if item['files'][item['main_file']]!=oldsource:continue
   for key,value in item['files'].items():
    if local_file(value).suffix.lower() in IMAGE_SUFFIXES:item['files'][key]=args.source
   item['dimensions'].update(width=args.width,height=args.height)
   for key in item['srcsets']:item['srcsets'][key]=[]
  aliases=c['pages'][page].setdefault('image_replacements',{})
  for key,value in aliases.items():
   if value['file']==oldsource:value.update(file=args.source,width=args.width,height=args.height)
  aliases[oldsource]={'file':args.source,'width':args.width,'height':args.height}
  c['pages'][page]['image_replacements']={k:v for k,v in aliases.items() if k!=v['file']}
 elif args.action=='remove':
  page,group,ids,i=find_position(c,args.id)
  item=c['photos'][args.id];source=item['files'][item['main_file']]
  for group,rows in c['pages'][page]['groups'].items():
   removed=[pid for pid in rows if c['photos'][pid]['files'][c['photos'][pid]['main_file']]==source]
   c['pages'][page]['groups'][group]=[pid for pid in rows if pid not in removed]
   for pid in removed:del c['photos'][pid]
 elif args.action=='move':
  page,group,ids,i=find_position(c,args.id);ids.pop(i)
  target=c['pages'][args.page or page]['groups'][args.group or group]
  if args.position<1 or args.position>len(target)+1:raise ValueError('Invalid target position')
  target.insert(args.position-1,args.id)
 elif args.action=='add':
  if not re.fullmatch(r'[a-z0-9-]+',args.id):raise ValueError('Use a unique lowercase ID')
  if min(args.width,args.height)<=0:raise ValueError('Positive dimensions required')
  if local_file(args.source).suffix.lower() not in IMAGE_SUFFIXES:raise ValueError('An image file is required')
  page=args.page.rstrip('/')+'/index.html' if not args.page.endswith('index.html') else args.page
  add_item(c,page,args.group,args.id,args.source,args.width,args.height,json.loads(args.translations.read_text()),args.position)
 print('Updated',write_all(c,save_catalog=args.action!='sync'),'files; Czech and translated editions generated together.')

if __name__=='__main__':
 try:main()
 except (ValueError,KeyError) as e:raise SystemExit('ERROR: '+str(e))
