---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第3册（章 5–13）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 3/6 册（章 5–13），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 5. P1 详解三：显存、分布式训练与长上下文

### 5.1 训练显存由什么组成

#### 30 秒标准答案

> 训练显存不能只按“参数量 × 数据类型字节数”估算。完整组成包括模型参数、梯度、优化器状态、可能的 FP32 master weights、activation、中间临时 buffer、通信 bucket 和显存碎片。推理主要看权重、KV Cache 和运行时 workspace；训练还要为反向传播和 optimizer 付出更大成本。

#### 数据类型字节数

| 类型 | 理论字节/元素 |
|---|---:|
| FP32 | 4 |
| FP16 | 2 |
| BF16 | 2 |
| FP8 | 1 |
| INT8 | 1 |
| INT4 | 0.5 |

实际文件和显存可能更大，因为还有：

- scale / zero-point；
- group metadata；
- 对齐与 padding；
- 未量化层；
- kernel workspace；
- 框架对象。

#### 只加载权重的粗估

`P` 个参数、每参数 `b` 字节：

```text
weight_memory ≈ P × b
```

例如 7B 参数：

```text
FP16/BF16: 7e9 × 2 ≈ 14 GB
FP32:      7e9 × 4 ≈ 28 GB
INT8:      7e9 × 1 ≈ 7 GB
INT4:      7e9 × 0.5 ≈ 3.5 GB
```

这是十进制 GB 粗估，不含任何额外开销，不能据此断言某张同容量 GPU 一定装得下。

---

### 5.2 AdamW 全量训练为什么常按约 16 bytes/param 起算

一种常见 mixed precision 配方：

```text
FP16/BF16 model parameter:  2 bytes
FP16/BF16 gradient:         2 bytes
FP32 master parameter:      4 bytes
FP32 Adam first moment m:   4 bytes
FP32 Adam second moment v:  4 bytes
----------------------------------
total:                     16 bytes/param
```

有的实现不保留独立 master weight，或梯度/optimizer 使用不同精度，所以可能是 12、16 或其他数字。正确面试说法：

> 16 bytes/param 是特定 Adam mixed-precision 配方的粗略下界，不是统一常数；还未包含 activation、临时 buffer 和碎片。

对于 7B：

```text
7e9 × 16 ≈ 112 GB
```

再加 activation 后，单卡显然很难做全量训练。

#### LoRA 显存为什么小很多但不是“只剩 adapter”

LoRA 冻结 base model：

- base weights 仍占显存；
- 不需要为全部 base weights 保存梯度和 Adam states；
- 只为 adapter 保存 trainable weights、gradients、optimizer states；
- activation 仍需反向，因此可能仍很大。

QLoRA 再把冻结 base weights 压到 4-bit，从而进一步降低权重占用。

---

### 5.3 Activation 显存为什么难用一个公式

Activation 与以下因素有关：

```text
batch size
× sequence length
× hidden size
× number of layers
× 每层保存的中间张量数量
× bytes
```

还受：

- 标准 Attention 是否保存 `n×n` 矩阵；
- FlashAttention；
- Gradient Checkpointing；
- FFN 中间维度；
- dropout；
- tensor/sequence parallel；
- autograd 实现。

长上下文下：

- 普通 Attention 中间项可能按 `n²` 增长；
- 即使 FlashAttention 避免物化完整矩阵，其他 activation 和计算仍随长度显著增长；
- batch 往往被迫下降。

粗略原则：

> 参数显存主要随模型规模增长；activation 主要随 batch、长度、层数和隐藏维度增长；KV Cache 是推理阶段随并发和上下文增长的核心状态。

---

### 5.4 Data Parallel

#### 30 秒标准答案

> Data Parallel（数据并行）在每张 GPU 放完整模型，各自处理不同 micro-batch，反向后对梯度做 all-reduce，使参数保持一致。它容易扩吞吐，但不解决单卡放不下完整模型的问题。

```text
GPU0: full model + batch shard 0
GPU1: full model + batch shard 1
...
backward
→ all-reduce gradients
→ 每卡执行相同 optimizer update
```

优点：

- 实现简单；
- 计算扩展自然；
- 每卡 batch 独立。

代价：

- 参数、梯度、optimizer states 在每卡复制；
- global batch 随卡数扩大，需要调整训练配方；
- 梯度 all-reduce 通信。

DDP（DistributedDataParallel）就是常见同步数据并行实现。

---

### 5.5 Tensor Parallel

#### 30 秒标准答案

> Tensor Parallel（张量并行）把一个大矩阵运算切到多张 GPU，例如按列切 QKV 投影、按行切输出投影。它能解决单层权重放不下的问题，但每层都需要频繁集合通信，所以通常优先在高速互联的单节点内使用。

示意：

```text
W = [W1 W2]
GPU0 计算 XW1
GPU1 计算 XW2
→ concat / all-reduce
```

关键：

- 切的是同一层 tensor；
- 通信发生频繁；
- NVLink/NVSwitch 等高速互联很重要；
- TP degree 过大可能通信压过计算。

对于 Attention，常按 head 切分；需要保证 head 数与 TP degree 兼容，GQA 的 KV heads 还会影响切分策略。

---

### 5.6 Pipeline Parallel

#### 30 秒标准答案

> Pipeline Parallel（流水线并行）把不同层放在不同 GPU，micro-batch 像流水线一样依次经过各 stage。它能放下超深模型、跨节点通信量相对可控，但存在 pipeline bubble、负载不均和调度复杂度。

```text
GPU0: layers 0-9
GPU1: layers 10-19
GPU2: layers 20-29
GPU3: layers 30-39
```

为减少空闲，输入拆成多个 micro-batch。问题：

- pipeline warmup/drain bubble；
- stage 计算不均；
- activation 需要跨 stage 传输；
- 多种 1F1B / interleaved schedule；
- batch 太小时利用率差。

---

### 5.7 ZeRO-1、ZeRO-2、ZeRO-3

ZeRO（Zero Redundancy Optimizer）的第一性目标是消除 Data Parallel 中每卡重复保存的训练状态。

| Stage | 分片对象 | 每卡仍复制 |
|---|---|---|
| ZeRO-1 | optimizer states | 参数、梯度 |
| ZeRO-2 | optimizer states + gradients | 参数 |
| ZeRO-3 | optimizer states + gradients + parameters | 需要时 all-gather 完整参数片段 |

假设 data parallel world size 为 `N`，被分片状态理想情况下可约缩到 `1/N`，但实际还有通信 buffer、临时 all-gather、碎片和不均匀分片。

