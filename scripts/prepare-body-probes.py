"""Rebuild body masks from the original petBody display-list descendants.
Includes single-fill eyelids and highlights; preserves original nested eye
color transforms so eye whites and pupils do not inherit the body palette.
Run before compose-official.py and apply-game-palette.py.
"""
import xml.etree.ElementTree as E,subprocess,concurrent.futures
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--ffdec',type=Path,required=True);args=p.parse_args()
base=args.source_dir;jar=str(args.ffdec)
def job(n):
 r=E.parse(base/f'skill{n}.xml');nodes={x.get('spriteId') or x.get('shapeId'):x for x in r.iter() if x.get('spriteId') or x.get('shapeId')};roots={x.get('characterId') for x in r.iter() if x.get('name')=='petBody'};seen=set()
 # Several expression clips omit the petBody instance name. Identify their
 # body containers by the same original two-fill body shape references.
 body_shapes=set()
 for id,x in nodes.items():
  if x.get('type','').startswith('DefineShape'):
   colors=[tuple(int(c.get(k,0)) for k in ['red','green','blue']) for c in x.iter('color')]
   if len(colors)==2 and set(colors)=={(255,255,255),(204,204,204)}:body_shapes.add(id)
 for id,x in nodes.items():
  if x.get('type')=='DefineSpriteTag' and any(z.get('characterId') in body_shapes for z in x.iter()):roots.add(id)
 def visit(id):
  if id in seen or id not in nodes:return
  seen.add(id)
  for x in nodes[id].iter():
   if x.get('characterId'):visit(x.get('characterId'))
 for id in roots:visit(id)
 count=0
 for id in seen:
  x=nodes[id]
  if not x.get('type','').startswith('DefineShape'):continue
  for c in x.iter('color'):
   rgb=tuple(int(c.get(k,0)) for k in ['red','green','blue'])
   if rgb==(255,255,255):v=(255,0,255)
   elif rgb==(204,204,204):v=(0,255,255)
   elif rgb==(153,153,153):v=(255,255,0)
   else:continue
   for k,value in zip(['red','green','blue'],v):c.set(k,str(value))
   count+=1
 out=base/f'probe{n}.xml';r.write(out,encoding='utf-8',xml_declaration=True)
 subprocess.run(['java','-jar',jar,'-xml2swf',str(out),str(base/f'probe{n}.swf')],stdout=subprocess.DEVNULL,check=True)
 sprite={1:898,2:538,4:1029,7:940}[n]
 with open(base/f'probe{n}.log','w') as log:subprocess.run(['java','-Djava.awt.headless=true','-jar',jar,'-selectid',str(sprite),'-zoom','4','-ignorebackground','-export','sprite',str(base/f'probe{n}'),str(base/f'probe{n}.swf')],stdout=log,stderr=log,check=True)
 print(n,'corrected',count,'body fills',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(job,[1,2,4,7]))
