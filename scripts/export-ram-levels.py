from pathlib import Path
import xml.etree.ElementTree as E,subprocess,json,concurrent.futures
import argparse
p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--ffdec',type=Path,required=True);args=p.parse_args()
base=args.source_dir;jar=str(args.ffdec)
r=E.parse(base/'lamubone.xml');nodes={x.get('spriteId') or x.get('shapeId'):x for x in r.iter() if x.get('spriteId') or x.get('shapeId')}
body=set()
for id,x in nodes.items():
 if x.get('type','').startswith('DefineShape'):
  colors=[tuple(int(c.get(k,0)) for k in ['red','green','blue']) for c in x.iter('color')]
  if len(colors)==2 and set(colors)=={(255,255,255),(204,204,204)}:body.add(id)
roots={x.get('characterId') for x in r.iter() if x.get('name')=='petBody'}
for id,x in nodes.items():
 if x.get('type')=='DefineSpriteTag' and any(z.get('characterId') in body for z in x.iter()):roots.add(id)
seen=set()
def visit(id):
 if id in seen or id not in nodes:return
 seen.add(id)
 for x in nodes[id].iter():
  if x.get('characterId'):visit(x.get('characterId'))
for id in roots:visit(id)
for id in seen:
 x=nodes[id]
 if not x.get('type','').startswith('DefineShape'):continue
 for c in x.iter('color'):
  rgb=tuple(int(c.get(k,0)) for k in ['red','green','blue']);v={(255,255,255):(255,0,255),(204,204,204):(0,255,255),(153,153,153):(255,255,0)}.get(rgb)
  if v:
   for k,value in zip(['red','green','blue'],v):c.set(k,str(value))
r.write(base/'probe.xml',encoding='utf-8',xml_declaration=True)
subprocess.run(['java','-jar',jar,'-xml2swf',str(base/'probe.xml'),str(base/'probe.swf')],stdout=subprocess.DEVNULL,check=True)
mapping=[('idle','down',6),('running-right','right',8),('running-left','left',8),('waving','happy',4),('jumping','dance',5),('failed','angry',8),('waiting','boring',6),('running','rightdown',6),('review','leftdown',6)]
meta={};jobs=[]
for form,id in [('junior','936'),('middle','1532'),('senior','1777'),('classic','2525')]:
 sp=nodes[id];labels=[];frame=1
 for x in sp.find('subTags'):
  if x.get('type')=='FrameLabelTag':labels.append((x.get('name'),frame))
  if x.get('type')=='ShowFrameTag':frame+=1
 ranges={label:(start,labels[i+1][1]-1 if i+1<len(labels) else frame-1) for i,(label,start) in enumerate(labels)}
 rows=[]
 for state,action,count in mapping:
  lo,hi=ranges[action];frames=[lo+int((hi-lo+1)*i/count) for i in range(count)];rows.append({'state':state,'gameAction':action,'frames':frames})
 meta[form]={'sourceSpriteId':int(id),'rows':rows};selected=sorted({n for row in rows for n in row['frames']})
 for variant in ['neutral','probe']:jobs.append((form,id,variant,selected))
(base/'animation-sources.json').write_text(json.dumps(meta,indent=2)+'\n')
def render(job):
 form,id,variant,frames=job;out=base/(form+'-'+variant);source=base/('lamubone.swf' if variant=='neutral' else 'probe.swf')
 with open(str(out)+'.log','w') as log:subprocess.run(['java','-Djava.awt.headless=true','-jar',jar,'-selectid',id,'-select',id+':'+','.join(map(str,frames)),'-zoom','4','-ignorebackground','-export','sprite',str(out),str(source)],stdout=log,stderr=log,check=True)
 print(form,variant,'exported',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(render,jobs))
