---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第2册（章 3–4）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 2/6 册（章 3–4），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 3. P1 详解一：Transformer 与模型结构

> 本章目标：不只会背名词，而是能从“信息如何流动、复杂度从哪里来、为什么这样设计”回答追问。
> 统一回答模板：30 秒答案 → 第一性原理 → 公式/数据流 → 技术权衡 → 项目映射 → 边界。

### 3.1 Transformer 整体架构

#### 30 秒标准答案

> Transformer 用 Attention 建模 token 之间的依赖，用前馈网络 FFN 做逐 token 的非线性特征变换，再通过残差连接和归一化稳定深层训练。原始 Transformer 是 Encoder-Decoder；现代生成式大模型通常采用 Decoder-only，每层主要由因果自注意力、FFN、残差和归一化组成。

#### 第一性原理

语言建模需要解决两个问题：

1. **上下文聚合**：当前 token 应该从哪些历史 token 取信息；
2. **特征变换**：聚合后如何把信息映射成更有用的高维表示。

Attention 解决第一个问题，FFN 解决第二个问题。残差连接让信息和梯度能跨层直达；归一化控制数值尺度。

Decoder-only 的一层可写成：

```text
x1 = x + Attention(Norm(x))
x2 = x1 + FFN(Norm(x1))
```

这是常见的 **Pre-LN（归一化在子层之前）** 结构。最后：

```text
hidden states
→ vocabulary projection
→ logits
→ softmax
→ 下一个 token 的概率分布
```

#### 为什么现代 LLM 多用 Decoder-only

- 训练目标和生成目标统一：都是“根据左侧上下文预测下一个 token”；
- 所有参数都服务于生成，不需要单独的 encoder；
- 数据格式统一，网页、代码、对话都可串成 token 序列训练；
- 自回归生成和 KV Cache 的工程生态成熟。

但不能说 Decoder-only 在所有任务上理论最优：

- Encoder-only 仍适合双向理解、分类、检索表示；
- Encoder-Decoder 对翻译、摘要、输入输出边界明确的 seq2seq 任务仍有优势；
- 最优架构取决于任务、训练数据、参数预算和推理约束。

#### 项目映射

你的金融 Agent 没有训练 Transformer，但三类组件依赖它：

- embedding 模型：把 query 和知识页编码为语义向量；
- cross-encoder reranker：让 query 与候选文档联合编码并打分；
- 生成模型：根据市场数据、RAG 证据、用户 prior 组织回答。

正确项目说法：

> 我没有重新训练基础模型，而是把不同 Transformer 能力放在系统中合适的位置：bi-encoder 负责大规模召回，cross-encoder 负责小规模精排，decoder-only LLM 负责受证据约束的生成。

---

### 3.2 Self-Attention：公式、参数量和复杂度

#### 30 秒标准答案

> Self-Attention 先把输入投影为 Query、Key、Value。Query 表示当前位置要找什么，Key 表示每个位置可被怎样匹配，Value 是真正被聚合的信息。通过缩放点积得到相关性，经 softmax 归一后对 Value 加权求和。

#### 核心公式

输入：

```text
X ∈ R^(n × d_model)
Q = XW_Q
K = XW_K
V = XW_V
```

