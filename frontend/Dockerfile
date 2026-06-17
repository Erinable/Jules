# ============================================
# Frontend Dockerfile - Node.js 18 Alpine
# ============================================

# 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装依赖所需的系统包
RUN apk add --no-cache libc6-compat

# 复制依赖配置文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 设置环境变量
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV development

# 开发阶段
FROM node:18-alpine AS development

WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache libc6-compat

# 复制 package.json
COPY package.json package-lock.json* ./

# 安装依赖（包括开发依赖）
RUN npm ci

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev"]

# 生产构建阶段
FROM node:18-alpine AS production-builder

WORKDIR /app

RUN apk add --no-cache libc6-compat

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# 构建生产版本
RUN npm run build

# 生产运行阶段
FROM node:18-alpine AS production

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=production-builder /app/public ./public
COPY --from=production-builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=production-builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
