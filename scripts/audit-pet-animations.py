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
plan=json.loads((assets.parents[1]/'scripts/selected-pet-clips.json').read_text())
for family,forms in plan.items():
 for form,selections in forms.items():
  name=form if family=='ram' else ('nono' if form=='super' else 'nono-'+form)
  for state,selection in selections.items():
   entry=rows[name][states.index(state)]
   assert selection['frames']==entry.get('actionFrames',entry.get('originalFrames')),(name,state,'selection/source mismatch')
total=0
refinements=json.loads((assets.parents[1]/'scripts/loop-refinements.json').read_text())
changes={(e['form'],e['state']):e['reason'] for e in refinements['edits']}
def assessment(form,state):
 if (form,state) in changes:return '更新：'+changes[form,state]
 if state=='jumping':
  if form=='nono-normal':return '保留：炸毛、压缩与眼神变化明显，五帧能读出被触碰的反应。'
  if form in ['nono','nono-annual','classic','super']:return '保留：五帧转身反馈明显，按原方向接回；不倒放整个旋转。'
  return '保留：水滴落下、淋湿、恢复的五帧反应明显；恢复后接下一轮落水。'
 if state=='idle':return '保留：小幅原始动态适合慢速待机，不需要大动作。'
 if state in ['running-left','running-right']:return '保留：朝向清楚，八帧保留移动节奏。'
 if state=='waving':return '保留：四帧内能看清表情或起伏，适合短促招呼；不强求原动作名称。'
 if state=='failed':return '保留：八帧中表情或身体变化清楚，回程接近起点。'
 if state=='waiting':return '保留：六帧短表情适合反复提醒，没有远离身体的道具。'
 if state=='running':return '保留：六帧中的充电、魔方、转身或摇摆足以读出持续活动。'
 return '保留：六帧笑脸或起伏能表达完成反馈，无需强求动作名称对应。'
report=['# 动作检查记录','',
'本轮逐项检查 11 个形态 × 9 个状态。更新 19 行，保留其余 80 行；以少帧下能否看清动作、交互反馈和重复播放的衔接为准。README 仅保留用户安装与选择说明。','',
'时长核对来自本机 ChatGPT.app 的宠物播放实现；是当前安装版本的行为，不承诺未来客户端保持不变。图集无法改写这些时长。','',
'| 状态 | 帧数 | 一遍时长 |','|---|---:|---:|',
'| 待机 | 6 | 6600 ms |','| 左右移动 | 各 8 | 1060 ms |','| 打招呼 | 4 | 700 ms |',
'| 跳跃／hover 反馈 | 5 | 840 ms |','| 失败 | 8 | 1220 ms |','| 等待 | 6 | 1010 ms |',
'| 工作 | 6 | 820 ms |','| 检查 | 6 | 1030 ms |','',
'默认非待机播放三遍后回慢速待机；客户端显式循环时会持续重复。末帧比中间帧长，因此不能靠重复首尾帧掩盖所有接缝。减少动态效果时只显示一帧。','',
'本轮保留全部 hover：浇水、转身、炸毛在五帧里反馈足够明显。叶冠摆动和表情可以补回程；完整旋转必须保持方向，不统一套往返序列。部分带特效动作的身体仍小于待机，后续若重做布局，应整行处理身体和特效，不能逐帧放大。','',
'19 行修改覆盖五种拉姆的待机与左右移动、两种失败表情、两种 NoNo 检查反馈。18 行重排完整原帧；初级失败补入缓存原片的中间姿势，整行使用同一变换并同步配色遮罩。没有重画、拼接眼睛或生成中间姿势。','',
'下表逐项列出保留或修改的判断。帧号供维护核对，动画好坏仍需结合实际时长观察。','',
'| 形态 | Codex 状态 | 原动画 | 原帧号（从 1 起） | 本轮判断 |','|---|---|---|---|---|']
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
  for r,count in enumerate(counts):
   assert im.crop((count*192,r*208,1536,(r+1)*208)).getbbox() is None,(name,r,'unused cell is not transparent')
  assert len(set(hashes))==9,(name,'duplicate row')
  total+=1
 for state,e in zip(states,entries):
  assert e['state']==state,(f,state)
  frames=e.get('actionFrames',e.get('originalFrames',e.get('frames')))
  assert len(frames)==counts[states.index(state)],(f,state)
  source=e.get('gameAction',e.get('sourceFile','base'))
  report.append(f"| {f} | {state} | {source} | {', '.join(map(str,frames))} | {assessment(f,state)} |")
report.extend(['',f'自动检查：{total} 张可下载图集的尺寸、非空帧、单元格边界、动态变化和整行完全重复检查通过。', '', '视觉检查使用默认配色逐帧对照图；本地对照页按相同的客户端时长播放修改前后图集。对动画观感的取舍仍以预览为准；不同形态使用相同原游戏动作属于正常情况。',''])
(assets.parents[1]/'ANIMATION-REVIEW.md').write_text('\n'.join(report))
print(f'{total} color/default atlases; 99 source rows; no empty, clipped, static or exactly duplicate rows.')
