---
title: zsh 不给未加引号的 $VAR 分词——整串命令成了「command not found」，rc=127 既不是红也不是绿
type: knowledge
agent: claude
source: finance-workspace-private 2026-09-20 晚，K3 独立审核复跑：`E="env -i … PYTHONPATH=…"; $E $PY probe.py` 两次 rc=127、PASS=0 FAIL=0；改成 shell 函数里显式写 `env -i …` 后同一探针 27/27、18/18。同一坑 2026-09-17 已进过私有记忆，仍复踩，故入共享库。
date: 2026-09-20
tags: [knowledge, shell, zsh, gate, false-red, harness]
status: verified
---

# 现象

把一串命令前缀存进变量再展开——`E="env -i HOME=… PATH=…"; $E python x.py`——在 bash 里正常，在 zsh 里 `$E` 不分词，整串「env -i HOME=… PATH=…」被当成**一个**可执行文件名，报 `no such file or directory`，退出码 127。只看退出码和 PASS/FAIL 计数，会得到「0 通过 0 失败」，像一次什么都没跑的绿，或者被当成红。

# 根因

zsh 默认关闭 `SH_WORD_SPLIT`：未加引号的参数展开不按空白切分（这是 zsh 有意为之，避免 bash 的分词事故）。命令替换 `$(…)` 反而会分词。Claude Code / 多数 macOS 终端的默认 shell 是 zsh，脚本片段却常按 bash 习惯写。

# 判别

- 退出码 **127** = 找不到命令，与被测对象无关；**126** = 找到但不可执行。二者都不是测试结论。
- 报错信息里出现整串带空格的「文件名」，就是这个坑。
- 记忆里另一条同族：`${PIPESTATUS[0]}`（bash）在 zsh 里是空，要用 `${pipestatus[1]}`。

# 做法

1. 不把命令存变量。写 shell 函数：`run() { env -i HOME=… "$PY" "$1"; }`，或直接展开写。
2. 非要用变量：zsh 用 `${=E}` 强制分词，或用数组 `E=(env -i HOME=…)` 后 `"${E[@]}"`（bash/zsh 通用）。
3. 任何门禁脚本先断言 rc ∉ {126, 127} 再解读 PASS/FAIL；rc=127 时直接判「无结论，重跑」，不写进收据。
4. 复跑前先 `echo` 一次要执行的命令看分词是否符合预期。

# 可迁移性

换任何项目都会犯：只要 harness 在 zsh 下拼命令前缀。属于「读数工具本身坏了」一类假红/假绿，与 [[zsh-no-word-split-fakes-a-gate-red]]、`capture-exit-code-before-anything-else-runs` 同族。面试可讲：为什么退出码要分「被测失败」和「测试基础设施失败」两类。
