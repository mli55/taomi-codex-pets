"""Re-export the original eye whites excluded from the body colour mask.
Only the middle Ram's dance masks and derived colour atlases are updated.
"""
import argparse,copy,importlib.util,json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--ffdec',type=Path,required=True);p.add_argument('--assets',type=Path,default=Path('dist/assets'));a=p.parse_args()
spec=importlib.util.spec_from_file_location('compose',Path(__file__).with_name('compose-selected-actions.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
neutral=E.parse(a.source/'middle-neutral.xml');probe=E.parse(a.source/'middle-probe.xml')
for sid in ['10','413','422']:
 old=probe.find(f'.//item[@shapeId="{sid}"]');original=neutral.find(f'.//item[@shapeId="{sid}"]')
 assert old is not None and original is not None
 old.clear();old.attrib.update(original.attrib)
 for child in original:old.append(copy.deepcopy(child))
work=a.source/'middle-eye-repair';work.mkdir(exist_ok=True);xml=work/'probe.xml';swf=work/'probe.swf';probe.write(xml,encoding='utf-8',xml_declaration=True)
manifest=json.loads((a.assets/'ram-preview/middle.json').read_text());frames=manifest['dance']['sourceFrames']
with (work/'export.log').open('w') as log:
 for command in [['-xml2swf',str(xml),str(swf)],['-selectid','1532','-select','1532:'+','.join(map(str,frames)),'-zoom','4','-ignorebackground','-export','sprite',str(work/'frames'),str(swf)]]:
  subprocess.run(['java','-Djava.awt.headless=true','-jar',str(a.ffdec),*command],stdout=log,stderr=log,check=True)
nd=next((a.source/'middle-smooth-neutral').iterdir());pd=next((work/'frames').iterdir())
pairs={n:c.clean(Image.open(nd/f'{n}.png'),Image.open(pd/f'{n}.png')) for n in frames}
def scale_for(images):
 boxes=[im.getbbox() for im in images];w=max(b[2] for b in boxes)-min(b[0] for b in boxes);h=max(b[3] for b in boxes)-min(b[1] for b in boxes);return min(168/w,182/h)
def pack(pairs,base_scale,size,wrap):
 boxes=[im.getbbox() for im,_ in pairs];box=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes));w,h=box[2]-box[0],box[3]-box[1];s=min(168/w,182/h,base_scale);sz=(max(1,round(w*s)),max(1,round(h*s)));out=Image.new('RGBA',size);mask=Image.new('RGB',size)
 for i,(im,m) in enumerate(pairs):
  dest=(192*(i%wrap)+(192-sz[0])//2,208*(i//wrap)+(208-sz[1])//2)
  out.paste(im.crop(box).resize(sz,Image.Resampling.LANCZOS),dest);mask.paste(m.crop(box).resize(sz,Image.Resampling.LANCZOS),dest)
 return out,mask
base=scale_for([c.clean(Image.open(nd/f'{n}.png'))[0] for n in manifest['down']['sourceFrames']])
existing=Image.open(a.assets/'ram-preview/middle-dance.png').convert('RGBA');out,mask=pack([pairs[n] for n in frames],base,existing.size,8)
assert out.tobytes()==existing.tobytes(),'Preview geometry changed'
mask.save(a.assets/'ram-preview/middle-dance-mask.png',optimize=True)
rows=json.loads((a.assets/'ram-level-animation-sources.json').read_text())['middle']['rows'];raw=next((a.source/'middle-neutral').iterdir())
base=scale_for([c.clean(Image.open(raw/f'{n}.png'))[0] for n in rows[0]['frames']])
out,mask=pack([pairs[n] for n in rows[-1]['frames']],base,(1536,208),8)
existing=Image.open(a.assets/'middle-neutral.png').convert('RGBA')
assert out.tobytes()==existing.crop((0,1664,1536,1872)).tobytes(),'Export geometry changed'
masks=Image.open(a.assets/'middle-mask.png');masks.paste(mask,(0,1664));masks.save(a.assets/'middle-mask.png',optimize=True)
subprocess.run(['python3',str(Path(__file__).with_name('apply-game-palette.py')),'--assets',str(a.assets),'--forms','middle'],check=True)
print('Updated middle dance masks; original pixels and frame placement unchanged.')
