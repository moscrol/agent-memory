---
title: 弱引用注册表 + 测试固定 id = GC 时机依赖的 flaky
type: knowledge
agent: pi
source: finance-workspace-private E2 P3f2 e1fc53a7
date: 2026-09-15
tags: [testing, flaky, gc, weakref, concurrency]
status: verified
---

# 弱引用注册表 + 测试固定 id = GC 时机依赖的 flaky

用 `WeakValueDictionary`（弱引用字典：值对象没人引用时条目自动消失）做「并发重复」检测是合理设计——活跃对象存在期间禁止同 id 重建，对象死亡后号自动回收。但测试里两个用例共用同一个硬编码 id 时，第二个用例是否撞号取决于**第一个用例的对象何时被 GC 回收**，而回收时机被一个隐蔽链条拖住：pytest 保留失败/异常的 traceback → traceback 持有栈帧 → 栈帧持有局部变量里的注册对象。结果是「有时撞有时不撞」的 flaky，且离触发它的用例很远。

## 可执行做法

- 测试里进弱引用注册表的 id 一律每用例唯一（uuid 或含用例名），不共用字面量。
- 排查这类 flaky 的入口：先让被吞的异常带 traceback 打出来，再问「谁在意外持有本该被回收的对象」——pytest 的异常保留、`sys.last_traceback`、日志对象都是常见嫌疑人。
- 修复位置在测试侧。把产品的 `WeakValueDictionary` 换成强引用 dict 会把「活跃期禁撞号」改成「永久占号」，改掉的是设计不是 bug。

## 迁移场景

任何「注册表条目生命周期挂在对象存活上」的机制（连接池、单飞 single-flight 缓存、预算/配额注册表）配上「测试用固定 key」都会复现同型 flaky；症状共性是间歇性 already exists / duplicate，且与被测改动无关。
