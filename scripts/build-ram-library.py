"""Build a read-only frame browser for every label in the eight official Ram sprites.

Original XML/SWF inputs are never changed. Each label is expanded to the longest
nested timeline, including its original blank/hold frames. No Codex sampling.
"""
import argparse,copy,json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
FORMS={
 'junior':('初级拉姆','lamubone.xml',936), 'middle':('中级拉姆','lamubone.xml',1532),
 'senior':('高级拉姆','lamubone.xml',1777), 'classic':('超级拉姆','lamubone.xml',2525),
 'super':('神力超级拉姆','skill7.xml',940), 'water':('神奇水系拉姆','skill2.xml',538),
 'wood':('弹力木系拉姆','skill4.xml',1029), 'fire':('霹雳火系拉姆','skill1.xml',898)}
NAMES={'down':'正面','leftdown':'左下','left':'向左','leftup':'左上','up':'背面','rightup':'右上','right':'向右','rightdown':'右下','food':'吃东西','drenk':'喝水','wash':'洗澡','medical':'医疗','woter':'woter · 原标签','tomatoo':'tomatoo · 原标签','dance':'跳舞','spring':'spring · 原标签','football':'踢球','thirst':'口渴','hungry':'饥饿','happy':'高兴','angry':'生气','boring':'无聊','revival':'复活','dight':'dight · 原标签','die':'死亡'}
DIRECTIONS={'down','leftdown','left','leftup','up','rightup','right','rightdown'}
CURRENT={'down','left','right','happy','angry','boring','football','dance'}

def prepare(form,args):
 name,filename,sid=FORMS[form];src=(args.levels if filename=='lamubone.xml' else args.elements)/filename
 tree=E.parse(src);root=tree.getroot();sprites={n.get('spriteId'):n for n in root.iter('item') if n.get('type')=='DefineSpriteTag'}
 def duration(key,seen=None):
  seen=set() if seen is None else seen
  if key in seen or key not in sprites:return 1
  seen.add(key);n=sprites[key]
  return max([int(n.get('frameCount'))]+[duration(x.get('characterId'),seen) for x in n.find('subTags') if x.get('characterId')])
 display={};snapshots={};pending=[]
 for node in sprites[str(sid)].find('subTags'):
  kind=node.get('type');depth=node.get('depth')
  if kind.startswith('RemoveObject'):display.pop(depth,None)
  elif kind.startswith('PlaceObject'):
   if node.get('characterId'):display[depth]=copy.deepcopy(node)
   elif depth in display:
    for child in node:
     old=display[depth].find(child.tag)
     if old is not None:display[depth].remove(old)
     display[depth].append(copy.deepcopy(child))
  elif kind=='FrameLabelTag':pending.append(node.get('name'))
  elif kind=='ShowFrameTag':
   for label in pending:snapshots[label]=copy.deepcopy(display)
   pending.clear()
 master=sprites[str(sid)];sub=master.find('subTags');sub.clear();frame=1;actions=[]
 for label,objects in snapshots.items():
  if label=='empty':continue
  length=max([duration(n.get('characterId')) for n in objects.values()]+[1]);start=frame
  sub.append(E.Element('item',{'type':'FrameLabelTag','name':label,'forceWriteAsLong':'true','namedAnchor':'false'}))
  sub.extend(copy.deepcopy(list(objects.values())))
  sub.extend(E.Element('item',{'type':'ShowFrameTag','forceWriteAsLong':'false'}) for _ in range(length))
  sub.extend(E.Element('item',{'type':'RemoveObject2Tag','depth':depth,'forceWriteAsLong':'false'}) for depth in objects)
  actions.append(dict(id=label,name=NAMES.get(label,label+' · 原标签'),frames=length,start=start,category='direction' if label in DIRECTIONS else 'action',adapted=label in CURRENT))
  frame+=length
 master.set('frameCount',str(frame-1));xml=args.work/(form+'.xml');tree.write(xml,encoding='utf-8',xml_declaration=True)
 return dict(id=form,name=name,spriteId=sid,fps=float(root.get('frameRate','24')),source=src.name,actions=actions,xml=xml,total=frame-1)

