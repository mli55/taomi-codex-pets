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
visual_path=assets.parents[1]/'scripts/animation-audit.json'
visual=json.loads(visual_path.read_text()) if visual_path.exists() else {'rows':[]}
reviews={(e['form'],e['state']):e for e in visual['rows']}
assert len(reviews)==len(visual['rows']),'duplicate visual review'
for (form,state),review in reviews.items():
 entry=rows[form][states.index(state)]
 assert review['frames']==entry.get('actionFrames',entry.get('originalFrames',entry.get('frames'))),(form,state,'visual review is stale; review the changed frames')
 assert review['source']==entry.get('gameAction',entry.get('sourceFile','base')),(form,state,'visual review source changed')
 assert review['verdict'] in ('retain','change'),(form,state,'invalid visual verdict')
row_count=sum(len(entries) for entries in rows.values())
changed_count=len(changes)
super_notes={
 'waving':'waving 四帧换成正面闭嘴微笑与轻点头，宝石贴近身体两侧',
 'jumping':'jumping 五帧只保留一次向前翻转，不把多个翻转压进同一轮',
 'running':'running 六帧按原方向完成连续摇摆与绕行',
 'waiting':'waiting 六帧保留小幅皱眉，排除突然塌落的姿势',
 'review':'review 六帧按原时间方向微笑，并以闭嘴姿势收尾',
}
super_changes=[note for state,note in super_notes.items() if ('super',state) in changes]
def assessment(form,state):
 if (form,state) in reviews:
  review=reviews[form,state]
  return ('待调整：' if review['verdict']=='change' else '复查保留：')+review['reason']
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
pending_count=sum(e['verdict']=='change' for e in reviews.values())
form_names={'junior':'初级拉姆','middle':'中级拉姆','senior':'高级拉姆','classic':'超级拉姆','water':'水系拉姆','wood':'木系拉姆','fire':'火系拉姆','nono-normal':'普通 NoNo','nono':'超能 NoNo','nono-annual':'至尊 NoNo'}
state_names=dict(zip(states,['待机','向右','向左','打招呼','悬停','失败','等待','工作','检查 / 完成反馈']))
summary=[]
if reviews:
 summary=['| 形态 | 保留 | 建议调整的动作 |','|---|---:|---|']
 for form,name in form_names.items():
  entries=[e for e in reviews.values() if e['form']==form]
  if entries:
   summary.append(f"| {name} | {sum(e['verdict']=='retain' for e in entries)} | {'、'.join(state_names[e['state']] for e in entries if e['verdict']=='change') or '无'} |")
 summary.append('')
report=['# 动作检查记录','',
f'源帧清单覆盖 {len(rows)} 个形态 × {len(states)} 个状态，共 {row_count} 行。已落地的历史优化共 {changed_count} 行；这个数量只记录修改，不能据此认定其余动作已通过视觉检查。','',
*([f"本轮以 `{visual['baseline'][:7]}` 为基准，逐项复查神力超级拉姆之外的 {len({e['form'] for e in reviews.values()})} 个形态、{len(reviews)} 个动作：{len(reviews)-pending_count} 个保留，{pending_count} 个建议调整。本轮只新增检查记录，尚未修改这些动画图集。详细依据保存在 `scripts/animation-audit.json`。",''] if reviews else []),
*summary,
'时长核对来自本机 ChatGPT.app 的宠物播放实现；是当前安装版本的行为，不承诺未来客户端保持不变。图集无法改写这些时长。','',
'| 状态 | 帧数 | 一遍时长 |','|---|---:|---:|',
'| 待机 | 6 | 6600 ms |','| 左右移动 | 各 8 | 1060 ms |','| 打招呼 | 4 | 700 ms |',
'| 跳跃／hover 反馈 | 5 | 840 ms |','| 失败 | 8 | 1220 ms |','| 等待 | 6 | 1010 ms |',
'| 工作 | 6 | 820 ms |','| 检查 | 6 | 1030 ms |','',
'默认非待机播放三遍后回慢速待机；客户端显式循环时会持续重复。末帧比中间帧长，因此不能靠重复首尾帧掩盖所有接缝。减少动态效果时只显示一帧。','',
'hover 逐形态检查浇水、转身和炸毛在五帧里的反馈与循环衔接。叶冠摆动和表情可以补回程；完整旋转必须保持方向，不统一套往返序列。部分带特效动作的身体仍小于待机，后续若重做布局，应整行处理身体和特效，不能逐帧放大。','',
'此前的 19 行优化覆盖五种拉姆的待机与左右移动、两种失败表情、两种 NoNo 检查反馈；其中初级失败补入缓存原片中间姿势，其余重排完整原帧。整行保持一致变换并同步配色遮罩，没有重画或生成中间姿势。','',
*([f'本次神力超级拉姆追加复查 {len(super_changes)} 行：'+ '；'.join(super_changes)+'。各行具体取舍见下表及改动清单中的 reason。',''] if super_changes else []),
'下表的“复查保留”和“待调整”为本轮逐项结论；神力超级拉姆沿用上一轮已完成的检查。帧号均从 1 起，供维护核对。','',
'| 形态 | Codex 状态 | 原动画 | 原帧号（从 1 起） | 当前判断 |','|---|---|---|---|---|']
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
report.extend(['',f'自动检查：{total} 张可下载图集的尺寸、非空帧、单元格边界、动态变化和整行完全重复检查通过。这些结构检查不能证明动画衔接自然。', '', '视觉检查使用默认配色逐帧对照图，并按客户端时长检查持续循环和三遍后回待机。配色版本另做结构检查，没有逐个颜色重复视觉审美判断。不同形态使用相同原游戏动作属于正常情况。',''])
if reviews:
 report.extend(['## 待调整项目与原片覆盖','', '候选帧是后续试放方案，尚未写入图集；最终采用前仍需验证整行比例、遮罩、循环和回待机。','', '| 形态 / 状态 | 处理建议 | 原片覆盖 / 限制 |','|---|---|---|'])
 for review in reviews.values():
  if review['verdict']=='change':
   report.append(f"| {review['form']} / {review['state']} | {review.get('nextStep','重新选择或处理原帧，并按客户端时长试放。')} | {review.get('coverage','见逐项视觉检查记录。')} |")
 report.append('')
(assets.parents[1]/'ANIMATION-REVIEW.md').write_text('\n'.join(report))
print(f'{total} color/default atlases; {row_count} source rows; no empty, clipped, static or exactly duplicate rows.')
