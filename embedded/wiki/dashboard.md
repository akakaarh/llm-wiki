---
type: dashboard
tags: [dataview, dashboard, wiki]
created: 2026-05-30
---

# Wiki Dashboard

## 概念页面

```dataview
TABLE tags, created
FROM "embedded/wiki/concepts"
SORT file.name ASC
```

## 来源文档

```dataview
TABLE tags, created
FROM "embedded/wiki/sources"
SORT file.name ASC
```

## 学习笔记

```dataview
TABLE tags, created
FROM "embedded/wiki/notes"
SORT file.name ASC
```

## 问题记录

```dataview
TABLE tags, created
FROM "embedded/wiki/questions"
SORT file.name ASC
```

## 最近更新

```dataview
TABLE file.mtime AS "更新时间"
FROM "embedded/wiki"
WHERE type != "dashboard"
SORT file.mtime DESC
LIMIT 10
```

## 按标签查找

```dataview
TABLE file.name AS "页面", type AS "类型"
FROM "embedded/wiki"
WHERE contains(tags, "gpio")
SORT file.name ASC
```

## 学习进度

```dataview
TABLE status, type
FROM "embedded/wiki/progress"
SORT file.name ASC
```

## 全部页面统计

```dataview
TABLE length(rows) AS "数量"
FROM "embedded/wiki"
GROUP BY type
SORT length(rows) DESC
```
