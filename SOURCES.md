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

先导出 neutral 原帧，再仅替换身体白/灰两个 fill 为探针颜色 `(255,0,255)` 与 `(0,255,255)`，同参数导出 probe。两份差分分离身体白色/阴影覆盖率，不改变头冠或眼睛。只为产生遮罩而使用探针色，它不进入最终宠物。丢弃原游戏地面投影和空帧，统一坐标与比例后，按原动作顺序抽样到 Codex 图集。

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

普通版召唤、魔方以及至尊版充电资源请求返回 404。因此普通版跳跃状态以自身开心表情代替，普通与至尊版忙碌状态使用自身斜向移动，至尊版等待状态使用自身待命动画。所有替代都来自对应版本，没有混用外形。两种版本的帧映射分别见 `nono-normal-animation-sources.json` 和 `nono-annual-animation-sources.json`。原 SWF 中一帧外壳容器延长至 63 帧以渲染其原有嵌套方向动画，不改变原始图形或颜色。


## 眼皮与身体换色

颜色遮罩沿原 SWF 的身体容器递归提取：命名为 `petBody` 的对象，以及引用同一身体形状但没有实例名的表情容器。包含眼皮白色填充和灰色描边，三通道分别覆盖原始 255、204、153 灰阶。原眼白与瞳孔的嵌套加法变色分别保持 +255 和 -255；不能仅根据同时有白色和灰色两种填充来判断身体，否则会漏掉单色眼皮。`scripts/prepare-body-probes.py` 保留原始嵌套颜色变换生成探针帧，再由 `compose-official.py` 与 `apply-game-palette.py` 生成最终图集。


## 元素形态定位

水、木、火原 Flash 动作有不同的注册点。`scripts/center_ram.py` 按每组动作的完整可见范围进行水平居中，同一组所有帧使用相同位移，保留原动作内部的摆动。颜色遮罩使用完全相同的位移；超级拉姆保持原定位。
