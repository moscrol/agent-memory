---
name: session-tutor
description: "tutor 的别名入口。用户输入“session tutor”、@session-tutor，或要求讲解并整理会话中的科普内容时触发；流程规则以 tutor skill 正文为唯一事实源。"
---

# Session Tutor Alias

读取并严格执行 `tutor` skill（`.agents/skills/tutor/SKILL.md`）的完整流程。

本文件只做入口转发，**不复述规则**——此前这里维护着一份 9 条的压缩转写，规则一改就要同步两处，镜像必漂（2026-08-12 去重）。教学模式、理解验收、提案格式、落库步骤，一律以 tutor 正文为准。

仅保留两条不依赖 tutor 正文也必须成立的兜底：

- 未收到用户对具体候选的明确批准（如“批准 T1 落库”）前，不得创建、修改、提交或推送任何 `70_tutor/` 文件；“理解了”不等于批准。
- 如果当前环境无法加载 `tutor` skill，停止写入并告知用户；不得用简化流程绕过人审闸门。
