"""Render exact source frames and replace only the reviewed atlas rows.
No retiming or generated artwork: the client playback contract stays unchanged.
"""
import argparse,json,copy,subprocess,importlib.util,xml.etree.ElementTree as E
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sp=importlib.util.spec_from_file_location('compose',Path(__file__).with_name('compose-selected-actions.py'));c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,default=Path(__file__).with_name('selected-pet-clips.json'));p.add_argument('--ram-source',type=Path,required=True);p.add_argument('--nono-source',type=Path,required=True);p.add_argument('--ffdec',required=True);p.add_argument('--assets',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
plan=json.loads(a.plan.read_text());ram=json.loads((a.ram_source/'original-actions.json').read_text());nono=json.loads((a.nono_source/'candidates.json').read_text());jobs=[];ramrows={};nonorows={}
for form,states in plan['ram'].items():
 info=ram[form];selected={}
 for state,selection in states.items():
  frames=selection['frames'];source=selection['sourceState']
  assert len(frames)==c.COUNTS[c.STATES.index(state)], (form,state)
  entry=next(x for x in info['rows'] if x['state']==source);action=next(x for x in info['actions'] if x['label']==selection.get('gameAction',entry['gameAction']));selected[state]={**entry,'registration':selection.get('registration'),'gameAction':action['label'],'state':state,'actionFrames':frames,'frames':[action['start']+f-1 for f in frames],'sourceFrameCount':action['sourceFrameCount']}
 ramrows[form]=selected;frames=sorted({n for row in selected.values() for n in row['frames']})
 for kind in ['neutral','probe']:
  xml=a.ram_source/(form+'-'+kind+'.xml');tree=E.parse(xml)
  # Eye whites in the level assets must not inherit the body probe colour.
  if kind=='probe' and form in ['junior','middle','senior','classic']:
   original=E.parse(a.ram_source/(form+'-neutral.xml'))
   for sid in ['10','413','422']:
    node=tree.find(f'.//item[@shapeId="{sid}"]');ref=original.find(f'.//item[@shapeId="{sid}"]')
    if node is not None and ref is not None:
     node.clear();node.attrib.update(ref.attrib)
     for child in ref:node.append(copy.deepcopy(child))
  dest=a.work/(form+'-'+kind);derived=dest.with_suffix('.xml');tree.write(derived,encoding='utf-8',xml_declaration=True)
  jobs.append((derived,info['spriteId'],frames,dest))
for variant,states in plan['nono'].items():
 nonorows[variant]={}
 for state,selection in states.items():
  frames=selection['frames'];source=selection['sourceState']
  assert len(frames)==c.COUNTS[c.STATES.index(state)], (variant,state)
  entry=next(x for x in nono if x['variant']==variant and x['state']==source)
  if 'sourceFile' in selection:
   filename=selection['sourceFile'];directory=Path(filename).stem;tree=E.parse(a.nono_source/(directory+'.xml'));symbol=tree.find('.//item[@type="SymbolClassTag"]');names=[n.text for n in symbol.find('names')];sid=symbol.find('tags')[names.index('pet')].text
   sprite=tree.find(f'.//item[@spriteId="{sid}"]')
   entry={**entry,'sourceFile':filename,'directory':directory,'sourceSpriteId':int(sid),'sourceFrameCount':int(sprite.get('frameCount'))}
  nonorows[variant][state]={**entry,'state':state,'originalFrames':frames,'registration':selection.get('registration')};jobs.append((a.nono_source/(entry['directory']+'.xml'),entry['sourceSpriteId'],sorted(set(frames)),a.work/entry['directory']))
def export(job):
 xml,sid,frames,dest=job
 if dest.exists() and any(d.is_dir() and all((d/f'{f}.png').exists() for f in frames) for d in dest.iterdir()):return
 swf=a.work/(dest.name+'.swf')
 with (a.work/(dest.name+'.log')).open('w') as log:
  for command in [['-xml2swf',str(xml),str(swf)],['-selectid',str(sid),'-select',str(sid)+':'+','.join(map(str,frames)),'-zoom','4','-ignorebackground','-export','sprite',str(dest),str(swf)]]:
   subprocess.run(['java','-Djava.awt.headless=true','-jar',a.ffdec,*command],stdout=log,stderr=log,check=True)
 print(dest.name,'rendered',flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(export,jobs))
for filename,forms in [('animation-sources.json',['super','water','wood','fire']),('ram-level-animation-sources.json',['junior','middle','senior','classic'])]:
 meta=json.loads((a.assets/filename).read_text())
 for form in forms:
  if form not in ramrows:continue
  atlas=Image.open(a.assets/(form+'-neutral.png')).convert('RGBA');mask=Image.open(a.assets/(form+'-mask.png')).convert('RGB');nd=next((a.work/(form+'-neutral')).iterdir());pd=next((a.work/(form+'-probe')).iterdir())
  for state,entry in ramrows[form].items():
   row=c.STATES.index(state);atlas.paste((0,0,0,0),(0,row*208,1536,(row+1)*208));mask.paste((0,0,0),(0,row*208,1536,(row+1)*208))
   pairs=[c.clean(Image.open(nd/f'{n}.png'),Image.open(pd/f'{n}.png')) for n in entry['frames']];c.pack_row(pairs,row,atlas,mask,registration=entry.get('registration'))
   meta[form]['rows'][row]=entry
  atlas.save(a.assets/(form+'-neutral.png'),optimize=True);mask.save(a.assets/(form+'-mask.png'),optimize=True)
 (a.assets/filename).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
for variant,states in nonorows.items():
 name='nono' if variant=='super' else 'nono-'+variant;atlas=Image.open(a.assets/(name+'.png')).convert('RGBA');meta=json.loads((a.assets/(name+'-animation-sources.json')).read_text())
 for state,entry in states.items():
  row=c.STATES.index(state);atlas.paste((0,0,0,0),(0,row*208,1536,(row+1)*208));nd=next((a.work/entry['directory']).iterdir());pairs=[c.clean(Image.open(nd/f'{n}.png')) for n in entry['originalFrames']];c.pack_row(pairs,row,atlas,registration=entry.get('registration'))
  meta[row]={k:entry[k] for k in ['state','sourceFile','sourceFrameCount','originalFrames','registration']}
 atlas.save(a.assets/(name+'.png'),optimize=True);(a.assets/(name+'-animation-sources.json')).write_text(json.dumps(meta,indent=2)+'\n')
print('Reviewed rows packed. Rebuild palettes before publishing these assets.',flush=True)
