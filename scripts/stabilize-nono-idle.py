"""Keep the original idle body fixed; composite only original screen-eye poses.
Run after generating source atlases and all NoNo palette variants.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_fill_holes, binary_erosion, binary_dilation
A=Path(__file__).resolve().parents[1]/'dist/assets'

def eyes(tile):
 a=np.array(tile);rgb=a[:,:,:3].astype(int)
 labels,_=label((rgb.max(2)<60)&(a[:,:,3]>128));sizes=np.bincount(labels.ravel());sizes[0]=0
 face=binary_fill_holes(labels==sizes.argmax());yy,xx=np.where(face)
 box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
 mask=face & (rgb.max(2)>75) & (rgb.max(2)-rgb.min(2)>35)
 # The eyes are inside the display, not the colored outline around it.
 mask &= binary_erosion(face,iterations=1)
 return box,mask

for name in ['nono-normal','nono-annual']:
 meta_path=A/(name+'-animation-sources.json');meta=json.loads(meta_path.read_text())
 if meta[0].get('registration')=='fixed-body-original-eyes':
  print(name,'already stabilized; regenerate source idle before changing selection');continue
 source=Image.open(A/(name+'.png')).convert('RGBA')
 row=0
 indices=list(range(6))
 donors=[source.crop((i*192,row*208,(i+1)*192,(row+1)*208)) for i in indices]
 original_source=meta[row]
 for path in [A/(name+'.png'),*sorted(A.glob(name+'-color-*.png'))]:
  atlas=Image.open(path).convert('RGBA');base=atlas.crop((0,0,192,208));box,mask=eyes(base)
  # Remove the base eyes while preserving screen glare and its contour.
  pixels=np.array(base);pixels[binary_dilation(mask,iterations=1),:3]=0
  blank=Image.fromarray(pixels)
  for col,donor in enumerate(donors):
   db,dm=eyes(donor);patch=np.array(donor);patch[:,:,3]=np.where(dm,patch[:,:,3],0)
   patch=Image.fromarray(patch).crop(db).resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
   tile=blank.copy();tile.alpha_composite(patch,(box[0],box[1]));atlas.paste(tile,(col*192,0))
  atlas.save(path,optimize=True)
 meta[0]['registration']='fixed-body-original-eyes'
 meta[0]['eyeSource']={k:original_source[k] for k in ['sourceFile','sourceFolder'] if k in original_source}
 meta[0]['eyeSource']['originalFrames']=[original_source['originalFrames'][i] for i in indices]
 meta[0]['bodyFrame']=meta[0]['originalFrames'][0]
 meta_path.write_text(json.dumps(meta,indent=2)+'\n')
 print(name,'body locked; original eye poses applied to all colors',flush=True)
