---
title: 金融时间长河与个人记忆的实际消费来源审计
type: inbox
agent: codex
source: 固定部署d5d7c5f6017e及候选afea1daf4源码、既有Pi与8792工件、只读台账元数据和隔离合成探针
date: 2026-10-07
tags: [inbox, finance, river, memory, consumption, audit]
status: draft
---

# 金融时间长河与个人记忆的实际消费来源审计

> 原始调研，待审阅。来源均于 **2026-10-07 VERIFIED** 读取；下文的 `[推断]` 不等于运行结果。真实模型调用0、外网调用0、生产数据库/用户台账写入0。只读取台账的计数、字段和哈希，不展示私人记忆正文。

## 结论及证据边界

时间长河、历史市场取证、个人记忆不是同一入口。河已有六轨切片、区间及投影；实际消费者主要是专用API/CLI、带读、教学、情景树及研究演化目录。通用Episode工具声明中没有river工具；当前对照工件也未提供其直接投影送达作者的证据。不能把“模型查了河所依赖的同一张行情表”当作“模型消费了六轨时间长河”。[六轨与切片](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:51)、[工具注册来源](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_tool_registry.py:50)、[实际P工件目录](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1)

个人记忆链已经能注册、召回和投递。P的D2/D5首个模型请求之前收到的是 `user_memory_gap/status=empty`，不是有效先验正文；D5/D7另有真实显式memory调用，均返回0张证据。隔离合成记录能通过同一runner进入Episode第一个请求，但使用的是桩模型，不能证明自然模型采用它或得到质量收益。[D2原件](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D2-stock-rephrased/continuous-episode.json)、[D5原件](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D5-theme-unseen/continuous-episode.json)、[D7原件](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D7-nonexistent-entity/continuous-episode.json)、[投递实现](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1091)

## 固定代码与方法

部署树为 `/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e`；候选实际路径为 `/Users/a77/fwp-wt-answer-quality-closeout-1007`，调研开工时HEAD为 `afea1daf4daa1f12fa3380e73f11355f0dcf4ed0`、树干净。“@afea1daf4”是版本标识，不是另一目录。逐文件SHA256及AST（抽象语法树）导入检查证明：river、river_query、river_window、river_projection、river_window_contract、user_memory、memory_prefetch、evidence_capabilities、userspace及agent_episode两树相同；episode_tools差异为finance查询口径说明，memory runner及其他开场预取函数的AST相同。[部署源码根](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e)、[候选源码根](/Users/a77/fwp-wt-answer-quality-closeout-1007)

| 核对对象 | 部署SHA256或AST哈希 | 与候选相同 |
|---|---|---|
| river.py | `645d12adfb2140483a945cc76b616e19b18d5561a00c7bd1012ef53621a8009d` | 是 |
| river_query.py | `d96968cf8a4b8d5edfee1b6ea2dad56e6b7cd989714dfd4238ead5a6712d2671` | 是 |
| river_window.py | `7089e1e3e5da54e46ee13f0a6669d4a4918f27d17a698b8cb26f61d460e585b3` | 是 |
| user_memory.py | `8ca9d2fb9c786f84bc112d40bc9339e21cf4fe1083406f4663841d2b137ce462` | 是 |
| memory_prefetch.py | `db1a2ea34f2ec037fcdc7a3cc18d09fb02750432ba9d60de3627f222fc534354` | 是 |
| memory_lookup_runner AST | `1b33534a6f0c8130f34401e0c9fdbc79fa770cb42e152affe76b31b7a7a0aa4a` | 是 |

这些哈希定位本次实际读取的正文，不给后续移动树移签。静态导入覆盖 `intelligence/api`、`services`、`runtime` 的Python文件；未执行API、河CLI或生产DuckDB查询，也没有读取凭据。[memory runner所在文件](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2000)

## 河：六轨、查询与消费者

六轨是 `market/theme/opinion/capital/stock/judgment`。前五轨读取canonical市场/板块/个股事实及研报目录；判断轨读取调用者提供的 `checkpoints.jsonl`，按题材精确同名和登记日期取可证伪点。它不是judgments/corrections语义召回。`slice_river` 的默认checkpoint路径由 `user_space()` 解析；专用 `/api/river/slice` 未传用户或checkpoint参数，不能用此API存在自证某个模型请求已读到该请求用户的私有记忆。[轨定义](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:51)、[判断轨](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:843)、[缺省路径](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:1053)、[API](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/api/river_routes.py:877)

