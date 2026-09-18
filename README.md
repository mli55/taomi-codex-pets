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
| waving | happy（中级为 dance） |
| jumping（鼠标悬停） | dance |
| failed | angry |
| waiting | boring |
| running | football |
| review（任务完成） | happy |

## 网站开发

```sh
npm start
npm run check
```

打开 `http://localhost:4173`。网站是静态 HTML/CSS/JavaScript，配色和 ZIP 打包都在浏览器中完成，无账号、无后端、无数据上传。网页字体无法联网加载时自动使用系统字体。

`scripts/compose-selected-actions.py` 将完整官方时间轴中选出的帧与三通道身体及眼皮遮罩对齐到 Codex 图集；`scripts/apply-game-palette.py` 按官方十色生成可直接安装的图集。这些脚本需要 Pillow、NumPy、SciPy。完整素材来源和处理方法见 [SOURCES.md](SOURCES.md)。

## NoNo 三种版本

三个版本均展示九种 Codex 状态。普通 NoNo 的等待／工作使用惊讶／充电，悬停使用生气；超能使用惊讶／玩魔方，悬停使用召唤旋转；至尊使用轻微皱眉／开机后半段，打招呼使用惊讶，悬停使用召唤旋转。三个版本的检查状态使用高兴；超能跳跃使用召唤旋转，打招呼使用生气片段。原始动作与逐帧选择以各 `*-animation-sources.json` 为准。

`scripts/prepare-full-ram.py` 展开拉姆嵌套动作；`scripts/prepare-full-nono.py` 从完整官方 NoNo 时间轴导出候选姿势；`scripts/compose-selected-actions.py` 生成初始图集。当前短片段由 `scripts/selected-pet-clips.json` 记录，`scripts/reselect-pet-clips.py` 精确导出选中帧并替换对应行，再运行两个配色脚本更新全部颜色。三种 NoNo 待机均直接选用原始完整帧，不拼接眼睛或固定身体；具体帧号见各版本来源记录。选帧优先保留正面首尾、身体稳定的近景，拉姆工作使用原口渴动作出现道具前的低头、眨眼片段，悬停使用舞蹈中的转身片段，检查使用高兴。逐动作的原片长度及选帧见各 `*-animation-sources.json`。网页展示实际安装图集和九个 Codex 状态，采用客户端逐帧时长；非待机动作播放三遍后回到待机。

可检索名称：Taomi、淘米、普通 NoNo、至尊 NoNo、Codex Pet、Codex Pets、Ram、拉姆、超级拉姆、摩尔庄园、NoNo、超能 NoNo、赛尔号。

角色、美术和原游戏内容权益归上海淘米及相关权利方所有。本仓库不以开源代码许可授权原游戏素材。Codex 格式说明参考 [官方 Pets 文档](https://learn.chatgpt.com/docs/pets)。

NoNo 换色：已从官方客户端和三种素材确认存在指定机身部件的换色机制；选项参考用户提供的游戏变色界面，色值为截图近似值；默认保留原素材颜色，不开放任意自配颜色。详见 [SOURCES.md](SOURCES.md)。

## GitHub Pages

网站从 `gh-pages` 分支根目录发布，内容对应 `dist/`。更新并提交源码后，运行 `git subtree push --prefix dist origin gh-pages` 同步网站。
