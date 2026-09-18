"""Pack the original lamubone growth stages and their body color masks."""
from pathlib import Path
import json,argparse
import numpy as np
from PIL import Image
from scipy.ndimage import label
p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--assets',type=Path,default=Path('dist/assets'));args=p.parse_args()
metadata=json.loads((args.source_dir/'animation-sources.json').read_text())
for form,info in metadata.items():
 nd=next((args.source_dir/(form+'-neutral')).iterdir());pd=next((args.source_dir/(form+'-probe')).iterdir());cache={}
 for n in {n for row in info['rows'] for n in row['frames']}:
  b=np.array(Image.open(nd/f'{n}.png').convert('RGBA'));pr=np.array(Image.open(pd/f'{n}.png').convert('RGBA'))
  labs,total=label(b[:,:,3]>5);diff=np.max(np.abs(b[:,:,:3].astype(float)-pr[:,:,:3].astype(float)),axis=2)>4
  sizes=np.bincount(labs.ravel(),weights=diff.ravel());sizes[0]=0
  if len(sizes)<2 or sizes.max()<10:raise ValueError(f'{form} frame {n} has no visible body')
  keep=labs==sizes.argmax();yy,xx=np.where(keep);box=(int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1)
  delta=b[:,:,:3].astype(float)-pr[:,:,:3].astype(float)
  gray=np.clip((delta[:,:,0]+2/3*delta[:,:,2])/170,0,1);dark=np.clip((delta[:,:,2]+51*gray)/153,0,1);white=np.clip((delta[:,:,1]+51*gray+102*dark)/255,0,1)
  b[~keep,3]=0;mask=np.stack([white,gray,dark],axis=2);mask[~keep]=0
  cache[n]=(Image.fromarray(b),Image.fromarray(np.uint8(np.round(mask*255)),'RGB'),box)
 # Preserve relative motion per action, sharing one scale across the form.
 rowboxes=[]
 for row in info['rows']:
  bs=[cache[n][2] for n in row['frames']];rowboxes.append((min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)))
 scale=min(160/max(b[2]-b[0] for b in rowboxes),174/max(b[3]-b[1] for b in rowboxes))
 out=Image.new('RGBA',(1536,1872));maskout=Image.new('RGB',out.size)
 for row,(data,box) in enumerate(zip(info['rows'],rowboxes)):
  sz=(round((box[2]-box[0])*scale),round((box[3]-box[1])*scale));ox=(192-sz[0])//2;oy=(208-sz[1])//2
  for col,n in enumerate(data['frames']):
   image,mask,_=cache[n];out.paste(image.crop(box).resize(sz,Image.Resampling.LANCZOS),(col*192+ox,row*208+oy));maskout.paste(mask.crop(box).resize(sz,Image.Resampling.LANCZOS),(col*192+ox,row*208+oy))
 out.save(args.assets/(form+'-neutral.png'),optimize=True);maskout.save(args.assets/(form+'-mask.png'),optimize=True)
 print(form,'packed',flush=True)
(args.assets/'ram-level-animation-sources.json').write_text(json.dumps(metadata,indent=2)+'\n')
