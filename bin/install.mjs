#!/usr/bin/env node
import { mkdir, readFile, writeFile, copyFile } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
const forms={junior:'初级拉姆',middle:'中级拉姆',senior:'高级拉姆',classic:'超级拉姆',super:'神力超级拉姆',water:'神奇水系拉姆',wood:'弹力木系拉姆',fire:'霹雳火系拉姆'};
const args=process.argv.slice(2);
if(args.includes('--help')||args.includes('-h')){
  console.log('用法: npx --yes github:mli55/taomi-codex-pets [--pet ram|nono] [--form junior|middle|senior|classic|super|water|wood|fire] [--color 1..10] [--variant normal|super|annual]\n使用原游戏的十种身体配色，默认黄色（2）。已有宠物不会被覆盖。');process.exit(0);
}
let pet='ram', form='super', color='2',variant='super';
for(let i=0;i<args.length;i+=2){
  const [flag,value]=args.slice(i,i+2);
  if(flag==='--pet'&&['ram','nono'].includes(value))pet=value;
  else if(flag==='--variant'&&['normal','super','annual'].includes(value))variant=value;
  else if(flag==='--form'&&Object.hasOwn(forms,value))form=value;
  else if(flag==='--color'&&/^(?:[1-9]|10)$/.test(value))color=value;
  else{console.error('参数无效。使用 --help 查看说明。');process.exit(1);}
}
const colorNames=['','红色','黄色','天蓝色','粉红色','橘黄色','灰色','黑色','紫色','土色','绿色'];
const colorSlugs=['','red','yellow','blue','pink','orange','gray','black','purple','brown','green'];
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(root,'dist','assets',pet==='nono'?(variant==='super'?'nono.png':'nono-'+variant+'.png'):form+'-'+color+'.png');
const baseId=pet==='nono'?`seer-${variant}-nono`:`mole-ram-${form}-${colorSlugs[+color]}`;
const displayName=pet==='nono'?({normal:'普通 NoNo',super:'超能 NoNo',annual:'至尊 NoNo'}[variant]):forms[form]+' · '+colorNames[+color];
try{
  const image=await readFile(source);
  if(image.length<24||image.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||image.readUInt32BE(16)!==1536||image.readUInt32BE(20)!==1872)throw Error('宠物图集缺失或格式不正确。');
  const base=path.join(process.env.CODEX_HOME||path.join(os.homedir(),'.codex'),'pets');
  await mkdir(base,{recursive:true});let id=baseId,destination=path.join(base,id),n=1;
  // mkdir without recursive is atomic: never overwrite an existing pet or symlink.
  while(true){try{await mkdir(destination);break;}catch(error){if(error.code!=='EEXIST')throw error;id=`${baseId}-${++n}`;destination=path.join(base,id);}}
  await copyFile(source,path.join(destination,'spritesheet.png'));
  await writeFile(path.join(destination,'pet.json'),JSON.stringify({id,displayName,description:(pet==='nono'?'赛尔号':'摩尔庄园')+'同人 Codex 宠物；角色权益归原权利方所有。',spriteVersionNumber:1,spritesheetPath:'spritesheet.png'},null,2)+'\n');
  console.log(`已安装 ${displayName}\n${destination}\n\n打开 Codex 设置 → Pets / 宠物，刷新后选择它。输入 /pet 唤出宠物。`);
}catch(error){console.error('安装失败：'+error.message);process.exitCode=1;}
