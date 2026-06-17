# Pre-commit Hooks Quick Reference

## Installation

### Backend
```bash
cd backend
poetry install
poetry run pre-commit install
```

### Frontend
```bash
cd frontend
npm install
# Hooks auto-install via prepare script
```

## Running Hooks Manually

### Backend
```bash
# All hooks on all files
poetry run pre-commit run --all-files

# Specific hook
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files
poetry run pre-commit run bandit --all-files

# Only on staged files
poetry run pre-commit run
```

### Frontend
```bash
# All checks
npm run lint
npm run type-check

# Auto-fix
npm run lint:fix
npm run format

# Test lint-staged (what runs on commit)
npx lint-staged
```

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Valid Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code refactoring
- `perf` - Performance
- `test` - Testing
- `build` - Build system
- `ci` - CI config
- `chore` - Maintenance
- `revert` - Revert commit

### Examples
```bash
git commit -m "feat: add user authentication"
git commit -m "fix(api): resolve timeout issue"
git commit -m "docs: update README"
git commit -m "test(auth): add unit tests"
```

## Backend Hooks

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| Ruff | Linting + Formatting | ✅ |
| mypy | Type checking | ❌ |
| Bandit | Security scanning | ❌ |
| Safety | Dependency check | ❌ |
| Poetry | Lock file check | ❌ |
| detect-secrets | Secret detection | ❌ |
| trailing-whitespace | Remove trailing spaces | ✅ |
| end-of-file-fixer | Add final newline | ✅ |
| sqlfluff | SQL formatting | ✅ |
| interrogate | Docstring coverage | ❌ |

## Frontend Hooks

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| ESLint | JavaScript/TypeScript linting | ✅ |
| Prettier | Code formatting | ✅ |
| TypeScript | Type checking | ❌ |
| Commitlint | Commit message validation | ❌ |

## Skip Hooks (Emergency Only)

```bash
# Skip all hooks
git commit --no-verify -m "emergency fix"

# Or use env variable
SKIP=ruff git commit -m "skip ruff only"
```

## Update Hooks

```bash
# Backend
cd backend
poetry run pre-commit autoupdate

# Frontend
cd frontend
npm update husky lint-staged @commitlint/cli
```

## Troubleshooting

### Backend: Command not found
```bash
poetry install
poetry run pre-commit install
```

### Frontend: Hooks not running
```bash
npm install
chmod +x .husky/pre-commit .husky/commit-msg
```

### Hooks too slow
Edit `.pre-commit-config.yaml` and add `stages: [manual]` to slow hooks

### CI passes but local fails
```bash
# Update dependencies
poetry update  # or npm update
# Run full check
poetry run pre-commit run --all-files
```

## Configuration Files

| File | Purpose |
|------|---------|
| `backend/.pre-commit-config.yaml` | Backend hook config |
| `frontend/.husky/pre-commit` | Frontend pre-commit script |
| `frontend/.husky/commit-msg` | Commit message validation |
| `frontend/commitlint.config.js` | Commitlint rules |
| `frontend/package.json` | lint-staged config |

## Common Issues

### 1. Line too long
**Error**: `E501 Line too long`
**Fix**: Break line into multiple lines or use implicit string concatenation

### 2. Import not sorted
**Error**: `I001 Import block is un-sorted`
**Fix**: Auto-fixed by Ruff or reorder-python-imports

### 3. Missing type annotation
**Error**: `ANN001 Missing type annotation`
**Fix**: Add type hints to function arguments

### 4. Invalid commit message
**Error**: `type may not be empty`
**Fix**: Use format: `feat: description` or `fix: description`

### 5. TypeScript error
**Error**: `Type 'X' is not assignable to type 'Y'`
**Fix**: Fix type definitions or add proper type assertions

## CI Integration

Pre-commit hooks run in CI:
- Backend CI: `.github/workflows/backend-ci.yml`
- Frontend CI: `.github/workflows/frontend-ci.yml`
- PR Checks: `.github/workflows/pr-checks.yml`

All hooks must pass before merging PRs.

## Best Practices

1. ✅ Commit small, logical changes
2. ✅ Fix hook issues immediately
3. ✅ Run manual checks before pushing
4. ✅ Keep hooks updated monthly
5. ❌ Don't skip hooks without documenting
6. ❌ Don't commit large files (>1MB)
7. ❌ Don't commit secrets or credentials

## Support

- Documentation: `PRE_COMMIT_SETUP.md`
- Issues: Create GitHub issue
- Questions: Ask in team chat

---

**Quick Start**: Install hooks, make changes, commit with proper format, let hooks ensure quality!
