(()=>{
'use strict';
const PETS={
 'nono-normal':{name:'普通 NoNo',variant:'normal',slug:'seer-normal-nono',busy:'忙碌',wait:'充电'},
 nono:{name:'超能 NoNo',variant:'super',slug:'seer-super-nono',busy:'玩魔方',wait:'充电'},
 'nono-annual':{name:'至尊 NoNo',variant:'annual',slug:'seer-annual-nono',busy:'忙碌',wait:'待命'}
};
const STATES = {
  idle: [0,6,650,'发呆中'], 'running-right': [1,8,120,'向右走'], 'running-left': [2,8,120,'向左走'],
  waving: [3,4,180,'和你打招呼'], jumping: [4,5,160,'开心地蹦一蹦'], failed: [5,8,160,'遇到问题啦'],
  waiting: [6,6,200,'等你回来'], running: [7,6,140,'认真忙碌中'], review: [8,6,180,'仔细检查中']
};
const root=document.getElementById('nono-panel');
const $ = id => document.getElementById('nono-'+id);
const canvas = $('pet'), ctx = canvas.getContext('2d');
const sheet = document.createElement('canvas'); sheet.width=1536; sheet.height=1872;
const sheetCtx=sheet.getContext('2d',{willReadFrequently:true});
let form='nono', color='original', state='idle', original=null, currentFrame=0, lastFrame=0, loadedForm=null, generation=0;
let paused=matchMedia('(prefers-reduced-motion: reduce)').matches;
const imageCache=new Map(); let bodyMask=null;
function markGroup(selector, selected) { root.querySelectorAll(selector).forEach(el=>{const active=selected(el);el.classList.toggle('selected',active);el.setAttribute('aria-pressed',String(active));}); }
function resetFrame(){currentFrame=0;lastFrame=0;render();}
function render(){ctx.clearRect(0,0,576,624);if(loadedForm!==form)return;const row=STATES[state][0];ctx.drawImage(sheet,currentFrame*192,row*208,192,208,0,0,576,624);}
function animate(time){const info=STATES[state];if(!paused && !document.hidden && !root.hidden && loadedForm===form && time-lastFrame>=info[2]){currentFrame=(currentFrame+1)%info[1];lastFrame=time;render();}requestAnimationFrame(animate);}
async function loadForm(next){
  form=next;const request=++generation;loadedForm=null;original=null;render();
  $('download').disabled=true;$('download-png').disabled=true;$('pet-label').textContent=PETS[form].name;
  $('install-command').textContent='npx --yes github:mli55/taomi-codex-pets --pet nono --variant '+PETS[form].variant;
  
  root.querySelector('[data-state=jumping]').textContent=form==='nono-normal'?'开心':'召唤';
  $('pet').setAttribute('aria-label',PETS[form].name+'动画预览');
  root.querySelector('[data-state=running]').textContent=PETS[form].busy;root.querySelector('[data-state=waiting]').textContent=PETS[form].wait;
  $('download-status').textContent='';
  $('state-label').textContent=root.querySelector('[data-state="'+state+'"]').textContent;
  root.querySelectorAll('.form').forEach(el=>{const a=el.dataset.form===form;el.classList.toggle('active',a);el.setAttribute('aria-pressed',String(a));});
  try{
    let images=imageCache.get(next);
    if(!images){
      images=await Promise.all([next+'.png'].map(async file=>{const image=new Image();image.src='assets/'+file;await image.decode();if(image.naturalWidth!==1536||image.naturalHeight!==1872)throw Error('宠物图集尺寸不正确');return image;}));
      imageCache.set(next,images);
    }
    if(request!==generation)return;
    sheetCtx.clearRect(0,0,1536,1872);sheetCtx.drawImage(images[0],0,0);original=sheetCtx.getImageData(0,0,1536,1872);loadedForm=next;
    resetFrame();$('download').disabled=false;$('download-png').disabled=false;
  }catch(error){if(request!==generation)return;$('download-status').textContent=error.message;}
}
root.querySelectorAll('.form').forEach(b=>b.addEventListener('click',()=>loadForm(b.dataset.form)));
root.querySelectorAll('[data-state]').forEach(b=>b.addEventListener('click',()=>{state=b.dataset.state;markGroup('[data-state]',el=>el.dataset.state===state);$('state-label').textContent=b.textContent;resetFrame();}));
function syncPause(){$('pause').textContent=paused?'▷ 播放动画':'Ⅱ 暂停动画';$('pause').setAttribute('aria-pressed',String(paused));}
$('pause').addEventListener('click',()=>{paused=!paused;syncPause();});syncPause();
$('background').addEventListener('click',()=>{const dark=$('preview-panel').classList.toggle('dark');$('background').querySelector('span').textContent=dark?'浅色背景':'深色背景';});
function slug(){return PETS[form].slug;}
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
  if(loadedForm!==form)return;const id=slug(),displayName=PETS[form].name;
  $('download').disabled=true;$('download-png').disabled=true;$('download-status').textContent='正在打包你选的NoNo…';
  try{const png=await pngBlob();
    if(onlyPng)downloadBlob(png,id+'-spritesheet.png');
    else{const metadata={id,displayName,spriteVersionNumber:1,spritesheetPath:'spritesheet.png'};
      const readme=`${displayName}\n\n安装：把本文件夹放进 CODEX_HOME/pets（默认 ~/.codex/pets；Windows 为 %USERPROFILE%\\.codex\\pets）。\n打开 Codex 设置 → Pets / 宠物，刷新并选择它。输入 /pet 唤出宠物。\n\n本包只含数据，不执行任何脚本。\n图集：1536×1872，8列9行，每格192×208。\n行：idle, running-right, running-left, waving, jumping, failed, waiting, running, review。\n帧数：6,8,8,4,5,8,6,6,6。\n游戏配色：原游戏配色\n\n来源与说明：https://github.com/mli55/taomi-codex-pets\n官方宠物文档：https://learn.chatgpt.com/docs/pets\n赛尔号同人作品，非官方出品；角色权益归原权利方所有。\n`;
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
loadForm('nono');requestAnimationFrame(animate);

})();
