// Timing and return-to-idle behaviour verified against the installed client.
// The PNG supplies poses; it cannot override this playback contract.
(()=>{
'use strict';
const idleDurations=[280,110,110,140,140,320];
const specs={idle:[0,6], 'running-right':[1,8,120,220], 'running-left':[2,8,120,220], waving:[3,4,140,280], jumping:[4,5,140,280], failed:[5,8,140,240], waiting:[6,6,150,260], running:[7,6,120,220], review:[8,6,150,280]};
function sequence(state,reducedMotion=false){
  const [row,count,duration,lastDuration]=specs[state];
  const action=Array.from({length:count},(_,column)=>({row,column,state,duration:state==='idle'?idleDurations[column]:(column===count-1?lastDuration:duration)}));
  if(reducedMotion)return{frames:[action[0]],loopStart:null};
  const idle=idleDurations.map((duration,column)=>({row:0,column,state:'idle',duration:duration*6}));
  if(state==='idle')return{frames:idle,loopStart:0};
  return{frames:[...action,...action,...action,...idle],loopStart:count*3};
}
function createPlayer(draw,reducedMotion=false){
  let clip=null,index=0,last=null;
  return{
    select(state){clip=sequence(state,reducedMotion);index=0;last=null;draw(clip.frames[index]);},
    tick(time,paused){
      if(!clip||paused||clip.loopStart===null){last=null;return;}
      if(last===null){last=time;return;}
      let changed=false;
      while(time-last>=clip.frames[index].duration){
        last+=clip.frames[index].duration;
        index=index+1<clip.frames.length?index+1:clip.loopStart;
        changed=true;
      }
      if(changed)draw(clip.frames[index]);
    }
  };
}
const actions=[['idle','待机'],['waving','打招呼'],['jumping','跳跃'],['running','工作'],['waiting','等待'],['review','检查'],['running-left','向左'],['running-right','向右'],['failed','失败']];
window.PetPlayback={sequence,createPlayer,actions};
})();
