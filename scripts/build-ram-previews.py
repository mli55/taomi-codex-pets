"""Build continuous-frame web previews from the existing official SWF timelines.
Codex export atlases are left untouched. Requires the prepared neutral/probe SWFs.
"""
import argparse,json,subprocess,importlib.util,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('--actions',nargs='+');p.add_argument('--reuse',action='store_true');p.add_argument('--source',type=Path,required=True);p.add_argument('--ffdec',required=True);p.add_argument('--output',type=Path,default=Path('dist/assets/ram-preview'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('compose',Path(__file__).with_name('compose-selected-actions.py'));compose=importlib.util.module_from_spec(spec);spec.loader.exec_module(compose)
info=json.loads((args.source/'original-actions.json').read_text())
selected={}
for f in ['animation-sources.json','ram-level-animation-sources.json']:selected.update(json.loads((args.output.parent/f).read_text()))

def job(form):
 data=info[form];sid=data['spriteId'];clips={}
 for action in data['actions']:
  name=action['label'];lo,hi=1,action['sourceFrameCount']-1
  if args.actions and name not in args.actions:continue
  # Retain the approved front-facing happy expression (avoid the somersault).
  if name not in ['down','left','right']:
   row=next(r for r in selected[form]['rows'] if r['gameAction']==name);lo,hi=min(row['actionFrames']),max(row['actionFrames'])
   if name=='happy':
    row=next(r for r in selected[form]['rows'] if r['state']=='jumping');lo,hi=min(row['actionFrames']),max(row['actionFrames'])
  if name=='happy':lo,hi={'super':(8,34),'classic':(20,35),'junior':(5,29),'middle':(1,10)}.get(form,(1,action['sourceFrameCount']-1))
  if name=='football':lo,hi={'super':(1,40),'junior':(104,126),'middle':(48,65),'classic':(60,96)}.get(form,(48,66))
  if form=='senior' and name in ['left','right']:hi=8
  clips[name]={'frames':list(range(action['start']+lo-1,action['start']+hi)), 'fps':24,'loop':'forward'}
 frames=sorted({n for c in clips.values() for n in c['frames']})
 folders=[]
 for kind in ['neutral','probe']:
  dest=args.source/(form+'-smooth-'+kind);folders.append(dest)
  if args.reuse:continue
  with (args.source/(form+'-smooth-'+kind+'.log')).open('w') as log:
   subprocess.run(['java','-Djava.awt.headless=true','-jar',args.ffdec,'-selectid',str(sid),'-select',str(sid)+':'+','.join(map(str,frames)),'-zoom','4','-ignorebackground','-export','sprite',str(dest),str(args.source/(form+'-'+kind+'.swf'))],stdout=log,stderr=log,check=True)
 dirs=[next(d.iterdir()) for d in folders];manifest=json.loads((args.output/(form+'.json')).read_text()) if args.actions else {};base_scale=None
 for action,clip in clips.items():
  processed=[compose.clean(Image.open(dirs[0]/f'{n}.png'),Image.open(dirs[1]/f'{n}.png')) for n in clip['frames']]
  # Keep the incoming/outgoing ball outside the pet's local stage instead of shrinking the pet to fit its offstage path.
  if form=='super' and action=='football':processed=[tuple(im.crop((160,190,490,610)) for im in pair) for pair in processed]
  valid=[(n,pair) for n,pair in zip(clip['frames'],processed) if pair[0].getbbox()]
  boxes=[pair[0].getbbox() for _,pair in valid];box=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes));w,h=box[2]-box[0],box[3]-box[1];scale=min(168/w,182/h,base_scale or 100)
  if base_scale is None:base_scale=scale
  size=(max(1,round(w*scale)),max(1,round(h*scale)));atlas=Image.new('RGBA',(1536,208*math.ceil(len(valid)/8)));mask=Image.new('RGB',atlas.size)
  for i,(_,pair) in enumerate(valid):
   dest=(192*(i%8)+(192-size[0])//2,208*(i//8)+(208-size[1])//2)
   for target,image in zip([atlas,mask],pair):target.paste(image.crop(box).resize(size,Image.Resampling.LANCZOS),dest)
  prefix=form+'-'+action;atlas.save(args.output/(prefix+'.png'),optimize=True);mask.save(args.output/(prefix+'-mask.png'),optimize=True)
  # These reviewed expressions are excerpts, not complete game loops.
  # Reverse along the same frames rather than snapping across the cut.
  count=len(valid)
  clip['loop']='forward' if action in ['down','left','right','happy','football'] else 'pingpong'
  manifest[action]={'image':prefix+'.png','mask':prefix+'-mask.png','frames':count,'fps':clip['fps'],'loop':clip['loop'],'sourceFrames':[n for n,_ in valid[:count]]}
 (args.output/(form+'.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(form,'smooth previews ready',flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(job,info))