#### Stage 越高为什么不一定越快

- 分片越彻底，通信和调度越多；
- ZeRO-3 前向/反向需要按层 all-gather 参数；
- 小模型或慢网络下，节省显存可能换来吞吐下降；
- 最合适 stage 取决于“是否装得下”与网络。

---

### 5.8 FSDP

#### 30 秒标准答案

> FSDP（Fully Sharded Data Parallel，全分片数据并行）在数据并行 worker 间分片参数、梯度和 optimizer states。计算某模块前 all-gather 参数，反向后 reduce-scatter 梯度并重新分片。概念上与 ZeRO-3 接近，但 API、模块 wrapping、state dict 和运行时实现属于 PyTorch 体系。

关键数据流：

```text
sharded parameters at rest
→ forward 前 all-gather 当前模块参数
→ 计算
→ 可 reshard
→ backward 需要时再 gather
→ gradients reduce-scatter
→ optimizer 更新本地 shard
```

#### FSDP 与 DDP

- DDP：每卡完整模型，all-reduce gradients；
- FSDP：训练状态分片，计算时临时聚合。

#### Auto wrap 的意义

分片粒度太大：

- 峰值 all-gather 高；
- overlap 较差。

粒度太小：

- collective 次数太多；
- launch overhead 大。

通常按 Transformer block wrap 是常见起点，但需要 profiling。

---

### 5.9 CPU Offload

把参数、optimizer states 或 KV/activation 的一部分放到 CPU 内存，在需要时传入 GPU。

优点：

- GPU 显存不够时可运行；
- 允许更大模型或 batch。

代价：

- PCIe/NVLink-C2C 带宽远低于 GPU HBM；
- 数据搬运可能成为瓶颈；
- CPU 内存和 pinned memory 压力；
- optimizer step 可能变慢；
- 与 accumulation、checkpoint 等组合有实现限制。

正确回答：

> Offload 首先解决 capacity，不一定提升 speed。若模型本来能在 GPU 装下，盲目 offload 往往变慢。

---

### 5.10 3D 并行怎么选

3D Parallelism 通常指：

```text
Data Parallel
× Tensor Parallel
× Pipeline Parallel
```

有时再结合：

- Sequence Parallel；
- Expert Parallel；
- Context Parallel；
- ZeRO/FSDP；
- CPU/NVMe offload。

#### 选择思路

1. **单卡能装下完整训练状态**：DDP 最简单；
2. **完整模型能装，optimizer/gradient 太大**：ZeRO/FSDP；
3. **单层或完整参数都放不下**：TP；
4. **层数多、跨节点**：PP；
5. **MoE**：增加 expert parallel；
6. **超长序列**：sequence/context parallel。

实际先问：

- GPU 型号和 HBM；
- 节点内 NVLink/NVSwitch；
- 节点间 InfiniBand 带宽；
- 模型层数、hidden、heads、experts；
- sequence length；
- 吞吐目标和 checkpoint 约束。

不能背“ZeRO 一定优于 TP”或“TP 只适合 NVLink”。它们解决的切分维度不同，常组合使用。

---

### 5.11 Sequence Parallel 与 Context Parallel

#### Sequence Parallel

把某些原本在每个 TP rank 重复的 sequence 维度 activation 切分，常用于 Norm、dropout 等区域，降低 activation 冗余。

#### Context Parallel

把超长序列的 token 维度分到不同设备，让每卡只持有部分上下文，再通过 ring/all-gather 等方式完成 Attention 所需的信息交换。

区别需结合具体框架定义；面试不要把二者说成统一标准 API。核心共同点：

> 当模型维度切分已不足以解决长序列 activation/attention 压力时，再沿 sequence/context 维切分。

---

### 5.12 长上下文训练的成本

设序列长度从 `n` 增加到 `2n`：

- 线性层 token 计算约变 2 倍；
- 标准全 Attention 的 pairwise 计算约变 4 倍；
- KV/普通 token activation 约变 2 倍；
- 数据 batch 往往需要下降；
- 有效训练 token 数和优化配方也变化。

因此“把 max_length 改大”不是完整长上下文训练：

- 位置编码需适配；
- 数据需要真实长依赖；
- packing 和 document mask；
- FlashAttention；
- checkpointing；
- context parallel；
- 长上下文评测；
- 防止短任务能力退化。

#### Packing

把多个短文拼进一条长序列提高 token 利用率，但必须：

- 用 document boundary mask 防止跨文档错误注意；
- 正确处理 position id；
- 正确处理 EOS；
- 避免 label 泄漏。

---

### 5.13 显存估算面试例题

#### 例 1：7B BF16 只做推理，为什么 16GB 卡仍可能不够

```text
weights ≈ 14GB
+ KV Cache
+ CUDA context
+ temporary workspace
+ fragmentation
+ logits / sampling buffer
```

所以理论权重刚好小于 16GB 仍不代表可运行。

#### 例 2：为什么 batch 和 context 都会吃显存

- batch 增加：并发序列数变多，activation/KV 都增加；
- context 增加：每条序列状态变长；
- 两者相乘决定大量运行时状态。

#### 例 3：Gradient Checkpointing 和 ZeRO 是否解决同一问题

- Checkpointing：主要压 activation；
- ZeRO/FSDP：主要压训练状态冗余；
- 两者正交，可组合。

#### 例 4：量化能否用于全量训练

低比特权重可用于某些量化训练方法，但普通 PTQ 量化模型不能直接视为稳定的全量训练方案。QLoRA 的关键是：

- 量化 base frozen；
- adapter 在较高精度训练；
- 不是直接对所有 4-bit 离散权重做普通 AdamW 更新。

---

### 5.14 与金融 Agent 的真实边界

你的项目是模型能力的消费与编排系统，不是基础模型训练平台：

- 没有证据表明执行过多机 3D parallel 训练；
- 没有证据表明使用 ZeRO/FSDP 训练金融模型；
- 没有维护训练集群或 checkpoint pipeline；
- 当前价值主要在数据、检索、证据、路由、评测和降级。

可以这样把知识迁移到项目：

> 如果未来需要本地部署或微调，我会先按权重、KV Cache、activation 和训练状态分别核算显存，再决定 QLoRA、FSDP 或推理量化，而不是只看模型参数量。当前项目优先调用外部或现成模型，因为核心需求是最新事实和可追溯证据。

---

## 6. P1 详解四：推理、KV Cache、量化与 Serving