单头注意力：

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k) + M)V
```

其中：

- `n`：序列长度；
- `d_model`：隐藏维度；
- `d_k`：每个 head 的 Query/Key 维度；
- `M`：mask；被屏蔽位置加上负无穷，softmax 后权重接近 0。

#### 为什么除以 `sqrt(d_k)`

假设 Q、K 每个分量独立、均值 0、方差 1：

```text
q · k = Σ(q_i k_i)
Var(q · k) ≈ d_k
```

维度越大，点积绝对值通常越大。直接送入 softmax 会让分布过尖：

- 最大项接近 1；
- 其他项接近 0；
- softmax 梯度变小，训练不稳定。

除以 `sqrt(d_k)` 后方差恢复到约 1，使 logits 处于较稳定尺度。

#### 参数量

标准 MHA（Multi-Head Attention，多头注意力）通常有：

```text
W_Q, W_K, W_V, W_O ∈ R^(d_model × d_model)
```

忽略 bias：

```text
参数量 ≈ 4 × d_model²
```

“多头”一般是把同一个总隐藏维度切成多个 head，并不必然让参数量随 head 数增加。

#### 时间和空间复杂度

标准全注意力：

```text
Q/K/V/O 投影：O(n d_model²)
注意力分数与加权：O(n² d_model)
注意力矩阵显存：O(n²)
```

因此：

- 短序列、大隐藏维度时，线性层计算可能占主导；
- 长序列时，`n²` 的 Attention 成本会成为核心瓶颈；
- 自回归 decode 有 KV Cache 后，每步只对历史 KV 做一次查询，但总 KV 读带宽仍随上下文增长。

#### 常见追问

**Q：Self-Attention 和 Cross-Attention 区别？**
A：Self-Attention 的 Q/K/V 来自同一序列；Cross-Attention 的 Q 来自解码端，K/V 来自编码端或外部序列。

**Q：Attention 能表达顺序吗？**
A：纯 Attention 对输入排列本身没有位置感，需要位置编码或位置偏置。

**Q：Attention 权重能否直接当解释？**
A：不能简单等同。它描述该层该头的加权路径，但不等于完整因果贡献；残差、FFN、后续层都会改变结果。

---

### 3.3 Multi-Head Attention 为什么有效

#### 30 秒标准答案

> 多头注意力把隐藏空间分成多个子空间，让不同 head 并行学习不同匹配模式，例如局部搭配、远程指代、实体关系或格式结构。它的价值不是简单复制同一个 Attention，而是增加表示子空间和关系模式的多样性。

#### 第一性原理

如果只有一个 attention distribution，所有关系要挤在同一种加权模式里。多头允许：

```text
head_i = Attention(XW_Q^i, XW_K^i, XW_V^i)
MHA(X) = Concat(head_1 ... head_h)W_O
```

在总维度固定时：

```text
d_head = d_model / h
```

每个 head 的维度更小，但多个 head 可以形成不同关系视角。

#### 需要避免的错误

- 不要说“每个 head 一定分别学习语法、实体、情感”；这是可能出现的现象，不是硬编码保证。
- 不要说“head 越多越好”；head 太多会让 `d_head` 太小，也增加调度和 kernel 开销。
- 多头中可能存在冗余，工程上才有 MQA/GQA 等压缩方案。

#### 项目映射

RAG 的 embedding 和 reranker 都使用多层、多头表示，但系统设计不依赖“解释某个 head”。你的可解释性来自：

- 可追溯文档来源；
- 检索分数和召回路径；
- claim 对应 evidence；
- 确定性质量检查。

这比用 attention heatmap 当金融结论解释更可靠。

---

### 3.4 Encoder-only、Decoder-only、Encoder-Decoder

| 架构 | Attention 可见范围 | 典型目标 | 擅长任务 |
|---|---|---|---|
| Encoder-only | 双向，token 可看左右文 | Masked LM、对比学习 | 分类、抽取、embedding、rerank |
| Decoder-only | 因果，只看左侧 | Next-token prediction | 生成、对话、代码、Agent |
| Encoder-Decoder | Encoder 双向；Decoder 因果并 cross-attend encoder | 条件序列生成 | 翻译、摘要、结构化 seq2seq |

#### 标准面试答案

> Encoder-only 更像“读懂整段文本后做判断”；Decoder-only 更像“按历史逐 token 续写”；Encoder-Decoder 先把输入编码成表示，再条件生成输出。三者不是简单的新旧替代关系，而是不同信息流约束。

#### 你的项目如何映射

- BGE 类 embedding：更接近 encoder 表示模型；
- cross-encoder reranker：把 query 和 document 放在一起做双向联合判断；
- 回答生成器：decoder-only LLM；
- 这形成“召回—精排—生成”的异构模型流水线。

---

### 3.5 Causal Mask、Padding Mask 与 Prefix Mask

#### Causal Mask

生成第 `t` 个 token 时只能看到 `≤t` 的 token：

```text
可见矩阵：
1 0 0 0
1 1 0 0
1 1 1 0
1 1 1 1
```

目的不是节省计算，而是防止训练时偷看未来答案，使训练条件与推理条件一致。

#### Padding Mask

一个 batch 内句子长度不同，需要把补齐的 pad token 屏蔽，否则模型会把填充当真实输入。

#### Prefix / Prefix-LM Mask

一个前缀区域内部可双向注意，生成区域保持因果注意：

```text
[可双向理解的 prefix] → [逐 token 生成的 suffix]
```

适用于某些条件生成或统一理解—生成任务。它不同于 PEFT 中的 Prefix Tuning；前者是 attention mask，后者是训练可学习的虚拟前缀表示。

#### 常见错误

- Causal Mask 不等于把未来 token 从训练样本删除；输入仍可并行计算，只是注意力矩阵屏蔽未来位置。
- 训练 decoder-only 时可一次并行算完整序列，推理时才必须自回归逐步生成。

---

### 3.6 RoPE：为什么旋转能编码相对位置

#### 30 秒标准答案

> RoPE（Rotary Positional Embedding，旋转位置编码）不把位置向量直接加到 token embedding，而是按位置旋转 Q 和 K 的二维分量。两个位置向量做点积时，旋转角之差自然对应相对距离，所以注意力分数能同时包含内容相似性和相对位置信息。

#### 第一性原理

把每两个维度看成二维向量。位置 `m` 对应旋转：

```text
R(mθ) =
[ cos(mθ)  -sin(mθ) ]
[ sin(mθ)   cos(mθ) ]
```

对 q、k 分别旋转：

```text
q_m = R(mθ)q
k_n = R(nθ)k
```

点积：

```text
q_m^T k_n
= q^T R(mθ)^T R(nθ) k
= q^T R((n-m)θ) k
```

结果依赖 `n-m`，因此自然带相对位置信息。

#### 优点

- 不增加随最大长度增长的位置参数表；
- 与点积注意力自然结合；
- 相对位置性质适合语言；
- 可用于 KV Cache，历史 K 的位置信息已经旋转后缓存。

#### 长上下文外推为什么困难

模型只在训练长度内见过一定角度和距离分布。推理长度超出训练范围时：

- 高频维度旋转过快，位置模式失真；
- 模型未学习过超远距离的注意力行为；
- 即使位置公式能算，也不代表模型能有效利用。

常见扩展方法：

- Position interpolation：把更长位置压缩到训练范围；
- NTK-aware scaling：按频率调整旋转尺度；
- YaRN 等方法：结合不同频段缩放和温度调整；
- 长上下文继续训练：让模型真正见到长序列。

正确说法：

> RoPE scaling 可以缓解位置外推，但“配置支持 128K”不等于模型在 128K 都有稳定检索、推理和忠实度，仍要做 needle、长文问答及业务任务评测。

---

### 3.7 ALiBi 与 RoPE 怎么选

ALiBi（Attention with Linear Biases）不旋转表示，而是在注意力 logits 上加入随距离增长的线性负偏置：

```text
score(i,j) = q_i · k_j / sqrt(d_k) - slope_h × distance(i,j)
```

| 对比项 | RoPE | ALiBi |
|---|---|---|
| 注入位置 | 旋转 Q/K | 修改 attention logits |
| 位置信息 | 相对旋转相位 | 距离惩罚偏置 |
| 参数 | 通常无可学习位置表 | 每个 head 固定 slope |
| 归纳偏置 | 内容与相对位置耦合 | 越远越受惩罚 |
| 生态 | 现代 decoder LLM 非常常见 | 一些长上下文模型使用 |

标准回答：

> ALiBi 更简单，具有明确的距离衰减偏置；RoPE 表达更丰富且生态更主流。不能脱离预训练方式直接替换，因为模型权重已经适应原位置方案。

---

### 3.8 LayerNorm、RMSNorm、Pre-LN、Post-LN

#### LayerNorm

对单个 token 的隐藏维度计算：

```text
μ = mean(x)
σ² = mean((x-μ)²)
LN(x) = γ ⊙ (x-μ) / sqrt(σ²+ε) + β
```

它同时做重新中心化和重新缩放。

#### RMSNorm

```text
rms(x) = sqrt(mean(x²)+ε)
RMSNorm(x) = γ ⊙ x / rms(x)
```

它不减均值，主要控制向量尺度，计算更简单。很多现代 LLM 使用 RMSNorm，但不能泛化成“RMSNorm 一定更准”；这是稳定性、效率和模型配方共同选择。

#### Post-LN

```text
x' = Norm(x + Sublayer(x))
```

原始 Transformer 使用。深层训练时梯度跨层路径会反复经过 Norm，通常更依赖 warmup 和初始化。

#### Pre-LN

```text
x' = x + Sublayer(Norm(x))
```

残差主干提供更直接的梯度通路，深层训练更稳定，因此现代 LLM 常见。

#### 追问：Pre-LN 的代价

- 深层表示变化有时不如 Post-LN 强；
- 最终输出前通常还要一个 final norm；
- 不能只看 Norm 位置，还要结合初始化、残差缩放、学习率。

---

### 3.9 FFN、GELU 与 SwiGLU

#### FFN 的作用

Attention 在 token 之间混合信息；FFN 在每个 token 内独立变换通道：

```text
FFN(x) = W_2 φ(W_1x)
```

它通常占 Transformer 大量参数和计算。

标准两层 FFN 参数量约：

```text
2 × d_model × d_ff
```

#### GELU

GELU（Gaussian Error Linear Unit）是平滑非线性函数，可理解为按输入大小做软门控。BERT、GPT 早期模型常用。

#### SwiGLU

常见形式：

```text
SwiGLU(x) = (SiLU(xW_gate) ⊙ xW_up)W_down
SiLU(z) = z × sigmoid(z)
```

含义：

- `W_up` 产生候选特征；
- `W_gate` 决定哪些特征通过；
- 逐元素乘法实现内容相关门控；
- `W_down` 投回隐藏维度。

SwiGLU 有三块矩阵，若 `d_ff` 不变会比普通 FFN 参数更多，所以很多架构会相应调整中间维度，不能只比较公式而忽略参数预算。

#### 项目类比

可用一个谨慎类比帮助理解：

> Attention 像从多份金融材料中决定“看谁”，FFN/SwiGLU 像对已聚合的信息做通道级加工和门控。但这只是认知类比，不能把神经网络内部机制等同于你的显式 Router。

---

### 3.10 MHA、MQA、GQA、MLA

#### 30 秒标准答案

> MHA 每个 Query head 都有自己的 K/V head，质量强但 KV Cache 大；MQA 让所有 Query head 共享一组 K/V，最省 KV 但可能损失表达；GQA 让若干 Query head 共享一组 K/V，是质量与效率折中；MLA 用低秩潜表示压缩 KV 相关状态，进一步降低缓存和带宽，但实现更复杂且依赖特定架构。

设：

- Query heads：`H_q`
- KV heads：`H_kv`

则：

```text
MHA: H_kv = H_q
GQA: 1 < H_kv < H_q
MQA: H_kv = 1
```

#### 为什么减少 KV head 能加速

自回归服务需要为每层、每个历史 token 保存 K 和 V。缓存近似正比于：

```text
H_kv × d_head
```

减少 `H_kv`：

- KV Cache 更小；
- 每步 decode 从显存读取的数据更少；
- 可容纳更多并发请求或更长上下文。

#### 质量权衡

- K/V 共享越多，不同 Query head 能访问的独立记忆子空间越少；
- MQA 最激进；
- GQA 常作为工程折中；
- 从 MHA 转 GQA 通常需要训练或 uptraining，不能只在配置中删 head。

#### MLA

MLA（Multi-head Latent Attention，多头潜在注意力）的核心思想是把 K/V 相关表示压缩到低维 latent，再在需要时恢复或吸收进投影计算。回答时应强调：

- 它不是简单的“更多 KV 共享”；
- 目标同样是减少 KV Cache 和内存带宽；
- 具体维度、RoPE 解耦方式依模型实现而异；
- 不要在没读目标模型实现时背一个万能公式。

---

### 3.11 FlashAttention：为什么“数学一样，速度更快”

#### 30 秒标准答案

> FlashAttention 是 IO-aware 的精确注意力算法。它不改变 Attention 的数学结果，而是把 Q/K/V 分块放进更快的片上 SRAM，通过 tiling 和 online softmax 避免把完整 `n×n` 注意力矩阵反复写入和读取高带宽显存 HBM，从而减少 IO、降低显存并提高速度。

#### 第一性原理

GPU 的算力增长快于显存带宽。标准 Attention 的问题不只是 FLOPs，而是：

```text
生成大矩阵 S = QK^T
→ 写回 HBM
→ 读出做 softmax
→ 再写回
→ 再读出乘 V
```

FlashAttention 分块计算，并维护每行 softmax 的：

- 当前最大值；
- 指数和；
- 累积输出。

因此不需要在 HBM 中物化完整 Attention 矩阵。

#### 必考边界

- 它是 exact attention，不是稀疏近似；
- 理论 Attention 计算量仍大体是 `O(n²d)`；
- 主要改进 IO 复杂度和中间显存；
- 实际加速依赖 GPU、数据类型、序列长度、head dimension、kernel 支持；
- FlashAttention 和 PagedAttention 不同：前者优化单次 attention kernel，后者管理 serving 的 KV Cache。

---

### 3.12 MoE：为什么参数很多但每 token 计算有限

#### 30 秒标准答案

> MoE（Mixture of Experts，混合专家）把一部分稠密 FFN 替换成多个 expert。Router 为每个 token 选择 top-k expert，只激活少数专家，所以总参数量可以很大，而单 token 的活跃计算量相对有限。核心挑战是路由稳定、负载均衡、跨设备通信和专家容量。

#### 数据流

```text
token hidden state
→ router logits
→ 选择 top-k experts
→ token 分发到 expert
→ expert FFN 计算
→ 加权合并
```

如果有 `E` 个 expert、每 token 只激活 `k` 个：

- 总参数量随 `E` 增长；
- 活跃 FFN 计算更接近 `k` 个 expert；
- 但 Router 和 all-to-all 通信不可忽略。

#### 为什么需要负载均衡

如果大部分 token 都被路由到少数专家：

- 热门 expert 超容量、排队或丢 token；
- 冷门 expert 学不到东西；
- 多卡计算不均衡；
- 吞吐下降。

因此常见辅助机制包括：

- load balancing auxiliary loss；
- expert capacity；
- router z-loss；
- expert parallelism；
- 无辅助损失的偏置调整等新方案。

#### Dense 与 MoE 怎么选

| 维度 | Dense | MoE |
|---|---|---|
| 每 token 激活 | 全部参数 | 少数 expert |
| 实现复杂度 | 较低 | 高 |
| 通信 | 常规并行通信 | 额外 token dispatch/all-to-all |
| 小规模部署 | 更简单 | 容易被调度开销抵消 |
| 扩大总参数 | 计算同步增加 | 可保持相近活跃参数 |

不能说“MoE 推理一定便宜”：虽然活跃 FLOPs 较低，但所有专家权重仍要存储或分布，通信、batch 和硬件利用率决定真实成本。

---

### 3.13 Tokenizer、BPE 与 SentencePiece

#### 30 秒标准答案

> Tokenizer 把字符串映射为离散 token id。BPE 从较小符号开始，反复合并高频相邻片段；SentencePiece 是直接从原始文本训练和执行子词切分的工具体系，可实现 BPE 或 Unigram，不依赖语言专用空格分词。

#### 为什么不能按“词”直接建词表

- 词表无限增长；
- 新词、公司名、代码无法覆盖；
- 中文没有天然空格；
- 纯字符序列又太长。

子词是折中：

- 高频词合成少量 token；
- 低频词拆成可组合片段；
- 未登录词仍能表示；
- 词表大小与序列长度之间可调。

#### BPE 过程

```text
1. 从字符/字节等基础符号开始
2. 统计相邻 pair 频率
3. 合并最高频 pair 为新 token
4. 重复直到达到目标词表大小
```

#### SentencePiece 要点

- 把空格也作为普通符号处理；
- 可直接处理中文、日文等文本；
- 常见模型包括 BPE 与 Unigram LM；
- “SentencePiece”不是与 BPE 同一层级的单一算法名称。

#### 词表大小的权衡

词表更大：

- 序列通常更短；
- embedding/output projection 参数更多；
- 稀有 token 学习样本更少。

词表更小：

- 参数更省；
- 序列更长，Attention/KV 成本增加；
- 代码、数字、中文可能被切得过碎。

#### 金融场景

金融文本特别关注：

- 股票代码 `600519` 是否被稳定保留；
- 公司名、产品名、英文缩写；
- 百分比、日期、小数；
- 同一实体的别名。

你的项目真实映射：

> 生成模型使用其自身 tokenizer；知识库 BM25 则使用独立的轻量 lexical tokenizer，采用汉字单字 + bigram，并保留拉丁字母和数字片段。这样做是为了零依赖、确定性和股票代码可检索，不代表它等同于 LLM 的 BPE tokenizer。

---

### 3.14 Transformer 高频追问与纠错

1. **Attention 的 `O(n²)` 指什么？**
   主要指 token 两两匹配形成的注意力分数规模；完整层还包括 `O(nd²)` 投影。

2. **FlashAttention 是否把复杂度降成线性？**
   没有。它主要减少 HBM IO 和中间显存，标准全注意力的理论 FLOPs 仍近似二次。

3. **RoPE 是否保证无限长度？**
   不保证。公式可计算不等于模型在未训练长度上会推理。

4. **RMSNorm 是否一定优于 LayerNorm？**
   不一定；它更简洁高效，但效果依模型配方。

5. **GQA 是否只是把 KV Cache 除以 group 数？**
   缓存确实按 KV head 数缩小，但质量、kernel 和投影参数也要一起考虑。

6. **MoE 的“参数量”应怎么报？**
   同时报总参数和每 token 活跃参数，否则容易误导。

7. **你的项目用了哪些？**
   使用了基于 Transformer 的现成 embedding、reranker 和 LLM 接口；没有自己训练 Transformer、改 RoPE、训练 MoE 或实现 FlashAttention kernel。

---

## 4. P1 详解二：训练、对齐与 PEFT

### 4.1 语言模型预训练目标

#### 30 秒标准答案

> Decoder-only 语言模型通常用最大似然训练：给定前面的 token，最大化真实下一个 token 的条件概率。工程上等价于最小化每个位置的交叉熵。模型不是逐句背诵规则，而是在海量样本上学习一个条件概率分布。

给定序列 `x_1 ... x_T`：

```text
P(x_1...x_T) = ∏ P(x_t | x_<t)
```

负对数似然损失：

```text
L_NLL = -Σ log Pθ(x_t | x_<t)
```

通常对有效 token 取平均。训练使用 teacher forcing：计算位置 `t` 时输入真实历史 token，而不是模型自己先前生成的 token。

#### 第一性原理

文本联合概率难以直接建模。链式法则把它拆成一系列“预测下一步”：

```text
看到“中国人民银行”
→ 下一个 token 可能是“发布”“决定”“表示”……
```

长期训练后，模型为了降低下一个 token 的预测误差，会学习：

- 词法和语法；
- 世界知识的统计关联；
- 文档结构；
- 代码和推理模式；
- 不同任务的隐式表示。

但 next-token objective 不自动保证：

- 事实永远正确；
- 遵循用户意图；
- 安全；
- 给出引用；
- 承认不确定。

所以才需要 SFT、偏好对齐和系统约束。

#### Perplexity

困惑度：

```text
PPL = exp(平均 token NLL)
```

PPL 越低表示模型对测试文本的平均预测更好，但：

- 不同 tokenizer 的 PPL 不宜直接比较；
- PPL 低不等于指令遵循、事实性或业务效果好；
- 金融 Agent 最终还要评测检索、引用、PIT 和决策支持。

---

### 4.2 Pre-training 与 Continue Pre-training

#### Pre-training

从随机初始化或接近随机初始化开始，在大规模通用语料上学习基础能力。关键工作包括：

- 数据收集、去重、清洗和配比；
- tokenizer；
- 模型架构与 scaling；
- 分布式训练；
- 数值稳定性；
- checkpoint 和评测。

#### Continue Pre-training

Continue Pre-training（CPT，继续预训练，也常叫 domain-adaptive pretraining）从已有 base model 出发，继续使用语言建模目标训练：

- 注入领域语料；
- 适配新语言或代码分布；
- 扩展上下文长度；
- 更新较大规模知识分布。

#### 与 SFT 的区别

| 维度 | CPT | SFT |
|---|---|---|
| 主要数据 | 大量原始领域文本 | instruction-response |
| 训练目标 | 通常预测所有文本 token | 通常重点计算 assistant answer loss |
| 主要目的 | 调整领域分布和基础表示 | 学会按指令完成任务 |
| 数据规模 | 往往较大 | 可较小但需高质量 |
| 风险 | 灾难性遗忘、语料污染 | 过拟合格式、能力偏移 |

一句话：

> 预训练更像“广泛阅读并形成语言和知识表示”，SFT 更像“看标准示范，学会如何回答”。

#### 金融项目选择

你的系统目前不需要 CPT：

- 金融事实变化快，写进权重后难更新、难引用；
- 已有知识库和市场数据库更适合外置事实；
- 你的核心瓶颈是证据治理和评测，不是 base model 完全看不懂金融语言。

如果未来确实发现模型连专业语料的语言分布都无法理解，且有大规模、合法、高质量金融原文，才考虑 CPT；不能用几十份研报就宣称完成领域继续预训练。

---

### 4.3 SFT：目标、数据格式与 masking

#### 30 秒标准答案

> SFT（Supervised Fine-Tuning，有监督微调）用高质量输入—理想输出示范继续训练模型。损失仍通常是 token-level cross-entropy，但会用 chat template 串联 system、user、assistant，并常把非 assistant token mask 掉，只让模型为目标回答承担损失。

示例：

```text
<system>你是金融研究助手</system>
<user>分析某公司利润增长的驱动</user>
<assistant>先区分收入、毛利率、费用率和一次性项目……</assistant>
```

常见 loss mask：

```text
system tokens:    ignore
user tokens:      ignore
assistant tokens: calculate loss
padding tokens:   ignore
```

有些配方也训练完整对话 token。面试时要说“取决于训练实现”，不要把 assistant-only 当唯一方案。

#### SFT 真正学到什么

- 指令遵循；
- 回答格式；
- 工具调用 schema；
- 领域表达；
- 拒答和安全示范；
- 某些任务模式。

它也可能吸收知识，但把 SFT 简化成“只学格式、绝不学知识”是错误的。更准确：

> SFT 可以改变知识行为和任务能力，但少量指令数据不是可靠、可更新、可引用的事实数据库。

#### 数据质量比数量更重要的原因

同一个问题若有冲突答案，模型收到相反梯度；模板化垃圾数据会让输出同质化。SFT 数据应检查：

- 正确性；
- 多样性；
- 难度覆盖；
- 去重；
- 长度和任务分布；
- 安全边界；
- train/validation 泄漏；
- chat template 一致性。

#### 项目映射

若未来给金融 Agent 做 SFT，合理目标是：

- 稳定输出“结论—证据—风险—翻转条件”格式；
- 稳定生成合法 tool call；
- 学会在证据不足时显式暴露缺口；
- 学会区分事实、解释、预测、动作。

不合理目标是：

- 把每日行情和最新公告长期写进 adapter；
- 用 SFT 代替 RAG freshness；
- 用少量自生成问答证明模型获得可靠金融知识。

---

### 4.4 经典 RLHF：SFT、Reward Model、PPO

#### 30 秒标准答案

> 经典 RLHF（Reinforcement Learning from Human Feedback，人类反馈强化学习）一般先得到 SFT 模型，再让模型对同一 prompt 生成多个回答，由人类排序训练 Reward Model，最后用 PPO 优化策略模型，使奖励上升，同时用 KL 惩罚限制它不要偏离参考模型太远。

#### 完整流水线

```text
1. Pretrained base model
2. SFT on demonstrations
3. 对同一 prompt 采样多个 responses
4. 人类给 preference/ranking
5. 训练 Reward Model
6. PPO 更新 policy
7. KL 约束 policy 与 reference model 的距离
8. 安全、能力和回归评测
```

#### Reward Model

输入 `(prompt, response)`，输出标量奖励：

```text
rθ(x,y)
```

偏好对 `(y_w, y_l)` 常用 Bradley-Terry 风格损失：

```text
L_RM = -log σ(r(x,y_w) - r(x,y_l))
```

#### PPO 中有哪些模型

典型工程可能包含：

1. policy / actor：正在优化的生成模型；
2. reference model：冻结，计算 KL；
3. reward model：给完整回答奖励；
4. value / critic：估计 value，降低策略梯度方差。

实现可能共享部分权重，但概念上要分清。

#### PPO 为什么复杂

- on-policy 采样成本高；
- 同时维护多个大模型；
- advantage、value、clip、KL 等超参敏感；
- reward hacking；
- 训练不稳定；
- 分布式 rollout 与训练调度复杂。

#### PPO 核心直觉

如果一次更新把 policy 推太远，旧数据将迅速失效。PPO 用概率比值裁剪限制更新：

```text
ratio = πθ(a|s) / πold(a|s)
L_clip = min(ratio × A, clip(ratio, 1-ε, 1+ε) × A)
```

在 LLM 中还常加：

```text
reward_total = reward_model_score - β × KL(policy || reference)
```

#### 常见错误

- RLHF 不等于“人直接给每个 token 奖励”；
- PPO 的 policy 不是“Actor + Critic 两个模型组成一个策略”；Actor 是 policy，Critic 是 value estimator；
- Reward Model 分数高不等于真实质量高，模型可能学会钻 RM 漏洞；
- KL 不是越小越好，过小可能没学到偏好，过大可能能力漂移。

---

### 4.5 DPO：为什么可以跳过显式 Reward Model 和 PPO

#### 30 秒标准答案

> DPO（Direct Preference Optimization，直接偏好优化）从 KL 约束的奖励最大化目标推导出一个偏好分类损失，直接提高 chosen 相对 rejected 的概率优势，并用 reference model 作为基准。它省掉显式 Reward Model 和 on-policy PPO，工程简单稳定，但依赖离线偏好数据，探索能力和在线奖励优化能力弱于通用 RL。

定义：

```text
Δ_policy =
log πθ(y_w|x) - log πθ(y_l|x)

