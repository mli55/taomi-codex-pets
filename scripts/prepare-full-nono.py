"""Export candidate poses from complete official NoNo action timelines."""
import argparse,json,subprocess,xml.etree.ElementTree as E
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

MAPPING={'waving':('action',2),'jumping':('exp',3),'failed':('exp',4),
         'waiting':('action',1),'running':('action',7),'review':('exp',1)}

def run(source, output, variant, state, kind, number, jar):
    name=f'{variant}-{kind}-{number}'
    swf=source/(name+'.swf');xml=output/(name+'.xml')
    with (output/(name+'.log')).open('w') as log:
        subprocess.run(['java','-Djava.awt.headless=true','-jar',str(jar),'-swf2xml',str(swf),str(xml)],stdout=log,stderr=log,check=True)
        tree=E.parse(xml);symbol=tree.find('.//item[@type="SymbolClassTag"]')
        names=[n.text for n in symbol.find('names')];sid=symbol.find('tags')[names.index('pet')].text
        sprites={n.get('spriteId'):n for n in tree.iter('item') if n.get('type')=='DefineSpriteTag'}
        pet=sprites[sid];length=int(pet.get('frameCount'))
        if length==1:
            def duration(id,seen=None):
                seen=set() if seen is None else seen
                if id in seen or id not in sprites:return 0
                seen.add(id);n=sprites[id]
                return max([int(n.get('frameCount'))]+[duration(x.get('characterId'),seen) for x in n.find('subTags') if x.get('characterId')])
            length=duration(sid);pet.set('frameCount',str(length))
            for _ in range(length-1):E.SubElement(pet.find('subTags'),'item',{'type':'ShowFrameTag','forceWriteAsLong':'false'})
            xml=output/(name+'-expanded.xml');tree.write(xml,encoding='utf-8',xml_declaration=True);swf=xml.with_suffix('.swf')
            subprocess.run(['java','-Djava.awt.headless=true','-jar',str(jar),'-xml2swf',str(xml),str(swf)],stdout=log,stderr=log,check=True)
        frames=sorted({1+round((length-2)*i/23) for i in range(24)})
        if variant=='annual' and state=='running':
            frames=sorted(set(frames) | {1,8,14,21,27,34})
        dest=output/name
        subprocess.run(['java','-Djava.awt.headless=true','-jar',str(jar),'-selectid',sid,
            '-select',sid+':'+','.join(map(str,frames)),'-zoom','4','-ignorebackground',
            '-export','sprite',str(dest),str(swf)],stdout=log,stderr=log,check=True)
    print(name,'exported',length,'frame timeline',flush=True)
    return {'variant':variant,'state':state,'sourceFile':name+'.swf','sourceSpriteId':int(sid),
        'sourceFrameCount':length,'candidateFrames':frames,'directory':name}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--ffdec',type=Path,required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True);jobs=[]
    for v in ['normal','super','annual']:
        for state,(kind,n) in MAPPING.items():
            if v=='annual' and state=='waiting':kind,n='exp',2
            if v=='annual' and state=='running':kind,n='action',6
            if v=='normal' and state=='running':n=4
            jobs.append((a.source_dir,a.output_dir,v,state,kind,n,a.ffdec))
    for variant in ['normal','super']:
        jobs.append((a.source_dir,a.output_dir,variant,'angry','exp',2,a.ffdec))
    jobs.append((a.source_dir,a.output_dir,'super','summon','action',6,a.ffdec))
    # The annual cube shot places the prop far from the body. Keep its ball
    # action available for the compact working loop instead.
    jobs.append((a.source_dir,a.output_dir,'annual','ball','action',4,a.ffdec))
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda j:run(*j),jobs))
    (a.output_dir/'candidates.json').write_text(json.dumps(results,indent=2)+'\n')
