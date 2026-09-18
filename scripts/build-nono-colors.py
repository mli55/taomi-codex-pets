"""Build screenshot-reference variants from original SWF tint containers.
The palette is approximate; source default PNGs remain untouched.
"""
from pathlib import Path
import json,xml.etree.ElementTree as E,subprocess,concurrent.futures,copy,sys
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
import argparse
parser=argparse.ArgumentParser(description='Render NoNo colors using the original color_ display containers.')
parser.add_argument('--base-dir',type=Path,required=True)
parser.add_argument('--action-dir',type=Path,required=True)
parser.add_argument('--work-dir',type=Path,required=True)
parser.add_argument('--ffdec',required=True)
parser.add_argument('--assets',type=Path,default=Path('dist/assets'))
parser.add_argument('--variants',nargs='+',default=['normal','super','annual'])
parser.add_argument('--rows',nargs='+',type=int)
args=parser.parse_args();OUT=args.work_dir;OUT.mkdir(parents=True,exist_ok=True);JAR=args.ffdec
jobs=[]
for variant in args.variants:
 name='nono' if variant=='super' else 'nono-'+variant
 rows=json.loads((args.assets/(name+'-animation-sources.json')).read_text())
 for row,entry in enumerate(rows):
  if args.rows is not None and row not in args.rows:continue
  if row<3 or (variant=='annual' and row==6 and 'sourceFile' not in entry):
   key=variant+'-base';xml=(args.base_dir/'nono-timeline.xml') if variant=='super' else (args.base_dir/'expanded'/(variant+'-nono-timeline.xml'))
  else:key=Path(entry['sourceFile']).stem;xml=args.action_dir/(key+'.xml')
  jobs.append(dict(variant=variant,name=name,row=row,key=key,xml=str(xml),frames=entry['originalFrames']))
unique={}
for j in jobs:
 d=unique.setdefault(j['key'],dict(j,frames=[]));d['frames']=sorted(set(d['frames']+j['frames']))
def export(j):
 # A cached export may predate a new frame selection.
 if all(any(folder.is_dir() and all((folder/f'{frame}.png').exists() for frame in j['frames'])
            for folder in (OUT/(j['key']+'-'+str(t))).iterdir())
        if (OUT/(j['key']+'-'+str(t))).exists() else False for t in [0,255]):return
 tree=E.parse(j['xml']);symbol=tree.find('.//item[@type="SymbolClassTag"]');names=[x.text for x in symbol.find('names')];sid=symbol.find('tags')[names.index('pet')].text
 for tint in [0,255]:
  t=copy.deepcopy(tree);count=0
  # Annual action SWFs omit instance names. Their recolorable shell is the
  # white/warm-gray shape used by color_1 in the direction asset; the cream
  # armor, yellow ears, eyes and effects are separate shapes.
  shells=set()
  if j['variant']=='annual' and not any(n.get('name','').startswith('color_') for n in t.iter('item')):
   for n in t.iter('item'):
    if not n.get('shapeId'):continue
    colors={tuple(int(c.get(k,0)) for k in ['red','green','blue']) for c in n.iter('color')}
    if colors=={(255,255,255),(217,211,200)}:shells.add(n.get('shapeId'))
  for node in t.iter('item'):
   if not node.get('name','').startswith('color_') and node.get('characterId') not in shells:continue
   node.set('placeFlagHasColorTransform','true');ct=node.find('colorTransform')
   if ct is None:ct=E.SubElement(node,'colorTransform')
   ct.attrib.update(dict(type='CXFORMWITHALPHA',hasAddTerms='true',hasMultTerms='true',nbits='10',alphaMultTerm='256',alphaAddTerm='0',redMultTerm='0',greenMultTerm='0',blueMultTerm='0',redAddTerm=str(tint),greenAddTerm=str(tint),blueAddTerm=str(tint)));count+=1
  if not count:raise ValueError(j['key']+' missing tint containers')
  dest=OUT/(j['key']+'-'+str(tint));xml=dest.with_suffix('.xml');swf=dest.with_suffix('.swf');t.write(xml,encoding='utf-8',xml_declaration=True)
  with dest.with_suffix('.log').open('w') as log:
   subprocess.run(['java','-Djava.awt.headless=true','-jar',JAR,'-xml2swf',str(xml),str(swf)],stdout=log,stderr=log,check=True)
   subprocess.run(['java','-Djava.awt.headless=true','-jar',JAR,'-selectid',sid,'-select',sid+':'+','.join(map(str,j['frames'])),'-zoom','4','-ignorebackground','-export','sprite',str(dest),str(swf)],stdout=log,stderr=log,check=True)
 print(j['key'],'exported',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(export,unique.values()))
(OUT/'jobs.json').write_text(json.dumps(jobs,indent=2))

def clean(image,probe=None):
    pixels=np.array(image.convert('RGBA'));mask=None
    if probe is not None:
        delta=pixels[:,:,:3].astype(float)-np.array(probe.convert('RGBA'))[:,:,:3].astype(float)
        gray=np.clip((delta[:,:,0]+2/3*delta[:,:,2])/170,0,1)
        dark=np.clip((delta[:,:,2]+51*gray)/153,0,1)
        white=np.clip((delta[:,:,1]+51*gray+102*dark)/255,0,1)
        mask=np.uint8(np.round(np.stack([white,gray,dark],axis=2)*255))
    components,_=label(pixels[:,:,3]>0)
    for index,area in enumerate(find_objects(components),1):
        if area is None:continue
        part=components[area]==index;rgb=pixels[area][:,:,:3][part]
        height=area[0].stop-area[0].start;width=area[1].stop-area[1].start
        # Remove detached ground ellipses, retaining balls, jewels and effects.
        shadow=len(rgb)>20 and width>1.7*height and np.mean((rgb.max(axis=1)<190)&(np.ptp(rgb.astype(int),axis=1)<5))>.98
        if shadow:
            pixels[area][part,3]=0
            if mask is not None:mask[area][part]=0
    if mask is not None:mask[pixels[:,:,3]==0]=0
    return Image.fromarray(pixels),None if mask is None else Image.fromarray(mask)