### 6.1 Prefill 与 Decode

#### 30 秒标准答案

> LLM 推理分 Prefill 和 Decode。Prefill 一次处理整段 prompt，生成各层 KV Cache，矩阵较大、并行度高，通常更偏计算密集；Decode 每步只输入新 token，读取全部历史 KV 并生成一个 token，矩阵较小、并行度低，常更受显存带宽和 KV Cache 访问限制。

#### Prefill

输入 `n` 个 prompt token：

```text
prompt
→ embedding
→ 所有 Transformer layers
→ 为每层生成 n 个 token 的 K/V
→ 得到最后位置 logits
```

特点：

- token 可并行计算；
- Attention 对 prompt 长度有二次部分；
- 大矩阵乘法较容易吃满 GPU；
- 决定 TTFT 的重要部分。

#### Decode

每一步：

```text
new token
→ 计算该 token 的 Q/K/V
→ Q 与历史所有 K 做 attention
→ 读取历史 V
→ 输出 logits
→ sampling 得到下一个 token
→ 新 K/V 追加到 cache
```

特点：

- 一次通常只处理每条序列的 1 个 token；
- 必须顺序进行，无法并行生成未来 token；
- 需反复读取模型权重和历史 KV；
- 高并发 batching 才能提高 GPU 利用率。

#### 为什么优化方向不同

- Prefill：chunked prefill、FlashAttention、计算并行；
- Decode：continuous batching、KV 管理、GQA/MQA/MLA、量化、speculative decoding。

---

### 6.2 KV Cache 原理与公式

#### 为什么需要缓存

没有 KV Cache 时，生成第 `t` 个 token 会重复计算前 `t-1` 个 token 的 K/V，浪费巨大。因为历史 token 的隐藏表示在固定层和固定上下文下不变，可以缓存。

#### 粗略显存公式

对 decoder-only 模型：

```text
KV bytes
≈ 2
× num_layers
× batch_or_concurrent_sequences
× cached_tokens_per_sequence
× num_kv_heads
× head_dim
× bytes_per_element
```

开头的 `2` 表示 Key 和 Value。

若请求长度不同，真实值应对每条序列的已缓存 token 求和，并考虑：

- beam / parallel samples；
- block padding；
- speculative tokens；
- prefix sharing；
- cross-attention cache；
- scale metadata；
- runtime fragmentation。

#### 示例

假设：

```text
layers = 32
tokens = 4096
kv_heads = 8
head_dim = 128
dtype = BF16 = 2 bytes
batch = 1
```

```text
KV ≈ 2×32×4096×8×128×2
   ≈ 512 MiB
```

并发 32 条、上下文都接近 4096 时，仅 KV 理论值约 16 GiB。说明 serving 不能只看权重。

#### MHA/MQA/GQA/MLA 影响

- MHA：`num_kv_heads = num_query_heads`；
- GQA：KV heads 减少到分组数；
- MQA：KV heads = 1；
- MLA：缓存低维 latent 与必要的位置相关分量，公式依架构。

所以 GQA/MQA 不只降低容量，也降低 decode 每步读取 KV 的带宽。

---

### 6.3 TTFT、TPOT、吞吐和端到端延迟

#### TTFT

TTFT（Time To First Token，首 token 延迟）：

```text
排队
+ tokenization
+ scheduling
+ prefill
+ 第一次 sampling
```

长 prompt 通常显著增加 TTFT。

#### TPOT / ITL

TPOT（Time Per Output Token，每输出 token 时间）或 ITL（Inter-Token Latency，token 间延迟）主要反映 decode 速度。

#### 端到端延迟

近似：

```text
E2E latency
≈ TTFT + output_tokens × TPOT
```

更精确时是首 token 后剩余 token 数。

#### 吞吐

常见：

- requests/s；
- input tokens/s；
- output tokens/s；
- total tokens/s。

必须注明口径，因为 prefill token 和 decode token 的计算特性不同。

#### 延迟与吞吐冲突

更大的 batch：

- GPU 利用率和吞吐上升；
- 请求可能排队更久；
- 单请求 latency 可能上升。

生产系统要看 SLO：

- p50/p95/p99 TTFT；
- p95 TPOT；
- 满载吞吐；
- 拒绝率；
- 成本/token。

---

### 6.4 Static Batching 与 Continuous Batching

#### Static Batching

等一批请求凑齐，一起生成到全部结束。短请求完成后仍可能等待最长请求，GPU slot 被浪费。

#### Continuous Batching

也叫 iteration-level batching。每个 decode iteration：

- 完成的请求立即移出；
- 新请求可加入；
- batch 组成动态变化；
- scheduler 在 prefill/decode 之间分配 token budget。

收益：

- 减少空闲 slot；
- 提升并发吞吐；
- 更适合请求长度不一致的在线服务。

代价：

- 调度更复杂；
- KV Cache 动态管理；
- 高负载下 TTFT 与 TPOT 要平衡；
- chunked prefill 可能影响 decode 抖动。

---

### 6.5 PagedAttention

#### 30 秒标准答案

> PagedAttention 借鉴虚拟内存分页，把每个请求逻辑连续的 KV Cache 拆成固定大小 block，物理显存可以非连续分配。这样能减少预留和碎片，支持动态增长、共享前缀和更高并发。它主要是 KV Cache 内存管理方法，不等于把 Attention 的理论计算复杂度降为线性。

#### 为什么传统连续分配浪费

请求最大长度未知。若提前按最大长度预留：

- 大量内部浪费；
- 并发下降。

若需要连续扩容：

- 搬移成本高；
- 外部碎片。

分页后：

```text
logical KV blocks for request A:
[0][1][2][3]

physical GPU blocks:
[7][21][4][18]
```

通过 block table 映射。

#### 与操作系统分页的不同

这是思想类比。GPU KV block 管理、attention kernel 和 swap/offload 策略由推理引擎实现，不等于直接调用 OS 虚拟内存机制。

---

### 6.6 Prefix Caching

#### 原理

若多个请求共享完全相同的 token prefix：

```text
[system prompt + 长文档] + question A
[system prompt + 长文档] + question B
```

可复用 prefix 对应的 KV Cache，避免重复 prefill。

#### 适合你的金融场景

- 同一份年报被连续追问；
- 固定 system prompt 和工具说明；
- 同一主题研究包上问多个问题；
- 多轮会话中前缀不变。

#### 关键限制