def build(info,args):
 form=info['id'];dest=args.work/form;swf=info['xml'].with_suffix('.swf');marker=args.work/(form+'.exported');out=args.output/form;out.mkdir(parents=True,exist_ok=True)
 if not marker.exists():
  with (args.work/(form+'.log')).open('w') as log:
   subprocess.run(['java','-Djava.awt.headless=true','-jar',str(args.ffdec),'-xml2swf',str(info['xml']),str(swf)],stdout=log,stderr=log,check=True)
   subprocess.run(['java','-Djava.awt.headless=true','-jar',str(args.ffdec),'-selectid',str(info['spriteId']),'-zoom','2','-ignorebackground','-export','sprite',str(dest),str(swf)],stdout=log,stderr=log,check=True)
  marker.write_text(str(info['total']))
 print(form,'rendered',info['total'],'frames',flush=True)
 folder=next(d for d in dest.iterdir() if d.is_dir());cell=(256,280);columns=12
 for action in info['actions']:
  frames=range(action['start'],action['start']+action['frames']);boxes=[];poster=None
  for f in frames:
   with Image.open(folder/f'{f}.png') as im:
    box=im.getbbox()
    if box:boxes.append(box);poster=f if poster is None else poster
  if not boxes:
   action.update(visible=False);continue
  bounds=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes));w,h=bounds[2]-bounds[0],bounds[3]-bounds[1];scale=min(232/w,256/h);size=(max(1,round(w*scale)),max(1,round(h*scale)));offset=((cell[0]-size[0])//2,(cell[1]-size[1])//2)
  atlas=Image.new('RGBA',(columns*cell[0],((action['frames']+columns-1)//columns)*cell[1]))
  for i,f in enumerate(frames):
   with Image.open(folder/f'{f}.png') as im:
    tile=im.convert('RGBA').crop(bounds).resize(size,Image.Resampling.LANCZOS)
    atlas.paste(tile,((i%columns)*cell[0]+offset[0],(i//columns)*cell[1]+offset[1]))
    if f==poster:
     thumb=Image.new('RGBA',cell);thumb.paste(tile,offset);thumb.save(out/(action['id']+'-poster.webp'),quality=88,method=4)
  atlas.save(out/(action['id']+'.webp'),quality=88,method=4)
  action.update(visible=True,sheet=f'assets/ram-library/{form}/{action["id"]}.webp',poster=f'assets/ram-library/{form}/{action["id"]}-poster.webp',columns=columns,cellWidth=cell[0],cellHeight=cell[1])
 info.pop('xml');print(form,'packed',len(info['actions']),'actions',flush=True);return info

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--forms',nargs='+',choices=list(FORMS),default=['super']);p.add_argument('--elements',type=Path,default=Path('/tmp/ram-swf-extract'));p.add_argument('--levels',type=Path,default=Path('/tmp/ram-low'));p.add_argument('--work',type=Path,default=Path('/tmp/ram-full-library'));p.add_argument('--output',type=Path,default=Path('dist/assets/ram-library'));p.add_argument('--ffdec',type=Path,default=Path('/tmp/ram-swf-extract/ffdec/ffdec.jar'));a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True);a.output.mkdir(parents=True,exist_ok=True)
 infos=[prepare(form,a) for form in a.forms]
 print('Exporting',sum(i['total'] for i in infos),'frames across',sum(len(i['actions']) for i in infos),'actions',flush=True)
 with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(lambda i:build(i,a),infos))
 (a.output/'manifest.json').write_text(json.dumps(dict(version=1,forms=result),ensure_ascii=False,indent=2)+'\n')
 print('Library ready',flush=True)