| 路径 | 实際工作与边界 | 到模型请求的证据 |
|---|---|---|
| `river.slice_river` | 一天×实体六轨，实体精确匹配；read_only DuckDB；Gap不当零；可选严格PIT、冻结版本、教学旁路 | 本次未读库运行；有源码路径，未认证通用作者消费 |
| `river_query` | 横截面scan、队列比较、区间累计；由API scan/cohort/range等调用 | 是专用查询/展示消费，不是Episode已取证证明 |
| `river_window_contract.window` | 逐日调用slice再派生累计，承接截止日/缺轨 | 是区间对象消费者；非默认模型菜单入口 |
| `river_window` | 日向量、窗口签名、聚类；未提供checkpoint路径则该维缺失 | CLI/派生签名路径；没有自然作者使用证明 |
| `river_projection.project` | 纯函数，输出块、遗漏、限制、来源及projection_hash | 参数例子含`ask_synthesis`并不证明该入口实际调用 |
| guided_reading | 取slice→固定task/budget投影→render带读 | 这里没有模型生成调用；人能看到不等于作者已收到 |
| 教学/情景树/研究演化 | 教学额外上下文、情景树推进、外部依据版本目录 | 有调用链；需各自工件才能证明模型消费，不能并到普通ask |

表中VERIFIED源码定位：[slice入口](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:996)、[river_query](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river_query.py:140)、[区间](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river_window_contract.py:203)、[窗口](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river_window.py:196)、[投影](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river_projection.py:318)、[带读](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/guided_reading.py:553)、[教学](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/teaching_framework/leader_succession.py:316)、[情景树](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/scenario_trees.py:669)、[研究演化](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_evolution/adapters.py:146)。研究演化明确排除judgment轨作为外部依据；那是被维护的用户对象。[排除位置](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_evolution/adapters.py:174)

AST解析 `_DEFAULT_TOOL_METADATA` 得19项声明、river名称0、memory_lookup在场。当前prod-1九份完整Episode中，river命名调用0、证据定位中`cp:`/`river:`投影引用0。Pi v6十份session的显式memory/river调用均0；D6六次为finance_query。该计数范围不包括不存在完整Episode的第十份P输入，也不排除模型在其他任务读取相同底层事实表。[声明来源](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_tool_registry.py:50)、[P原件](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1)、[Pi路径与封存映射](/Users/a77/.finance-runtime/model-first-harness-1006/blind-review-v6/sealed/key.json)

## 个人记忆：装配、投递与真实活性

`userspace` 按显式user、环境user、default解析身份，用户根优先 `FORESIGHT_USERS_DIR`。memory_lookup要求能力已授权且user/root明确，否则不注册；这避免每个请求静默读取default私库。召回读取judgments/corrections及方法记录，判断可靠性另使用checkpoints/verdicts；默认keyword，每类最多5条，读取窗口200条。它返回用户先验，不是市场事实。[身份/路径](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/userspace.py:63)、[注册门](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1974)、[召回](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/user_memory.py:473)、[可靠性](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/user_memory.py:215)

opening-memory与显式调用共用同一runner及投影。已解析公司/题材研究和个人回顾可触发开场预取；单纯盘面复盘不是该集合。预取最多1秒、两个读取线程，正文每项1000字符、总6000；先过滤未来/未知日期，再截断。显式历史截止不允许用无日期先验。晚到结果不进入其他turn，不占模型工具slot但仍占时间与上下文。[触发集合](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/evidence_capabilities.py:552)、[投影与限额](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/memory_prefetch.py:16)、[预取调用](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2173)

Episode在第一次模型请求前把registry.opening_prefetch加入证据账本，并以user消息 `source=opening_prefetch` 投递，不伪造模型tool_call。[执行入口](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1091)、[先种入后调用](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1591)

| 本轮读取的真实工件 | 活性事实 | 能证明的阶段 |
|---|---|---|
| P D2 | model_input seq4，196字符，SHA256 `116294f61cddfff0c0e22d257f22496971a80014574960ed6051a526d05f757a`；首模型seq8；memory tier为gap、status=empty | 缺口提示已装配/送达；没有有效先验使用证明 |
| P D5 | model_input seq4，747字符，SHA256 `c5b15c359e7c7a1da14f4b1dba78f17f43bc5bd8fee03d0cead61aceb8fc8837`；首模型seq8；显式memory结果seq14，0证据、1gap | 自动路径及显式工具调用均活跃，未取得有效先验 |
| P D7 | 显式memory结果seq26，0证据、1gap；没有memory开场证据 | 模型选择了工具；未证明读到有效用户记忆 |

注意上述开场字符可能包含其他开场来源，不能把整块747字符都算记忆量。九份P Episode合计显式memory请求2次、真实 `user_memory` 证据0、memory gap证据2；十份Pi session memory请求0。来源：[D2](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D2-stock-rephrased/continuous-episode.json)、[D5](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D5-theme-unseen/continuous-episode.json)、[D7](/Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D7-nonexistent-entity/continuous-episode.json)、[Pi封存映射](/Users/a77/.finance-runtime/model-first-harness-1006/blind-review-v6/sealed/key.json)

## 台账可达性与隔离合成证据

既有health原件声明用户根 `/Users/a77/.local/share/finance-workbench/users`。本次未连接8792采新health，因此它是既有运行根证据，非当前进程环境的重新认证。只读扫描该根：236个目录（含测试/审计身份，不能说236个真实用户），原始JSON记录judgments14、corrections235、checkpoints262、verdicts730；无非法JSON行。原始行含状态事件，不等于有效召回条数。[既有运行根](/Users/a77/.finance-runtime/model-first-harness-1006/deploy-e33021db023d/health.json)、[只读扫描根](/Users/a77/.local/share/finance-workbench/users)