Δ_ref =
log πref(y_w|x) - log πref(y_l|x)
```

DPO 损失：

```text
L_DPO =
-log σ(β(Δ_policy - Δ_ref))
```

直觉：

- 如果 policy 比 reference 更偏好 chosen，目标变好；
- 如果只无脑提高两个回答概率而不改变相对偏好，不足以优化目标；
- `β` 控制偏离 reference 的尺度。

#### DPO 与 PPO 对比

| 维度 | DPO | PPO-based RLHF |
|---|---|---|
| 数据 | 离线 chosen/rejected | 在线 rollout + reward |
| 显式 RM | 不需要 | 通常需要 |
| Critic | 不需要 | 通常需要 |
| 工程复杂度 | 较低 | 高 |
| 探索新策略 | 弱 | 更强 |
| 奖励类型 | 偏好对最自然 | 可接任意可计算 reward |
| 稳定性 | 通常更容易 | 超参和系统更复杂 |

不能说 DPO“全面取代 PPO”。如果任务有可验证环境奖励、需要在线探索、多步决策或持续更新，RL 方法仍可能更合适。

---

### 4.6 IPO、KTO、ORPO、SimPO、GRPO、RLVR 的位置

这些方法不要背成孤立缩写，应先按问题分类：

```text
离线 preference optimization
  DPO / IPO / KTO / ORPO / SimPO

