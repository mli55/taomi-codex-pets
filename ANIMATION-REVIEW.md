# 动作检查记录

当前发布图集的动作与循环检查记录。

逐帧检查 11 个形态的九种 Codex 状态。优先区分悬停、工作与检查；保留原游戏图形。打招呼与悬停可来自同一长动画，但使用不同片段。循环不强制以恢复帧结尾；转圈保留原方向，表情及摇摆使用邻近姿势接回首帧。

普通和神力拉姆工作采用此前悬停的转身片段，悬停恢复最初 woter 的水珠落下、淋湿和恢复片段及整体缩放。超级拉姆使用跳舞前段的摇摆工作、后段的转身悬停。转身限制舞台位移；每行使用统一缩放，配色遮罩与图形一起定位。初级和中级正面仍保留此前确认的原动态。

NoNo：普通使用充电工作、惊讶等待、生气悬停；超能使用魔方工作、惊讶等待、召唤旋转悬停；至尊使用开机后半段工作、轻微皱眉等待、惊讶打招呼、召唤旋转悬停。三个版本的检查状态使用高兴；超能打招呼按选择使用生气片段。

保留 47 行重排已有像素，11 行补充原始中间姿势；woter 单独恢复到调整前，待机和左右移动未改。

预览按客户端逐帧时长播放，非待机三遍后回待机。动画文件无法改变客户端状态触发或持续时间。

