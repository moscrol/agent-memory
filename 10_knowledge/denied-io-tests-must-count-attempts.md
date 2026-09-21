---
title: 禁止 IO 的测试必须记录尝试而不只抛异常
type: knowledge
agent: pi
source: finance-workspace-private E2 P3b 8ea6c5c1
date: 2026-09-14
tags: [testing, permissions, io, fail-closed]
status: verified
---

# 禁止 IO 的测试必须记录尝试而不只抛异常

证明“没有执行不允许的读取”时，给网络函数挂一个只会抛异常的替身不充分：生产代码可能捕获异常并返回空结果，测试仍然通过，但外呼尝试已经发生。

## 可执行做法

1. 替身先把调用追加到attempts，再抛错。
2. 测试结束断言attempts为空；不只断言最终无证据/无异常。
3. 同时测正向路径：临时数据要真实返回，防止把所有工具关掉而空洞通过。
4. 覆盖正常、缺源、空结果、过期路径；危险回落往往只在非正常路径触发。
5. 把连接、DNS解析、子进程等适用的不同通道分开拦；Python层探针不等于OS网络沙箱，不承诺覆盖任意原生库绕过。

## 已落地

`finance-workspace-private@8ea6c5c1` 的 `intelligence/tests/test_e2_local_freeze.py` 用上述模式测试四类临时本地工具。网络socket.connect/connect_ex/getaddrinfo与subprocess.Popen均累计调用；真实DuckDB/JSON/用户台账运行，不替换本地runner。

2026-09-22 codex续验：`fix/market-date-advisory-0921@b41c8d475` 的未来快照读取变异存活。`Path.read_text`替身抛出的AssertionError被loader当坏文件捕获，最终旧快照正确却掩盖未来文件已尝试读取。`b1e04452b`改为累计路径、返回后断言，同一变异从绿变红；完整24项反证仅签对应测试，完整Python/独立与真实验收仍阻塞。原件在该枝 `docs/verification/2026-09-22-market-cutoff-snapshot/`，不是只读最终返回值就认证无IO。

这是通用测试手法而非独立工具：每个项目的外呼通道和允许边界不同，机械保障应落到其回归测试，而不是另造一个声称覆盖所有IO的脚本。
