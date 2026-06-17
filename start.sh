#!/bin/bash
# ============================================
# Jules 项目启动脚本
# ============================================

set -e

echo "======================================"
echo "Jules AI 代码生成平台 - 环境启动"
echo "======================================"
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，从 .env.example 创建"
    cp .env.example .env
    echo "✅ .env 文件已创建，请编辑填入必要的 API 密钥"
    echo ""
    echo "必填项："
    echo "  - ANTHROPIC_API_KEY"
    echo "  - OPENAI_API_KEY (可选)"
    echo "  - LANGSMITH_API_KEY (可选)"
    echo ""
    read -p "是否继续？ (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ 环境变量文件已就绪"
echo ""

# 停止并清理旧容器
echo "🧹 清理旧容器..."
docker-compose down 2>/dev/null || true
echo ""

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build
echo ""

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d
echo ""

# 等待服务就绪
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose ps
echo ""

# 检查后端健康状态
echo "🔍 检查后端健康状态..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ 后端服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 后端服务启动失败"
        echo "查看日志: docker-compose logs backend"
        exit 1
    fi
    echo "   等待中... ($i/30)"
    sleep 2
done

echo ""
echo "======================================"
echo "✅ Jules 环境启动成功！"
echo "======================================"
echo ""
echo "📍 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   ReDoc 文档: http://localhost:8000/redoc"
echo ""
echo "📝 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo "   进入容器: docker-compose exec backend bash"
echo ""
echo "🎉 开始使用 Jules！"
