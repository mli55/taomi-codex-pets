"""Pack original game frames and exact body-color masks into the Codex v1 atlas.

Input: JPEXS zoom=4 PNG exports from the official SWFs, both neutral and
body-colored versions. Run prepare-body-probes.py first so single-fill
eyelids are included. No image synthesis or pose generation is performed.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects

parser = argparse.ArgumentParser()
parser.add_argument('--source-dir', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
spec = json.loads((args.source_dir / 'original-actions.json').read_text())
mapping = [('idle','down',6), ('running-right','right',8), ('running-left','left',8),
           ('waving','happy',4), ('jumping','happy',5), ('failed','angry',8),
           ('waiting','boring',6), ('running','rightdown',6), ('review','dance',6)]
forms = {'super':(7,(255,215,39)), 'water':(2,(76,180,235)),
         'wood':(4,(85,187,56)), 'fire':(1,(255,102,37))}
args.output_dir.mkdir(parents=True, exist_ok=True)
metadata={}
for form,(number,reference_color) in forms.items():
    colored_dir=next((args.source_dir/f'final{number}').iterdir())
    neutral_dir=next((args.source_dir/f'neutral{number}').iterdir())
    probe_dir=next((args.source_dir/f'probe{number}').iterdir())
    frame_cache={}
    def read_frame(n):
        if n in frame_cache:return frame_cache[n]
        image=Image.open(colored_dir/f'{n}.png').convert('RGBA')
        neutral=Image.open(neutral_dir/f'{n}.png').convert('RGBA')
        probe=Image.open(probe_dir/f'{n}.png').convert('RGBA')
        a=np.asarray(image); b=np.asarray(neutral); p=np.asarray(probe)
        components,total=label(a[:,:,3]>5)
        difference=np.max(np.abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float)),axis=2)>4
        sizes=np.bincount(components.ravel(),weights=difference.ravel()); sizes[0]=0
        if len(sizes)<2 or sizes.max()<30:return None
        keep=components==int(sizes.argmax())
        ys,xs=np.where(keep); box=(int(xs.min())-1,int(ys.min())-1,int(xs.max())+2,int(ys.max())+2)
        # Largest connected component is the complete pet; discard detached ground shadow.
        delta=b[:,:,:3].astype(float)-p[:,:,:3].astype(float)
        gray=np.clip((delta[:,:,0]+(2/3)*delta[:,:,2])/170,0,1)
        dark=np.clip((delta[:,:,2]+51*gray)/153,0,1)
        white=np.clip((delta[:,:,1]+51*gray+102*dark)/255,0,1)
        clean=a.copy();clean[~keep,3]=0
        neutral_clean=b.copy();neutral_clean[~keep,3]=0
        weights=np.zeros_like(a[:,:,:3]);weights[:,:,0]=np.round(white*255);weights[:,:,1]=np.round(gray*255);weights[:,:,2]=np.round(dark*255);weights[~keep]=0
        result=(Image.fromarray(clean),Image.fromarray(neutral_clean),Image.fromarray(weights,'RGB'),box)
        frame_cache[n]=result;return result
    rows=[]
    for state,game_action,count in mapping:
        action=next(a for a in spec[form]['actions'] if a['label']==game_action)
        available=[n for n in range(action['start'],action['end']+1) if read_frame(n) is not None]
        if not available:raise ValueError(f'{form}/{game_action}: no frames')
        chosen=[available[min(len(available)-1,int(i*len(available)/count))] for i in range(count)]
        rows.append((state,game_action,chosen))
    selected=[frame_cache[n] for _,_,ns in rows for n in ns]
    union=(min(f[3][0] for f in selected),min(f[3][1] for f in selected),max(f[3][2] for f in selected),max(f[3][3] for f in selected))
    width,height=union[2]-union[0],union[3]-union[1]
    scale=min(166/width,182/height)
    dest_size=(round(width*scale),round(height*scale))
    atlas=Image.new('RGBA',(1536,1872));neutral_atlas=Image.new('RGBA',atlas.size);mask_atlas=Image.new('RGB',atlas.size)
    ox=(192-dest_size[0])//2; oy=(208-dest_size[1])//2
    for row,(_,_,ns) in enumerate(rows):
        for col,n in enumerate(ns):
            colored,neutral,mask,_=frame_cache[n]
            pos=(col*192+ox,row*208+oy)
            atlas.paste(colored.crop(union).resize(dest_size,Image.Resampling.LANCZOS),pos)
            neutral_atlas.paste(neutral.crop(union).resize(dest_size,Image.Resampling.LANCZOS),pos)
            mask_atlas.paste(mask.crop(union).resize(dest_size,Image.Resampling.LANCZOS),pos)
    # The production base is neutral; palette choices use the game's verified RGB table.
    neutral_atlas.save(args.output_dir/f'{form}-neutral.png',optimize=True)
    mask_atlas.save(args.output_dir/f'{form}-mask.png',optimize=True)
    metadata[form]={'sourceSpriteId':spec[form]['spriteId'],'rows':[{'state':s,'gameAction':a,'frames':ns} for s,a,ns in rows]}
    print(form,'packed',len(frame_cache),'original frames, box',union)
(args.output_dir/'animation-sources.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')

# Original elemental clips use different Flash registration points per action.
from center_ram import center
center(args.output_dir)