def pack_row(frames,row,atlas,mask_atlas=None,base_scale=None):
    boxes=[im.getbbox() for im,_ in frames]
    if any(b is None for b in boxes):raise ValueError(f'Empty selected frame in row {row}')
    box=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes))
    width,height=box[2]-box[0],box[3]-box[1]
    scale=min(168/width,182/height,base_scale if base_scale is not None else 100)
    size=(max(1,round(width*scale)),max(1,round(height*scale)))
    ox=(192-size[0])//2;oy=(208-size[1])//2
    for col,(im,mask) in enumerate(frames):
        dest=(col*192+ox,row*208+oy)
        atlas.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),dest)
        if mask_atlas is not None:mask_atlas.paste(mask.crop(box).resize(size,Image.Resampling.LANCZOS),dest)
    return scale


assets=args.assets
palette=[(c['id'],c['name'],c['rgb']) for c in json.loads((assets/'nono-palette.json').read_text())]
for variant in args.variants:
 name='nono' if variant=='super' else 'nono-'+variant
 atlases=[Image.new('RGBA',(1536,1872)) for _ in range(2)]
 for j in [j for j in jobs if j['variant']==variant]:
  row=j['row'];probes=[]
  if variant=='annual' and row==6 and j['key'].endswith('-base'):
   for atlas in atlases:atlas.paste(atlas.crop((0,0,1536,208)),(0,row*208))
   continue
  for tint in [0,255]:
   folder=next((OUT/(j['key']+'-'+str(tint))).iterdir());probes.append([Image.open(folder/f'{f}.png').convert('RGBA') for f in j['frames']])
  if row>=3:
   # Bounds and removal of detached shadows always follow the white probe,
   # keeping colored bodies from being mistaken for black floor ellipses.
   white=[clean(im)[0] for im in probes[1]]
   black=[]
   for im,w in zip(probes[0],white):
    a=np.array(im);a[:,:,3]=np.array(w)[:,:,3];black.append(Image.fromarray(a))
   for atlas,frames in zip(atlases,[black,white]):pack_row([(im,None) for im in frames],row,atlas)
  else:
   for col,(black,white) in enumerate(zip(*probes)):
    a=np.array(white);labs,n=label(a[:,:,3]>2)
    for k,sl in enumerate(find_objects(labs)):
     if sl is None:continue
     member=labs[sl]==k+1;rgb=a[sl][:,:,:3][member]
     if len(rgb)>20 and np.mean((np.max(rgb,axis=1)<170)&(np.ptp(rgb.astype(int),axis=1)<4))>.98:a[sl][member,3]=0
    w=Image.fromarray(a);box=w.getbbox();w=w.crop(box);b=np.array(black);b[:,:,3]=a[:,:,3];b=Image.fromarray(b).crop(box)
    ar=np.array(w);mask=(ar[:,:,3]>80)&(ar[:,:,:3].max(axis=2)<48);labs,n=label(mask);sizes=np.bincount(labs.ravel());sizes[0]=0
    if len(sizes)>1 and sizes.max()>15:
     yy,xx=np.where(labs==sizes.argmax());fw=xx.max()-xx.min()+1;cx=(xx.min()+xx.max())/2;cy=(yy.min()+yy.max())/2;scale=min(61/fw,168/w.width,180/w.height)
    else:cx=w.width/2;cy=w.height*.65;scale=min(168/w.width,180/w.height)
    size=(max(1,round(w.width*scale)),max(1,round(w.height*scale)));x=max(8,min(184-size[0],round(96-cx*scale)));y=max(8,min(200-size[1],round(132-cy*scale)))
    for atlas,im in zip(atlases,[b,w]):atlas.alpha_composite(im.resize(size,Image.Resampling.LANCZOS),(col*192+x,row*208+y))
 black,white=[np.array(im).astype(float) for im in atlases]
 for key,color_name,rgb in palette:
  if rgb is None:continue
  out=white.copy();out[:,:,:3]=black[:,:,:3]+(white[:,:,:3]-black[:,:,:3])*np.array(rgb)/255
  result=Image.fromarray(np.clip(np.round(out),0,255).astype('uint8'))
  if args.rows is not None:
   existing=Image.open(assets/f'{name}-color-{key}.png').convert('RGBA')
   for row in args.rows:existing.paste(result.crop((0,row*208,1536,(row+1)*208)),(0,row*208))
   result=existing
  result.save(assets/f'{name}-color-{key}.png',optimize=True)
 # Keep the legacy white download in sync even though the picker uses original.
 legacy=assets/f'{name}-color-white.png'
 if legacy.exists():
  result=Image.fromarray(np.clip(np.round(white),0,255).astype('uint8'))
  if args.rows is not None:
   existing=Image.open(legacy).convert('RGBA')
   for row in args.rows:existing.paste(result.crop((0,row*208,1536,(row+1)*208)),(0,row*208))
   result=existing
  result.save(legacy,optimize=True)
 print(name,'colors packed',flush=True)
 # A contact sheet for visual verification of actual source container recoloring.
 contact=Image.new('RGBA',(192*4,208*3),'#e9edf3')
 for i,(key,_,_) in enumerate(palette[1:]):
  im=Image.open(assets/f'{name}-color-{key}.png').crop((0,0,192,208));contact.alpha_composite(im,((i%4)*192,(i//4)*208))
 contact.convert('RGB').save(OUT/(name+'-colors.jpg'))
