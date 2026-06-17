# CI/CD Quick Reference

## Workflow Triggers Quick Reference

| Workflow | Push (main/develop) | PR | Tags | Manual | Schedule |
|----------|--------------------|----|------|---------|----------|
| Backend CI | ✅ (backend/*) | ✅ | ❌ | ❌ | ❌ |
| Frontend CI | ✅ (frontend/*) | ✅ | ❌ | ❌ | ❌ |
| Docker Build | ✅ | ✅ | ✅ v* | ❌ | ❌ |
| DB Migration | ✅ (alembic/*) | ✅ | ❌ | ❌ | ❌ |
| PR Checks | ❌ | ✅ | ❌ | ❌ | ❌ |
| Deploy | ❌ | ❌ | ✅ v* | ✅ | ❌ |
| Code Quality | ✅ | ❌ | ❌ | ✅ | ✅ Weekly |

## Common Commands

### Testing Workflows Locally
```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run backend CI
act -W .github/workflows/backend-ci.yml

# Run specific job
act -j test -W .github/workflows/backend-ci.yml

# Run with secrets
act -W .github/workflows/backend-ci.yml -s GITHUB_TOKEN=xxx
```

### Manual Deployment
```bash
# Via GitHub CLI
gh workflow run deploy.yml -f environment=staging

# Via GitHub UI
Actions > Deploy to Production > Run workflow > Select environment
```

### Viewing Workflow Status
```bash
# Install GitHub CLI
brew install gh

# List workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch a run in real-time
gh run watch <run-id>
```

## Workflow Status Checks

### Required for PR Merge (main branch)
- ✅ Backend CI: lint-and-format
- ✅ Backend CI: security-check
- ✅ Backend CI: test
- ✅ Frontend CI: lint-and-format
- ✅ Frontend CI: test
- ✅ Frontend CI: build
- ✅ PR Checks: pr-validation
- ✅ PR Checks: conflict-check

### Optional but Recommended
- Docker Build: build-backend
- Docker Build: build-frontend
- DB Migration: validate-migrations (if migrations changed)
- Code Quality: all jobs

## Environment Variables

### Backend CI/CD
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key

# Optional
ANTHROPIC_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
LANGSMITH_API_KEY=xxx
```

### Frontend CI/CD
```bash
# Build-time
NEXT_PUBLIC_API_URL=https://api.example.com

# Runtime (via docker-compose)
API_URL=http://backend:8000
```

## Secrets Configuration

### Deployment Secrets
```bash
DEPLOY_SSH_KEY        # SSH private key (RSA 4096)
DEPLOY_USER           # SSH username
DEPLOY_HOST           # Server IP or hostname
DEPLOY_PATH           # /opt/jules or /var/www/jules
BACKEND_URL           # https://api.jules.dev
FRONTEND_URL          # https://jules.dev
```

### Optional Secrets
```bash
SONAR_TOKEN           # SonarQube authentication
SONAR_HOST_URL        # https://sonarqube.example.com
CODECOV_TOKEN         # Codecov upload token
NEXT_PUBLIC_API_URL   # Frontend API URL
```

## Artifact Retention

| Artifact | Retention | Size Limit |
|----------|-----------|------------|
| Coverage Reports | 30 days | 50 MB |
| Build Artifacts | 7 days | 100 MB |
| Security Reports | 90 days | 10 MB |
| Test Reports | 30 days | 20 MB |

## Troubleshooting Quick Fixes

### Problem: Workflow not triggering
```yaml
# Check path filters - make sure changes match
paths:
  - 'backend/**'
  - '.github/workflows/backend-ci.yml'
```

### Problem: PostgreSQL connection failed
```bash
# Check service health configuration
--health-cmd pg_isready
--health-interval 10s
--health-timeout 5s
--health-retries 5
```

### Problem: Poetry dependencies not cached
```bash
# Verify cache key matches poetry.lock
key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
```

### Problem: Docker build out of memory
```yaml
# Add resource limits or use smaller base image
FROM python:3.11-slim  # instead of python:3.11
```

### Problem: Deployment health check fails
```bash
# Increase wait time before health check
sleep 60  # increase from 30
```

## Performance Optimization

### Cache Strategy
```yaml
# 1. Dependencies cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/poetry.lock') }}

# 2. Build cache (Docker)
cache-from: type=gha
cache-to: type=gha,mode=max

# 3. Node modules cache
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
```

### Parallel Jobs
```yaml
# Run tests in parallel
strategy:
  matrix:
    test-group: [unit, integration, e2e]
steps:
  - run: pytest tests/${{ matrix.test-group }}
```

### Skip Unnecessary Runs
```yaml
# Only run on relevant changes
paths:
  - 'backend/**'
  - '!backend/**.md'  # Exclude markdown
```

## Deployment Checklist

### Pre-deployment
- [ ] All CI checks passing
- [ ] Code review approved
- [ ] Version tag created (`git tag -a v1.0.0 -m "Release 1.0.0"`)
- [ ] CHANGELOG updated
- [ ] Database migration tested
- [ ] Secrets configured in GitHub

### During deployment
- [ ] Monitor workflow run
- [ ] Check health checks pass
- [ ] Verify services are running
- [ ] Check logs for errors

### Post-deployment
- [ ] Smoke test critical paths
- [ ] Monitor error rates
- [ ] Check database migrations applied
- [ ] Verify application metrics

### Rollback (if needed)
```bash
# Manual rollback
ssh deploy@server
cd /opt/jules
git checkout v1.0.0  # previous version
docker compose up -d
```

## Monitoring URLs

### GitHub Actions
- Workflow runs: `https://github.com/[owner]/[repo]/actions`
- Specific workflow: `https://github.com/[owner]/[repo]/actions/workflows/[workflow].yml`

### Container Registry
- Packages: `https://github.com/[owner]/[repo]/pkgs/container/[package]`

### Security
- Security tab: `https://github.com/[owner]/[repo]/security`
- Dependabot alerts: `https://github.com/[owner]/[repo]/security/dependabot`

## Release Process

### 1. Create Release Branch
```bash
git checkout -b release/v1.0.0
```

### 2. Update Version
```bash
# Backend
poetry version 1.0.0

# Frontend
npm version 1.0.0
```

### 3. Update CHANGELOG
```markdown
## [1.0.0] - 2026-06-17
### Added
- New feature X
### Fixed
- Bug Y
```

### 4. Create PR and Merge
```bash
gh pr create --title "Release v1.0.0" --body "Release notes..."
# After approval and CI passes
gh pr merge
```

### 5. Tag Release
```bash
git checkout main
git pull
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 6. Monitor Deployment
```bash
gh run watch
# Or visit: https://github.com/[owner]/[repo]/actions
```

## Emergency Procedures

### Stop Running Workflow
```bash
gh run cancel <run-id>
# Or via UI: Actions > [workflow run] > Cancel workflow
```

### Emergency Rollback
```bash
# Trigger deployment with previous tag
gh workflow run deploy.yml -f environment=production

# Or manually via SSH
ssh deploy@server "cd /opt/jules && git checkout v1.0.0 && docker compose up -d"
```

### Disable Workflow Temporarily
```bash
gh workflow disable <workflow-name>
# Re-enable: gh workflow enable <workflow-name>
```

## Useful GitHub CLI Commands

```bash
# List workflows
gh workflow list

# View workflow definition
gh workflow view <workflow-name>

# List recent runs
gh run list --limit 10

# Download artifacts
gh run download <run-id>

# View logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed
```

## Contact & Support

- **CI/CD Issues**: Create issue with `ci/cd` label
- **Emergency**: Contact DevOps team via Slack #devops-alerts
- **Documentation**: `.github/README.md`
- **Runbooks**: `docs/runbooks/`

---

**Last Updated:** 2026-06-17
