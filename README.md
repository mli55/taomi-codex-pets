# Taomi Codex Pets · 拉姆与 NoNo

网站：[mli55.github.io/taomi-codex-pets](https://mli55.github.io/taomi-codex-pets/)

把摩尔庄园原页游拉姆带进 Codex。支持初级、中级、高级、超级拉姆，以及神力超级、水系、木系、火系，使用原客户端的十种身体配色。

本项目是同人格式适配，不是官方宠物产品。成品角色图像来自原页游 SWF；没有使用 AI 重绘素材。

本仓库同时收录赛尔号普通 NoNo、超能 NoNo 和至尊 NoNo，使用各自官方原素材与配色。网站通过两个 Tab 切换，分别下载宠物包。


## 安装

需要 Node.js 18 或更新版本：

```sh
npx --yes github:mli55/taomi-codex-pets --form super --color 2
```

NoNo（默认超能版）：

```sh
npx --yes github:mli55/taomi-codex-pets --pet nono --variant super
```

`--variant`（NoNo）：`normal` 普通版、`super` 超能版、`annual` 至尊版。

`--pet`：`ram`（默认）或 `nono`。

`--form`：`junior` 初级、`middle` 中级、`senior` 高级、`classic` 超级、`super` 神力超级、`water` 水系、`wood` 木系、`fire` 火系。


`--color`：1 红色、2 黄色、3 天蓝色、4 粉红色、5 橘黄色、6 灰色、7 黑色、8 紫色、9 土色、10 绿色。

安装器只复制宠物数据到 `CODEX_HOME/pets`，默认 `~/.codex/pets`，不会覆盖已有宠物。打开 Codex「设置 → Pets / 宠物」，刷新后选择它；输入 `/pet` 唤出宠物。

也可以在网站选好形态与颜色，下载 ZIP，解压后把整个宠物文件夹放进上述目录。包内只有 `pet.json`、`spritesheet.png` 和说明文件。网页中的「复制给 Codex 的安装说明」会生成与你所选宠物一致的提示词。

## 格式与原版还原

- 图集：1536 × 1872，8 列 × 9 行，单格 192 × 208，透明 PNG。
- 每行有效帧：6、8、8、4、5、8、6、6、6；剩余格透明。
- 原游戏切换元素形态时保留宠物颜色，本网站也保持相同规则。
- 身体与阴影使用原客户端 `GV.petColor_1` 至 `GV.petColor_10` 的加法颜色变换。叶冠、眼白和宝石不受换色影响。
- 原动作抽样适配到 Codex 的九种状态，不是重新设计的动作。具体原动作与帧号见 [animation-sources.json](dist/assets/animation-sources.json)。

| Codex 状态 | 原页游动作 |
| --- | --- |
| idle | down |
| running-right | right |
| running-left | left |
| waving | happy |
| jumping（鼠标悬停） | happy |
| failed | angry |
| waiting | boring |
| running | rightdown |
| review（任务完成） | dance |

## 网站开发

```sh
npm start
npm run check
```

打开 `http://localhost:4173`。网站是静态 HTML/CSS/JavaScript，配色和 ZIP 打包都在浏览器中完成，无账号、无后端、无数据上传。网页字体无法联网加载时自动使用系统字体。

`scripts/compose-official.py` 将官方 SWF 导出的原始帧与三通道身体与眼皮遮罩对齐到 Codex 图集；`scripts/apply-game-palette.py` 按官方十色生成可直接安装的图集。这些脚本需要 Pillow、NumPy、SciPy。完整素材来源和处理方法见 [SOURCES.md](SOURCES.md)。

## NoNo 三种版本

超能 NoNo 的九行状态依次使用：待命、右移、左移、高兴、召唤、悲伤、充电、玩魔方、惊讶。原始帧来自赛尔号官方服务器，未重新配色。`scripts/compose-nono.py` 对齐原面屏并去除独立地面投影；帧号见 [nono-animation-sources.json](dist/assets/nono-animation-sources.json)。

普通 NoNo 和至尊 NoNo 的原版造型分别提取自官方 `normal/` 与 `annual/` 资源。普通版跳跃状态使用原开心表情；普通与至尊版忙碌状态使用原斜向移动；至尊版等待状态使用原待命动作。对应原动作缺失时，不混用其他版本的素材。映射见 `dist/assets/nono-normal-animation-sources.json` 和 `nono-annual-animation-sources.json`。

可检索名称：Taomi、淘米、普通 NoNo、至尊 NoNo、Codex Pet、Codex Pets、Ram、拉姆、超级拉姆、摩尔庄园、NoNo、超能 NoNo、赛尔号。

角色、美术和原游戏内容权益归上海淘米及相关权利方所有。本仓库不以开源代码许可授权原游戏素材。Codex 格式说明参考 [官方 Pets 文档](https://learn.chatgpt.com/docs/pets)。

NoNo 换色：已从官方客户端和三种素材确认存在指定机身部件的换色机制；完整官方色值尚未核实，目前不开放自配颜色。详见 [SOURCES.md](SOURCES.md)。

## GitHub Pages

网站从 `gh-pages` 分支根目录发布，内容对应 `dist/`。更新并提交源码后，运行 `git subtree push --prefix dist origin gh-pages` 同步网站。
