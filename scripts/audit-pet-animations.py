"""Check published color atlases and write the current 99-row source inventory."""
from pathlib import Path
import json,hashlib
from PIL import Image

assets=Path(__file__).resolve().parents[1]/'dist/assets'
counts=[6,8,8,4,5,8,6,6,6]
states=['idle','running-right','running-left','waving','jumping','failed','waiting','running','review']
ram={**json.loads((assets/'animation-sources.json').read_text()),**json.loads((assets/'ram-level-animation-sources.json').read_text())}
rows={k:v['rows'] for k,v in ram.items()}
for f in ['nono-normal','nono','nono-annual']:rows[f]=json.loads((assets/(f+'-animation-sources.json')).read_text())
colors=json.loads((assets/'palette.json').read_text())
ncolors=json.loads((assets/'nono-palette.json').read_text())
total=0
report=['# 动作检查记录','', '当前版本在本地预览；此前快照为 `7132242`。', '',
'逐帧检查 11 个形态的九种 Codex 状态。优先区分悬停、工作与检查；保留原游戏图形。打招呼与悬停可来自同一长动画，但使用不同片段。循环首尾回到同一姿势的重复帧用于衔接，不代表不同状态复用同一动画。', '',
'拉姆工作采用原口渴动作出现水瓶、气泡前的片段。悬停采用转身，并限制舞台位移；每行使用统一缩放，配色遮罩与图形一起定位。初级和中级正面仍保留此前确认的原动态。', '',
'NoNo：普通使用充电工作、惊讶等待、生气悬停；超能使用魔方工作、惊讶等待、召唤旋转悬停；至尊使用开机后半段工作、轻微皱眉等待、惊讶打招呼、召唤旋转悬停。三个版本的检查状态使用高兴；超能打招呼按选择使用生气片段。', '',
'预览按客户端逐帧时长播放，非待机三遍后回待机。动画文件无法改变客户端状态触发或持续时间。', '',
'| 形态 | Codex 状态 | 原动画 | 原帧号（从 1 起） |','|---|---|---|---|']
for f,entries in rows.items():
 names=[f+'.png']+([f+'-'+key+'.png' for key in colors] if f in ram else [f+'-color-'+c['id']+'.png' for c in ncolors if c['rgb'] is not None])
 for name in names:
  im=Image.open(assets/name).convert('RGBA');assert im.size==(1536,1872),name
  hashes=[]
  for r,count in enumerate(counts):
   frames=[]
   for j in range(count):
    tile=im.crop((j*192,r*208,(j+1)*192,(r+1)*208));b=tile.getbbox();assert b is not None,(name,r,j)
    assert b[0]>0 and b[1]>0 and b[2]<192 and b[3]<208,(name,r,j,'touching cell boundary',b)
    frames.append(tile.tobytes())
   assert len(set(frames))>1,(name,r,'static row')
   hashes.append(hashlib.sha256(b''.join(frames)).hexdigest())
  assert len(set(hashes))==9,(name,'duplicate row')
  total+=1
 for state,e in zip(states,entries):
  assert e['state']==state,(f,state)
  frames=e.get('actionFrames',e.get('originalFrames',e.get('frames')))
  assert len(frames)==counts[states.index(state)],(f,state)
  source=e.get('gameAction',e.get('sourceFile','base'))
  report.append(f"| {f} | {state} | {source} | {', '.join(map(str,frames))} |")
report.extend(['',f'自动检查：{total} 张可下载图集的尺寸、非空帧、单元格边界、动态变化和整行完全重复检查通过。', '', '视觉检查使用默认配色逐帧图，并在本地网页确认实际预览。对动画观感的取舍仍以预览为准；不同形态使用相同原游戏动作属于正常情况。',''])
(assets.parents[1]/'ANIMATION-REVIEW.md').write_text('\n'.join(report))
print(f'{total} color/default atlases; 99 source rows; no empty, clipped, static or exactly duplicate rows.')
