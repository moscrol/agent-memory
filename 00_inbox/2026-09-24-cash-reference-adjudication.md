---
title: "09-23 甘源食品与嘉益股份除息参考价具名裁决"
type: inbox
agent: codex
source: "https://static.cninfo.com.cn/finalpage/2026-09-16/1225565802.PDF; https://static.cninfo.com.cn/finalpage/2026-09-16/1225568790.PDF"
date: 2026-09-24
tags: [inbox, finance, market-recovery, evidence]
status: draft
---

# 09-23 甘源食品与嘉益股份除息参考价具名裁决

> 原始调研产出，服务于发布工单 #900。只读查证，未写数据库或知识图谱，不能代替恢复及发布准入。

## 已读一手来源

两份公司实施公告 PDF 均于 2026-09-24 实际下载、抽取并阅读全文，状态 VERIFIED；不是依据搜索摘要。原件及哈希在 `/Users/a77/.finance-runtime/reviews/workbench-release-20260924-independent/reference-sources-v1/receipt.json`。

- **甘源食品 002991.SZ**：总股本 93,215,831 股，回购专户 1,605,872 股不参与分红；参与分配股数 91,609,959，名义每股派息 0.63 元，现金合计 57,714,274.17 元。公告规定按总股本折算，每 10 股 6.191467 元，保留六位小数直接截取，对应每股参考扣减 **0.6191467 元**；登记日 09-22、除息日 09-23。来源：[公司实施公告，第 1、2、3 页](https://static.cninfo.com.cn/finalpage/2026-09-16/1225565802.PDF)。PDF SHA256 `4fc6ce4c1623a3ad983aeece911552cf1575139c6f5ecde019a8f51e5f4727c4`。
- **嘉益股份 301004.SZ**：总股本 145,806,262 股，回购专户 3,058,092 股不参与分红；参与分配股数 142,748,170，名义每股派息 0.80 元，现金合计 114,198,536.00 元。公告规定按总股本折算，每 10 股 7.832210 元，保留六位小数直接截取，对应每股参考扣减 **0.7832210 元**；登记日 09-22、除息日 09-23。来源：[公司实施公告，第 1、2、3、4 页](https://static.cninfo.com.cn/finalpage/2026-09-16/1225568790.PDF)。PDF SHA256 `2a7f134a258dc11723612ac07c61f8d2d2fc80f8d6329af5729ccd69c5244f94`。

## 第三源与复算

新浪不复权历史响应于同日读取、解码并冻结，状态 VERIFIED，供应商来源不冒充交易所官方数据。原始响应和解码参数与 PDF 同目录。

| 股票 | 09-22 收盘 | 公告扣减 | 未取整参考价 | 分位参考价 | 09-23 收盘 | 涨跌幅 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 甘源食品 | 38.27 | 0.6191467 | 37.6508533 | 37.65 | 37.50 | -0.40% |
| 嘉益股份 | 34.60 | 0.7832210 | 33.8167790 | 33.82 | 32.93 | -2.63% |

价格来源：[甘源食品新浪不复权历史](https://finance.sina.com.cn/realstock/company/sz002991/hisdata_klc2/klc_kl.js)、[嘉益股份新浪不复权历史](https://finance.sina.com.cn/realstock/company/sz301004/hisdata_klc2/klc_kl.js)。两份响应 09-23 的 `prevclose` 分别为 37.65、33.82，也与已冻结的具名日期腾讯报价相同。

[推断] 按公告规定复算扣减后，以分为价格粒度计算参考价，再按 `100*(close/pre_close-1)` 取两位，得到上述结果；它同时被两个行情来源佐证，不是任选一家供应商。复算使用 Decimal，先对**每十股**折算分红截取六位，再除以十；不能先对每股取六位。

## 裁决边界

- [推断] 本次两行差异来自“对有权参与分配股东的名义每股分红”和“按公司全部股份折算的参考扣减”语义不同。原同花顺 `dividend_per_share=0.63/0.8` 不应全局覆盖成参考扣减；具名修复应绑定公告、日期与独立参考价依据。
- 仅裁决 2026-09-23 的两只现金分红事件，不证明全市场复权完整性，不改变官方换手率/历史全集/停牌证明的状态。后续仍须绑定日期专用 writer，验证 canonical 行及派生消费者，再验发布组合。
- 可复跑计算与断言：`/Users/a77/.finance-runtime/reviews/workbench-release-20260924-independent/adjudicate_cash_references.py`；结果：同目录 `cash-reference-adjudication.json`。输出固定 `database_writes=false`、`publication_attempted=false`、`production_ready=false`。

## 提炼提示

可迁移原则：字段同名不等于口径相同。供应商名义分红字段的值可能正确，但直接用于除息参考价的公式可能不适用；有回购股不参与分配时，应按实施公告认定基数和截位顺序。