default账户canonical loader本次读到judgments0、有效corrections4，无读错误。固定公共词查询“复盘/盘面/主线/风险/分母”通过纯keyword选择得到1条，日期2026-09-26，记录规范化SHA256 `f91242f844834e0bfe7a48ab91a2fc2de0955ae4fa7559ce5fd7bf939f88a930`。这里只证明可达和可选，不把正文送给真实模型；该日期晚于v6历史题的2026-07截止，不能期待历史题注入它。[default台账](/Users/a77/.local/share/finance-workbench/users/default/corrections.jsonl)、[canonical loader](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/corrections.py:143)、[关键词选择](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/user_memory.py:77)

隔离探针仅写临时合成alice台账并在结束后删除；关闭其他市场开场预取、禁止socket连接、固定keyword、关闭向量缓存。真实注册/召回/投影/Episode循环得到memory证据1张，开场与显式lookup哈希相同 `31ab6f01bc1c1159`；首个桩模型请求含合成纠偏及非市场事实标识、不含临时私路径，request SHA256 `c16afdce7272252a438b0283a3c650d30cfd1ee11dd1fa26bd8df36aeadab0bc`，17436字符。仅1次桩调用、0真实模型、runtime工具调用0，model_input seq4，outcome partial。这证明请求装配与投递，不证明自然采用或收益。[同runner](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2000)、[共享投影](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/memory_prefetch.py:64)、[首请求投递](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1091)

## 五段证据状态

| 功能 | 存在 | 装配 | 送达模型 | 实际使用 | 自然收益 |
|---|---|---|---|---|---|
| 河六轨/查询/投影 | VERIFIED源码 | 专用消费者有链路 | 本次P/Pi未证直接投影送达 | API/脚本消费者可定位，未证作者使用 | 未验证 |
| 显式memory_lookup | VERIFIED源码 | 身份+权限门已在真实P激活 | 真实空结果已返回；合成非空已投递 | P有2次选择调用；非空自然先验使用未证 | 未验证 |
| opening-memory | VERIFIED源码 | P D2/D5已自动装配 | 真实缺口提示+合成非空首请求 | 自然作者是否遵循有效先验未证 | 未验证 |
| checkpoints/verdicts校准 | VERIFIED读链 | reliability及河judgment用途分开 | 随召回结果可形成先验/校准说明 | 本批有效记录无自然使用证据 | 未验证 |

表的事实分别由上文源码、P原件和隔离探针支持；`未验证` 不转换成“没有能力”。历史memory三臂实验的veteran相对coldstart均分变化0.5/20，工件自己声明约2.4/20噪声底，不能用它认证当前版本的收益。[既有实验原件](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/eval/runs/20260827T191014Z-user-memory-diff.json)

## 可测开关与边界

- 个人召回：`FINANCE_MEMORY_RECALL_MODE=keyword|semantic|hybrid`，默认keyword；`FINANCE_MEMORY_VECTOR_CACHE_DIR=off`关缓存写。semantic/hybrid可能加载嵌入模型并写缓存，本次未运行它们。不要把关闭身份或换空用户称为等条件召回消融。[配置](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/memory_semantic.py:46)
- 开场记忆无独立环境开关。现有 `registry.opening_prefetch` 可在隔离副本置空而保留同身份/权限及显式memory工具；这是可消融接口，不是本次改动或模型运行授权。保留同一截止日和可见台账，避免把未来记录过滤当缺记忆。[注册返回](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2173)、[seed](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1091)
- 带读：`FORESIGHT_GUIDED_READING`，显式override优先于环境，再看新用户判据；零历史用户默认开。`FORESIGHT_TEACHING_LABELS_DB`控制额外教学读数。[开关](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/guided_reading.py:134)
- 河：`knowledge_cutoff`、`require_strict`、`allow_hindsight`、`frozen_snapshot_root`、`checkpoints_path`、投影task/rules/budget都是已有接口。比较不同投影需保持同切片哈希，不将实体别名归一化误当跨供应商数值可比。[slice](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river.py:996)、[投影](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/river_projection.py:318)
- 情景树：`FORESIGHT_SCENARIO_TREE_RESOLVE`未on则不推进；on路径会append用户情景台账，此轮未执行，不能作为只读消融直接开。[写入边界](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/scenario_trees.py:654)

## 提炼提示

[推断] 本轮实际比较若要识别记忆增益，必须确认同身份、相同可见截止和确实相关的有效先验已经进入请求，再看自然回答是否准确使用及是否改变判断。仅有工具菜单、脚本PASS、首请求包含文本或多个视角标题，都不能直接支持“比Pi更好”。本笔记只提供来源与可消融接口，不新增模型预算、不充当独立gold、不修改部署。[实际消费入口](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2000)、[模型输入入口](/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:1749)
