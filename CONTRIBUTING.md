# Contributing to Jules

感谢您对 Jules AI 代码生成平台的贡献！本文档提供了如何参与项目的详细指南。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码审查流程](#代码审查流程)
- [问题反馈](#问题反馈)
- [联系方式](#联系方式)

---

## 行为准则

### 我们的承诺

为了营造一个开放和包容的环境，我们承诺：

- 尊重不同的观点和经验
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 我们的标准

**积极行为示例**:

- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

**不可接受的行为**:

- ❌ 使用性化的语言或图像
- ❌ 侮辱性/贬损性评论，人身或政治攻击
- ❌ 公开或私下骚扰
- ❌ 未经明确许可发布他人的私人信息
- ❌ 其他在专业环境中可能被认为不适当的行为

---

## 如何贡献

### 贡献类型

我们欢迎以下类型的贡献：

1. **Bug 修复** - 修复现有问题
2. **新功能** - 添加新的功能特性
3. **文档改进** - 改进或补充文档
4. **测试** - 添加或改进测试用例
5. **性能优化** - 提升系统性能
6. **代码重构** - 改进代码质量和可维护性

---

## 开发流程

### 1. Fork 项目

```bash
# 在 GitHub 上 Fork 项目
# 克隆到本地
git clone https://github.com/YOUR_USERNAME/jules.git
cd jules

# 添加上游仓库
git remote add upstream https://github.com/your-org/jules.git
```

---

### 2. 创建功能分支

```bash
# 拉取最新代码
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/my-new-feature

# 或 Bug 修复分支
git checkout -b fix/bug-description
```

**分支命名规范**:

- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关

---

### 3. 进行开发

#### 代码规范

遵循项目的代码规范（详见 [docs/development.md](docs/development.md)）：

**Python**:

```bash
# 运行代码检查
cd backend
poetry run ruff check .
poetry run mypy app/
poetry run bandit -r app/
```

**TypeScript**:

```bash
# 运行代码检查
cd frontend
npm run lint
npm run type-check
```

#### 编写测试

- **后端**: 使用 pytest，确保测试覆盖率 ≥ 80%
- **前端**: 使用 Vitest，确保测试覆盖率 ≥ 80%

```bash
# 后端测试
cd backend
poetry run pytest --cov=app --cov-report=term

# 前端测试
cd frontend
npm run test:coverage
```

#### 更新文档

如果您的更改影响了以下内容，请更新相应文档：

- API 端点 → 更新 `backend/app/api/v1/README.md`
- 数据模型 → 更新 `docs/database.md`
- 配置项 → 更新 `README.md` 和 `.env.example`
- 使用方法 → 更新 `docs/development.md`

---

### 4. 提交代码

#### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具
- `perf`: 性能优化

**示例**:

```bash
# 新功能
git commit -m "feat(agent): add support for GPT-4 Turbo

- Implement GPT-4 Turbo model support
- Update LLMClient configuration
- Add unit tests

Closes #123"

# Bug 修复
git commit -m "fix(api): resolve task status update race condition

The task status was not being updated correctly under
concurrent requests. Added database-level locking.

Fixes #456"

# 文档更新
git commit -m "docs(readme): update installation instructions

- Add macOS-specific steps
- Clarify environment variable setup
- Fix broken links"
```

---

### 5. 推送并创建 Pull Request

```bash
# 推送到您的 Fork
git push origin feature/my-new-feature

# 创建 Pull Request（使用 GitHub CLI）
gh pr create \
  --title "feat: add my new feature" \
  --body "## Changes\n- Added X\n- Fixed Y\n\n## Testing\n- Unit tests added\n- Integration tests passed\n\nCloses #123"
```

#### Pull Request 检查清单

在提交 PR 前，确保：

- [ ] 代码遵循项目规范
- [ ] 所有测试通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 更新了相关文档
- [ ] 提交信息遵循 Conventional Commits
- [ ] 没有合并冲突
- [ ] PR 描述清晰，包含变更说明

#### PR 模板

```markdown
## 变更说明

简要描述您的更改内容。

## 变更类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 测试

## 测试

描述您如何测试了这些更改：

- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 测试通过（覆盖率 ≥ 80%）
- [ ] 更新了文档
- [ ] 没有合并冲突

## 截图（如适用）

如果是 UI 相关的更改，请提供截图。

## 相关 Issue

Closes #123
```

---

## 代码审查流程

### 审查标准

代码审查者会关注：

1. **功能正确性**
   - 代码是否实现了预期功能
   - 是否有边界情况处理
   - 错误处理是否完善

2. **代码质量**
   - 是否遵循项目规范
   - 代码是否清晰易读
   - 是否有适当的注释

3. **测试覆盖**
   - 是否有足够的测试
   - 测试是否覆盖关键路径
   - 测试覆盖率是否达标

4. **性能**
   - 是否有性能问题（N+1 查询、大循环）
   - 数据库查询是否优化
   - 是否有内存泄漏

5. **安全**
   - 是否有 SQL 注入风险
   - 是否有 XSS 漏洞
   - 是否有硬编码的密钥

### 审查意见分类

- 🔴 **Blocker**: 必须修复才能合并
- 🟡 **Suggestion**: 建议修改，但不强制
- 🟢 **Nitpick**: 可选的小改进

### 响应审查意见

```bash
# 根据审查意见修改代码
git add .
git commit -m "refactor: address code review feedback"
git push origin feature/my-new-feature
```

### 合并要求

PR 合并需要：

- ✅ 至少 1 个 Approver 批准
- ✅ 所有 CI/CD 检查通过
- ✅ 没有未解决的 Blocker 意见
- ✅ 没有合并冲突

---

## 问题反馈

### 如何报告 Bug

创建 Issue 时，请包含以下信息：

```markdown
## Bug 描述

简要描述 Bug。

## 重现步骤

1. 执行步骤 1
2. 执行步骤 2
3. 看到错误

## 期望行为

描述您期望发生什么。

## 实际行为

描述实际发生了什么。

## 环境信息

- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Node.js: [e.g., 18.17.0]
- Docker: [e.g., 20.10.24]
- 浏览器: [e.g., Chrome 115]

## 日志/错误信息

```

粘贴相关的错误日志

```

## 截图（如适用）

如果适用，请添加截图。
```

### 如何请求新功能

```markdown
## 功能描述

简要描述您希望添加的功能。

## 动机

为什么需要这个功能？它解决了什么问题？

## 建议的实现方式

（可选）您有什么实现建议吗？

## 替代方案

（可选）您考虑过哪些替代方案？

## 其他上下文

添加任何其他相关信息。
```

---

## 发布流程

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR** (主版本): 不兼容的 API 更改
- **MINOR** (次版本): 向后兼容的新功能
- **PATCH** (补丁版本): 向后兼容的 Bug 修复

示例：`1.2.3`

- `1` - 主版本
- `2` - 次版本
- `3` - 补丁版本

### 发布检查清单

- [ ] 所有测试通过
- [ ] 更新 `CHANGELOG.md`
- [ ] 更新版本号（`pyproject.toml`, `package.json`）
- [ ] 创建 Git 标签
- [ ] 构建 Docker 镜像
- [ ] 推送到镜像仓库
- [ ] 创建 GitHub Release

---

## 开发资源

### 文档

- [README.md](README.md) - 项目概览和快速开始
- [docs/development.md](docs/development.md) - 开发指南
- [docs/architecture/](docs/architecture/) - 架构文档
- [docs/database.md](docs/database.md) - 数据库文档

### 工具

- [GitHub Issues](https://github.com/your-org/jules/issues) - 问题追踪
- [GitHub Discussions](https://github.com/your-org/jules/discussions) - 讨论区
- [GitHub Projects](https://github.com/your-org/jules/projects) - 项目看板

### 社区

- **Slack**: [jules-dev.slack.com](https://jules-dev.slack.com)
- **Discord**: [discord.gg/jules](https://discord.gg/jules)
- **邮件列表**: <dev@jules-ai.dev>

---

## 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下发布。

---

## 致谢

感谢所有为 Jules 做出贡献的开发者！

---

## 联系方式

如果您有任何问题，请通过以下方式联系我们：

- **GitHub Issues**: <https://github.com/your-org/jules/issues>
- **邮箱**: <team@jules-ai.dev>
- **Slack**: [jules-dev.slack.com](https://jules-dev.slack.com)

---

**最后更新**: 2026-06-17
