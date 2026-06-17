# CI/CD Configuration Documentation

This directory contains GitHub Actions workflows for continuous integration and continuous deployment of the Jules AI Code Generation Platform.

## Workflows Overview

### 1. Backend CI (`backend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (backend changes)
- Pull requests to `main` or `develop` branches (backend changes)

**Jobs:**

#### Lint and Format Check
- Runs Ruff linter
- Checks code formatting with Ruff formatter
- Runs mypy type checking

#### Security Check
- Runs Bandit security analysis
- Uploads security report as artifact

#### Test
- Runs full test suite with coverage
- Requires PostgreSQL and Redis services
- Uploads coverage to Codecov
- Uploads HTML coverage report as artifact
- **Coverage threshold:** 80%

#### Code Quality Analysis
- Runs Radon complexity check
- Generates maintainability index

**Required Services:**
- PostgreSQL 15
- Redis 7

---

### 2. Frontend CI (`frontend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (frontend changes)
- Pull requests to `main` or `develop` branches (frontend changes)

**Jobs:**

#### Lint and Format Check
- Runs ESLint
- TypeScript type checking
- Prettier format check

#### Test
- Runs Vitest test suite with coverage
- Uploads coverage to Codecov
- Uploads coverage report as artifact

#### Build
- Builds Next.js application
- Uploads build artifacts

#### Bundle Size Check
- Analyzes production bundle size
- Reports size to job summary

---

### 3. Docker Build (`docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Version tags (`v*`)
- Pull requests to `main`

**Jobs:**

#### Build Backend
- Builds backend Docker image
- Pushes to GitHub Container Registry
- Multi-platform support (amd64, arm64)
- Uses build cache for optimization

#### Build Frontend
- Builds frontend Docker image
- Pushes to GitHub Container Registry
- Multi-platform support (amd64, arm64)
- Injects build-time environment variables

#### Security Scan
- Runs Trivy vulnerability scanner
- Scans for CRITICAL and HIGH severity issues
- Uploads results to GitHub Security

**Image Tagging Strategy:**
- Branch name (e.g., `main`, `develop`)
- Semantic version (e.g., `v1.2.3`, `1.2`)
- Commit SHA with branch prefix

---

### 4. Database Migration CI (`db-migration.yml`)

**Triggers:**
- Push to `main` or `develop` branches (migration changes)
- Pull requests to `main` or `develop` branches (migration changes)

**Jobs:**

#### Validate Migrations
- Checks for migration conflicts
- Tests upgrade migrations
- Tests downgrade migrations
- Tests full migration cycle
- Verifies database schema

#### Check Migration Message Quality
- Ensures migration files have descriptive names
- Checks for migration docstrings
- Only runs on pull requests

**Required Services:**
- PostgreSQL 15

---

### 5. Pull Request Checks (`pr-checks.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches

**Jobs:**

#### PR Validation
- Validates PR title follows conventional commits
- Checks PR description length (minimum 50 characters)
- Detects breaking changes

#### Size Check
- Analyzes PR size (files, lines changed)
- Warns on large PRs (>1000 line changes)

#### Conflict Check
- Detects merge conflicts

#### Dependency Review
- Reviews new dependencies for security issues
- Blocks high severity vulnerabilities
- Denies GPL licenses

#### Label Check
- Checks for appropriate PR labels

**Conventional Commit Format:**
```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build
```

---

### 6. Deploy (`deploy.yml`)

**Triggers:**
- Version tags (`v*`) - automatic production deployment
- Manual workflow dispatch - choose environment

**Supported Environments:**
- Production
- Staging

**Deployment Steps:**
1. SSH connection to deployment server
2. Pull latest code/checkout version tag
3. Login to container registry
4. Pull latest Docker images
5. Run database migrations
6. Restart services with zero downtime
7. Clean up old images
8. Health check verification

**Rollback:**
- Automatic rollback on deployment failure
- Reverts to previous version

**Required Secrets:**
- `DEPLOY_SSH_KEY`: SSH private key
- `DEPLOY_USER`: SSH username
- `DEPLOY_HOST`: Server hostname
- `DEPLOY_PATH`: Deployment directory path
- `BACKEND_URL`: Backend health check URL
- `FRONTEND_URL`: Frontend health check URL

---

### 7. Code Quality Monitoring (`code-quality.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Weekly schedule (Monday 2 AM UTC)
- Manual workflow dispatch

**Jobs:**

#### SonarQube Analysis
- Full codebase analysis
- Coverage reports integration
- Code smell detection
- Security hotspot identification

#### Code Metrics
- Lines of code analysis
- Cyclomatic complexity
- Maintainability index
- Comments PR with metrics

#### Dependency Audit
- npm audit for frontend
- Safety check for backend
- Uploads audit results

#### License Check
- Verifies license compliance
- Generates license reports
- Checks both frontend and backend dependencies

---

## Setup Instructions

### 1. Repository Secrets

Configure the following secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

