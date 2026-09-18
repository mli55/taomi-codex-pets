const tabs=[...document.querySelectorAll('[role="tab"]')];
function selectPet(pet,focus=false){
 for(const tab of tabs){const selected=tab.dataset.pet===pet;tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;document.getElementById(tab.getAttribute('aria-controls')).hidden=!selected;if(selected&&focus)tab.focus();}
 document.getElementById('install-link').href='#'+pet+'-install';
 document.body.dataset.pet=pet;
}
for(const tab of tabs){tab.addEventListener('click',()=>selectPet(tab.dataset.pet));tab.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const i=tabs.indexOf(tab);const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowLeft'?-1:1)+tabs.length)%tabs.length;selectPet(tabs[next].dataset.pet,true);}});}

for(const pet of ['ram','nono']){
 const button=document.getElementById(pet+'-copy-command');
 const code=document.getElementById(pet+'-install-command');
 const status=button.querySelector('.copy-status');
 let timer;
 function reset(){clearTimeout(timer);status.textContent='复制';button.classList.remove('copied');}
 new MutationObserver(reset).observe(code,{childList:true,characterData:true,subtree:true});
 button.addEventListener('click',async()=>{
  const command=code.textContent;
  try{
   await navigator.clipboard.writeText(command);
   if(code.textContent!==command)return;
   clearTimeout(timer);status.textContent='已复制';button.classList.add('copied');
   timer=setTimeout(reset,2500);
  }catch{status.textContent='复制失败';timer=setTimeout(reset,2500);}
 });
}