| 形态 | Codex 状态 | 原动画 | 原帧号（从 1 起） |
|---|---|---|---|
| super | idle | down | 1, 5, 8, 12, 15, 19 |
| super | running-right | right | 1, 4, 6, 9, 11, 14, 16, 19 |
| super | running-left | left | 1, 4, 6, 9, 11, 14, 16, 19 |
| super | waving | dance | 1, 7, 13, 7 |
| super | jumping | dance | 127, 138, 149, 160, 171 |
| super | failed | angry | 1, 3, 6, 8, 11, 8, 6, 3 |
| super | waiting | boring | 1, 8, 14, 21, 14, 8 |
| super | running | dance | 19, 28, 37, 46, 37, 28 |
| super | review | happy | 8, 12, 20, 28, 20, 12 |
| water | idle | down | 1, 3, 4, 6, 7, 9 |
| water | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| water | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| water | waving | dance | 1, 7, 13, 7 |
| water | jumping | woter | 1, 4, 6, 10, 27 |
| water | failed | angry | 1, 6, 11, 16, 23, 16, 11, 6 |
| water | waiting | boring | 1, 4, 8, 11, 8, 4 |
| water | running | dance | 127, 136, 145, 154, 163, 172 |
| water | review | happy | 1, 2, 3, 2, 3, 2 |
| wood | idle | down | 1, 3, 4, 6, 7, 9 |
| wood | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| wood | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| wood | waving | dance | 1, 7, 13, 7 |
| wood | jumping | woter | 1, 3, 6, 12, 24 |
| wood | failed | angry | 1, 6, 11, 16, 23, 16, 11, 6 |
| wood | waiting | boring | 1, 4, 8, 11, 8, 4 |
| wood | running | dance | 127, 136, 145, 154, 163, 172 |
| wood | review | happy | 1, 2, 3, 2, 3, 2 |
| fire | idle | down | 1, 3, 4, 6, 7, 9 |
| fire | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| fire | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| fire | waving | dance | 1, 7, 13, 7 |
| fire | jumping | woter | 1, 4, 7, 13, 24 |
| fire | failed | angry | 1, 6, 11, 16, 23, 16, 11, 6 |
| fire | waiting | boring | 1, 4, 8, 11, 8, 4 |
| fire | running | dance | 127, 136, 145, 154, 163, 172 |
| fire | review | happy | 1, 2, 3, 2, 3, 2 |
| junior | idle | down | 1, 3, 6, 8, 11, 13 |
| junior | running-right | right | 1, 3, 4, 6, 8, 10, 11, 13 |
| junior | running-left | left | 1, 3, 4, 6, 8, 10, 11, 13 |
| junior | waving | dance | 1, 7, 13, 7 |
| junior | jumping | woter | 1, 3, 6, 16, 38 |
| junior | failed | angry | 14, 28, 41, 41, 41, 41, 41, 28 |
| junior | waiting | boring | 22, 32, 42, 63, 73, 32 |
| junior | running | dance | 128, 137, 146, 155, 164, 173 |
| junior | review | happy | 1, 6, 13, 22, 13, 6 |
| middle | idle | down | 1, 5, 6, 5, 1, 1 |
| middle | running-right | right | 1, 3, 5, 7, 8, 10, 12, 14 |
| middle | running-left | left | 1, 3, 5, 7, 8, 10, 12, 14 |
| middle | waving | dance | 1, 7, 13, 7 |
| middle | jumping | woter | 1, 3, 7, 11, 32 |
| middle | failed | angry | 1, 7, 12, 18, 24, 18, 12, 7 |
| middle | waiting | boring | 179, 188, 197, 207, 197, 188 |
| middle | running | dance | 128, 137, 146, 155, 164, 173 |
| middle | review | happy | 1, 3, 4, 3, 4, 3 |
| senior | idle | down | 1, 3, 4, 6, 7, 8 |
| senior | running-right | right | 1, 2, 3, 4, 5, 6, 7, 8 |
| senior | running-left | left | 1, 2, 3, 4, 5, 6, 7, 8 |
| senior | waving | dance | 1, 7, 13, 7 |
| senior | jumping | woter | 1, 3, 6, 10, 24 |
| senior | failed | angry | 1, 6, 11, 16, 23, 16, 11, 6 |
| senior | waiting | boring | 1, 4, 8, 11, 8, 4 |
| senior | running | dance | 128, 137, 146, 155, 164, 173 |
| senior | review | happy | 1, 2, 3, 2, 3, 2 |
| classic | idle | down | 1, 3, 4, 6, 7, 9 |
| classic | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| classic | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| classic | waving | dance | 1, 3, 6, 3 |
| classic | jumping | dance | 63, 69, 75, 81, 87 |
| classic | failed | angry | 6, 9, 12, 16, 21, 24, 18, 12 |
| classic | waiting | boring | 1, 3, 5, 9, 5, 3 |
| classic | running | dance | 10, 19, 28, 36, 28, 19 |
| classic | review | happy | 20, 24, 29, 34, 29, 24 |
| nono-normal | idle | base | 5, 3, 1, 3, 5, 5 |
| nono-normal | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono-normal | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono-normal | waving | normal-action-2.swf | 67, 72, 82, 91 |
| nono-normal | jumping | normal-exp-2.swf | 1, 6, 11, 40, 6 |
| nono-normal | failed | normal-exp-4.swf | 1, 9, 14, 19, 24, 19, 14, 9 |
| nono-normal | waiting | normal-exp-3.swf | 1, 7, 13, 22, 13, 7 |
| nono-normal | running | normal-action-1.swf | 1, 4, 7, 9, 12, 15 |
| nono-normal | review | normal-exp-1.swf | 24, 27, 39, 30, 39, 27 |
| nono | idle | base | 1, 2, 3, 3, 2, 1 |
| nono | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono | waving | super-exp-2.swf | 14, 18, 26, 30 |
| nono | jumping | super-action-6.swf | 42, 45, 48, 51, 53 |
| nono | failed | super-exp-4.swf | 1, 6, 12, 17, 22, 17, 12, 6 |
| nono | waiting | super-exp-3.swf | 1, 7, 17, 23, 17, 7 |
| nono | running | super-action-7.swf | 46, 52, 58, 64, 58, 52 |
| nono | review | super-exp-1.swf | 89, 90, 92, 94, 92, 90 |
| nono-annual | idle | base | 1, 3, 5, 7, 5, 1 |
| nono-annual | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono-annual | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono-annual | waving | annual-exp-3.swf | 1, 6, 11, 6 |
| nono-annual | jumping | annual-action-6.swf | 45, 49, 53, 57, 61 |
| nono-annual | failed | annual-exp-4.swf | 1, 7, 10, 13, 16, 13, 10, 7 |
| nono-annual | waiting | annual-exp-2.swf | 11, 14, 16, 18, 16, 14 |
| nono-annual | running | annual-action-2.swf | 53, 55, 57, 59, 57, 55 |
| nono-annual | review | annual-exp-1.swf | 1, 4, 9, 6, 9, 4 |

自动检查：124 张可下载图集的尺寸、非空帧、单元格边界、动态变化和整行完全重复检查通过。

视觉检查使用默认配色逐帧图，并在本地网页确认实际预览。对动画观感的取舍仍以预览为准；不同形态使用相同原游戏动作属于正常情况。