- 必须是 token 级前缀相同，不是“语义相似”；
- 只能减少共享前缀的 prefill 计算；
- 不会加速新生成 token 的 decode；
- 缓存会占显存，需要 eviction policy；
- prompt 中时间戳、随机 ID、证据顺序变化会破坏命中率。

工程启示：

> 稳定、规范化 prompt 不只是方便评测，也有利于 prefix cache 命中。

---

### 6.7 Speculative Decoding

#### 30 秒标准答案

> Speculative Decoding 用较小 draft model 或其他轻量方法一次提出多个候选 token，再由目标模型并行验证。只接受与目标模型分布一致的部分，因此在正确实现下不必改变目标分布。收益取决于接受率、draft 成本和验证 kernel；不是任何模型都加速。

#### 数据流

```text
draft model 先生成 k 个候选
→ target model 一次并行验证
→ 接受连续通过的 token
→ 在首次拒绝处按 target 分布修正
→ 重复
```

为什么可能更快：

- 原本 target 每次 forward 只得到 1 个 token；
- 现在一次 target 验证可能接受多个 token；
- 以更多单次计算换更少串行步骤。

#### 影响因素

- draft 与 target 越一致，acceptance rate 越高；
- draft 太大则自身成本高；
- batch 很大时 target 本已高利用率，收益可能下降；
- 采样温度越高，候选更难命中；
- 额外 KV、树候选和调度有内存开销。

EAGLE、MTP、n-gram speculation 等属于不同 draft 机制，不应混为一个固定算法。

---

### 6.8 Sampling：Temperature、Top-k、Top-p

模型输出 logits `z_i`。

#### Temperature

```text
p_i = softmax(z_i / T)
```

- `T < 1`：分布更尖，稳定保守；
- `T > 1`：分布更平，随机多样；
- `T → 0`：接近 greedy，但实现通常单独处理。

Temperature 不会给模型增加知识，只改变采样分布。

#### Top-k

只保留概率最高的 k 个 token，重新归一化。

- 固定候选数；
- 在分布很尖或很平时不自适应。

#### Top-p / Nucleus Sampling

按概率从高到低累计，保留累计概率达到 `p` 的最小集合。

- 候选数随分布自适应；
- 常用于开放生成。

#### Repetition Penalty

降低已出现 token 或 n-gram 的再次概率，可缓解复读。但过强会：

- 破坏必须重复的公司名和数字；
- 让措辞不自然；
- 不能修复训练或 prompt 的根因。

#### 金融回答建议

- 事实抽取、JSON、工具调用：低温或 greedy，更重确定性；
- 开放式 brainstorming：可适度提高温度；
- 高风险结论：多采样不是事实校验，应回到证据和规则；
- 固定随机种子也不等于跨硬件、框架绝对复现。

---

### 6.9 Greedy、Beam Search 与 Sampling

#### Greedy

每步选概率最大 token：

- 快、确定；
- 局部最优不保证全局序列概率最高；
- 容易单调或重复。

#### Beam Search

保留 top-B 条候选序列：

- 适合翻译等目标较确定的任务；
- 计算和 KV Cache 约随 beam 扩大；
- 开放对话中可能更模板化；
- 长度惩罚影响大。

#### Sampling

按概率采样：

- 产生多样结果；
- 适合创作和候选生成；
- 事实任务需外部校验。

Agent 工具调用通常偏 greedy/低温；研究假设生成可多样采样，但最终答案必须走证据门。

---

### 6.10 量化的三个问题：量化什么、何时量化、怎么计算

#### 量化对象

- Weight-only：W8A16、W4A16；
- Weight + Activation：W8A8、FP8 W8A8；
- KV Cache quantization；
- optimizer states；
- training-aware quantization。

`W4A16` 表示权重 4-bit，activation/计算路径通常更高精度。

#### 何时量化

- PTQ（Post-Training Quantization）：训练后量化；
- QAT（Quantization-Aware Training）：训练中模拟量化误差；
- 在线量化：加载时动态转换；
- 预量化 checkpoint：离线校准后保存。

#### 基本映射

将浮点数映射到整数：

```text
q = clamp(round(x / scale) + zero_point)
x_hat = scale × (q - zero_point)
```

可按：

- per-tensor；
- per-channel；
- per-group；
- 对称/非对称。

group 更小通常精度更好，但 scale metadata 和 kernel 开销更高。

---

### 6.11 INT8、INT4、FP8 的权衡

#### INT8

- 容量约为 FP16 权重一半；
- W8A8 可利用整数矩阵乘；
- activation outlier 处理很重要；
- 精度通常较稳，但速度依硬件/kernel。

#### INT4

- 权重容量约为 FP16 的四分之一；
- 常见 weight-only；
- 对 group size、校准和 kernel 更敏感；
- 适合容量受限和单机部署；
- 反量化开销可能限制速度。

#### FP8

- 浮点格式保留指数结构；
- 适合支持 FP8 Tensor Core 的新硬件；
- 可量化 weights、activations、KV；
- 需要 scale recipe；
- 旧 GPU 不能因为文件是 FP8 就获得原生加速。

#### 必考纠错

> 低比特一定减少存储，但不保证端到端更快。真实速度取决于硬件原生指令、矩阵形状、batch、反量化融合、kernel、内存带宽和未量化算子。

---

### 6.12 GPTQ、AWQ、GGUF、Marlin

#### GPTQ

GPTQ 是训练后 weight-only 量化家族，通常逐层/逐块利用校准数据和近似二阶信息，尽量降低量化引入的输出误差。

特点：

- 常见 4-bit；
- 需要校准；
- 有大量预量化模型；
- 速度取决于对应 runtime/kernel。

#### AWQ

AWQ（Activation-aware Weight Quantization）利用 activation 统计识别重要权重通道并做缩放/保护，目标是在低比特下保持精度。

特点：

- 常见 W4A16；
- 需要代表性校准数据；
- 适配高性能 kernel 时可加速；
- 校准分布不匹配会影响质量。

#### GGUF

GGUF 更准确地说是 llama.cpp 生态常用的模型文件格式/容器，支持多种量化类型和 metadata，适合 CPU、Apple Silicon 和本地混合推理。它不是一个单独量化数学算法。

#### Marlin

Marlin 是面向特定低比特权重的高性能 GPU kernel/执行方案。它说明：

> “量化方法”和“让量化模型真正跑得快的 kernel”是两层问题。

#### 选择建议

