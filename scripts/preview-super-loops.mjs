#!/usr/bin/env node
// Rebuild this local review page after changing the atlas. No packages required.
import {execFileSync} from 'node:child_process';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = new URL('../qa/super-loops/', import.meta.url);
const baselineRef = '76892a3';
const atlasPath = 'dist/assets/super-1.png';
const baseline = execFileSync('git', ['show', `${baselineRef}:${atlasPath}`], {cwd: root, maxBuffer: 20 * 1024 * 1024});
const current = await readFile(new URL('../' + atlasPath, import.meta.url));
for (const [name, image] of [['baseline', baseline], ['current', current]]) {
  if (image.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a' || image.readUInt32BE(16) !== 1536 || image.readUInt32BE(20) !== 1872) {
    throw new Error(`${name}: expected a 1536 × 1872 PNG atlas`);
  }
}

// Fail early if the client contract changes, instead of silently showing wrong rows.
const context = {window: {}};
vm.runInNewContext(await readFile(new URL('../dist/pet-playback.js', import.meta.url), 'utf8'), context);
const playback = context.window.PetPlayback;
const limits = {'idle': 6, 'running-right': 8, 'running-left': 8, waving: 4, jumping: 5, failed: 8, waiting: 6, running: 6, review: 6};
if (playback.actions.length !== 9) throw new Error('Expected all nine pet states');
for (const [state] of playback.actions) {
  const clip = playback.sequence(state);
  const count = state === 'idle' ? clip.frames.length : clip.loopStart / 3;
  if (count !== limits[state]) throw new Error(`Unexpected frame count for ${state}: ${count}`);
  if (clip.frames.some(frame => !(frame.duration > 0) || frame.row < 0 || frame.row > 8 || frame.column < 0 || frame.column > 7)) throw new Error(`Invalid playback frame for ${state}`);
}

