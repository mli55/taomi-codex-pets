import {readFile} from 'node:fs/promises';
for(const form of ['junior','middle','senior','classic','super','water','wood','fire','nono','nono-normal','nono-annual']){
  const image=await readFile(new URL('../dist/assets/'+form+'.png',import.meta.url));
  if(image.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||image.readUInt32BE(16)!==1536||image.readUInt32BE(20)!==1872)throw Error(form+': invalid sprite atlas');
  if(image.length>20*1024*1024)throw Error(form+': exceeds 20 MiB');
  console.log(form+': 1536 × 1872 PNG, '+image.length+' bytes');
}
const html=await readFile(new URL('../dist/index.html',import.meta.url),'utf8');
for(const resource of ['app.js','pet-playback.js','ram.js','nono.js','style.css']){if(!html.includes(resource))throw Error('missing '+resource);await readFile(new URL('../dist/'+resource,import.meta.url));}
console.log('All asset and entrypoint checks passed.');