在线或采样式 reinforcement learning
  PPO / GRPO / 其他 policy-gradient 方法

奖励来源
  人类偏好、AI 反馈、Reward Model、可验证规则
```

#### IPO

IPO（Identity Preference Optimization）可理解为对 DPO 类目标的改造，强调避免偏好数据可分时 logits 无限制增大，使用更明确的 margin/回归式约束以改善泛化。

面试重点：

- 它属于离线偏好优化；
- 目标是改善 DPO 可能的过拟合或偏好 margin 无限扩张问题；
- 不要在没看具体论文实现时声称“永远优于 DPO”。

#### KTO

KTO（Kahneman-Tversky Optimization）可以使用“这个回答好/坏”的二元反馈，不要求每条数据都有严格 chosen-rejected 配对。

适用场景：

- 点赞/点踩日志；
- 正负样本不天然成对；
- 配对标注成本高。

#### ORPO

ORPO（Odds Ratio Preference Optimization）把 SFT 的生成损失与偏好 odds-ratio 目标组合，可在一个阶段同时做 instruction learning 与 preference alignment，并通常不需要独立 reference model。

应回答的权衡：

- pipeline 更简化；
- 但 SFT 与偏好权重需要调节；
- 参考模型缺失不代表完全没有正则化问题。

#### SimPO

SimPO（Simple Preference Optimization）常用长度归一化的平均 log probability 作为隐式 reward，并加入 target margin；不依赖 reference model。

为什么关注长度归一：

- 序列总 log probability 随长度累加；
- 不处理长度可能产生偏差；
- 平均 log probability 更接近逐 token 质量，但也不是万能。

#### GRPO

GRPO（Group Relative Policy Optimization）对同一 prompt 采样一组回答，用组内奖励相对值构造 advantage，避免单独训练与 policy 同规模的 critic。

直觉：

```text
同题生成 G 个答案
→ 计算各自 reward
→ 用组均值/方差标准化
→ 高于组平均的回答得到正 advantage
→ 低于组平均的得到负 advantage
```

优势：

- 省 critic 显存和训练；
- 适合一题多采样；
- 可与可验证奖励结合。

局限：

- 多次采样本身昂贵；
- 组内 reward 方差不足时学习信号弱；
- reward 设计错误仍会被 hacking；
- GRPO 不等于“不要 reference/KL/clip”，具体实现仍可能使用这些稳定机制。

#### RLVR

RLVR（Reinforcement Learning with Verifiable Rewards，可验证奖励强化学习）更像一类训练范式，不是唯一固定算法：

- 数学题用最终答案检查；
- 代码题运行测试；
- 结构化输出做 schema validation；
- 工具任务检查执行结果。

可验证 reward 相比人类偏好更客观、可扩展，但只覆盖“容易自动验证”的维度。形式正确不等于推理可靠，测试也可能不完备。

#### 与金融 Agent 的关系

你的项目目前**没有执行这些模型训练**。可迁移思想是：

- output review 类似规则反馈，但没有更新模型参数；
- claim fidelity、引用覆盖率、PIT 检查可形成部分可验证 reward；
- 将来可以用这些信号做数据筛选或训练实验；
- 金融预测最终回报噪声大、延迟长、非平稳，不能简单当高质量 RL reward。

---

### 4.7 LoRA：低秩更新到底省了什么

#### 30 秒标准答案

> LoRA（Low-Rank Adaptation，低秩适配）冻结原权重 `W`，把任务更新写成低秩矩阵乘积 `BA`，只训练 A、B。它显著减少可训练参数、梯度和优化器状态，但前向与反向仍要通过基座模型，所以计算量和 activation 显存不会按参数比例同等下降。

设：

```text
W ∈ R^(d_out × d_in)
A ∈ R^(r × d_in)
B ∈ R^(d_out × r)
```

则：

```text
y = Wx + (α/r)BAx
```

可训练参数：

```text
r(d_in + d_out)
```

远小于：

```text
d_in × d_out
```

当 `r << d_in,d_out` 时节省明显。

#### 初始化

常见做法让一个矩阵随机初始化，另一个为零，使初始：

```text
BA = 0
```

模型开始时行为与 base model 一致，同时非零一侧使梯度能打破对称并开始学习。

#### target modules

常见目标：

- `q_proj`, `k_proj`, `v_proj`, `o_proj`；
- 也可包括 `gate_proj`, `up_proj`, `down_proj`。

不能说固定只调 Q/K 最优。目标矩阵、rank 和数据分布需要实验。

#### LoRA 真正节省

- trainable weights；
- gradients；
- optimizer states；
- 多任务 adapter 存储；
- 分布式同步的可训练梯度量。

不完全节省：

- 基座权重仍要加载；
- 主网络前向仍执行；
- 反向要计算传向 adapter 的梯度；
- activation 仍可能是大头。

#### 合并

推理前可计算：

```text
W_merged = W + (α/r)BA
```

从而避免额外 adapter matmul。多 adapter 动态服务时可能保持未合并，以换取灵活性。

---

### 4.8 QLoRA 与其他 PEFT

#### QLoRA

QLoRA 的核心：

- 冻结的 base weights 以 4-bit 存储；
- 计算时按需要反量化到较高精度；
- 训练 LoRA adapter；
- 常见关键技术包括 NF4、double quantization、paged optimizer。

它减少的是基座权重存储和相关内存压力，不代表所有计算都直接用 4-bit 完成。

#### 为什么 QLoRA 可能不更快

- 反量化有开销；
- 低比特 kernel 和硬件支持决定吞吐；
- 小 batch 或不匹配的 kernel 可能更慢；
- 主要卖点首先是“能装下并训练”，不是无条件更高 tokens/s。

#### PEFT 家族

| 方法 | 训练什么 | 优点 | 代价 |
|---|---|---|---|
| LoRA | 权重旁路低秩矩阵 | 效果/生态/可合并较好 | 仍需主模型前反向 |
| Adapter | 层间小网络 | 模块化 | 常增加推理层和延迟 |
| Prompt Tuning | 输入端可学习软 token | 参数极少 | 小模型/复杂任务效果可能弱 |
| Prefix Tuning | 每层 attention 的可学习 prefix K/V | 更深层影响注意力 | 占用有效 prefix/KV，实现更复杂 |
| P-Tuning | 学习连续 prompt 表示 | 适合特定任务 | 版本定义多，面试需说明具体方案 |

#### 全量微调还是 PEFT

考虑：

- 数据量和任务分布变化有多大；
- 计算预算；
- 是否要保留通用能力；
- 是否要服务多个任务；
- 是否可接受 adapter 管理；
- 质量提升是否经评测证明。

不能用“10k 数据以上一定全量微调”这类固定阈值。模型规模、数据质量、任务距离和预算更关键。

---

### 4.9 数据工程：去重、过滤、配比与主动学习

#### 为什么数据是训练的第一性瓶颈

梯度只反映训练样本。如果样本错误、重复、泄漏或冲突，优化器会高效地学错。

#### 去重

层级：

- exact dedup：完全相同文档；
- near dedup：MinHash/SimHash 等近重复；
- semantic dedup：embedding 相近；
- benchmark contamination：训练语料含测试答案。

重复过多会：

- 浪费 token 预算；
- 放大特定来源偏见；
- 增加记忆化；
- 使 validation 虚高。

#### 质量过滤

- 规则：长度、乱码、广告、重复率、语言；
- classifier：质量、安全、领域；
- perplexity：异常文本筛选；
- source weighting：可信来源更高权重；
- 人工抽检。

注意：用模型过滤数据会把过滤模型的偏见带入训练集。

#### 数据配比

训练分布不是简单“全部混合”。要控制：

- 通用 vs 领域；
- 中文 vs 英文；
- 代码 vs 自然语言；
- 简单 vs 困难；
- 安全 vs 能力；
- 新数据 vs replay 旧数据。

#### 主动学习

优先标注模型最不确定、最易错或业务价值最高的样本：

```text
模型运行
→ 找失败簇/低置信/分歧样本
→ 人工标注
→ 加入下一轮训练
→ 再评测
```

你的项目已有潜在数据源：

- output review 的失败类型；
- answer feedback；
- experience cards；
- claim fidelity 缺口；
- 历史回放的 hit/miss。

但这些目前是系统评测/记忆信号，不等于已经形成训练闭环。

---

### 4.10 灾难性遗忘

#### 30 秒标准答案

> 灾难性遗忘是模型在新分布上继续训练后，新任务变好但原有能力下降。原因是同一参数被新梯度覆盖。缓解方法包括混入通用 replay 数据、降低学习率、减少训练步数、PEFT、正则化以及持续做旧能力回归评测。

#### 判断方式

不能只看领域 validation：

```text
领域集提升
通用集下降
安全集下降
格式集提升
```

这就是多目标权衡，不应只报告最好的一项。

#### 缓解

- domain data 与 general replay 混合；
- 更小 learning rate；
- warmup 和合理 schedule；
- early stopping；
- LoRA/adapter 限制更新空间；
- checkpoint soup/merge 需谨慎；
- 多套能力评测矩阵。

PEFT 可能缓解遗忘，但不保证不忘：adapter 仍可能改变输出行为，且合并后也可能损害通用能力。

---

### 4.11 AdamW、学习率、Warmup 与 Cosine Decay

#### AdamW

Adam 使用梯度一阶矩和二阶矩做自适应更新。AdamW 把 weight decay 与梯度更新解耦：

```text
m_t = β1 m_(t-1) + (1-β1)g_t
v_t = β2 v_(t-1) + (1-β2)g_t²
θ ← θ - lr × m_hat/(sqrt(v_hat)+ε) - lr × wd × θ
```

面试重点：

- AdamW 不是“Adam 加 L2 完全等价”；
- 解耦 weight decay 更符合直接缩小权重的意图；
- Norm 和 bias 参数是否 decay 取决于配方。

#### Warmup

训练初期参数和 optimizer moments 尚未稳定，直接使用峰值学习率容易发散。Warmup 让 lr 从小到大。

#### Cosine Decay

Warmup 后按余弦逐渐降低学习率：

```text
lr(t) = lr_min + 0.5(lr_max-lr_min)(1+cos(π progress))
```

直觉：

- 前期大步学习整体结构；
- 后期小步收敛；
- 不是所有任务都必须 cosine，也可 constant、linear decay、WSD 等。

#### 学习率选择

不能死背“7B 一定 3e-4”：

- pretraining、CPT、SFT、LoRA 的 lr 尺度不同；
- global batch、数据质量、模型规模、初始化和 optimizer 都影响；
- 应通过 loss、gradient norm、validation 和小规模 sweep 决定。

---

### 4.12 Batch、Gradient Accumulation 与 Clipping

#### Global Batch

```text
global_batch
= micro_batch_per_gpu
× gradient_accumulation_steps
× data_parallel_world_size
```

若按 token 计，应进一步乘有效 sequence tokens。

#### Gradient Accumulation

多次 micro-batch 前反向后再 optimizer step：

- 降低单步 activation 显存；
- 模拟更大 global batch；
- 不能减少完成同样 token 数的总计算；
- accumulation 越多，参数更新频率越低。

#### Gradient Clipping

常见 global norm clipping：

```text
if ||g|| > c:
    g ← g × c / ||g||
