---
title: 监控门禁的 mtime 陷阱
type: failure-shape
tags: [monitoring, filesystem, git, false-negative]
date: 2026-08-14
source: finance-workspace-private check_kb_freshness.py 假绿事故
status: verified
---

# 监控门禁的 mtime 陷阱

## 失败形状

**用文件修改时间（mtime）判断数据新鲜度时，批量改写操作会把 mtime 刷到操作日期，导致监控门禁误报正常。**

## 真实案例

知识库证据断更检测脚本 `check_kb_freshness.py` 取 `max(文件名日期, mtime)` 作为批次日期：

```python
# 旧版（有陷阱）
candidates = [_date_from_name(p.name)]
candidates.append(datetime.fromtimestamp(p.stat().st_mtime).date())
for d in candidates:
    if d is not None and (latest is None or d > latest):
        latest = d
```

**触发场景**（任何一个都会把 mtime 刷到今天）：
- 批量 frontmatter 改写（补 `source_quality` 字段、format 重排）
- `git checkout` 切换分支（文件内容未变，mtime 变为 checkout 时刻）
- 文本编辑器的批量替换（即使只改空格/换行）
- `touch` 命令或文件复制

**后果**：卖方研报线实际断更 11 天，但因公告线 1 天前 + mtime 被批量改写刷到今天，门禁报"1 天前"并发绿。

## 根本原因

**mtime 记录的是"文件系统最后修改时刻"，不是"数据内容的业务时间"。** 两者在以下场景会分离：
- 历史数据补录（内容是 2026-01-15，写入是 2026-08-14）
- 格式/字段规范化（业务数据未变，文件重写）
- Git 操作（checkout/merge/rebase 会更新 mtime）

## 正确做法

### 原则 1：监控应读取业务时间字段

```python
# 从文件内���或结构化索引读取业务日期
data = json.load(f)
latest = max(item["source_date"] for item in data["items"])
```

**不要从文件系统元数据推断业务属性。**

### 原则 2：读取运行时消费的数据结构

本例中检索层读取 `evidence_index.json`（证据关系台账），而不是扫描 `wiki/sources/*.md`：
- `evidence_index.json` 是检索的唯一入口，反映真实可用证据
- `sources/*.md` 可能存在但未入索引（ingest 中断、校验失败）
- **监控与消费路径一致时，才能准确反映可用性**

### 原则 3：多条管线分线监控

```python
# 按数据来源分组统计
for item in items:
    quality = item.get("source_quality", "unknown")
    lines[quality].append(item["source_date"])

# 各线独立报告
for lane, dates in lines.items():
    age = (today - max(dates)).days
    print(f"{lane}: {age} days")
```

**全局最大值会让活跃线掩盖断流线。** 分线报告才能精确定位哪条管线断了。

## 验收方法

构造"只改 mtime、不改内容"的场景，断言监控仍能识别断更：

```python
# 构造 30 天前的业务数据
old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
data = {"items": [{"source_date": old_date, "source_quality": "test"}]}

# 写文件（mtime = 今天）
with open(test_file, "w") as f:
    json.dump(data, f)

# 断言监控报 30 天前，不是 0 天前
assert monitor(test_file) == 30
```

## 适用范围

任何用文件时间戳做数据新鲜度监控的场景：
- CI/CD 缓存失效判断
- 数据湖分区裁剪（`mtime` vs `event_time`）
- 增量备份（`mtime` vs `created_at`）
- 日志归档（`mtime` vs `log_timestamp`）

## 不适用场景

当监控目标就是"文件系统变化"时，mtime 是正确的：
- 配置文件热重载（监控 `/etc/app.conf` 是否被修改）
- 构建缓存失效（源码 mtime > 产物 mtime 则重编译）

**判别标准**：问"我关心的是文件何时被写入，还是数据何时产生"。前者用 mtime，后者用业务字段。

## 相关

- [[evidence-hygiene-three-failure-shapes]] — 证据卫生的三大失败形状
- [[contract-vs-delivery-mismatch]] — 契约与交付不符（另一类监控盲区）
- Git worktree 多树共享索引时的提交纪律（mtime 无法区分"谁改的"）