- 快速 QLoRA：bitsandbytes/NF4 生态；
- GPU 4-bit serving：看引擎支持的 AWQ/GPTQ/Marlin；
- 本地 CPU/Mac：GGUF/llama.cpp；
- 新 NVIDIA GPU 高吞吐：评估 FP8；
- 最终必须在目标模型、目标硬件和真实请求上 benchmark。

---

### 6.13 CPU 与 GPU 推理

#### GPU

适合：

- 大吞吐；
- 低延迟；
- 较大 batch；
- FP16/BF16/FP8/INT8 Tensor Core；
- 多并发服务。

限制：

- HBM 昂贵；
- 运维和功耗；
- 模型需适配多卡和 kernel。

#### CPU

适合：

- 小模型或低并发；
- 成本敏感；
- 数据不能离开本机；
- GGUF 低比特；
- prompt 不长、延迟要求不极端。

限制：

- 内存带宽通常低于 GPU HBM；
- 大模型每 token 需读取大量权重；
- 延迟和吞吐可能较差。

#### Apple Silicon / 统一内存

可运行较大低比特模型，开发体验和隐私好；但统一内存容量不等于高端数据中心 GPU 的吞吐，仍受带宽、kernel 和并发限制。

#### 选择公式

不要只问“模型能否装下”，还要问：

```text
目标 p95 latency
并发数
输入/输出 token 分布
每天 token 量
硬件成本和利用率
数据隐私
运维能力
```

---

### 6.14 vLLM、SGLang、TensorRT-LLM、LMDeploy

#### vLLM

定位：通用、高吞吐、OpenAI-compatible 的开源 LLM serving engine。

常见能力：

- PagedAttention；
- continuous batching；
- prefix caching；
- chunked prefill；
- speculative decoding；
- 多种量化；
- tensor/pipeline parallel；
- LoRA serving。

适合：快速搭建通用模型服务、模型生态广、吞吐优先。

#### SGLang

定位：高性能 serving runtime + 面向复杂生成程序/结构化调用的生态。

常见能力：

- Radix/Prefix cache 思路；
- continuous batching；
- speculative decoding；
- 多种 attention backend 和量化；
- tensor/data/expert parallel；
- structured output、复杂 LLM program 优化。

适合：复杂 Agent workload、前缀复用高、需要细粒度 runtime 控制。

#### TensorRT-LLM

定位：NVIDIA GPU 上的高性能编译和推理栈。

特点：

- 深度利用 TensorRT/CUDA kernel；
- FP8/INT8/INT4 等 NVIDIA 优化；
- inflight batching、KV 管理、多 GPU；
- 为特定模型和硬件调优可获得很高性能。

代价：

- NVIDIA 绑定更强；
- 构建 engine、版本兼容和部署复杂度较高；
- 自定义模型适配成本可能高。

#### LMDeploy

定位：开源大模型部署工具链，提供高性能推理后端、量化和服务接口，在中文模型生态中常见。

适合：

- 快速部署支持列表内模型；
- TurboMind/PyTorch backend；
- 量化与 OpenAI-compatible 服务。

#### 不能做的“排行榜回答”

不要说“vLLM 一定最快”：

- 模型架构不同；
- 输入输出长度不同；
- batch/concurrency 不同；
- GPU 不同；
- 量化不同；
- structured decoding、LoRA、speculation 支持不同。

标准选型流程：

```text
先定义 workload 和 SLO
→ 筛选模型/量化/硬件支持
→ 用真实 trace benchmark
→ 比 p95 latency、throughput、memory、稳定性和运维成本
```

---

### 6.15 Chunked Prefill 与 Prefill/Decode 调度

长 prompt 的 prefill 如果一次独占 GPU：

- 其他 decode 请求 token 间延迟抖动；
- TTFT 排队；
- batch token budget 难平衡。

Chunked Prefill 把长 prompt 拆为若干 chunk，与 decode iteration 混排：

优点：

- 更平滑调度；
- 控制单轮 prefill token 量；
- 改善 decode latency。

代价：

- 调度和 kernel launch 增加；
- TTFT 可能因分片和让路变长；
- 最优 chunk size 依 workload。

生产 serving 不只是“模型 forward 更快”，而是一个排队与资源调度问题。

---

### 6.16 金融 Agent 的推理选型

#### 当前真实实现

- Workbench 通过可选 LLM 配置做回答精修；
- 无可用 LLM key 时可降级为结构化模板/确定性输出；
- 事实来源是 DuckDB、知识库和关系数据；
- 没有证据表明当前生产使用 vLLM、SGLang、TensorRT-LLM 或 LMDeploy；
- 没有证据表明已部署 GPU 集群、量化模型或 speculative decoding。

#### 面试正确说法

> 当前项目把模型调用封装成可选生成层，优先保证无模型或模型失败时仍能输出结构化结果。如果未来本地化部署，我会先测 workload：金融问答通常 prompt 较长、输出中等、同一报告可能被多次追问，因此 prefix caching 和 chunked prefill 可能有价值；若并发上升，再比较 vLLM 和 SGLang。是否量化要在真实金融问答与结构化 tool call 集上验证，不能只看通用 benchmark。

#### 一个合理容量规划例子

先记录一周 trace：

- prompt p50/p95 tokens；
- output p50/p95 tokens；
- 峰值并发；
- 相同 prefix 比例；
- quick/deep 模式占比；
- 可接受 TTFT/TPOT。

再选择：

```text
模型大小
→ 精度/量化
→ 单卡或多卡
→ serving engine
→ max model length
→ concurrency/token budget
→ prefix cache
→ benchmark
```

这比先说“我要上 vLLM”更像真实工程决策。

---

### 6.17 推理高频追问与纠错

1. **KV Cache 是否缓存所有 hidden state？**
   主要缓存各层 Attention 的 K/V，不是把所有中间 activation 都保留用于反向。

2. **Prefix cache 是否对相似文档生效？**
   通常要求 token 前缀完全一致；语义相似不是 cache key。

3. **PagedAttention 是否让单请求算得更少？**
   主要减少 KV 浪费和碎片，支持高并发；不必然减少该请求所需 attention FLOPs。

4. **INT4 是否必然比 FP16 快 4 倍？**
   不。容量约四分之一是理论权重存储对比，端到端速度受反量化和 kernel 限制。

5. **TTFT 高应该只优化模型？**
   还要看排队、tokenization、prompt 长度、RAG、网络、scheduler 和 prefill。

6. **Speculative Decoding 是否改变答案？**
   严格接受/修正算法可保持目标分布；某些近似实现或配置可能改变输出，需要说明。