function startReview() {
  'use strict';
  const {actions, sequence} = window.PetPlayback;
  const stateNames = Object.fromEntries(actions);
  const mode = document.querySelector('#mode');
  const speed = document.querySelector('#speed');
  const toggle = document.querySelector('#toggle');
  const error = document.querySelector('#error');
  const cards = [];
  let paused = false;
  let lastTime = null;
  let ready = false;

  const images = ['baseline.png', '../../dist/assets/super-1.png?v=' + document.body.dataset.build].map(src => {
    const image = new Image();
    image.src = src;
    return image;
  });
  function setPaused(value) {
    paused = value;
    lastTime = null;
    toggle.textContent = paused ? '继续播放' : '暂停全部';
    toggle.setAttribute('aria-pressed', String(paused));
  }
  function makeClip(state) {
    const original = sequence(state);
    const count = state === 'idle' ? original.frames.length : original.loopStart / 3;
    return mode.value === 'loop'
      ? {frames: original.frames.slice(0, count), loopStart: 0, count}
      : {...original, count};
  }
  function draw(card) {
    if (!ready) return;
    const frame = card.clip.frames[card.index];
    card.contexts.forEach((ctx, index) => {
      ctx.clearRect(0, 0, 192, 208);
      ctx.drawImage(images[index], frame.column * 192, frame.row * 208, 192, 208, 0, 0, 192, 208);
    });
    const count = frame.state === 'idle' ? sequence('idle').frames.length : card.clip.count;
    let phase = '';
    if (mode.value === 'client' && card.state !== 'idle') {
      phase = frame.state === 'idle' ? '已回到待机 · ' : '第 ' + (Math.floor(card.index / card.clip.count) + 1) + '/3 轮 · ';
    }
    card.status.textContent = phase + stateNames[frame.state] + ' ' + (frame.column + 1) + '/' + count + ' 帧 · ' + frame.duration + ' ms';
    card.element.dataset.edge = frame.column === 0 ? 'first' : frame.column === count - 1 ? 'last' : '';
    card.edge.textContent = frame.column === 0 ? '首帧' : frame.column === count - 1 ? '末帧' : '\u00a0';
    card.frameButtons.forEach((button, index) => {
      const selected = frame.state === card.state && frame.column === index;
      button.setAttribute('aria-pressed', String(selected));
    });
  }
  function reset() {
    for (const card of cards) {
      card.clip = makeClip(card.state);
      card.index = 0;
      card.elapsed = 0;
      draw(card);
    }
    lastTime = null;
  }
  function step(card, direction) {
    setPaused(true);
    if (direction > 0) {
      card.index = card.index + 1 < card.clip.frames.length ? card.index + 1 : card.clip.loopStart;
    } else {
      card.index = card.index > 0 ? card.index - 1 : card.clip.frames.length - 1;
    }
    card.elapsed = 0;
    draw(card);
  }
  const grid = document.querySelector('#grid');
  for (const [state, label] of actions) {
    const element = document.createElement('article');
    element.className = 'card';
    const clip = makeClip(state);
    element.innerHTML = '<header><div><h2>' + label + '</h2><small>' + state + ' · ' + clip.count + ' 帧</small></div><span class="edge"></span></header>' +
      '<div class="comparison"><figure><figcaption>调整前</figcaption><canvas width="192" height="208" aria-label="' + label + '调整前"></canvas></figure>' +
      '<figure><figcaption>调整后</figcaption><canvas width="192" height="208" aria-label="' + label + '调整后"></canvas></figure></div>' +
      '<p class="status" aria-live="off"></p><div class="controls"><button type="button" class="previous" aria-label="' + label + '上一帧">←</button>' +
      '<div class="frames" aria-label="' + label + '选择帧"></div><button type="button" class="next" aria-label="' + label + '下一帧">→</button></div>';
    const card = {state, clip, index: 0, elapsed: 0, element, contexts: [...element.querySelectorAll('canvas')].map(canvas => canvas.getContext('2d')), status: element.querySelector('.status'), edge: element.querySelector('.edge'), frameButtons: []};
    const frames = element.querySelector('.frames');
    for (let column = 0; column < clip.count; column++) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = column + 1;
      button.title = '暂停并查看第 ' + (column + 1) + ' 帧';
      button.addEventListener('click', () => {
        setPaused(true);
        card.index = column;
        card.elapsed = 0;
        draw(card);
      });
      card.frameButtons.push(button);
      frames.append(button);
    }
    element.querySelector('.previous').addEventListener('click', () => step(card, -1));
    element.querySelector('.next').addEventListener('click', () => step(card, 1));
    cards.push(card);
    grid.append(element);
  }
  toggle.addEventListener('click', () => setPaused(!paused));
  document.querySelector('#reset').addEventListener('click', reset);
  mode.addEventListener('change', reset);
  speed.addEventListener('change', () => {lastTime = null;});
  document.addEventListener('visibilitychange', () => {lastTime = null;});
  document.addEventListener('keydown', event => {
    if (event.code === 'Space' && !/^(BUTTON|SELECT|INPUT|TEXTAREA)$/.test(event.target.tagName)) {
      event.preventDefault();
      setPaused(!paused);
    }
  });
  function tick(time) {
    if (ready && !paused) {
      if (lastTime !== null) {
        // Do not skip through an entire action after the tab was inactive.
        const delta = Math.min(time - lastTime, 250) * Number(speed.value);
        for (const card of cards) {
          card.elapsed += delta;
          let changed = false;
          while (card.elapsed >= card.clip.frames[card.index].duration) {
            card.elapsed -= card.clip.frames[card.index].duration;
            card.index = card.index + 1 < card.clip.frames.length ? card.index + 1 : card.clip.loopStart;
            changed = true;
          }
          if (changed) draw(card);
        }
      }
      lastTime = time;
    } else {
      lastTime = null;
    }
    requestAnimationFrame(tick);
  }
  Promise.all(images.map(image => image.decode())).then(() => {
    ready = true;
    reset();
    requestAnimationFrame(tick);
  }).catch(reason => {
    error.hidden = false;
    error.textContent = '图片载入失败：' + reason.message + '。请从仓库根目录启动本地 HTTP 服务。';
  });
}