#### Required for all workflows:
```bash
GITHUB_TOKEN  # Automatically provided by GitHub
```

#### Required for deployment:
```bash
DEPLOY_SSH_KEY      # SSH private key for deployment server
DEPLOY_USER         # SSH username
DEPLOY_HOST         # Deployment server hostname
DEPLOY_PATH         # Path to deployment directory
BACKEND_URL         # Backend URL for health checks
FRONTEND_URL        # Frontend URL for health checks
```

#### Optional (for enhanced features):
```bash
SONAR_TOKEN             # SonarQube authentication token
SONAR_HOST_URL          # SonarQube server URL
NEXT_PUBLIC_API_URL     # Frontend API endpoint
CODECOV_TOKEN           # Codecov upload token (optional)
```

### 2. GitHub Container Registry

Enable GitHub Packages in your repository:
1. Go to `Settings > Actions > General`
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"

### 3. Environment Configuration

Create environments in GitHub (`Settings > Environments`):
- **production**: Requires approval, protected
- **staging**: Auto-deploy on develop branch

### 4. Branch Protection Rules

Recommended branch protection for `main` and `develop`:
1. Require pull request reviews (minimum 1)
2. Require status checks to pass:
   - Backend CI: All jobs
   - Frontend CI: All jobs
   - PR Checks: All jobs
   - Docker Build: Build jobs
3. Require branches to be up to date
4. Require signed commits (recommended)

---

## Local Development

### Running workflows locally with act

Install [act](https://github.com/nektos/act):
```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

Run a workflow locally:
```bash
# Backend CI
act -W .github/workflows/backend-ci.yml

# Frontend CI
act -W .github/workflows/frontend-ci.yml

# Specific job
act -j lint-and-format -W .github/workflows/backend-ci.yml
```

### Pre-commit Hooks

Install pre-commit hooks to catch issues before CI:
```bash
cd backend
poetry run pre-commit install
```

---

## Workflow Badges

Add status badges to your README.md:

```markdown
[![Backend CI](https://github.com/your-org/jules/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/your-org/jules/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/your-org/jules/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/your-org/jules/actions/workflows/frontend-ci.yml)
[![Docker Build](https://github.com/your-org/jules/actions/workflows/docker-build.yml/badge.svg)](https://github.com/your-org/jules/actions/workflows/docker-build.yml)
```

---

## Troubleshooting

### Common Issues

#### 1. PostgreSQL connection issues in CI
```yaml
# Ensure health checks are configured correctly
options: >-
  --health-cmd pg_isready
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

#### 2. Poetry cache issues
Clear the cache and re-run:
```bash
# In workflow, add:
- name: Clear Poetry cache
  run: poetry cache clear pypi --all
```

#### 3. Docker build fails with OOM
Increase build memory or use smaller base images:
```dockerfile
# Use slim images
FROM python:3.11-slim
```

#### 4. Deployment health check timeout
Increase sleep duration before health checks:
```yaml
- name: Health check
  run: |
    sleep 60  # Increase from 30 to 60 seconds
```

---

## Monitoring and Notifications

### GitHub Actions Dashboard
View all workflow runs: `Actions` tab in repository

### Notifications
Configure in `Settings > Notifications`:
- Email notifications on workflow failure
- Slack/Discord webhooks (via GitHub Apps)

### Metrics
Monitor workflow metrics:
- Average run time
- Success rate
- Resource usage

---

## Cost Optimization

### GitHub Actions Minutes

#### Free tier:
- Public repositories: Unlimited
- Private repositories: 2,000 minutes/month

#### Optimization tips:
1. Use caching for dependencies
2. Run jobs in parallel
3. Skip unnecessary jobs with path filters
4. Use self-hosted runners for intensive tasks

### Example: Skip workflow if no relevant changes
```yaml
on:
  push:
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'
```

---

## Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets
2. **Use GITHUB_TOKEN** - Automatically provided, limited scope
3. **Pin action versions** - Use specific versions or SHA
4. **Review dependency updates** - Use Dependabot
5. **Enable branch protection** - Prevent force pushes
6. **Use environment secrets** - Separate prod/staging secrets
7. **Audit workflow permissions** - Minimal required permissions

---

## Maintenance

### Regular Tasks

#### Weekly:
- Review security scan results
- Check dependency audit reports
- Monitor workflow success rates

#### Monthly:
- Update action versions
- Review and optimize workflow run times
- Clean up old artifacts

#### Quarterly:
- Review and update branch protection rules
- Audit secrets and rotate if necessary
- Review and update deployment procedures

---

## Contributing

When adding new workflows:
1. Test locally with `act` first
2. Document in this README
3. Add appropriate triggers and filters
4. Use caching where applicable
5. Follow existing naming conventions
6. Add status checks to branch protection

---

## Support

For issues or questions:
- Create an issue in the repository
- Check GitHub Actions documentation: https://docs.github.com/actions
- Contact DevOps team: devops@jules-ai.dev

---

**Last Updated:** 2026-06-17
**Maintained by:** DevOps Team
