"""Sample full nested SWF clips, not the short labels in their parent timeline.

Writes derived SWFs/PNGs to --output-dir; never modifies the original SWFs.
The output is consumed by compose-selected-actions.py. Requires prepared probe XMLs.
"""
import argparse
import copy
import json
import subprocess
import xml.etree.ElementTree as E
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MAPPING = [('idle','down',6), ('running-right','right',8), ('running-left','left',8),
           ('waving','happy',4), ('jumping','happy',5), ('failed','angry',8),
           ('waiting','boring',6), ('running','football',6), ('review','dance',6)]
FORMS = {'super': (7,940), 'water': (2,538), 'wood': (4,1029), 'fire': (1,898)}
LEVELS = {'junior':936, 'middle':1532, 'senior':1777, 'classic':2525}

def prepare(source, output, form, extra_actions=('thirst','woter','spring')):
    level = form in LEVELS
    number, sprite_id = (form, LEVELS[form]) if level else FORMS[form]
    neutral_xml = 'lamubone.xml' if level else f'skill{number}.xml'
    probe_xml = 'probe.xml' if level else f'probe{number}.xml'
    tree = E.parse(source / neutral_xml)
    sprites = {n.get('spriteId'): n for n in tree.iter('item') if n.get('type') == 'DefineSpriteTag'}
    def duration(sid, seen=None):
        seen = set() if seen is None else seen
        if sid in seen or sid not in sprites:
            return 0
        seen.add(sid)
        sprite = sprites[sid]
        return max([int(sprite.get('frameCount'))] + [duration(n.get('characterId'), seen)
            for n in sprite.find('subTags') if n.get('characterId')])
    display, snapshots, pending = {}, {}, []
    for node in sprites[str(sprite_id)].find('subTags'):
        kind, depth = node.get('type'), node.get('depth')
        if kind.startswith('RemoveObject'):
            display.pop(depth, None)
        elif kind.startswith('PlaceObject'):
            # Current official master timelines place complete action containers.
            if node.get('characterId'):
                display[depth] = copy.deepcopy(node)
            elif depth in display:
                for child in node:
                    old = display[depth].find(child.tag)
                    if old is not None:
                        display[depth].remove(old)
                    display[depth].append(copy.deepcopy(child))
        elif kind == 'FrameLabelTag':
            pending.append(node.get('name'))
        elif kind == 'ShowFrameTag':
            for name in pending:
                snapshots[name] = copy.deepcopy(display)
            pending.clear()
    labels = list(dict.fromkeys([a for _,a,_ in MAPPING] + list(extra_actions)))
    timeline, actions, rows, frame = [], [], [], 1
    for action in labels:
        objects = snapshots[action]
        length = max(duration(n.get('characterId')) for n in objects.values())
        if not length:
            raise ValueError(f'{form}/{action}: no nested timeline')
        start = frame
        timeline.append(E.Element('item', {'type':'FrameLabelTag','forceWriteAsLong':'true',
            'name':action,'namedAnchor':'false'}))
        for node in objects.values():
            timeline.append(copy.deepcopy(node))
        timeline.extend(E.Element('item', {'type':'ShowFrameTag','forceWriteAsLong':'false'}) for _ in range(length))
        for depth in objects:
            timeline.append(E.Element('item', {'type':'RemoveObject2Tag','depth':depth,'forceWriteAsLong':'false'}))
        for state, name, count in MAPPING:
            if name == action:
                local = [1 + round((length-1)*i/(count-1)) for i in range(count)]
                rows.append({'state':state,'gameAction':action,'sourceFrameCount':length,
                    'actionFrames':local,'frames':[start+n-1 for n in local]})
        candidates = sorted({1+round((length-2)*i/23) for i in range(24)})
        if form == 'super' and action == 'football':
            candidates = sorted(set(candidates) | set(range(10,21,2)))
        if action == 'happy':
            candidates = sorted(set(candidates) | set(range(1,min(length,41))))
        if form == 'junior' and action == 'football':
            candidates = sorted(set(candidates) | set(range(23,69,9)))
        actions.append({'label':action,'start':start,'end':start+length-1,
            'sourceFrameCount':length,'candidateFrames':[start+n-1 for n in candidates]})
        frame += length
    jobs = []
    for prefix, xml in [('neutral',neutral_xml), ('probe',probe_xml)]:
        t = E.parse(source/xml)
        master = t.find(f'.//item[@spriteId="{sprite_id}"]')
        master.set('frameCount',str(frame-1))
        sub = master.find('subTags'); sub.clear()
        sub.extend(copy.deepcopy(timeline))
        dest = output / f'{form}-{prefix}.xml'
        t.write(dest, encoding='utf-8', xml_declaration=True)
        jobs.append((dest, sprite_id, sorted({n for a in actions for n in a['candidateFrames']})))
    return {'spriteId':sprite_id,'actions':actions,'rows':sorted(rows,key=lambda r:[s for s,_,_ in MAPPING].index(r['state']))}, jobs

def export(job, jar):
    xml, sprite, frames = job
    swf = xml.with_suffix('.swf')
    with xml.with_suffix('.log').open('w') as log:
        subprocess.run(['java','-Djava.awt.headless=true','-jar',str(jar),'-xml2swf',str(xml),str(swf)],stdout=log,stderr=log,check=True)
        subprocess.run(['java','-Djava.awt.headless=true','-jar',str(jar),'-selectid',str(sprite),
            '-select',str(sprite)+':'+','.join(map(str,frames)),'-zoom','4','-ignorebackground',
            '-export','sprite',str(xml.with_suffix('')),str(swf)],stdout=log,stderr=log,check=True)
    print(xml.stem, 'exported',len(frames),'full-timeline samples',flush=True)

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--ffdec',type=Path,required=True)
    p.add_argument('--levels-dir',type=Path)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    spec,jobs={},[]
    for form in FORMS:
        spec[form],more=prepare(a.source_dir,a.output_dir,form);jobs.extend(more)
    if a.levels_dir:
        for form in LEVELS:
            spec[form],more=prepare(a.levels_dir,a.output_dir,form);jobs.extend(more)
    (a.output_dir/'original-actions.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda job:export(job,a.ffdec),jobs))
