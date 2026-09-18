"""Pack reviewed short clips from the full official timelines into Codex v1.

The fixed row counts are a client contract, not a frame-rate setting. Source
timelines remain untouched. Selections below are action-local frame numbers.
"""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects

STATES=['idle','running-right','running-left','waving','jumping','failed','waiting','running','review']
COUNTS=[6,8,8,4,5,8,6,6,6]

def sample(lo,hi,count):
    return [round(lo+(hi-lo)*i/(count-1)) for i in range(count)]

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

def pack_row(frames,row,atlas,mask_atlas=None,base_scale=None,registration=None):
    boxes=[im.getbbox() for im,_ in frames]
    if any(b is None for b in boxes):raise ValueError(f'Empty selected frame in row {row}')
    if registration=='bounded' or isinstance(registration,dict) and registration.get('mode')=='bounded':
        # One scale for the whole row; keep a small amount of source travel.
        # Long stage translations must not shrink a desktop hover reaction.
        width=max(b[2]-b[0] for b in boxes);height=max(b[3]-b[1] for b in boxes)
        scale=min(168/width,182/height,base_scale if base_scale is not None else 100)
        centers=[((b[0]+b[2])/2,(b[1]+b[3])/2) for b in boxes]
        cx=sum(x for x,y in centers)/len(centers);cy=sum(y for x,y in centers)/len(centers)
        if isinstance(registration,dict):
            scale=registration.get('scale',scale);cx,cy=registration.get('sourceCenter',[cx,cy])
        for col,((im,mask),b,(x,y)) in enumerate(zip(frames,boxes,centers)):
            size=(max(1,round((b[2]-b[0])*scale)),max(1,round((b[3]-b[1])*scale)))
            dx=round(max(-8,min(8,(x-cx)*scale)));dy=round(max(-10,min(10,(y-cy)*scale)))
            if size[0]>188 or size[1]>204:raise ValueError('New pose exceeds the preserved scale')
            x=max(2,min(190-size[0],(192-size[0])//2+dx));y=max(2,min(206-size[1],(208-size[1])//2+dy))
            dest=(col*192+x,row*208+y)
            atlas.paste(im.crop(b).resize(size,Image.Resampling.LANCZOS),dest)
            if mask_atlas is not None:mask_atlas.paste(mask.crop(b).resize(size,Image.Resampling.LANCZOS),dest)
        return scale
    box=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes))
    if isinstance(registration,dict) and registration.get('mode')=='fixed':
        box=tuple(registration['sourceBox']);scale=registration['scale']
        ox=(192-round((box[2]-box[0])*scale))//2;oy=(208-round((box[3]-box[1])*scale))//2
        dx,dy=registration.get('cellOffset',[0,0]);ox+=dx;oy+=dy
        for col,((im,mask),b) in enumerate(zip(frames,boxes)):
            # Extend the source crop for a new pose, retaining the previous scale/origin.
            crop=(min(box[0],b[0]),min(box[1],b[1]),max(box[2],b[2]),max(box[3],b[3]))
            size=(round((crop[2]-crop[0])*scale),round((crop[3]-crop[1])*scale))
            x=ox+round((crop[0]-box[0])*scale);y=oy+round((crop[1]-box[1])*scale)
            if x<1 or y<1 or x+size[0]>191 or y+size[1]>207:raise ValueError('New frame does not fit the preserved scale/origin')
            atlas.paste(im.crop(crop).resize(size,Image.Resampling.LANCZOS),(col*192+x,row*208+y))
            if mask_atlas is not None:mask_atlas.paste(mask.crop(crop).resize(size,Image.Resampling.LANCZOS),(col*192+x,row*208+y))
        return scale
    width,height=box[2]-box[0],box[3]-box[1]
    scale=min(168/width,182/height,base_scale if base_scale is not None else 100)
    size=(max(1,round(width*scale)),max(1,round(height*scale)))
    ox=(192-size[0])//2;oy=(208-size[1])//2
    for col,(im,mask) in enumerate(frames):
        dest=(col*192+ox,row*208+oy)
        atlas.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),dest)
        if mask_atlas is not None:mask_atlas.paste(mask.crop(box).resize(size,Image.Resampling.LANCZOS),dest)
    return scale

def ram_targets(form,action,count,length):
    if form=='senior' and action in ['left','right']:return list(range(1,9))
    if action in ['down','left','right']:return sample(1,length-2,count)
    if action=='dance':
        if form=='middle' and count==4:return [1,10,19,28]
        return sample(18,63,count) if form=='classic' else sample(136,181,count)
    if action=='football':
        lo,hi={'super':(10,20),'junior':(23,68),'middle':(20,52),'classic':(20,52)}.get(form,(7,38))
        return sample(lo,hi,count)
    if action=='happy':
        # Front-facing smiles and a short bounce; omit the somersault section.
        clips={
            'super':{4:[8,12,24,34],5:[8,12,20,28,34]},
            'junior':{4:[5,13,21,29],5:[5,11,17,23,29]},
            'middle':{4:[1,4,7,10],5:[1,3,5,7,10]},
            'classic':{4:[20,25,30,35],5:[20,24,28,32,35]},
        }
        return clips.get(form,{4:[1,5,25,31],5:[1,4,7,25,30]})[count]
    if action=='angry':
        lo,hi={'super':(1,18),'junior':(14,107),'classic':(1,37),'middle':(1,40)}.get(form,(1,length-2))
        return sample(lo,hi,count)
    if action=='boring':
        lo,hi={'super':(1,34),'junior':(22,83),'classic':(138,175),'middle':(1,65)}.get(form,(1,40))
        return sample(lo,hi,count)
    raise ValueError(action)