7. **金融任务温度应该设 0 吗？**
   结构化事实任务可低温，但事实正确性仍靠数据和校验；温度 0 不能消灭幻觉。

---

## 7. P1 面试速查表、项目映射与自测

### 7.1 一页公式速查

#### Attention

```text
Q = XW_Q, K = XW_K, V = XW_V
Attention(Q,K,V) = softmax(QK^T/sqrt(d_k) + Mask)V
```

```text
标准 Attention：
投影 O(nd²)
注意力 O(n²d)
注意力矩阵 O(n²)
```

#### 语言模型

```text
P(x_1...x_T) = ∏ P(x_t|x_<t)
L_NLL = -Σ log Pθ(x_t|x_<t)
PPL = exp(mean NLL)
```

#### LoRA

```text
W' = W + (α/r)BA
trainable params = r(d_in+d_out)
```

#### KV Cache

```text
KV bytes ≈
2 × layers × concurrent_sequences × cached_tokens
  × kv_heads × head_dim × bytes_per_element
```

#### 训练 Global Batch

```text
global_batch =
micro_batch_per_gpu
× accumulation_steps
× data_parallel_world_size
```

#### RRF（与你项目直接相关）

```text
RRF(d) = Σ 1/(k + rank_i(d))
```

---

### 7.2 概念对照速查

| 容易混淆 | 正确区分 |
|---|---|
| Self-Attention vs Cross-Attention | Q/K/V 同源 vs Q 与 K/V 不同源 |
| Causal Mask vs Prefix Tuning | 注意力可见性约束 vs PEFT 可学习前缀 |
| RoPE vs ALiBi | 旋转 Q/K vs logits 距离偏置 |
| MQA vs GQA | 1 组 KV vs 多组但少于 Q heads |
| FlashAttention vs PagedAttention | 优化 Attention IO vs 管理 KV blocks |
| Pretraining vs SFT | 原始文本语言建模 vs 指令示范 |
| DPO vs PPO | 离线偏好损失 vs 在线 rollout 强化学习 |
| LoRA vs QLoRA | 低秩 adapter vs 4-bit frozen base + LoRA |
| DDP vs FSDP | 每卡完整模型 vs 训练状态分片 |
| Checkpointing vs ZeRO | 压 activation vs 压训练状态冗余 |
| Quantization vs GGUF | 数值压缩方法 vs 模型文件格式/生态 |
| TTFT vs TPOT | 首 token 延迟 vs 后续 token 间延迟 |
| RAG freshness vs 模型知识 | 外部证据是否最新 vs 权重内统计知识 |

---

### 7.3 你的金融 Agent：技术能力矩阵

| 技术 | 当前项目状态 | 面试如何讲 |
|---|---|---|
| Transformer 基础模型训练 | 未实现 | 理解原理，消费现成模型能力 |
| Embedding | 已有 RAG 链路 | BGE dense 负责语义召回 |
| BM25 | 已实现 | `rank_bm25` + 自定义 tokenizer |
| Hybrid + RRF | 已实现 | BM25/dense 排名融合 |
| Cross-encoder rerank | 已实现代码链路 | 对候选页联合编码打分 |
| RAG freshness gate | 已实现 | stale/unknown 默认不得进严格证据 |
| LLM 回答精修 | 可选实现 | 无 key 时可降级 |
| SFT/LoRA/QLoRA | 未实现 | 未来只考虑格式、工具和行为适配 |
| RLHF/DPO/GRPO | 未实现 | 当前是系统层对齐，不是参数训练 |
| vLLM/SGLang serving | 未实现/未验证 | 可作为未来本地部署选型 |
| FP8/INT4 production | 未实现/未验证 | 必须在真实问答集 benchmark |
| FSDP/ZeRO 训练 | 未实现 | 能解释容量规划，但不能说有实战 |
| Agent Router | 已实现 | known/planner/data-gap/clarification |
| 风险门控 | 已实现一部分 | 低风险、置信度阈值、默认 preview |
| Output review | 已实现 advisory | 不是已验证自动裁判 |
| PIT/no-lookahead | 已有机制 | 历史回放只用当时可得信息 |

---

### 7.4 把 P1 技术自然接到项目，而不是硬贴

#### 问：你为什么没微调一个金融大模型？

> 我的目标是研究事实的时效性和可追溯性。行情、公告和产业证据变化快，把它们写进模型权重会更新慢、难引用，所以先选择 RAG + 结构化数据库。微调更适合稳定回答格式、工具调用和缺口表达；只有积累足够高质量失败样本并建立离线评测后，我才会考虑 LoRA/SFT。

#### 问：如果未来本地部署，你怎么选推理框架？

> 先采集真实 workload，包括 prompt/output 长度、峰值并发、重复 prefix 和 TTFT/TPOT SLO。这个项目可能是长 prompt、中等输出、同一研报多轮追问，因此 prefix caching 和 chunked prefill 值得测。然后在目标硬件上比较 vLLM 与 SGLang，而不是先凭框架名做决定。

#### 问：INT4 会不会影响金融回答？

> 可能。金融任务对数字、代码、结构化 tool call 和细粒度事实区分敏感。我会分别测检索后回答忠实度、引用正确率、数值抽取、JSON 合法率和延迟，而不是只看通用 benchmark。低比特先保证容量，速度和质量要实测。

#### 问：你项目中的“对齐”是什么？

> 不是 RLHF，而是系统层对齐：把事实源外置，用户记忆只当 prior，RAG 过期证据禁止进入严格回答，回答必须暴露反证和数据缺口，再做 claim-level fidelity 与 output review。它不更新模型参数，但能约束系统行为。

#### 问：长上下文模型能否把整个知识库塞进去？

> 不能把“能放下”等同于“能可靠利用”。全塞会增加 TTFT、成本和干扰，也缺乏新鲜度、权限和引用治理。我的系统仍先检索和精排，只把少量高质量证据给模型；长上下文用于保留更完整的候选材料，而不是替代 RAG。

---

### 7.5 20 道口头自测题

先用 30 秒回答，再检查是否包含“原理—权衡—项目边界”。

