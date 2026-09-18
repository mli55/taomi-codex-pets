"""Reproduce official GV.petColor ColorTransform offsets for all ten colors."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,default=Path('dist/assets'));p.add_argument('--forms',nargs='+',default=['super','water','wood','fire','junior','middle','senior','classic']);a=p.parse_args()
palette=json.loads((a.assets/'palette.json').read_text())
for form in a.forms:
 neutral=np.array(Image.open(a.assets/f'{form}-neutral.png').convert('RGBA'))
 mask=np.array(Image.open(a.assets/f'{form}-mask.png').convert('RGB')).astype(float)/255
 for key,entry in palette.items():
  white=np.clip(255+np.array(entry['offset']),0,255)-255;gray=np.clip(204+np.array(entry['offset']),0,255)-204
  dark=np.clip(153+np.array(entry['offset']),0,255)-153
  result=neutral.copy();result[:,:,:3]=np.clip(np.round(neutral[:,:,:3].astype(float)+mask[:,:,0,None]*white+mask[:,:,1,None]*gray+mask[:,:,2,None]*dark),0,255)
  im=Image.fromarray(result);im.save(a.assets/f'{form}-{key}.png',optimize=True)
  if entry['slug']=='yellow':im.save(a.assets/f'{form}.png',optimize=True)
 print(form,'10 official colors prepared')
