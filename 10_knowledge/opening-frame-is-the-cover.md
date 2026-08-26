---
title: 成片封面是第 0 帧，不是旁边一张图
type: knowledge
agent: cursor
source: vidio Foresight 投资人片 2026-08-26（用户看 r9 说「0:00 没看到封面」）
date: 2026-08-26
tags: [knowledge, methodology, video, hyperframes, gsap, cover]
status: verified
related: ["[[../20_projects/vidio]]"]
---

# 成片封面是第 0 帧，不是旁边一张图

## 失败形状

单独做了一张很完整的封面 PNG，用户打开的却是成片。第 0 帧是空纸 / 空场，字标还在淡入。旁路文件再精致，播放器第一眼也看不见。

## 根因（两种叠在一起）

1. **交付物认错。** 封面技能默认出 5:2 编辑图；成片是 16:9。用户说「做封面」且接下来「看看成片」，要的是**成片第一帧**，不是另一张图。
2. **GSAP `fromTo` 会先把东西藏掉。** `fromTo(..., { opacity: 0 }, ...)` 默认 `immediateRender: true`：时间轴还没走到淡入，第 0 帧已经是隐藏态。HTML/CSS 里字标写得再大，渲出来的第一帧仍是空的。

换任何 HTML+GSAP / HyperFrames 片子都会再犯。After Effects 里 opacity 从 0 起、Web 里 CSS animation 初始 `opacity: 0`，形状相同。

## 做法

- 成片封面 = 定稿 mp4 的 t=0。旁路 PNG 只给分享/投影，不能代替第一帧。
- 开幕字标：**CSS 默认就是落定态**；GSAP 用 `set()` 钉住，不要从隐藏 `fromTo`。
- 视觉跟成片设计系统走（画幅、纸色、字标），不要因为封面车道默认 `rn-cover-skill` 就换一套 5:2 暖白编辑风。
- 验收抽 t=0，不要抽「封面目录里有没有 PNG」。

## 成立条件

只适用于「封面是给这段成片用的」。独立海报、小红书封面、文章头图仍走封面图文车道。
