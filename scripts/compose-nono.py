"""Mechanically adapt original Seer NoNo PNG frames to the Codex v1 contract."""
from pathlib import Path
import argparse,json
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects
p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--variant',choices=['super','normal','annual'],default='super');args=p.parse_args()
spec=[('idle','nono-timeline-frames',1,7,6),('running-right','nono-timeline-frames',48,55,8),('running-left','nono-timeline-frames',16,23,8),('waving','super-exp-1_1-frames',63,94,4),('jumping','super-action-6_1-frames',43,78,5),('failed','super-exp-4_1-frames',1,59,8),('waiting','super-action-1_1-frames',1,30,6),('running','super-action-7_1-frames',1,106,6),('review','super-exp-3_1-frames',1,30,6)]
if args.variant!='super':
 v=args.variant
 spec=[('idle',v+'-nono-frames',1,7,6),('running-right',v+'-nono-frames',48,55,8),('running-left',v+'-nono-frames',16,23,8),('waving',v+'-exp-1-frames',1,40 if v=='normal' else 20,4),('jumping',v+'-exp-1-frames',30,60,5) if v=='normal' else ('jumping',v+'-action-6-frames',43,65,5),('failed',v+'-exp-4-frames',1,60,8),('waiting',v+'-action-1-frames',15,67,6) if v=='normal' else ('waiting',v+'-nono-frames',1,7,6),('running',v+'-nono-frames',56,63,6),('review',v+'-exp-3-frames',1,40,6)]
atlas=Image.new('RGBA',(1536,1872));sources=[]
for row,(state,folder,first,last,count) in enumerate(spec):
 directory=next((args.source_dir/folder).iterdir());available=sorted(directory.glob('*.png'),key=lambda p:int(p.stem));selected=[]
 for i in range(count):
  target=first+(last-first)*i/max(1,count-1);selected.append(min(available,key=lambda p:abs(int(p.stem)-target)))
 if state=='idle' and args.variant=='super':selected=[directory/f'{n}.png' for n in [1,2,3,3,2,1]]
 frames=[]
 for path in selected:
  a=np.array(Image.open(path).convert('RGBA'));labs,n=label(a[:,:,3]>2)
  for k,sl in enumerate(find_objects(labs)):
   if sl is None:continue
   member=labs[sl]==k+1;rgb=a[sl][:,:,:3][member];alpha=a[sl][:,:,3][member]
   # The original game draws a detached black floor ellipse. Keep other original effects.
   if len(rgb)>20 and np.mean((np.max(rgb,axis=1)<170)&(np.ptp(rgb.astype(int),axis=1)<4))>.98:
    part=a[sl];part[member,3]=0
  im=Image.fromarray(a);box=im.getbbox()
  if not box:raise ValueError(str(path)+' has no visible pet')
  frames.append(im.crop(box))
 # Register to the original black face screen, so camera zooms in game clips
 # do not make the desktop companion abruptly change size between states.
 for col,im in enumerate(frames):
  a=np.array(im);black=(a[:,:,3]>80)&(a[:,:,:3].max(axis=2)<48)
  labs,n=label(black);sizes=np.bincount(labs.ravel());sizes[0]=0
  if len(sizes)>1 and sizes.max()>15:
   yy,xx=np.where(labs==sizes.argmax());fw=xx.max()-xx.min()+1
   cx=(xx.min()+xx.max())/2;cy=(yy.min()+yy.max())/2
   scale=min(61/fw,168/im.width,180/im.height)
  else:cx=im.width/2;cy=im.height*.65;scale=min(168/im.width,180/im.height)
  resized=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
  x=max(8,min(184-resized.width,round(96-cx*scale)))
  y=max(8,min(200-resized.height,round(132-cy*scale)))
  atlas.alpha_composite(resized,(col*192+x,row*208+y))
 sources.append({'state':state,'sourceFolder':folder,'originalFrames':[int(f.stem) for f in selected]})
args.output_dir.mkdir(exist_ok=True,parents=True);name='nono' if args.variant=='super' else 'nono-'+args.variant
atlas.save(args.output_dir/(name+'.png'),optimize=True)
(args.output_dir/(name+'-animation-sources.json')).write_text(json.dumps(sources,indent=2)+'\n')
print('Packed 9 original animations into 1536×1872 atlas.')
