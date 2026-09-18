(()=>{
'use strict';
const PETS = {
  junior:{name:'初级拉姆'},
  middle:{name:'中级拉姆'},
  senior:{name:'高级拉姆'},
  classic:{name:'超级拉姆'},
  super: { name: '神力超级拉姆', hue: 51 },
  water: { name: '神奇水系拉姆', hue: 204 },
  wood: { name: '弹力木系拉姆', hue: 116 },
  fire: { name: '霹雳火系拉姆', hue: 23 }
};
// Only combinations present in the original game assets are selectable.
const COMBINATIONS = {
  normal:{junior:'junior',middle:'middle',senior:'senior'},
  divine:{water:'water',wood:'wood',fire:'fire'}, classic:{base:'classic',super:'super'}
};
let type='classic', variant='super';
const selectedVariants={normal:'junior',divine:'water',classic:'super'};
function syncConfiguration(){
  markGroup('.type-option',el=>el.dataset.type===type);
  markGroup('.variant-option',el=>el.dataset.variant===variant);
  root.querySelectorAll('.variant-option').forEach(el=>{
    el.disabled=!Object.hasOwn(COMBINATIONS[type],el.dataset.variant);
  });
}
function chooseType(next){
  if(!Object.hasOwn(COMBINATIONS,next))return;
  type=next;variant=selectedVariants[type];
  syncConfiguration();loadForm(COMBINATIONS[type][variant]);
}
function chooseVariant(next){
  if(!Object.hasOwn(COMBINATIONS[type],next))return;
  variant=next;selectedVariants[type]=next;
  syncConfiguration();loadForm(COMBINATIONS[type][variant]);
}
const PALETTE = {"1": {"name": "红色", "slug": "red", "offset": [255, -199, -250], "swatch": "#ff3805"}, "2": {"name": "黄色", "slug": "yellow", "offset": [0, -21, -255], "swatch": "#ffea00"}, "3": {"name": "天蓝色", "slug": "blue", "offset": [-215, -57, 31], "swatch": "#28c6ff"}, "4": {"name": "粉红色", "slug": "pink", "offset": [51, -148, 0], "swatch": "#ff6bff"}, "5": {"name": "橘黄色", "slug": "orange", "offset": [102, -118, -255], "swatch": "#ff8900"}, "6": {"name": "灰色", "slug": "gray", "offset": [-150, -150, -150], "swatch": "#696969"}, "7": {"name": "黑色", "slug": "black", "offset": [-215, -210, -215], "swatch": "#282d28"}, "8": {"name": "紫色", "slug": "purple", "offset": [-82, -194, 112], "swatch": "#ad3dff"}, "9": {"name": "土色", "slug": "brown", "offset": [-87, -148, -199], "swatch": "#a86b38"}, "10": {"name": "绿色", "slug": "green", "offset": [-189, -41, -189], "swatch": "#42d642"}};
const root=document.getElementById('ram-panel');
const PREVIEW_ACTIONS=PetPlayback.actions;
const actionGroup=root.querySelector('.states');
actionGroup.replaceChildren(...PREVIEW_ACTIONS.map(([key,name])=>{const b=document.createElement('button');b.dataset.state=key;b.textContent=name;b.title=key;b.setAttribute('aria-pressed',String(key==='idle'));b.classList.toggle('selected',key==='idle');return b;}));
const $ = id => document.getElementById('ram-'+id);
const canvas = $('pet'), ctx = canvas.getContext('2d');
const sheet = document.createElement('canvas'); sheet.width=1536; sheet.height=1872;
const sheetCtx=sheet.getContext('2d',{willReadFrequently:true});
let form='super', color='2', state='idle', original=null, currentFrame=0, playbackRow=0, loadedForm=null, generation=0;
let hovering=false;
let paused=matchMedia('(prefers-reduced-motion: reduce)').matches;
const imageCache=new Map(); let bodyMask=null;
function markGroup(selector, selected) { root.querySelectorAll(selector).forEach(el=>{const active=selected(el);el.classList.toggle('selected',active);el.setAttribute('aria-pressed',String(active));}); }
const player=PetPlayback.createPlayer(frame=>{
  currentFrame=frame.column;playbackRow=frame.row;
  canvas.dataset.animationState=frame.state;
  canvas.dataset.frame=String(frame.column+1);
  canvas.dataset.row=String(frame.row);
  const activeState=hovering?'jumping':state;
  const selected=actionGroup.querySelector('[data-state="'+activeState+'"]');
  if(selected)$('state-label').textContent=selected.textContent+(frame.state==='idle'&&activeState!=='idle'?' · 已回到待机':'');
  render();
},matchMedia('(prefers-reduced-motion: reduce)').matches);
function resetFrame(){player.select(hovering?'jumping':state);}
canvas.addEventListener('pointerenter',event=>{if(event.pointerType==='touch')return;hovering=true;resetFrame();});
canvas.addEventListener('pointerleave',()=>{hovering=false;resetFrame();});
canvas.addEventListener('pointercancel',()=>{hovering=false;resetFrame();});
function render(){
  ctx.clearRect(0,0,576,624);if(loadedForm!==form)return;
  ctx.drawImage(sheet,currentFrame*192,playbackRow*208,192,208,0,0,576,624);
}
function animate(time){
  player.tick(time,paused||document.hidden||root.hidden||loadedForm!==form);
  requestAnimationFrame(animate);
}
function tintedPixels(source,mask){
  const pixels=new ImageData(new Uint8ClampedArray(source.data),source.width,source.height);
  const offsets=PALETTE[color].offset;
  const white=offsets.map(v=>Math.max(0,Math.min(255,255+v))-255);
  const gray=offsets.map(v=>Math.max(0,Math.min(255,204+v))-204);
  const dark=offsets.map(v=>Math.max(0,Math.min(255,153+v))-153);
  for(let i=0;i<pixels.data.length;i+=4){const w=mask[i]/255,g=mask[i+1]/255,d=mask[i+2]/255;if(!w&&!g&&!d)continue;
    for(let c=0;c<3;c++)pixels.data[i+c]=Math.max(0,Math.min(255,pixels.data[i+c]+white[c]*w+gray[c]*g+dark[c]*d));
  }
  return pixels;
}
function applyColor(){
  if(!original||loadedForm!==form)return;
  sheetCtx.putImageData(tintedPixels(original,bodyMask),0,0);
  render();
}
async function loadForm(next){
  form=next;const request=++generation;loadedForm=null;original=null;render();
  $('download').disabled=true;$('download-png').disabled=true;$('pet-label').textContent=PETS[form].name;
  canvas.setAttribute('aria-label',PETS[form].name+'动画预览');
  
  $('install-command').textContent='npx --yes github:mli55/taomi-codex-pets --form '+form+' --color '+color;
  $('download-status').textContent='';
  try{
    let images=imageCache.get(next);
    if(!images){
      images=await Promise.all([next+'-neutral.png',next+'-mask.png'].map(async file=>{const image=new Image();image.src='assets/'+file+'?v=animation-review2';await image.decode();if(image.naturalWidth!==1536||image.naturalHeight!==1872)throw Error('宠物图集尺寸不正确');return image;}));
      imageCache.set(next,images);
    }
    if(request!==generation)return;
    sheetCtx.clearRect(0,0,1536,1872);sheetCtx.drawImage(images[1],0,0);bodyMask=sheetCtx.getImageData(0,0,1536,1872).data;
    sheetCtx.clearRect(0,0,1536,1872);sheetCtx.drawImage(images[0],0,0);original=sheetCtx.getImageData(0,0,1536,1872);loadedForm=next;
    applyColor();resetFrame();$('download').disabled=false;$('download-png').disabled=false;
  }catch(error){if(request!==generation)return;$('download-status').textContent=error.message;}
}
function chooseColor(next){color=next;markGroup('.swatch',el=>el.dataset.color===next);applyColor();$('download-status').textContent='';
  $('install-command').textContent='npx --yes github:mli55/taomi-codex-pets --form '+form+' --color '+color;}
root.querySelectorAll('.type-option').forEach(b=>b.addEventListener('click',()=>chooseType(b.dataset.type)));
root.querySelectorAll('.variant-option').forEach(b=>b.addEventListener('click',()=>chooseVariant(b.dataset.variant)));
root.querySelectorAll('.swatch').forEach(b=>b.addEventListener('click',()=>chooseColor(b.dataset.color)));

actionGroup.addEventListener('click',event=>{const b=event.target.closest('button[data-state]');if(!b)return;state=b.dataset.state;markGroup('[data-state]',el=>el.dataset.state===state);$('state-label').textContent=b.textContent;resetFrame();});
function syncPause(){$('pause').textContent=paused?'▷ 播放动画':'Ⅱ 暂停动画';$('pause').setAttribute('aria-pressed',String(paused));}
$('pause').addEventListener('click',()=>{paused=!paused;syncPause();});syncPause();
$('background').addEventListener('click',()=>{const dark=$('preview-panel').classList.toggle('dark');$('background').querySelector('span').textContent=dark?'浅色背景':'深色背景';});
function slug(){return `mole-ram-${form}-${PALETTE[color].slug}`;}
function pngBlob(){return new Promise((resolve,reject)=>sheet.toBlob(b=>b?resolve(b):reject(Error('图片导出失败，请重试。')),'image/png'));}
function downloadBlob(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}
const encoder=new TextEncoder();
const crcTable=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
function crc32(data){let crc=0xffffffff;for(const byte of data)crc=crcTable[(crc^byte)&255]^(crc>>>8);return(crc^0xffffffff)>>>0;}
// A dependency-free, UTF-8 ZIP writer (STORE). Pet packages contain data only.
function makeZip(files){
  const parts=[],central=[];let offset=0,centralSize=0;
  for(const file of files){const name=encoder.encode(file.name),data=typeof file.data==='string'?encoder.encode(file.data):file.data,crc=crc32(data);
    const local=new Uint8Array(30+name.length),v=new DataView(local.buffer);v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(12,33,true);v.setUint32(14,crc,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,name.length,true);local.set(name,30);parts.push(local,data);
    const c=new Uint8Array(46+name.length),cv=new DataView(c.buffer);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(8,0x800,true);cv.setUint16(14,33,true);cv.setUint32(16,crc,true);cv.setUint32(20,data.length,true);cv.setUint32(24,data.length,true);cv.setUint16(28,name.length,true);cv.setUint32(42,offset,true);c.set(name,46);central.push(c);offset+=local.length+data.length;centralSize+=c.length;
  }
  const end=new Uint8Array(22),v=new DataView(end.buffer);v.setUint32(0,0x06054b50,true);v.setUint16(8,files.length,true);v.setUint16(10,files.length,true);v.setUint32(12,centralSize,true);v.setUint32(16,offset,true);return new Blob([...parts,...central,end],{type:'application/zip'});
}
async function exportPet(onlyPng=false){
  if(loadedForm!==form)return;const id=slug(),displayName=PETS[form].name+' · '+PALETTE[color].name;
  $('download').disabled=true;$('download-png').disabled=true;$('download-status').textContent='正在打包你选的拉姆…';
  try{const png=await pngBlob();
    if(onlyPng)downloadBlob(png,id+'-spritesheet.png');
    else{const metadata={id,displayName,spriteVersionNumber:1,spritesheetPath:'spritesheet.png'};
      const readme=`${displayName}\n\n安装：把本文件夹放进 CODEX_HOME/pets（默认 ~/.codex/pets；Windows 为 %USERPROFILE%\\.codex\\pets）。\n打开 Codex 设置 → Pets / 宠物，刷新并选择它。输入 /pet 唤出宠物。\n\n本包只含数据，不执行任何脚本。\n图集：1536×1872，8列9行，每格192×208。\n行：idle, running-right, running-left, waving, jumping, failed, waiting, running, review。\n帧数：6,8,8,4,5,8,6,6,6。\n动作：正面、向右、向左、招呼（中级为跳舞，其余为高兴）、跳舞（悬停）、生气、无聊、踢球（工作中）、高兴（完成）。\n游戏配色：${PALETTE[color].name}（ID ${color}）\n\n来源与说明：https://github.com/mli55/taomi-codex-pets\n官方宠物文档：https://learn.chatgpt.com/docs/pets\n摩尔庄园同人作品，非官方出品；角色权益归原权利方所有。\n`;
      downloadBlob(makeZip([{name:id+'/pet.json',data:JSON.stringify(metadata,null,2)},{name:id+'/spritesheet.png',data:new Uint8Array(await png.arrayBuffer())},{name:id+'/README.txt',data:readme}]),id+'.zip');}
    $('download-status').textContent='已开始下载。';
  }catch(error){$('download-status').textContent=error.message||'下载失败，请重试。';}
  finally{const ready=loadedForm===form;$('download').disabled=!ready;$('download-png').disabled=!ready;}
}
$('download').addEventListener('click',()=>exportPet());$('download-png').addEventListener('click',()=>exportPet(true));
$('copy-prompt').addEventListener('click',async()=>{
  const prompt=`请帮我安装已经下载的 Codex 宠物包 ${slug()}.zip。先在我的下载目录找到该文件，检查 ZIP 只包含宠物数据，没有绝对路径或路径穿越；读取 pet.json，核对 spritesheet.png 是1536×1872透明图集。将宠物文件夹放到 CODEX_HOME/pets（未配置时用 ~/.codex/pets）。如果同名宠物存在，请保留原文件，改用新目录。完成后告诉我在设置 → Pets 刷新并选择 ${PETS[form].name}。源码：https://github.com/mli55/taomi-codex-pets`;
  try{await navigator.clipboard.writeText(prompt);$('copy-prompt').textContent='✓ 已复制，粘贴给 Codex 即可';}
  catch{const box=document.createElement('textarea');box.value=prompt;box.setAttribute('aria-label','安装说明，请手动复制');box.style.cssText='width:100%;min-height:140px;margin-top:12px';$('copy-prompt').after(box);box.focus();box.select();$('copy-prompt').textContent='请复制下方安装说明';}
});
syncConfiguration();loadForm(COMBINATIONS[type][variant]);requestAnimationFrame(animate);

})();
