---
title: 两个转发参数在所有夹具里同值时，删转发的变异必存活——阳性对照要在包装层把两个值分开
type: knowledge
source: finance-workspace-private 工单 #72 自适应研究回路传输层绝对截止收口（2026-09-22）
date: 2026-09-22
tags: [methodology, mutation-testing, verification, fixtures, timeout]
status: verified
related: ["[[mutation-test-before-claiming-silent]]", "[[gate-assertion-granularity]]"]
---

# 两个转发参数在所有夹具里同值时，删转发的变异必存活

## 现象

包装函数 `_open_deadline_http_response(request, timeout, *, deadline, is_cancelled)` 把两个时限交给传输层：
`timeout` 是单发片，`deadline` 是共享研究截止。验收要求「把 `deadline=` 改为不传，至少一条常规用例红」。
实际：定向 25 条 + 引用传输层的 13 个文件 351 条**全绿**，13 场景严格探针也 0 越窗。作者在传输层模块上做过四条变异「四杀零存活」，同样对此盲。

## 为什么

- 探针夹具里 `timeout == deadline`（都是 0.8 s）：两值同值，丢掉任意一个不改变任何可观测量。
- 唯一区分两值的测试直接调 `llm_http_transport.urlopen(...)`，绕过了包装函数——被删的那一行根本没执行。
- 传输层模块的变异只能证明「传输层拿到 deadline 会守」，证明不了「有人把 deadline 交给了它」。

「转发」这件事只有在**转发与不转发产生不同观测**的夹具下才被证明；同值夹具与绕层夹具都让这条缝不可观测。

## 做法

1. 在**做转发的那一层**写一条测试，两个值明显拉开：片 10 s、共享截止 0.5 s、对端滴流 ~2.9 s，断言包装层自己的异常类型且墙钟 < 2 s。
2. 变异（`deadline=None`）下应红（DID NOT RAISE），`git checkout --` 还原后绿，sha256 与 HEAD 比对。
3. 同族追问：包装函数还转发了什么？本例 `is_cancelled=` 同样无人守（15 条 cancel 测试在变异下全绿）——现有取消测试都在「有行到达」时取消，传输层的 0.05 s 轮询只在停顿期才有区别。

## 判据

声明某条转发/管道被守之前，列出它转发的每个参数，问两句：这两个值在所有夹具里会不会相同？测试是从包装层进还是从被调方进？任一答案不好，就先补包装层的不同值夹具，再跑删转发变异。
运行时 `PYTHONDONTWRITEBYTECODE=1`、从已提交的还原点做，`--basetemp=X/Y` 前先 `mkdir -p X`（否则 tmp_path 夹具 setup 抛 FileNotFoundError 伪红）。