```

用于抑制异常大梯度，但如果长期每步都被 clip，应排查：

- learning rate；
- 数据异常；
- loss scaling；
- 数值精度；
- 模型实现错误。

Clipping 是安全带，不是修复所有发散的万能药。

---

### 4.13 FP32、FP16、BF16、FP8 与 Loss Scaling

| 格式 | 位数 | 关键特点 | 常见用途 |
|---|---:|---|---|
| FP32 | 32 | 范围和精度高 | master weights、敏感计算 |
| FP16 | 16 | 尾数较多但指数范围小 | 混合精度，常需 loss scaling |
| BF16 | 16 | 与 FP32 相同指数位宽，尾数较少 | 现代训练常用，范围更稳 |
| FP8 | 8 | 更低精度，需逐 tensor scaling/recipe | 新硬件训练和推理加速 |

#### FP16 为什么需要 Loss Scaling

小梯度可能低于 FP16 可表示范围而下溢为 0。把 loss 乘以 `S`：

```text
scaled_loss = S × loss
scaled_grad = S × grad
```

反向后再除以 `S`。动态 loss scaling 在溢出时降低 `S`，稳定时提高。

#### BF16

BF16 指数范围接近 FP32，因此通常更少需要 loss scaling；但尾数更短，局部精度更低。现代训练中“范围”往往比额外尾数更重要。

#### FP8

FP8 动态范围和精度更有限，通常不能只靠一个全局 loss scale，需要：

- 每个 tensor 或分组 scale；
- amax 历史；
- E4M3/E5M2 等格式选择；
- 高精度累加和敏感算子保留。

不能说“FP8 就是把所有张量无脑改成 8 位”。

---

### 4.14 Gradient Checkpointing

#### 30 秒标准答案

> Gradient Checkpointing 用计算换显存。普通反向传播保存很多中间 activation；checkpointing 只保存部分边界，反向时重新执行前向来恢复中间结果，因此 activation 显存降低，但训练变慢。

数据流：

```text
普通：
forward 保存所有 activation
→ backward 直接使用