1. 为什么 Attention 要除以 `sqrt(d_k)`？
2. Attention 的 `O(n²)` 到底来自哪一步？
3. Multi-Head 为什么比单头更有表达力？
4. Decoder-only 训练为什么能并行，推理却不能并行生成未来 token？
5. RoPE 为什么能表达相对位置？
6. RoPE scaling 为什么不等于可靠长上下文？
7. Pre-LN 为什么通常更容易训练深层模型？
8. SwiGLU 比普通 FFN 多了什么？
9. MHA、MQA、GQA 如何影响 KV Cache？
10. FlashAttention 与 PagedAttention 有什么本质区别？
11. MoE 为什么总参数大但活跃计算小？最大工程难点是什么？
12. SFT 和预训练损失看似相同，为什么效果目标不同？
13. RLHF 中 policy、reference、reward、critic 各做什么？
14. DPO 为什么能不训练显式 Reward Model？它损失了什么能力？
15. LoRA 具体省了哪些显存，哪些没有省？
16. 为什么 QLoRA 不一定比 LoRA 更快？
17. ZeRO-3/FSDP 与 Gradient Checkpointing 分别解决什么？
18. Prefill 和 Decode 分别受什么限制？
19. 为什么 INT4 权重只有约四分之一，不代表速度四倍？
20. 你的金融 Agent 实际用了哪些 P1 技术，哪些只是未来选型？

---

### 7.6 8 道白板计算题

#### 题 1

`d_model=4096` 的标准 MHA，忽略 bias，Q/K/V/O 投影约多少参数？

答案：

```text
4 × 4096² ≈ 67.1M
```

#### 题 2

序列长度从 4K 变 8K，标准 Attention score 数量变几倍？

答案：约 4 倍；线性层 token 计算约 2 倍。

#### 题 3

一个 7B BF16 模型权重理论占多少？

答案：约 14GB 十进制；不含 KV、workspace 和碎片。

#### 题 4

LoRA 对一个 `4096×4096` 矩阵使用 `r=8`，可训练参数多少？

答案：

```text
8×4096 + 4096×8 = 65,536
```

原矩阵：

```text
4096² = 16,777,216
```

约为原矩阵的 0.39%。

#### 题 5

32 层、8 KV heads、head_dim 128、4096 tokens、BF16、batch 1，KV 约多少？

答案：约 512MiB。

#### 题 6

每卡 micro-batch 2，8 卡 DP，accumulation 16，global batch 多少条序列？

答案：

```text
2×8×16 = 256
```

#### 题 7

为什么 Adam mixed-precision 常粗估 16 bytes/param？

答案：2B 参数 + 2B 梯度 + 4B master weight + 4B m + 4B v；实现可能不同。

#### 题 8

GQA 从 32 个 KV heads 减到 8 个，其他不变，KV Cache 理论变为多少？

答案：约原来的 1/4。

---

### 7.7 典型错误答案纠正

| 错误说法 | 更准确说法 |
|---|---|
| Decoder-only 理论上永远最优 | 它对通用生成高效统一，但架构选择依任务 |
| FlashAttention 将复杂度降到 O(n) | 它主要减少 IO/显存，精确全注意力 FLOPs 仍近似二次 |
| DPO 不需要 Reward Model，所以没有奖励 | 它把隐式 reward/preference 关系写入直接优化目标 |
| GRPO 不需要任何其他模型 | 它省 critic，但仍需 policy、采样和 reward，可能还有 reference/KL |
| LoRA 训练时间一定远小于全参 | 状态和通信省很多，但主模型前反向仍执行 |
| BF16 比 FP16 全面更精确 | BF16 范围大，FP16 尾数精度更高；稳定性配方不同 |
| INT4 一定最快 | 低存储不等于 kernel/端到端最快 |
| vLLM 只支持 PagedAttention | 现代 vLLM 还有 continuous batching、prefix caching、量化等 |
| 长上下文替代 RAG | 长窗口不解决新鲜度、引用、权限和噪声 |
| output review 就是 RLHF | 没有用反馈更新 policy 参数就不是 RLHF |

---

### 7.8 建议的 7 天 P1 复习法

**Day 1：Transformer 数据流**
手画一层 Decoder：Norm → QKV → Masked Attention → Residual → FFN → Residual。

**Day 2：位置与 Attention 优化**
推导 `sqrt(d_k)`、RoPE 相对位置；口述 MHA/MQA/GQA 和 FlashAttention。

**Day 3：训练流水线**
讲清 Pretraining → SFT → preference alignment；对比 PPO/DPO/GRPO。

**Day 4：LoRA 与训练稳定性**
白板写 LoRA 维度和参数量；复习 AdamW、warmup、BF16、checkpointing。

**Day 5：显存与分布式**
做 7B/14B 权重和 Adam 粗估；讲 DDP、TP、PP、ZeRO、FSDP。

**Day 6：推理与量化**
讲 Prefill/Decode、KV 公式、TTFT/TPOT、PagedAttention、INT4/FP8。

**Day 7：项目模拟面试**
每道题最后必须加一句：“我的项目已实现什么、没实现什么、为什么这样选。”

---

## 8. 项目故事 STAR 模板

### 故事 1：从“会聊天”到“可审计金融研究 Agent”

S：金融问答容易出现看似合理但无证据的结论。
T：让 Agent 输出可追溯、可降级、可复验的研究回答。
A：设计多源检索 `[S/G/R/W/M]`，引入证据分层、反证、缺口、output review、claim fidelity。
R：系统从“生成答案”升级成“带证据、带边界、可审稿的研究工作台”。
边界：尚未证明预测更准，主要提升可审计性。

### 故事 2：知识库 RAG 从单向量召回升级成 Hybrid

S：金融术语、股票代码、同义概念混杂，单一检索容易漏。
T：提升召回覆盖并保持可解释。
A：BM25 + BGE dense + RRF + exact boost + wikilink neighbor + rerank。
R：具备完整工程链路和 A/B 评测框架。
边界：真实收益还需可信人工标注 query set。

### 故事 3：Agent Memory 解决多工具上下文断裂

S：Codex、Claude、Devin 等多个 Agent 参与同一项目，偏好和交接容易丢。
T：构建跨 Agent 共享记忆底座。
A：Git + Markdown + YAML frontmatter + Obsidian，分层目录、frontmatter、writeback、lint。
R：换工具不丢上下文，人类可读，Git 可审计。
边界：不是强一致数据库，检索层仍在演进。

### 故事 4：金融回测防前视

S：历史研究容易把未来信息提前用于过去决策。
T：把“信息发生时间”和“系统可得时间”分开。
A：定义 `publish_time/available_time`，PIT 截断，快照回放，claim 级验证。
R：让系统能区分“事后正确解释”和“当时可做判断”。
边界：不是所有存量页面都已完成时间治理。

---

## 9. 面试中一定要诚实表达的限制

