"""Add all audited super-NoNo action/exp files and its eight directions to the library."""
from pathlib import Path
import argparse,json,copy,subprocess,importlib.util,xml.etree.ElementTree as E
from concurrent.futures import ThreadPoolExecutor
spec=importlib.util.spec_from_file_location('ram_library',Path(__file__).with_name('build-ram-library.py'));lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
NAMES={'action-1':'充电','action-2':'开机','action-3':'关机','action-4':'玩球','action-5':'吃电池','action-6':'召唤','action-7':'玩魔方','exp-1':'开心','exp-2':'生气','exp-3':'惊讶','exp-4':'悲哀'}
ADAPTED={'action-1','action-2','action-7','exp-1','exp-3','exp-4'}
def prepare(label,args):
 source=args.sources/('super-'+label+'.swf');xml=args.work/('nono-'+label+'.xml')
 subprocess.run(['java','-Djava.awt.headless=true','-jar',str(args.ffdec),'-swf2xml',str(source),str(xml)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 tree=E.parse(xml);root=tree.getroot();symbol=root.find('.//item[@type="SymbolClassTag"]');sid=symbol.find('tags')[[n.text for n in symbol.find('names')].index('pet')].text;sprites={n.get('spriteId'):n for n in root.iter('item') if n.get('type')=='DefineSpriteTag'}
 def duration(key,seen=None):
  seen=set() if seen is None else seen
  if key in seen or key not in sprites:return 1
  seen.add(key);n=sprites[key];return max([int(n.get('frameCount'))]+[duration(x.get('characterId'),seen) for x in n.find('subTags') if x.get('characterId')])
 master=sprites[sid];length=duration(sid)
 for _ in range(length-int(master.get('frameCount'))):E.SubElement(master.find('subTags'),'item',{'type':'ShowFrameTag','forceWriteAsLong':'false'})
 master.set('frameCount',str(length));tree.write(xml,encoding='utf-8',xml_declaration=True)
 return dict(id='nono-'+label,name='超能 NoNo',spriteId=int(sid),fps=float(root.get('frameRate','25')),source=source.name,xml=xml,total=length,actions=[dict(id=label,name=NAMES[label],frames=length,start=1,category='action',adapted=label in ADAPTED)])
def directions(args):
 xml=args.work/'nono-directions.xml';tree=E.parse(args.base);root=tree.getroot();symbol=root.find('.//item[@type="SymbolClassTag"]');sid=symbol.find('tags')[[n.text for n in symbol.find('names')].index('pet')].text;master=root.find(f'.//item[@spriteId="{sid}"]');length=int(master.get('frameCount'));body=root.find('.//item[@spriteId="149"]');actions=[];frame=1
 for n in body.find('subTags'):
  if n.get('type')=='FrameLabelTag':actions.append(dict(id=n.get('name'),name=lib.NAMES[n.get('name')],start=frame,category='direction',adapted=n.get('name') in ['down','left','right']))
  if n.get('type')=='ShowFrameTag':frame+=1
 for i,a in enumerate(actions):a['frames']=(actions[i+1]['start'] if i+1<len(actions) else length+1)-a['start']
 tree.write(xml,encoding='utf-8',xml_declaration=True);return dict(id='nono-directions',name='超能 NoNo',spriteId=int(sid),fps=float(root.get('frameRate','25')),source='super/nono_1.swf',xml=xml,total=length,actions=actions)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,default=Path('/tmp/official-pet-resource-audit'));p.add_argument('--base',type=Path,default=Path('/tmp/nono-assets/nono-timeline.xml'));p.add_argument('--work',type=Path,default=Path('/tmp/nono-full-library'));p.add_argument('--output',type=Path,default=Path('dist/assets/ram-library'));p.add_argument('--ffdec',type=Path,default=Path('/tmp/ram-swf-extract/ffdec/ffdec.jar'));a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 def run(label):return lib.build(prepare(label,a),a)
 with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(run,NAMES))
 base=lib.build(directions(a),a);actions=base['actions']+[x for r in result for x in r['actions']]
 for r in [base]+result:
  for action in r['actions']:action['fps']=r['fps']
 info=dict(id='nono',name='超能 NoNo',fps=25,actions=actions,total=sum(x['frames'] for x in actions),source='super/nono_1.swf + action/1–7_1.swf + exp/1–4_1.swf')
 (a.output/'nono-manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
 manifest=a.output/'manifest.json'
 data=json.loads(manifest.read_text()) if manifest.exists() else {'version':1,'forms':[]}
 data['forms']=[f for f in data['forms'] if f['id']=='super']+[info]
 manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('NoNo library ready',len(actions),'actions',flush=True)
