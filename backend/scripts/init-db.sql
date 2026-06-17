-- ============================================
-- Jules 数据库初始化脚本
-- ============================================

-- 设置时区
SET timezone = 'UTC';

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建数据库（如果使用多数据库架构）
-- CREATE DATABASE jules_test;

-- 输出初始化信息
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully';
    RAISE NOTICE 'Extensions: uuid-ossp, pg_trgm';
END $$;
