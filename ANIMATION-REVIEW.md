# 动作检查记录

当前版本在本地预览；此前快照为 `7132242`。

逐帧检查 11 个形态的九种 Codex 状态。优先区分悬停、工作与检查；保留原游戏图形。打招呼与悬停可来自同一长动画，但使用不同片段。循环首尾回到同一姿势的重复帧用于衔接，不代表不同状态复用同一动画。

拉姆工作采用原口渴动作出现水瓶、气泡前的片段。悬停采用转身，并限制舞台位移；每行使用统一缩放，配色遮罩与图形一起定位。初级和中级正面仍保留此前确认的原动态。

NoNo：普通使用充电工作、惊讶等待、生气悬停；超能使用魔方工作、惊讶等待、召唤旋转悬停；至尊保留召唤后半段工作和轻微皱眉等待，惊讶用于悬停。三个版本的检查状态使用高兴；超能打招呼按选择使用生气片段。

预览按客户端逐帧时长播放，非待机三遍后回待机。动画文件无法改变客户端状态触发或持续时间。

| 形态 | Codex 状态 | 原动画 | 原帧号（从 1 起） |
|---|---|---|---|
| super | idle | down | 1, 5, 8, 12, 15, 19 |
| super | running-right | right | 1, 4, 6, 9, 11, 14, 16, 19 |
| super | running-left | left | 1, 4, 6, 9, 11, 14, 16, 19 |
| super | waving | dance | 1, 7, 13, 1 |
| super | jumping | dance | 127, 145, 154, 172, 181 |
| super | failed | angry | 1, 3, 6, 8, 11, 6, 3, 1 |
| super | waiting | boring | 1, 8, 14, 21, 14, 1 |
| super | running | thirst | 13, 19, 25, 31, 25, 13 |
| super | review | happy | 8, 12, 20, 28, 12, 8 |
| water | idle | down | 1, 3, 4, 6, 7, 9 |
| water | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| water | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| water | waving | dance | 1, 7, 13, 1 |
| water | jumping | dance | 127, 145, 154, 172, 181 |
| water | failed | angry | 1, 6, 11, 16, 23, 11, 6, 1 |
| water | waiting | boring | 1, 4, 8, 11, 4, 1 |
| water | running | thirst | 46, 51, 56, 61, 56, 46 |
| water | review | happy | 1, 2, 3, 2, 2, 1 |
| wood | idle | down | 1, 3, 4, 6, 7, 9 |
| wood | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| wood | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| wood | waving | dance | 1, 7, 13, 1 |
| wood | jumping | dance | 127, 145, 154, 172, 181 |
| wood | failed | angry | 1, 6, 11, 16, 23, 11, 6, 1 |
| wood | waiting | boring | 1, 4, 8, 11, 4, 1 |
| wood | running | thirst | 46, 51, 56, 61, 56, 46 |
| wood | review | happy | 1, 2, 3, 2, 2, 1 |
| fire | idle | down | 1, 3, 4, 6, 7, 9 |
| fire | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| fire | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| fire | waving | dance | 1, 7, 13, 1 |
| fire | jumping | dance | 127, 145, 154, 172, 181 |
| fire | failed | angry | 1, 6, 11, 16, 23, 11, 6, 1 |
| fire | waiting | boring | 1, 4, 8, 11, 4, 1 |
| fire | running | thirst | 46, 51, 56, 61, 56, 46 |
| fire | review | happy | 1, 2, 3, 2, 2, 1 |
| junior | idle | down | 1, 3, 6, 8, 11, 13 |
| junior | running-right | right | 1, 3, 4, 6, 8, 10, 11, 13 |
| junior | running-left | left | 1, 3, 4, 6, 8, 10, 11, 13 |
| junior | waving | dance | 1, 7, 13, 1 |
| junior | jumping | dance | 128, 146, 155, 164, 173 |
| junior | failed | angry | 14, 28, 41, 41, 41, 28, 28, 14 |
| junior | waiting | boring | 22, 32, 42, 63, 73, 22 |
| junior | running | thirst | 1, 8, 16, 23, 16, 1 |
| junior | review | happy | 1, 6, 13, 22, 6, 1 |
| middle | idle | down | 1, 5, 6, 5, 1, 1 |
| middle | running-right | right | 1, 3, 5, 7, 8, 10, 12, 14 |
| middle | running-left | left | 1, 3, 5, 7, 8, 10, 12, 14 |
| middle | waving | dance | 1, 7, 13, 1 |
| middle | jumping | dance | 128, 146, 155, 164, 173 |
| middle | failed | angry | 1, 7, 12, 18, 24, 12, 7, 1 |
| middle | waiting | boring | 179, 188, 197, 207, 197, 179 |
| middle | running | thirst | 1, 8, 16, 23, 16, 1 |
| middle | review | happy | 1, 3, 4, 3, 3, 1 |
| senior | idle | down | 1, 3, 4, 6, 7, 8 |
| senior | running-right | right | 1, 2, 3, 4, 5, 6, 7, 8 |
| senior | running-left | left | 1, 2, 3, 4, 5, 6, 7, 8 |
| senior | waving | dance | 1, 7, 13, 1 |
| senior | jumping | dance | 128, 146, 155, 164, 173 |
| senior | failed | angry | 1, 6, 11, 16, 23, 11, 6, 1 |
| senior | waiting | boring | 1, 4, 8, 11, 4, 1 |
| senior | running | thirst | 46, 51, 56, 61, 56, 46 |
| senior | review | happy | 1, 2, 3, 2, 2, 1 |
| classic | idle | down | 1, 3, 4, 6, 7, 9 |
| classic | running-right | right | 1, 2, 3, 4, 6, 7, 8, 9 |
| classic | running-left | left | 1, 2, 3, 4, 6, 7, 8, 9 |
| classic | waving | dance | 1, 3, 6, 1 |
| classic | jumping | dance | 1, 63, 81, 90, 1 |
| classic | failed | angry | 1, 6, 10, 15, 24, 10, 6, 1 |
| classic | waiting | boring | 1, 3, 5, 9, 5, 1 |
| classic | running | thirst | 5, 14, 22, 31, 22, 5 |
| classic | review | happy | 20, 24, 29, 34, 24, 20 |
| nono-normal | idle | base | 5, 3, 1, 3, 5, 5 |
| nono-normal | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono-normal | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono-normal | waving | normal-action-2.swf | 67, 72, 82, 91 |
| nono-normal | jumping | normal-exp-2.swf | 1, 6, 11, 40, 1 |
| nono-normal | failed | normal-exp-4.swf | 1, 9, 14, 19, 24, 19, 9, 1 |
| nono-normal | waiting | normal-exp-3.swf | 1, 7, 13, 22, 7, 1 |
| nono-normal | running | normal-action-1.swf | 1, 4, 7, 12, 15, 1 |
| nono-normal | review | normal-exp-1.swf | 24, 27, 39, 30, 27, 24 |
| nono | idle | base | 1, 2, 3, 3, 2, 1 |
| nono | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono | waving | super-exp-2.swf | 14, 18, 26, 30 |
| nono | jumping | super-action-6.swf | 42, 45, 48, 51, 56 |
| nono | failed | super-exp-4.swf | 1, 6, 12, 17, 22, 17, 12, 1 |
| nono | waiting | super-exp-3.swf | 1, 7, 17, 23, 7, 1 |
| nono | running | super-action-7.swf | 46, 52, 58, 64, 58, 46 |
| nono | review | super-exp-1.swf | 89, 90, 92, 94, 92, 89 |
| nono-annual | idle | base | 1, 3, 5, 7, 5, 1 |
| nono-annual | running-right | base | 48, 49, 50, 51, 52, 53, 54, 55 |
| nono-annual | running-left | base | 16, 17, 18, 19, 20, 21, 22, 23 |
| nono-annual | waving | annual-action-2.swf | 53, 56, 59, 64 |
| nono-annual | jumping | annual-exp-3.swf | 1, 6, 11, 6, 1 |
| nono-annual | failed | annual-exp-4.swf | 1, 7, 10, 13, 16, 13, 7, 1 |
| nono-annual | waiting | annual-exp-2.swf | 11, 14, 16, 18, 16, 11 |
| nono-annual | running | annual-action-6.swf | 45, 48, 50, 56, 59, 64 |
| nono-annual | review | annual-exp-1.swf | 1, 4, 9, 6, 4, 1 |

自动检查：124 张可下载图集的尺寸、非空帧、单元格边界、动态变化和整行完全重复检查通过。

视觉检查使用默认配色逐帧图，并在本地网页确认实际预览。对动画观感的取舍仍以预览为准；不同形态使用相同原游戏动作属于正常情况。
