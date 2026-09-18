# 素材来源与处理记录

取得日期：2026-09-18（UTC）。最终发布的角色素材全部来自原页游文件，不包含生成图片。

## 官方源

| 形态 | 原资源 | SHA-256 |
| --- | --- | --- |
| 神力超级拉姆 | http://mole.61.com/resource/petcloth/swf2/pet101/skill_7.swf | `4bcaaba6cc71bb956a2e8617ee016c9d1b3cce405afcb823b0947bd9ba4dfa20` |
| 神奇水系 | http://mole.61.com/resource/petcloth/swf2/pet5/skill_2.swf | `def307887b5de28bedcef4fae30fd980e8a9537f156b77f0b4527be235857464` |
| 弹力木系 | http://mole.61.com/resource/petcloth/swf2/pet5/skill_4.swf | `8b2844001dd346c5bdc0f6dba8da83da15c618c0d46a12c68b011f3bdfacd926` |
| 霹雳火系 | http://mole.61.com/resource/petcloth/swf2/pet5/skill_1.swf | `ef8b8dd20db563b6dcde2ee3b69d47707453bd147076a676b84aeec7dbd1ef94` |

官方服务器上述资源通过 HTTP 提供；下载内容与 [Miigon/RecMoleRes](https://github.com/Miigon/RecMoleRes) 的存档逐一核对，SHA-256 相同。未运行游戏登录或访问玩家账户。

## 颜色依据

原客户端 `ClientCommonDLL.swf` 的 `GV` 类定义 `petColor_1` 至 `petColor_10`；`GF.setPetColor` 使用 Flash `ColorTransform`。`ClientAppDLL.swf` 中 `LamuUIManage` 与 `lamuAvatar` 将玩家的 `PetColor` 应用于元素拉姆，不强制按元素改色。

所有乘数为 1，RGB 加数如下；每个通道相加后钳制到 0–255。白色基底为 255，阴影基底为 204，因此不能用普通色相旋转或乘法染色替代。

| ID | 游戏名 | R | G | B |
| --- | --- | --- | --- | --- |
| 1 | 红色 | 255 | -199 | -250 |
| 2 | 黄色 | 0 | -21 | -255 |
| 3 | 天蓝色 | -215 | -57 | 31 |
| 4 | 粉红色 | 51 | -148 | 0 |
| 5 | 橘黄色 | 102 | -118 | -255 |
| 6 | 灰色 | -150 | -150 | -150 |
| 7 | 黑色 | -215 | -210 | -215 |
| 8 | 紫色 | -82 | -194 | 112 |
| 9 | 土色 | -87 | -148 | -199 |
| 10 | 绿色 | -189 | -41 | -189 |

## 导出方法

使用 [JPEXS Free Flash Decompiler 26.3.0](https://github.com/jindrapetrik/jpexs-decompiler/releases/tag/version26.3.0) 导出 master sprite，zoom=4：超拉 940，水 538，木 1029，火 898。透明 PNG 保留原矢量轮廓。

先导出 neutral 原帧，再替换身体白色、灰色和深灰色填充为三通道探针，同参数导出 probe。两份差分分离身体各灰阶覆盖率，不改变头冠或眼睛。只为产生遮罩而使用探针色，它不进入最终宠物。丢弃原游戏地面投影和空帧，统一坐标与比例后，按原动作顺序抽样到 Codex 图集。

九种 Codex 状态使用现有原游戏动作映射，因此与原 Flash 客户端完整嵌套时间轴的播放节奏不完全相同。没有声称恢复整个游戏运行时。

## 参考项目

- [MoleRuffle](https://github.com/moleworld-dev/MoleRuffle)：用户提供，帮助确认官方资源的 HTTP 基址；未复制项目代码。
- [Moles-World](https://github.com/MyApril15/Moles-World)：用户提供，已检查，主要为 Unity 登录场景；最终宠物素材不取自该仓库。
- [Petdex](https://github.com/FanFPu/petdex)：用户指定的宠物展示/安装体验参考；未提交任何宠物到第三方平台。

本项目是原游戏素材的同人格式适配，并非摩尔庄园、淘米或 OpenAI 官方发行。角色及原游戏素材权益保留给原权利方。


# 超能 NoNo 原游戏素材来源

从赛尔号官方游戏服务器直接获取。使用 JPEXS Free Flash Decompiler 26.3.0 导出透明 PNG，再通过仓库脚本整理为 Codex 图集。未使用生成图片或重新配色。

客户端 `NonoModel` 对超能且非至尊 NoNo 使用 `resource/nono/super/` 路径；本项目采用 `nono_1.swf` 原版形象，未混用普通或年度至尊版本。

- [super-exp-4_1.swf](https://seer.61.com/resource/nono/super/exp/4_1.swf)
  SHA-256：`9693bb4a504590d33427a0c3d25e4b0898d77e85a4dcab88b8da7996b3757855`
- [super-action-6_1.swf](https://seer.61.com/resource/nono/super/action/6_1.swf)
  SHA-256：`955c877cd5f86a835dec6ea0d12857a304e7c6e52e79df0be363798e79b78f0e`
- [super-action-1_1.swf](https://seer.61.com/resource/nono/super/action/1_1.swf)
  SHA-256：`574b3e2a12b3aa31bc7a590ca1a18cfeff7a0119eec679e0adec0f4f43760e52`
- [super-exp-3_1.swf](https://seer.61.com/resource/nono/super/exp/3_1.swf)
  SHA-256：`38c8b5fefeef95b9db442ed579b03b82c7f5f42df231f1a8add67cd4d822d0eb`
- [super-action-7_1.swf](https://seer.61.com/resource/nono/super/action/7_1.swf)
  SHA-256：`9bc374f42ce2bb244fd223cb27960be2a4f53cd4af0daf39fca214116658b884`
- [super-exp-1_1.swf](https://seer.61.com/resource/nono/super/exp/1_1.swf)
  SHA-256：`3ede441079bd1937b896f3bb2384f0a3c8c24521cebd3d7fe5aa3cdc4f53af3c`
- [super-nono_1.swf](https://seer.61.com/resource/nono/super/nono_1.swf)
  SHA-256：`02cb616f69773323748ca2c4b64a7bf7c83769b68ef92397abdd48aa82c684c8`

逐状态帧号见 `dist/assets/nono-animation-sources.json`；机器可读资源清单见 `dist/assets/nono-source-files.json`。原素材权益归原权利方所有，本仓库不以开源代码许可证覆盖游戏素材。


## 普通 NoNo 与至尊 NoNo

官方客户端 `NonoModel` 使用 `normal/nono.swf` 加载普通版、`annual/nono.swf` 加载至尊版。下面各文件均从官方赛尔号服务器直接获取，保留原配色，没有重绘或把超能版改色。

- [normal-nono.swf](https://seer.61.com/resource/nono/normal/nono.swf)
  SHA-256：`04f8898bb343ffbc51008d3449e533f48119e4129a979bf4c7be8f0d580f4f5d`
- [normal-action-1.swf](https://seer.61.com/resource/nono/normal/action/1.swf)
  SHA-256：`fa88e18544b079133abafa4fe21f9795cb4d5b88f4b311a5039f6c2334b66cef`
- [normal-exp-1.swf](https://seer.61.com/resource/nono/normal/exp/1.swf)
  SHA-256：`6eb171e97ef7d1a30eefd040e017f55d6c9eaabd4c53cda812a727dd160a1c4c`
- [normal-exp-3.swf](https://seer.61.com/resource/nono/normal/exp/3.swf)
  SHA-256：`5efc9b61572da954765b84b7627916682db9801242003561bd5a45b476d43cb1`
- [normal-exp-4.swf](https://seer.61.com/resource/nono/normal/exp/4.swf)
  SHA-256：`9b19c04a08270b5182759db8d56aad091bdeb510b41b48cb5fdbb3abf9d039f5`
- [annual-nono.swf](https://seer.61.com/resource/nono/annual/nono.swf)
  SHA-256：`fd47e004e353765fc0929444a41743220dc79ee66e58bab2ddced95514cf2f76`
- [annual-action-6.swf](https://seer.61.com/resource/nono/annual/action/6.swf)
  SHA-256：`ed2ef1a8f60d6ab6af7f43daa8c06b0867a93b8fb320034987f50cba3dfd8bba`
- [annual-exp-1.swf](https://seer.61.com/resource/nono/annual/exp/1.swf)
  SHA-256：`417cc2271f3b7e2da0647e67f4d8aaa307d69430218c4aacc0a320974e0d8241`
- [annual-exp-3.swf](https://seer.61.com/resource/nono/annual/exp/3.swf)
  SHA-256：`50c60d610abcc3e2cc25493d630d4849f620b40a1b2134bf14335219231c8c46`
- [annual-exp-4.swf](https://seer.61.com/resource/nono/annual/exp/4.swf)
  SHA-256：`01f263c5cb4fbf57259e136fe42197cf0fbe1281df2c5f49dd2a1e7224d638c0`

普通版召唤、魔方以及至尊版充电资源请求返回 404。当前普通版工作状态使用充电，超能版使用玩魔方，至尊版使用召唤后半段；普通与超能版悬停使用生气，至尊版使用惊讶，至尊版等待状态使用自身生气动作的轻微表情片段。所有动作都来自对应版本，没有混用外形。两种版本的帧映射分别见 `nono-normal-animation-sources.json` 和 `nono-annual-animation-sources.json`。原 SWF 中一帧外壳容器延长至 63 帧以渲染其原有嵌套方向动画，不改变原始图形或颜色。


## 眼皮与身体换色

颜色遮罩沿原 SWF 的身体容器递归提取：命名为 `petBody` 的对象，以及引用同一身体形状但没有实例名的表情容器。包含眼皮白色填充和灰色描边，三通道分别覆盖原始 255、204、153 灰阶。原眼白与瞳孔的嵌套加法变色分别保持 +255 和 -255；不能仅根据同时有白色和灰色两种填充来判断身体，否则会漏掉单色眼皮。`scripts/prepare-body-probes.py` 保留原始嵌套颜色变换生成探针帧，再由 `prepare-full-ram.py`、`compose-selected-actions.py` 与 `apply-game-palette.py` 生成最终图集。


## 元素形态定位

水、木、火原 Flash 动作有不同的注册点。`scripts/compose-selected-actions.py` 按每组选中帧的完整可见范围统一定位和缩放，同一组所有帧使用相同位移，保留原动作内部的摆动。颜色遮罩使用完全相同的变换。


## 拉姆基础成长形态

来源：[官方 lamubone.swf](http://mole.61.com/resource/NPC/lamubone.swf)，SHA-256：`01abf65f3e8db098068a830268bd7a7cefefc1edc93a44565788783d23f8a0cf`。客户端 `LamuNPC` 默认载入此文件，`LamuUIManage` 使用 `level` 加实际等级选择形态。`level2 / level3 / level4 / level101` 分别对应本项目初级、中级、高级、超级选项；其中超级是普通外观，独立于已有的神力超级拉姆。

`export-ram-levels.py` 准备保留原色和眼部变换的三通道身体探针；当前通过 `prepare-full-ram.py --levels-dir` 展开长动作，由 `compose-selected-actions.py` 按动作组统一定位。帧号和来源见 `ram-level-animation-sources.json` 与 `ram-level-source-files.json`。

## NoNo 换色核对

官方 `RobotCoreDLL.swf` 的 `NonoModel.onResLoad` 会读取服务端 `_info.color`，对 `color_1` 和可选的 `color_2` 调用 `DisplayUtil.FillColor`；`onNonoEvent` 的 `COLOR_CHANGE` 分支会实时重设这两个部件。

三种官方素材均已核对：

| 版本 | 可换色实例 | 原始 Sprite ID |
| --- | --- | --- |
| 普通 | color_1、color_2 | 126、39 |
| 超能（一级） | color_1 | 57 |
| 至尊 | color_1 | 91 |

这证实三个原页游版本均有机身换色机制，不代表改变全部画面或统一改变光耳颜色，也不保证当前游戏仍向玩家开放旧的换色入口。完整官方选色表尚未核实，因此本次仅记录核对结果，默认保留原始 NoNo 配色。后续加入的颜色选项依据用户提供的游戏变色界面，RGB 为截图近似值，不声称是官方精确色表。


## 完整时间轴与动作重选

此前按主时间轴的短标签区间取帧，会只得到嵌套长动作的开头。现在先展开完整嵌套时间轴并导出覆盖全程的候选姿势，再选取可读的短片段；不是将整个长动作等间隔压缩到几张图片。拉姆工作状态使用原口渴动作中尚未出现水瓶或气泡的低头、眨眼片段，检查状态使用高兴；打招呼和悬停分别使用舞蹈前段的摇摆与后段的转身，不重复同一片段。

NoNo 改为开机、惊讶、悲哀、充电或待命、玩球或玩魔方、开心。至尊 `annual/action/7.swf` 已确认可下载，但角色与魔方相距过远，会使身体缩得太小；当前成品使用 `annual/action/6.swf` 的召唤后半段。普通 `normal/action/2.swf`、`normal/action/4.swf` 和至尊 `annual/action/2.swf` 来自同一官方资源路径。新增机器可读来源见 `dist/assets/action-source-files.json`。

Codex v1 的每行动画图片数固定为 6、8、8、4、5、8、6、6、6；这不是帧率。v2 没有提高这些动作的帧数，额外两行用于鼠标方向姿势。当前文件仍为 v1。网页只列可用成品动作，不把官方资源目录中尚未打包的动作显示为可用。


### 高兴动作精修

拉姆的高兴改为正面笑脸及轻跳片段；水、木、火和高级形态跳过遮脸的翻身区间，基础超级拉姆截取正面大笑，初级采用一次起跳到落地。打招呼与完成两行分别选 4 帧和 6 帧；悬停改用 5 帧舞蹈。短片段逐帧导出，不再只靠稀疏候选帧就近匹配。高级左右移动避开原动画仅剩地面投影的一帧；初级踢球与至尊 NoNo 魔方也补导出准确帧号，消除原先重复引用同一原帧的情况。至尊 NoNo 的颜色图集同步更新。

中级拉姆跳舞的眼白形状 10、413、422 在部分原始关键帧中没有额外的 +255 颜色变换；它们仍然是眼白，不能作为身体探针重新着色。`export-ram-levels.py` 已排除这些形状，`repair-middle-dance-eyes.py` 可对已有导出定点重建跳舞遮罩，并校验原图像素与帧定位完全一致。网页连续预览和十色下载图集同步修正。

主页的拉姆与 NoNo 预览直接读取 ZIP/PNG 导出所用的同一张图集。`dist/pet-playback.js` 按本机客户端的逐帧时长播放：非待机动作重复三遍后转入慢速待机循环，最后一帧保留客户端规定的停顿，减少动态效果时显示首帧。主页不再加载连续原片或额外做往返播放；原片资料库独立保留。ZIP 在点击下载时由当前图集即时生成。

当前精确选帧和行分配由 `scripts/selected-pet-clips.json` 记录。`reselect-pet-clips.py` 从原素材逐帧导出，舞蹈、高兴和生气优先收回正面姿态，部分短片段倒序回到起始帧；帧数与播放时长均遵循原客户端。每行统一缩放，避免远处道具挤小身体，拉姆工作行已移除玩球。悬停行采用每行统一缩放，并限制原片舞台位移，防止大幅转身时角色整体缩小；此定位同时用于身体和配色遮罩。新选帧保留眼白排除规则；旧的定点眼白修复脚本针对旧帧号，不应用于重选后的图集。

NoNo 待机固定身体：`stabilize-nono-idle.py` 保留第一帧身体和屏幕高光，仅提取同版本原素材中的眼睛，按屏幕位置对齐。普通、至尊使用原待机眼睛，超能使用惊讶动画最初的睁眼／闭眼片段；没有使用睁大眼睛的部分。所有颜色同步处理，六帧的身体、耳朵与外轮廓完全一致；节奏仍为客户端规定的 6.6 秒。来源记录在每份 `*-animation-sources.json` 的 `eyeSource`。

超能 NoNo：打招呼改为 `super-exp-2.swf` 生气帧 14、18、26、30；检查改为 `super-action-6.swf` 召唤旋转帧 42、45、48、51、54、56。其余七行逐像素保留，包括固定身体的待机。
