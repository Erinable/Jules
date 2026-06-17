# 部署架构

**版本**: v1.0  
**日期**: 2026-06-16  

---

## 1. 部署策略

### 1.1 环境划分

| 环境 | 用途 | 域名 | 数据库 |
|------|------|------|--------|
| Development | 本地开发 | localhost:3000 | Docker Compose |
| Staging | 预发布测试 | staging.example.com | 托管 PostgreSQL |
| Production | 生产环境 | app.example.com | 托管 PostgreSQL (高可用) |

---

## 2. 本地开发环境

### 2.1 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aicodegen
      - REDIS_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=aicodegen
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A app.worker worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aicodegen
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres

volumes:
  postgres_data:
  redis_data:
```

### 2.2 快速启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

---

## 3. 生产环境部署

### 3.1 云平台选择

推荐部署方案：
1. **AWS**: ECS + RDS + ElastiCache
2. **GCP**: Cloud Run + Cloud SQL + Memorystore
3. **Azure**: Container Apps + Azure Database + Azure Cache

### 3.2 架构图（AWS 示例）

```mermaid
graph TB
    Internet[互联网] --> CF[CloudFront CDN]
    CF --> ALB[Application Load Balancer]
    
    ALB --> FE1[Frontend<br/>ECS Fargate]
    ALB --> FE2[Frontend<br/>ECS Fargate]
    
    FE1 --> APIALB[API Load Balancer]
    FE2 --> APIALB
    
    APIALB --> BE1[Backend API<br/>ECS Fargate]
    APIALB --> BE2[Backend API<br/>ECS Fargate]
    
    BE1 --> RDS[(RDS PostgreSQL<br/>Multi-AZ)]
    BE2 --> RDS
    
    BE1 --> ElastiCache[(ElastiCache Redis<br/>Cluster)]
    BE2 --> ElastiCache
    
    BE1 --> S3[S3 Bucket<br/>代码存储]
    BE2 --> S3
    
    Worker1[Celery Worker<br/>ECS Fargate] --> ElastiCache
    Worker2[Celery Worker<br/>ECS Fargate] --> ElastiCache
    
    CloudWatch[CloudWatch Logs] --> BE1
    CloudWatch --> BE2
```

### 3.3 ECS Fargate 任务定义

```json
{
  "family": "backend-api",
  "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/backend:latest",
      "portMappings": [
        {"containerPort": 8000, "protocol": "tcp"}
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "secrets": [
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/backend-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## 4. 容器镜像

### 4.1 前端 Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

### 4.2 后端 Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. CI/CD 流水线

### 5.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=app tests/
      
      - name: Run quality checks
        run: |
          ruff check app/
          mypy app/
          bandit -r app/
  
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/backend:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/backend:$IMAGE_TAG
          docker tag $ECR_REGISTRY/backend:$IMAGE_TAG $ECR_REGISTRY/backend:latest
          docker push $ECR_REGISTRY/backend:latest
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster production-cluster \
            --service backend-api \
            --force-new-deployment
```

---

## 6. 数据库迁移

### 6.1 Alembic 配置

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

from app.models import Base
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### 6.2 部署时自动迁移

```bash
# 在容器启动前执行
alembic upgrade head
```

---

## 7. 监控与日志

### 7.1 Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### 7.2 应用指标

```python
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 自动收集 HTTP 指标
Instrumentator().instrument(app).expose(app)

# 自定义指标
code_generation_counter = Counter(
    "code_generation_total",
    "Total code generation requests"
)

agent_execution_time = Histogram(
    "agent_execution_seconds",
    "Agent execution time",
    ["agent_type"]
)

quality_score = Gauge(
    "quality_score",
    "Current quality score",
    ["project_id"]
)
```

---

## 8. 备份策略

### 8.1 数据库备份

```bash
# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$TIMESTAMP.sql

# 上传到 S3
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql s3://backups/db/

# 保留最近 30 天
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### 8.2 Cron 定时任务

```cron
# 每天凌晨 2 点备份
0 2 * * * /usr/local/bin/backup.sh
```

---

## 9. 扩展策略

### 9.1 水平扩展

**API 层**：
- Auto Scaling Group（AWS）
- 目标：CPU 使用率 < 70%
- 最小实例：2，最大实例：10

**Worker 层**：
- 基于队列长度自动扩展
- 队列任务 > 100 时增加 Worker

### 9.2 垂直扩展

| 组件 | 初始配置 | 扩展后 |
|------|---------|-------|
| API | 1 CPU, 2GB | 2 CPU, 4GB |
| Worker | 2 CPU, 4GB | 4 CPU, 8GB |
| PostgreSQL | db.t3.medium | db.r5.large |
| Redis | cache.t3.micro | cache.r5.large |

---

## 10. 灾难恢复

### 10.1 RTO/RPO 目标

| 指标 | 目标值 |
|------|--------|
| RTO (Recovery Time Objective) | < 1 小时 |
| RPO (Recovery Point Objective) | < 15 分钟 |

### 10.2 恢复流程

1. **数据库恢复**：从 S3 最近备份恢复
2. **容器恢复**：从 ECR 拉取最新镜像
3. **配置恢复**：从 AWS Secrets Manager 获取
4. **服务启动**：ECS 自动启动任务
5. **健康检查**：验证所有服务正常

---

## 11. 成本估算（AWS）

| 服务 | 配置 | 月成本（USD） |
|------|------|--------------|
| ECS Fargate (API) | 2 实例 × 1CPU/2GB | $60 |
| ECS Fargate (Worker) | 2 实例 × 2CPU/4GB | $120 |
| RDS PostgreSQL | db.t3.medium (Multi-AZ) | $120 |
| ElastiCache Redis | cache.t3.micro | $15 |
| S3 | 100GB 存储 | $3 |
| CloudFront | 1TB 传输 | $85 |
| **总计** | | **$403/月** |

*注：LLM API 调用成本另计*