def compose_ram(source,output):
    spec=json.loads((source/'original-actions.json').read_text());metadata={}
    for form,info in spec.items():
        nd=next((source/(form+'-neutral')).iterdir());pd=next((source/(form+'-probe')).iterdir())
        atlas=Image.new('RGBA',(1536,1872));masks=Image.new('RGB',atlas.size);rows=[];cache={};scale=None
        for row,(state,count) in enumerate(zip(STATES,COUNTS)):
            entry=next(r for r in info['rows'] if r['state']==state);source_action='dance' if form=='middle' and state=='waving' else entry['gameAction'];action=next(a for a in info['actions'] if a['label']==source_action)
            valid=[]
            for n in action['candidateFrames']:
                if not (nd/f'{n}.png').exists():continue
                if n not in cache:cache[n]=clean(Image.open(nd/f'{n}.png'),Image.open(pd/f'{n}.png'))
                if cache[n][0].getbbox():valid.append(n)
            targets=ram_targets(form,action['label'],count,action['sourceFrameCount'])
            chosen=[min(valid,key=lambda n:abs(n-action['start']+1-t)) for t in targets]
            used_scale=pack_row([cache[n] for n in chosen],row,atlas,masks,scale)
            if scale is None:scale=used_scale
            rows.append({'state':state,'gameAction':action['label'],'sourceFrameCount':action['sourceFrameCount'],
                'actionFrames':[n-action['start']+1 for n in chosen],'frames':chosen})
        if form=='middle':
            # Put the more animated dance clip on jumping; exchange its old happy clip with review.
            mapping={4:(8,[0,1,2,4,5]),8:(4,[0,1,2,2,3,4])}
            previous=[dict(entry) for entry in rows]
            for image in [atlas,masks]:
                old=image.copy()
                for target,(source,indices) in mapping.items():
                    image.paste(0,(0,target*208,1536,(target+1)*208))
                    for col,index in enumerate(indices):
                        image.paste(old.crop((index*192,source*208,(index+1)*192,(source+1)*208)),(col*192,target*208))
            for target,(source,indices) in mapping.items():
                rows[target]={**previous[source],'state':previous[target]['state'],
                    'actionFrames':[previous[source]['actionFrames'][i] for i in indices],
                    'frames':[previous[source]['frames'][i] for i in indices]}
        atlas.save(output/f'{form}-neutral.png',optimize=True);masks.save(output/f'{form}-mask.png',optimize=True)
        metadata[form]={'sourceSpriteId':info['spriteId'],'sampling':'reviewed clips from full nested timelines','rows':rows}
        print(form,'packed',flush=True)
    for filename,forms in [('animation-sources.json',['super','water','wood','fire']),('ram-level-animation-sources.json',['junior','middle','senior','classic'])]:
        (output/filename).write_text(json.dumps({k:metadata[k] for k in forms},ensure_ascii=False,indent=2)+'\n')

def nono_targets(variant,state,count,length):
    if variant=='super' and state=='angry':return [14,18,22,26,30]
    if variant=='annual' and state=='waiting':return [11,14,16,18,16,11]
    if variant=='annual' and state=='running':return [45,48,50,56,59,64]
    if state=='waving':
        frames={'normal':[1,10,20,67],'super':[59,74,89,103],'annual':[10,17,23,34]}[variant]
        return [frames[i] for i in sample(0,len(frames)-1,count)]
    ranges={'jumping':(1,36),'failed':(1,min(90,length-2)),'waiting':(1,17),'review':(1,41)}
    if state=='running':ranges[state]={'normal':(29,85),'super':(46,103),'annual':(1,34)}[variant]
    if variant=='annual' and state=='review':ranges[state]=(1,28)
    if variant=='super' and state=='review':ranges[state]=(1,25)
    lo,hi=ranges[state];return sample(lo,min(hi,length-2),count)

def compose_nono(source,output,existing):
    candidates=json.loads((source/'candidates.json').read_text())
    for variant in ['normal','super','annual']:
        name='nono' if variant=='super' else 'nono-'+variant
        atlas=Image.open(existing/(name+'.png')).convert('RGBA')
        old=json.loads((existing/(name+'-animation-sources.json')).read_text());rows=[]
        for row,(state,count) in enumerate(zip(STATES,COUNTS)):
            if row<3:rows.append(old[row]);continue
            atlas.paste((0,0,0,0),(0,row*208,1536,(row+1)*208))
            hover_source='waving' if variant=='super' else 'review'
            source_state=('angry' if variant=='super' else hover_source) if state=='jumping' else ('jumping' if state==hover_source else state)
            entry=next(e for e in candidates if e['variant']==variant and e['state']==source_state)
            folder=next((source/entry['directory']).iterdir());cache={}
            for n in entry['candidateFrames']:
                im,_=clean(Image.open(folder/f'{n}.png'))
                if im.getbbox():cache[n]=(im,None)
            targets=nono_targets(variant,source_state,count,entry['sourceFrameCount'])
            chosen=[min(cache,key=lambda n:abs(n-t)) for t in targets]
            pack_row([cache[n] for n in chosen],row,atlas)
            rows.append({'state':state,'sourceFile':entry['sourceFile'],'sourceFrameCount':entry['sourceFrameCount'],'originalFrames':chosen,'hoverRemapped':source_state!=state})
        atlas.save(output/(name+'.png'),optimize=True)
        (output/(name+'-animation-sources.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        print(name,'packed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ram-source',type=Path,required=True);p.add_argument('--nono-source',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--existing-assets',type=Path,default=Path('dist/assets'))
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    compose_ram(a.ram_source,a.output_dir);compose_nono(a.nono_source,a.output_dir,a.existing_assets)