checkpoint：
forward 只存检查点
→ backward 重新计算区间 activation
→ 求梯度
```

它不减少：

- 模型参数；
- optimizer states；
- 理论训练任务本身。

它主要减少 activation memory，尤其适合深层和长序列。

---

### 4.15 训练异常排查

#### Loss spike

排查顺序：

1. 是否特定数据 batch 异常；
2. learning rate 是否过大或 schedule 跳变；
3. gradient norm 是否突增；
4. 混合精度 overflow；
5. 分布式通信或 checkpoint 恢复错误；
6. tokenizer/chat template/mask 错位。

单次 spike 后恢复不一定致命；持续恶化才说明训练失稳。

#### NaN / Inf

- 降低 lr；
- 检查 loss scaling；
- 检查除零、log(0)、softmax mask 全负无穷；
- 使用 BF16 或敏感算子 FP32；
- 检查异常样本；
- 记录首个出现 NaN 的 layer/gradient。

#### 训练 loss 降，验证 loss 升

典型过拟合或分布不匹配：

- early stop；
- 更多/更干净数据；
- dropout/weight decay；
- 降 rank 或训练步数；
- 检查 validation 是否代表真实业务；
- 检查 train/val template 是否一致。

#### Loss 正常但生成坏

- loss mask 是否训练错角色；
- EOS 是否正确；
- chat template 是否一致；
- decoding 参数；
- 训练数据是否模板化；
- 只看 token loss 没看任务评测；
- checkpoint 转换/adapter 加载错误。

---

### 4.16 训练章节的项目边界

面试建议这样说：

> 我的金融 Agent 当前没有训练基础模型，也没有做 RLHF、DPO 或 GRPO。项目的“对齐”主要发生在系统层：事实必须来自数据源，RAG 有新鲜度门禁，用户记忆只当 prior，回答需要证据、反证和缺口，输出再经过确定性 review。未来如果积累了足够反馈，可以先把失败样本做成 SFT 或偏好数据，但会先建立离线评测，避免为了训练而训练。

不能说：

- “我用了 RLHF”——规则审稿不是 RLHF；
- “经验卡就是 Reward Model”——它是文本化经验记忆；
- “用户点赞就是 DPO”——只有整理成偏好对并更新模型才是训练；
- “用了 API 模型就等于部署了推理框架”。

---

