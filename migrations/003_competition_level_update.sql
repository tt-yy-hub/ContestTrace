-- 数据库迁移脚本：更新竞赛级别字段

-- 1. 修改原始公告表 raw_notices
-- 删除 raw_html 字段
ALTER TABLE raw_notices DROP COLUMN raw_html;

-- 将 source_department 重命名为 publisher
ALTER TABLE raw_notices RENAME COLUMN source_department TO publisher;

-- 2. 修改竞赛公告表 competition_notices
-- 将 category 重命名为 competition_category
ALTER TABLE competition_notices RENAME COLUMN category TO competition_category;

-- 添加 competition_level 字段
ALTER TABLE competition_notices ADD COLUMN competition_level TEXT;