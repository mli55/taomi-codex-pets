// Shared by browser ZIP exports and the CLI installer.
(()=>{
'use strict';
const states=['idle','running-right','running-left','waving','jumping','failed','waiting','running','review'];
const counts=[6,8,8,4,5,8,6,6,6];
const instructions=`本包使用原游戏素材，现有 spritesheet.png 为可安装的 v1 成品（1536×1872，8列9行）。

如需补全 v2，请先读取 v2-reference.json，并实际查看 spritesheet.png 的全部九行动作作为参考。正面和左右候选帧的位置已标注；左右行走姿势只是候选，需要检查视线含义，不是已批准的 looking 帧。
保留原图集前九行的像素、配色、帧顺序与单格大小。只为缺失的16个 looking 方向补素材；优先复用合适的原素材。原游戏的背面/up 不能作为抬头，正面/down 不能作为低头。不要通过旋转整只角色或重复帧冒充不同视线。
附带图集已包含当前选择的配色。补图时把图集和从中裁出的正面、侧面参考实际传给生成工具；只读文字不足以约束外观。保持原版轮廓、眼睛、材质和尺寸，避免额外特效。
每个方向是一个姿势，不是各做一套动画。000为上，090为屏幕右，180为下，270为屏幕左；按顺时针每22.5度排列。必须检查上下和斜向的视线，以及相邻方向的大小、位置是否连续。
全部16方向通过检查后，追加两行，输出1536×2288图集，再将 spriteVersionNumber 改为2。不要把未完成的图集标成v2。保留原v1包，v2另存目录。
仅安装现有包时直接安装v1；用户要求补全v2时可据此继续，无需重做九种动作。
`;
function manifest(displayName){return {schemaVersion:1,displayName,source:'spritesheet.png',sourceSpriteVersionNumber:1,targetSpriteVersionNumber:2,cellSize:[192,208],targetSize:[1536,2288],preserveRows:states.map((state,row)=>({row,state,frames:counts[row]})),references:[{role:'neutral',row:0,column:0,status:'reference'},{role:'screen-right',row:1,column:0,status:'candidate-needs-gaze-review'},{role:'screen-left',row:2,column:0,status:'candidate-needs-gaze-review'}],lookDirections:Array.from({length:16},(_,i)=>({degrees:i*22.5,row:9+Math.floor(i/8),column:i%8,status:'needs-source-review-or-completion'})),notes:'No look direction is certified yet. Side-facing original frames are candidates; rear-facing game movement is not upward gaze.'};}
globalThis.PetUpgrade={instructions,manifest};
})();
