# NoNo 配色依据

NoNo 的颜色选项参考用户提供的两张「变色大突破」游戏截图。白色、黄色、深红、紫、红、绿、粉、浅黄、蓝、灰、橙、黄绿共 12 个选项；名称用于辨认色块，不声称是游戏内色名。

- 原截图地址：https://newsimg.5054399.com/uploads/userup/1411/041122229250.jpg
- 同期换色教程：https://news.7k7k.com/51seer/20141104-680821.html
- 早期变色芯片记录：https://news.4399.com/seer/seertuijiangonglue/jinghuagonglue/201004-07-65790.html

截图色盘带有渐变和压缩。`dist/assets/nono-palette.json` 中非默认 RGB 是第二张 480×311 截图的色块中心附近 7×7 像素中位数，仅为截图近似值，不是从官方配置提取的精确值。白色选项直接使用现有原版图集，不对默认素材重新着色。

取样中心（x,y）：黄 (307,71)、深红 (359,68)、紫 (397,97)、红 (425,138)、绿 (421,184)、粉 (397,228)、浅黄 (309,254)、蓝 (265,225)、灰 (243,182)、橙 (244,136)、黄绿 (269,92)。

换色范围依据官方 `RobotCoreDLL.swf` 的 `NonoModel`：方向动画为 `color_1` / `color_2`，动作动画为 `color_` 开头的子容器。使用原 SWF 的这些容器生成黑、白端点，再按 RGB 插值得到图集；眼睛、发光效果、道具等容器不整体染色。当前支持普通与超能 NoNo。至尊版部分动作没有对应命名的换色容器，为避免动作间恢复原色，暂时只提供原色。这里的离线配色选项不表示所有颜色在原游戏各会员等级中都能取得。

生成脚本：

```sh
python3 scripts/build-nono-colors.py --base-dir /path/to/nono-assets --action-dir /path/to/nono-actions-v3 --work-dir /path/to/color-export --ffdec /path/to/ffdec.jar
```

需要已导出的原始时间轴 XML、动作 XML 和现有 animation-sources.json 帧选择记录。脚本仅生成附加配色，不覆盖默认 PNG。网站预览、ZIP/PNG 下载、`--nono-color` 命令安装使用同一张图集。
