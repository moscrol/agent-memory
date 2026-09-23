---
title: 重试预算必须同时限制时间与次数
type: knowledge
status: verified
date: 2026-09-23
source: finance-workspace-private 工单85，离线红绿与变异对照
tags: [engineering, reliability, retry, contracts]
---

# 重试预算必须同时限制时间与次数

## 失败形状

只累计 sleep 会漏掉请求本身耗时；接受 Retry-After=0 而没有次数上限，可产生无界快速重试。即使底层正确返回 partial，CLI退出0或包装器无条件ok=true仍会把缺口报成成功。

## 可迁移约束

- 用 monotonic 截止判断是否还能开始下一次重试，计入请求与等待；同时设置明确次数上限，拒绝非有限/负预算。
- 每次网络等待至多使用剩余额度；须区分 socket timeout 与强制中断在途读取的硬截止，不能过度承诺。
- 新错误码的新预算不可悄悄改变已有错误码的次数语义。混合限流路径要分别检查。
- 继续其他请求与允许发布部分结果是独立决策。部分完成状态必须传到 CLI 退出码、父编排和发布保护，不能只留在 stdout。
- 阳性对照不只看“有重试”：将次数上限设0，恢复成功的测试必须转红；再恢复运行确认绿。跨入口用测试直接断言部分结果不会被包装成成功。

## 来源与边界

同花顺候选最终代码 `0f0231553`：边界7针先红；CLI/夜跑/旧单体3针先红再绿；冻结干净定向130P。关闭429重试2F、恢复2P。原件与取舍：`fwp-wt-hithink-research-0923/docs/handoffs/2026-09-23-hithink-research-observations-85.md`。这是离线合同验证，不证明真实供应商限流窗口已经恢复。