1. **这是个人金融研究系统，不是多人生产 SaaS。**
2. **Workbench 默认本地 `127.0.0.1`，没有生产级公网认证。**
3. **RAG 检索已实现工程链路，但 README 明确仍是 POC。**
4. **评测集还需要真实问题和人工校准。**
5. **output_review 是 advisory gate，不是已验证的自动裁判。**
6. **Temporal Facts 的 active/superseded/invalidated 时序边还在规划。**
7. **daily-loop 的完整“盘前预测→盘后验证→写回记忆”闭环尚未完全自动化。**
8. **记忆 prior 化和贝叶斯仲裁是正确方向，但 Workbench 仍有旧 synthesis 被直接引用的缺口。**

这种诚实不会减分，反而显得你真的做过工程。

---

## 10. 30 秒自我介绍项目版

> 我自己落地了一个 A 股金融研究 Agent。它的核心不是让大模型直接给投资结论，而是把本地 DuckDB 盘面数据、Markdown/Obsidian 知识库、结构化关系图谱、Hybrid RAG、用户经验记忆和回答质检组合起来。
> 技术上我重点做了三件事：第一，知识库侧实现 BM25 + dense embedding + RRF + rerank 的检索链路；第二，金融回答侧把事实、推演、预测分层，并用引用、反证、缺口和 claim-level fidelity 降低幻觉；第三，用 Git + Markdown 的 agent-memory 解决多 Agent 协作和长期记忆沉淀。
> 我会诚实区分已实现和未实现：现在它更像个人研究工作台，不是生产 SaaS；检索和评测框架已经具备，但真实效果还需要更可靠的人工标注集和历史盲测。

---

## 11. 下一步学习顺序

1. 先背熟 P0：Agent / Memory / RAG / Hybrid / rerank / 防幻觉 / 评测 / 无前视。
2. 每个题都按“四段法”回答：
   - 第一性原理；
   - 标准答案；
   - 我的项目怎么做；
   - 边界和改进。
3. 用本手册第 3—7 章系统复习 P1，不再只背缩写。
4. 做白板估算：Attention、LoRA 参数量、训练状态、KV Cache。
5. 最后做模拟面试：围绕你的项目连续追问，而不是孤立背题。

---

## 12. 口径校对参考

本扩展版以原始论文与当前官方文档的稳定概念为主，避免照抄 PDF 中的旧框架结论。建议面试前按目标公司的模型栈再查看最新版本：

- Transformer：<https://arxiv.org/abs/1706.03762>
- RoPE / RoFormer：<https://arxiv.org/abs/2104.09864>
- RMSNorm：<https://arxiv.org/abs/1910.07467>
- GLU/SwiGLU：<https://arxiv.org/abs/2002.05202>
- GQA：<https://arxiv.org/abs/2305.13245>
- FlashAttention：<https://arxiv.org/abs/2205.14135>
- LoRA：<https://arxiv.org/abs/2106.09685>
- QLoRA：<https://arxiv.org/abs/2305.14314>
- DPO：<https://arxiv.org/abs/2305.18290>
- PyTorch FSDP2：<https://docs.pytorch.org/docs/stable/distributed.fsdp.fully_shard.html>
- NVIDIA 混合精度 / FP8：<https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/>
- vLLM：<https://docs.vllm.ai/>
- SGLang：<https://docs.sglang.io/>
- Hugging Face 量化选型：<https://huggingface.co/docs/transformers/en/quantization/selecting>

版本敏感提醒：

- serving 框架支持的模型、量化和硬件变化很快；
- FP8/INT4 是否加速必须以目标 GPU 和 kernel 为准；
- GRPO、RLVR、speculative decoding 变种较多，回答时先说明所指论文或实现；
- 不要把官方 feature list 等同于你在项目中实际启用和验证过。

---

## 13. V3 阅读方式：从“知道术语”升级到“讲清为什么这样实现”

V2 解决的是大模型基础知识问题；V3 解决的是项目深挖问题。

面试官问你的项目时，真正想判断的通常不是你能否说出 RAG、Agent、Memory、DuckDB，而是：

1. 你遇到的业务问题是什么；
2. 为什么一次 LLM 调用解决不了；
3. 哪些环节应该确定性执行，哪些环节可以交给概率模型；
4. 为什么选当前方案，而不是另一种常见方案；
5. 真实代码在哪里，输入和输出是什么；
6. 数据缺失、检索失败、模型失败时如何处理；
7. 如何知道系统比原来更好；
8. 哪些已经实现，哪些只是 POC、设计或下一步。

本章之后每项技术都尽量按同一套结构讲：

```text
业务问题
→ 第一性原理
→ 技术选型
→ 架构与模块边界
→ 真实代码实施
→ 输入输出与数据流
→ 异常和降级
→ 评测与证据
→ 当前实现边界
→ 30 秒答案 / 2 分钟答案 / 追问
```

### 13.1 你的系统不是一条“LLM 链”，而是四条彼此约束的链

```text
控制链
用户问题 → 澄清 → 路由 → QuestionPlan → 工具/数据块调度

证据链
S/G/R/W/M/V/D/L → evidence audit → 反证 → 引用 → claim lineage

生成链
AnswerSpec → 模板回答或可选 LLM synthesis → output review → 修订 → 校验

学习链
interaction → judgment/correction → checkpoint → verdict → experience card
```

四条链不能混为一谈：

- **控制链**决定“下一步做什么”；
- **证据链**决定“结论凭什么成立”；
- **生成链**决定“怎样表达且不越界”；
- **学习链**决定“下次能否减少同类错误”。

如果把它们全部交给一次自由生成，任何一步错误都会藏在一段流畅文本里，既难定位，也难回放。

### 13.2 确定性系统与概率模型的分工

| 问题 | 更适合的实现 |
|---|---|
| 股票代码、日期、表名、数据是否存在 | 确定性解析 / SQL / schema |
| 风险等级、是否允许自动执行 | 规则和门禁 |
| 索引是否新鲜、命令是否超时 | 程序检查 |
| 数字是否与来源一致 | claim-level 校验 |
| 用户到底想问什么 | 规则优先，必要时 LLM 辅助 |
| 多源证据如何组织为解释 | LLM 或模板 |
| 如何提出反证和后续验证点 | 规则骨架 + LLM 表达 |
| 最终语言是否清楚 | LLM 擅长 |

一句话：

> 把不能错、能形式化检查的部分交给程序；把开放语义理解和表达交给模型；模型输出再回到程序约束。

这也是整个金融 Agent 的主设计哲学。

---

