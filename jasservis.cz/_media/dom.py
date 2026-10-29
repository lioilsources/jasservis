from html.parser import HTMLParser
import re
VOID=set('area base br col embed hr img input link meta param source track wbr'.split())
class Node:
 def __init__(self,tag,attrs,start,opening,parent=None):self.tag=tag;self.attrs=dict(attrs);self.start=start;self.opening=opening;self.end=opening;self.parent=parent;self.children=[]
 def descendants(self):
  for c in self.children:yield c;yield from c.descendants()
class DOM(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=False);self.s=s;self.lines=[0]+[m.end() for m in re.finditer('\n',s)];self.root=Node('root',[],0,0);self.root.end=len(s);self.stack=[self.root];self.nodes=[];self.feed(s)
 def pos(self):line,col=self.getpos();return self.lines[line-1]+col
 def handle_starttag(self,t,a):
  n=Node(t,a,self.pos(),self.pos()+len(self.get_starttag_text()),self.stack[-1]);n.parent.children.append(n);self.nodes.append(n)
  if t not in VOID:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t) if t not in VOID else None
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:
    n=self.stack[i];n.end=self.s.find('>',self.pos())+1;self.stack=self.stack[:i];break
 def units(self):
  chosen=[]
  for n in self.nodes:
   if n.tag=='img' and n.attrs.get('src') and '/logos/' not in n.attrs['src'] and 'logo-aw-dev' not in n.attrs['src'] and '/themes/' not in n.attrs['src'] and 'firmy.cz' not in n.attrs['src']:
    unit=n;p=n.parent
    while p is not None and p.tag!='root':
     if p.tag=='figure' and len([x for x in p.descendants() if x.tag=='img'])==1:unit=p;break
     p=p.parent
    if unit is n and n.parent.tag=='a' and n.parent.end>n.end:unit=n.parent
    chosen.append(unit)
   elif n.tag=='li' and 'data-preview' in n.attrs:chosen.append(n)
   elif 'data-img-url' in n.attrs:chosen.append(n)
  return sorted({n.start:n for n in chosen}.values(),key=lambda n:n.start)
