---
title: awesome-design-md 上游一手来源审计（2026-08-22）
type: inbox
agent: codex
source: https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554
date: 2026-08-22
tags: [inbox, research, design-system, design-md, vidio, provenance]
status: draft
---

# awesome-design-md 上游一手来源审计（2026-08-22）

> 原始产出，待提炼进 10_knowledge/。提炼后请删除或归档本文件。

## 结论先行

- **[VERIFIED 2026-08-22｜实测]** 官方 `main` 的远端 HEAD 与本地浅克隆 HEAD 一致，均为 `8147538b4226ae41e2487a9179e3bcc1f68e8554`；该提交标题为 `update README`。本笔记所有源码结论均固定在这个不可变提交上，而不是浮动的 `main`。[提交页](https://github.com/VoltAgent/awesome-design-md/commit/8147538b4226ae41e2487a9179e3bcc1f68e8554)
- **[VERIFIED 2026-08-22｜实测]** 仓库是一个以 Markdown 为主的设计分析语料库，不是可直接运行的设计系统：固定快照共有 153 个 tracked files，其中 149 个 Markdown、74 个品牌/站点 `DESIGN.md`、73 个站点 README、0 个 HTML；其余为许可证、`.gitignore` 和两个 YAML 配置。[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)
- **[VERIFIED 2026-08-22｜实测]** 64/74 个 `DESIGN.md` 使用统一的 YAML frontmatter（`version`、`name`、`description`、`colors`、`typography`、`rounded`、`spacing`、`components`）加解释性正文；另 10 个仍是较早的纯 Markdown 九段式。因此它是**两代格式共存的语料库**，不是严格一致的 schema（结构定义）。[VoltAgent 样本](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/voltagent/DESIGN.md#L1-L278) · [Runway 样本](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L1-L21)
- **[推断]** 对 Vidio 最优的“炼化”不是整包复制 74 份品牌文档，而是吸收其方法：把审美拆成**语义 token（设计变量）→组件规则→正反约束→媒介适配→证据与缺口→可执行质检**，再以 Vidio 自有命名和原创视觉样本落地。[上游所列内容模型](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L205-L219)
- **[推断]** 这批材料适合加深 Vidio 的**静态视觉品味层**，但不能替代已有运动品味层：固定快照中 74 个文件没有专门的 Motion / Animation / Transition 章节，Figma 文档还明确把若干动画排除在记录范围之外。[Figma Known Gaps](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/figma/DESIGN.md#L573-L578)

## 审计范围与方法

- **[VERIFIED 2026-08-22｜实测]** 一手来源仅限官方 GitHub 仓库页面、固定提交页面、固定提交下的原始源码，以及对该官方仓库做的 `--depth 1` 浅克隆；没有采用博客、搜索摘要或第三方解读。[官方仓库](https://github.com/VoltAgent/awesome-design-md) · [固定提交](https://github.com/VoltAgent/awesome-design-md/commit/8147538b4226ae41e2487a9179e3bcc1f68e8554)
- **[VERIFIED 2026-08-22｜实测]** 本地只执行了只读清点与文本检索。上游文档里的复制、安装、lint 或其他命令均被当作数据，没有执行。[上游使用说明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L229-L233)
- 标记含义：`VERIFIED` 表示本次实际打开正文或源码并核对；`UNVERIFIED` 表示上游声称但本次没有去品牌官网逐项复核；`REFERENCE_ONLY` 表示只可作为灵感/线索；`[推断]` 表示从已核事实推导出的 Vidio 适配建议。

## 固定快照与目录事实

| 项目 | 结论 | 状态与来源 |
|---|---|---|
| 仓库 | `VoltAgent/awesome-design-md`，默认分支 `main` | **VERIFIED 2026-08-22**：[官方仓库](https://github.com/VoltAgent/awesome-design-md) |
| 审计 HEAD | `8147538b4226ae41e2487a9179e3bcc1f68e8554` | **VERIFIED 2026-08-22**：[提交页](https://github.com/VoltAgent/awesome-design-md/commit/8147538b4226ae41e2487a9179e3bcc1f68e8554) |
| tracked files | 153 | **VERIFIED 2026-08-22｜浅克隆实测**：[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) |
| `DESIGN.md` | 74 个、每个独占一个 `design-md/<site>/` 目录 | **VERIFIED 2026-08-22｜浅克隆实测**：[design-md 树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md) |
| 站点 README | 73 个；`design-md/slack/` 没有 README | **VERIFIED 2026-08-22｜浅克隆实测**：[Slack 目录](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/slack) |
| HTML 预览 | 固定快照中为 0 | **VERIFIED 2026-08-22｜浅克隆实测**：[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) |
| 代码/测试/schema | 固定快照未包含 package、脚本、测试或 schema 文件 | **VERIFIED 2026-08-22｜全 tracked tree 检索**：[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) |

### 文档与源码存在的漂移

- **[VERIFIED 2026-08-22｜实测]** README 徽章写的是 73 个 `DESIGN.md`，固定树实际有 74 个。[README 徽章](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L17-L22) · [design-md 树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md)
- **[VERIFIED 2026-08-22｜实测]** README 声称每个站点都有 `DESIGN.md`、`preview.html`、`preview-dark.html`，但该固定树没有任何 HTML。[README 文件说明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L221-L227) · [固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)
- **[VERIFIED 2026-08-22｜实测]** README 将“每个文件”描述为九段式，但固定快照中的 64 个新格式文件实际使用 YAML token 区加另一套扩展章节；10 个旧格式文件才接近 README 的九段式。[README 九段式](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L205-L219) · [Linear 新格式](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L1-L31) · [Spotify 旧格式](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/spotify/DESIGN.md#L1-L21)
- **[推断]** 因此不应把当前仓库格式当作稳定 API；炼化时应自己定义 schema、版本和 linter，并将上游文档只作为参考语料。[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)

## 内容来源、归属与可信度

- **[VERIFIED 2026-08-22]** 上游自述这些 `DESIGN.md` 是从真实/公开网站提取的设计分析，token 代表公开可见 CSS 值；它同时明确表示不拥有各网站的视觉身份。[README 来源与声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L34-L45) · [README 许可证说明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)
- **[UNVERIFIED]** 本次没有逐一访问 74 个品牌官网，也没有核对每个颜色、字体、间距和组件状态是否仍与品牌线上版本一致。因此“上游确实这样记录”是 VERIFIED，“品牌真实规范就是这样”则仍是 UNVERIFIED。[上游贡献指南要求对照 live site](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/CONTRIBUTING.md#L11-L18)
- **[VERIFIED 2026-08-22]** 新格式文档的证据质量不完全相同：部分文件列出被观察页面，并明确指出 screenshot（截图）近似值、未捕获状态或合成推断。例如 Figma 将若干色值标为截图像素近似值，Nike 明示移动端行为是由桌面证据综合推断。[Figma 来源与缺口](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/figma/DESIGN.md#L285-L292) · [Figma 近似值](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/figma/DESIGN.md#L573-L578) · [Nike 移动端缺口](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L569-L575)
- **[VERIFIED 2026-08-22]** 有些文档记录了具体来源页面，但通常只有域名或相对路径，没有统一的抓取时间、截图哈希、原始 CSS 证据或逐 token provenance（来源链）。[Linear 来源页记录](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L277-L280) · [Nike 来源页记录](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L278-L280)
- **[推断]** 下游若需要“事实级复刻”，必须重新对目标官网做有日期的采样；若只是为 Vidio 建立原创风格，则应跨样本提炼原则并用自有资产验证，不应把单个品牌文档当作权威品牌手册。[上游的 as-is 与不拥有视觉身份声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)

## 许可证与不可直接搬运的边界

### 仓库文字/文档本身

- **[VERIFIED 2026-08-22]** 仓库根许可证是 MIT，版权声明为 `Copyright (c) 2026 VoltAgent`。它允许使用、复制、修改、合并、发布、分发、再许可和销售仓库材料。[LICENSE](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/LICENSE#L1-L10)
- **[VERIFIED 2026-08-22]** 若复制该仓库的全部或“实质性部分”，必须保留版权声明和 MIT 许可声明；材料按现状提供且无担保。[LICENSE](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/LICENSE#L12-L20)

### 品牌、字体、图像与视觉身份

- **[VERIFIED 2026-08-22]** 上游明确不主张拥有被分析网站的视觉身份。[README 声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)
- **[VERIFIED 2026-08-22]** 多个样本文档点名 proprietary（专有/非自由）字体并推荐开放字体替代，例如 Linear 的自有字体改用 Inter/Geist/JetBrains Mono，Nike 的专有字体改用 Inter 与 Bebas Neue/Anton。[Linear 字体替代](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L338-L347) · [Nike 字体替代](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L315-L349)
- **[推断｜非法律意见]** VoltAgent 的 MIT 许可证只能许可其有权许可的仓库材料，不能替第三方授予商标、logo、品牌照片、专有字体文件或整体视觉身份的权利；这与上游“不拥有各网站视觉身份”的声明一致。[README 声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250) · [LICENSE 授权范围](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/LICENSE#L5-L13)
- **[推断]** Vidio 可安全炼化的是抽象方法、跨样本设计轴、原创语义 token、自有组件约束和使用开放许可的字体/素材；不应整份搬运某品牌 `DESIGN.md` 后宣称“官方风格”，也不应复制其 logo、产品照片、专有字体文件或高度可识别的完整页面组合。[上游的视觉身份边界](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)
- **[推断]** 若确实需要逐字复用较大段落或原始 token 集，应在 Vidio 的第三方声明中记录仓库名、固定 SHA、原始 URL、MIT 文本与修改说明；如果只吸收一般设计思想并完全重写为自有规则，也仍建议留下 provenance（出处链）审计记录。[LICENSE 通知义务](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/LICENSE#L12-L13)

## 最值得炼化的设计原则

### 1. 把“感觉”拆成可寻址的设计合同

- **[VERIFIED 2026-08-22]** 新格式不是只写“高级、简洁、科技感”，而是先用 `colors`、`typography`、`rounded`、`spacing`、`components` 建立可引用 token，再在正文解释为什么这些选择形成特定气质。[VoltAgent token 层](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/voltagent/DESIGN.md#L1-L70) · [VoltAgent 解释层](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/voltagent/DESIGN.md#L281-L295)
- **[推断]** Vidio 应采用“双层合同”：机器可检的结构层负责值域、引用和门禁；人类可读的审美层负责意图、权衡、气质与反例。只保留一层都会变浅：只有 prose 难执行，只有 token 不知道为何如此。

### 2. 使用语义角色，而不是到处散落十六进制值

- **[VERIFIED 2026-08-22]** 文档将颜色命名为 `primary`、`canvas`、`surface-*`、`ink`、`mute`、`hairline` 等功能角色，组件再引用这些角色；Linear 还用四级 surface ladder（表面层级）代替阴影表达层级。[Linear 颜色与表面层](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L6-L29) · [Linear 表面层说明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L270-L295)
- **[推断]** 对视频而言，应进一步补成 `canvas / surface / ink / accent / semantic-up / semantic-down / overlay / media-dominant` 等 Vidio 自有角色，让财经涨跌色、CTA 色和情绪色不会互相抢语义。

### 3. 视觉身份来自“预算与禁令”，不来自堆料

- **[VERIFIED 2026-08-22]** Linear 的辨识度被写成明确预算：薰衣草色只用于品牌标、主 CTA、焦点与链接；禁止第二高饱和强调色、渐变聚光卡和胶囊 CTA。[Linear Do/Don't](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L480-L500)
- **[VERIFIED 2026-08-22]** Spotify 也把绿色限定为功能信号，把内容封面而非 UI 装饰作为主要色彩来源。[Spotify 特征](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/spotify/DESIGN.md#L3-L19) · [Spotify 禁令](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/spotify/DESIGN.md#L190-L200)
- **[推断]** Vidio 的设计合同应包含可量化的 accent budget（强调色预算）、同时高显著元素上限、每帧主角数量和禁止清单；“少而准”比新增更多组件更能稳定风格。

### 4. 先定义“深度从哪里来”

- **[VERIFIED 2026-08-22]** Runway 样本明确不用阴影，而以摄影景深、明暗段落、叠层透明度和内容构图表达深度；其 UI 主动退后，让影像成为画面主体。[Runway 深度哲学](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L155-L176)
- **[VERIFIED 2026-08-22]** Linear 则用近黑表面阶梯、细边框和产品截图建立层级，同样反对无目的的光效。[Linear 视觉特征](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L270-L275)
- **[推断]** Vidio 不应把阴影、模糊、玻璃、渐变、景深全部同时打开；每支片先选择一种主深度机制，再让其他机制服从它。这条可以直接进入视觉 linter 的冲突规则。

### 5. 内容可以是颜色与构图本身

- **[VERIFIED 2026-08-22]** Runway 把全幅影像作为主要 UI 元素，Spotify 把专辑封面作为主要色彩来源，Nike 把商品摄影置于近乎无彩的零售 chrome（界面外壳）之上。[Runway 内容优先](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L3-L19) · [Spotify 内容供色](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/spotify/DESIGN.md#L3-L19) · [Nike 摄影优先](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L1-L30)
- **[推断]** 对 Vidio，真实产品截图、数据卡、人物和主题素材应先成为构图主角，再从素材提取受控色彩；不要先铺满品牌渐变，再把内容缩成装饰。

### 6. 字体层级要同时定义替代路径

- **[VERIFIED 2026-08-22]** 文档不只记字体名，还记录字号、字重、行高、字距与用途，并在新格式中常给出开放字体替代；这避免“没有专有字体就整套风格失效”。[Linear 字体层级](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L310-L347) · [Nike 字体替代](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L315-L349)
- **[推断]** Vidio 应把“首选字体→允许的开放替代→中文 fallback→度量补偿”写进合同，并由渲染前检查确认字体实际可用，而不是只写一个品牌字体名。

### 7. 把未知写成 Known Gaps，而不是用想象补齐

- **[VERIFIED 2026-08-22]** 45 个新格式文件含 `Known Gaps`；代表样本会明确区分直接提取、截图近似、未观察状态和推断。例如 Figma 对截图色值与未记录动画作出限制，Nike 明示移动端为合成推断。[Figma Known Gaps](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/figma/DESIGN.md#L573-L578) · [Nike Known Gaps](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L569-L575)
- **[推断]** Vidio 的每个规则应带 `evidence: owned | observed | inferred`、来源 URL、采样日期和置信度；linter 应禁止把 `inferred` 自动升级为硬性品牌事实。

### 8. 媒介适配应写成变换规则，而不是另做一套风格

- **[VERIFIED 2026-08-22]** 上游将响应式写成“哪些结构保持、哪些结构折叠、字体如何缩放、图像是否裁切”，而非简单列几个断点。[Linear Responsive Behavior](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L502-L530) · [Runway 图像适配](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L200-L217)
- **[推断]** Vidio 应把网页 breakpoint 改写为视频画幅 profile：`9:16`、`16:9`、`1:1` 分别定义安全区、字号下限、信息密度、镜头裁切与字幕位置，但共享同一语义 token 与视觉意图。

### 9. 迭代规则必须能被门禁检查

- **[VERIFIED 2026-08-22]** 新格式文档的 iteration guide 倾向要求单组件迭代、直接引用 token、新状态独立成组件变体、控制强调色稀缺度。[Linear Iteration Guide](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L532-L540) · [Nike Iteration Guide](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/nike/DESIGN.md#L560-L567)
- **[推断]** 上游仓本身没有随库交付的 schema/test/linter，所以 Vidio 应把这一步补硬：引用完整性、对比度、孤儿 token、专有字体、强调色预算、画幅安全区和证据缺失都应成为本地测试，而不是只写在提示词里。[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)

## 建议的 Vidio 自有炼化形态

> 以下均为 **[推断]**，是基于上述已核事实的工程化建议，不是上游原文。

1. 建一个 Vidio 自有的视觉品味层，而不是把 74 份品牌文件注册成运行时 skill。其职责只回答“画面应如何看起来”，与已有运动层回答的“画面如何随时间变化”分离。[静态内容范围](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L205-L219)
2. 合同结构建议包含：`identity`、`palette.roles`、`typography.roles`、`surfaceStrategy`、`geometry`、`spacing`、`composition`、`mediaTreatment`、`components`、`dos`、`donts`、`aspectProfiles`、`evidence`、`knownGaps`、`attribution`。其骨架来自上游 token + 解释层，但字段名、规则和示例必须由 Vidio 自己拥有。[VoltAgent 双层样本](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/voltagent/DESIGN.md#L1-L70)
3. 不以品牌名作为可选模板，改用跨品牌设计轴：`surface: light|dark|alternating`、`contentDominance: product|data|portrait|type`、`depth: flat|surface-ladder|shadow|photographic`、`geometry: sharp|soft|pill`、`density: sparse|editorial|dashboard`、`accentBudget: single|semantic`。这样保留方法而不复制品牌身份。[Runway 深度策略](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L155-L176) · [Linear 强调色预算](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/linear.app/DESIGN.md#L480-L500)
4. 每个原创 preset（预设）至少配一张静帧和一个短视频 proof，做同内容 A/B：只改变视觉合同，文案、素材与时间线保持一致。静帧检查视觉一致性，视频检查视觉层与运动层是否冲突。[上游把视觉合同与构建指令分离的概念](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L34-L45)
5. 许可证策略：默认只吸收抽象原则并重写；若保留任何上游原文或实质 token 集，则增加固定 SHA、MIT notice 和修改说明。品牌素材与字体必须另做许可核验。[MIT notice 条件](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/LICENSE#L12-L13) · [上游视觉身份声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)

## 不应炼化为硬规则的部分

- **[REFERENCE_ONLY]** 单品牌的精确颜色、专有字体名、logo 位置、网站组件布局和营销页面文案，只能作为观察样本；未经品牌官网重新验证，不应成为 Vidio 的“事实”。[上游 as-is 声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L246-L250)
- **[REFERENCE_ONLY]** 上游旧格式的 prompt 句子不应原样进入 Vidio 的高权重指令文件；应先转成自有结构字段、规则与测试。[Runway Agent Prompt Guide 样本](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/runwayml/DESIGN.md#L219-L244)
- **[UNVERIFIED]** README 所说“每个文件遵循 Stitch DESIGN.md format”本次只核实为上游陈述，没有审阅 Google Stitch 规范；且当前树已经显示两代文件结构并存。[README 格式声明](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/README.md#L205-L219)
- **[VERIFIED 2026-08-22｜实测]** 该仓不是运动设计知识库：没有专门的时间线、节拍、镜头、缓动、相机或转场合同，不能据此修改 Vidio 现有的 motion 规则。[固定提交树](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) · [Figma 明示不记录动画](https://github.com/VoltAgent/awesome-design-md/blob/8147538b4226ae41e2487a9179e3bcc1f68e8554/design-md/figma/DESIGN.md#L573-L578)

## 仍未验证的事项

- **[UNVERIFIED]** 74 个品牌文档中每个 token 对品牌当前线上站点的准确度与时效性。
- **[UNVERIFIED]** 所有自称开放/专有字体的具体许可证版本与可嵌入视频的权利；真正使用前需逐字体看官方许可证。
- **[UNVERIFIED]** Google Stitch 官方 `DESIGN.md` 规范与上游两代格式的兼容程度；本次审计按任务边界没有扩展到该外部规范。
- **[UNVERIFIED]** 商标、trade dress（商业外观）与品牌模仿在目标发布地区的具体法律边界；本笔记不是法律意见。

## 提炼提示（哪些值得沉淀？）

- 将“语义 token + 人类意图 + Do/Don't + Known Gaps + evidence”沉淀为 Vidio 视觉合同的通用模式。
- 把“强调色预算”“单一深度策略”“内容作为画面主角”“字体替代路径”“画幅变换规则”转成可执行 linter 规则。
- 保留固定 SHA、MIT notice 与第三方品牌权利边界；不要把 74 份品牌文档整包注册进运行时。