const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>神力超级拉姆 · 循环对比</title>
<style>
:root{color-scheme:light;font:14px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#253528;background:#edf1e9}
*{box-sizing:border-box}body{margin:0}main{max-width:1432px;margin:0 auto;padding:28px 20px 40px}h1{font-size:26px;margin:0 0 7px}h2{font-size:17px;margin:0}p{margin:7px 0}small,.intro{color:#627160}.intro{max-width:980px}.toolbar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:20px 0;padding:14px 16px;border:1px solid #cad4c5;border-radius:12px;background:#f8faf5f5;box-shadow:0 3px 12px #1f35150a}label{display:flex;align-items:center;gap:7px}button,select{font:inherit;min-height:34px;border:1px solid #c2cfbd;border-radius:7px;padding:5px 10px;background:white;color:inherit}button{cursor:pointer}button:hover{background:#e5eddf}button:focus-visible,select:focus-visible{outline:3px solid #79a85d;outline-offset:2px}#toggle{background:#335b32;color:white;border-color:#335b32;min-width:94px}#grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(416px,1fr));gap:18px}.card{padding:15px;background:#fff;border:1px solid #d3dccd;border-radius:14px;overflow:hidden}.card header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.edge{font-size:12px;min-width:42px;text-align:center;border-radius:5px;padding:3px 6px;color:#7b6041;background:#faf3e8}.card[data-edge=first] .edge{background:#e5f0df;color:#42672d}.comparison{display:flex;justify-content:space-evenly;gap:12px}figure{margin:0;width:192px;flex:0 0 192px}figcaption{font-size:12px;text-align:center;margin-bottom:5px;color:#627160}canvas{display:block;width:192px;height:208px;border-radius:7px;background-color:#f4f5f1;background-image:linear-gradient(45deg,#e8ebe5 25%,transparent 25%),linear-gradient(-45deg,#e8ebe5 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e8ebe5 75%),linear-gradient(-45deg,transparent 75%,#e8ebe5 75%);background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0}.status{font-size:12px;color:#627160;text-align:center;min-height:18px;margin:12px 0 9px;font-variant-numeric:tabular-nums}.controls{display:flex;align-items:center;justify-content:center;gap:8px}.frames{display:flex;gap:3px}.controls button{min-width:29px;padding:4px 7px;min-height:30px;font-size:12px}.frames button[aria-pressed=true]{background:#335b32;color:white;border-color:#335b32}.note{font-size:12px;color:#627160;margin-top:20px}#error{padding:15px;background:#ffe6df;color:#8a281a;border-radius:10px}@media(max-width:470px){main{padding:18px 8px}.card{padding:10px}#grid{grid-template-columns:416px;overflow-x:auto}.toolbar{position:static;padding:10px}h1{font-size:23px}}
</style>
</head>
<body data-build="${Date.now()}">
<main>
<h1>神力超级拉姆 · 循环对比</h1>
<p class="intro">九个状态使用 Codex 固定帧数、192 × 208 原尺寸与客户端时长。左右同步，观察末帧回到首帧的衔接；点击帧号或箭头可暂停逐帧检查。</p>
<div class="toolbar">
<button id="toggle" type="button" aria-pressed="false">暂停全部</button>
<button id="reset" type="button">从头播放</button>
<label>模式 <select id="mode"><option value="loop">单行动作连续循环</option><option value="client">Codex：3 轮后回到待机</option></select></label>
<label>速度 <select id="speed"><option value="1">1×</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select></label>
</div>
<p id="error" role="alert" hidden></p>
<div id="grid"></div>
<p class="note">调整前：Git ${baselineRef} 的 super-1.png。调整后：当前 dist/assets/super-1.png。时长来自 dist/pet-playback.js；待机按客户端的 6 倍慢速播放。此页只用于本地检查，不影响安装文件。</p>
</main>
<script src="../../dist/pet-playback.js"></script>
<script>(${startReview.toString()})();</script>
</body>
</html>
`;

await mkdir(output, {recursive: true});
await writeFile(new URL('baseline.png', output), baseline);
await writeFile(new URL('index.html', output), html);
console.log(`Generated ${fileURLToPath(output)}index.html (nine states; baseline ${baselineRef})`);
console.log('Serve the repository root: python3 -m http.server 4173');
console.log('Open http://localhost:4173/qa/super-loops/');
