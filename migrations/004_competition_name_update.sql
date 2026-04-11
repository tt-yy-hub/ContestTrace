-- 数据库迁移脚本：更新竞赛名称和级别字段

-- 1. 检查并删除旧字段
ALTER TABLE competition_notices DROP COLUMN IF EXISTS category;
ALTER TABLE competition_notices DROP COLUMN IF EXISTS competition_category;

-- 2. 添加新字段
ALTER TABLE competition_notices ADD COLUMN IF NOT EXISTS competition_name TEXT;
