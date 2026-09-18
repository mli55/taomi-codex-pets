"""Move energetic NoNo gestures into Codex's five-frame hover (jumping) row.
Run once after composing source atlases and their colors; metadata guards repeats.
"""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'dist/assets'
COUNTS=[6,8,8,4,5,8,6,6,6]
def sample(length,count):return [round(i*(length-1)/(count-1)) for i in range(count)]
for name,other in [('nono',3),('nono-normal',8),('nono-annual',8)]:
 meta=ROOT/(name+'-animation-sources.json');rows=json.loads(meta.read_text())
 if rows[4].get('hoverRemapped'):continue
 paths=[ROOT/(name+'.png')]+sorted(ROOT.glob(name+'-color-*.png'))
 for path in paths:
  atlas=Image.open(path);old=atlas.copy()
  for target,source in [(4,other),(other,4)]:
   atlas.paste((0,0,0,0),(0,target*208,1536,(target+1)*208))
   for col,src in enumerate(sample(COUNTS[source],COUNTS[target])):
    atlas.paste(old.crop((src*192,source*208,(src+1)*192,(source+1)*208)),(col*192,target*208))
  atlas.save(path,optimize=True)
 old=[dict(r) for r in rows]
 for target,source in [(4,other),(other,4)]:
  rows[target]={**old[source],'state':old[target]['state'],'originalFrames':[old[source]['originalFrames'][i] for i in sample(COUNTS[source],COUNTS[target])],'hoverRemapped':True}
 meta.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 print(name,'hover gesture remapped',flush=True)
