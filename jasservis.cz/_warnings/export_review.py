"""Deterministic review export: shared licensed assets, translated catalogue and source register.
No manufacturer manuals, private SSP files or source-image crops are republished.
"""
import csv,io,json,zipfile,hashlib

def review_export_outputs(root,here,cat):
 outputs=[]
 for lang in ['cs','en','de']:
  f=io.StringIO();w=csv.writer(f,delimiter=';',lineterminator='\n')
  cols=['id','name','meaning','action','note','alt','kind','state','colour','group','shared_image','source_scope_json'];w.writerow(cols)
  for i in cat['items']:w.writerow([i['id']]+[i[k][lang]for k in ['name','meaning','action','note','alt']]+[i[k]for k in ['kind','state','color','group','graphic_path']]+[json.dumps(i['scopes'],ensure_ascii=False)])
  outputs.append((here/f'catalog-texts.{lang}.csv','\ufeff'+f.getvalue()))
 f=io.StringIO();w=csv.writer(f,delimiter=';',lineterminator='\n');w.writerow(['shared_file','sha256','author','licence','licence_url','source_url','catalogue_ids'])
 paths=sorted({i['graphic_path']for i in cat['items']})
 for path in paths:
  items=[i for i in cat['items']if i['graphic_path']==path];g=items[0]['graphic_source'];w.writerow([path,hashlib.sha256((root/path).read_bytes()).hexdigest(),g['author'],g['license'],g.get('license_url',''),g.get('page',''),','.join(i['id']for i in items)])
 outputs.append((here/'used-symbols.csv','\ufeff'+f.getvalue()))
 # Fixed ZIP timestamps make --check meaningful and avoid unrelated archive churn.
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  def add(name,data):
   zi=zipfile.ZipInfo(name,date_time=(2026,10,30,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,data.encode('utf-8')if isinstance(data,str)else data)
  add('README.txt','J&S SERVIS — independent content review, preview only.\nIncomplete catalogue; scope is per model, edition and equipment.\nSemantic records, model assignments, colour variants and distinct shapes are different counts.\nAll CZ/EN/DE texts are in catalog-texts.*.csv and locales.json. Source/edition/page data are in catalog.json and review registers. Shared symbol files appear once, with credits and licences in used-symbols.csv.\nNo full owner manuals, private SSPs, user photographs or manufacturer source artwork included. Standard licensed depictions are not OEM facsimiles. Missing or unclear symbols are not replaced with approximate icons.\nTechnical tests are not content verification. Missing photo groups are explicitly listed in attachment-groups.json.\n')
  for p,data in outputs:add(p.name,data)
  for name in ['catalog.json','locales.json','attachment-groups.json','terramar-photo-review.json','terramar-1125-overview-review.json','chapter-review.json','review-register.json','caddy-source-graphic-review.json','work-queues.json','unified-round-review.json','q4-climate-function-review.json','enyaq-independent-review.json','multivan-requested-review.json']:
   add(name,(here/name).read_bytes())
  for lang in ['cs','en','de']:
   for stem in ['terramar-photo-comparison','terramar-1125-overview-review','all-terramar-photo-occurrences','q4-climate-function-review','enyaq-independent-review','enyaq-requested-photo-status','multivan-requested-photo-status']:
    p=here/f'{stem}.{lang}.csv';add(p.name,p.read_bytes())
  for path in paths:add(path,(root/path).read_bytes())
 outputs.append((here/'catalog-review-export.zip',buf.getvalue()))
 return outputs
