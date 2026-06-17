# Pre-commit Hooks Setup Guide

This document provides instructions for setting up and using pre-commit hooks in the Jules project.

## Overview

Pre-commit hooks automatically run checks before each commit to ensure code quality and prevent common issues. We use:
- **Backend (Python)**: `pre-commit` framework
- **Frontend (Node.js)**: `husky` + `lint-staged` + `commitlint`

## Backend Setup (Python)

### 1. Install Pre-commit

The backend uses Poetry, and `pre-commit` is already in the dev dependencies. Install it:

```bash
cd backend
poetry install
```

### 2. Install Git Hooks

Install the pre-commit hooks into your local Git repository:

```bash
poetry run pre-commit install
```

### 3. Run Hooks Manually (Optional)

To run all hooks on all files:

```bash
poetry run pre-commit run --all-files
```

### Backend Hooks Overview

The following hooks run automatically before each commit:

#### Code Quality
- **Ruff**: Fast Python linter and formatter (replaces flake8, isort, black)
- **mypy**: Static type checking
- **reorder-python-imports**: Import sorting

#### Security
- **Bandit**: Security vulnerability scanner
- **Safety**: Dependency vulnerability checker
- **detect-secrets**: Prevents committing secrets

#### File Quality
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **mixed-line-ending**: Ensures consistent line endings (LF)
- **check-yaml/json/toml**: Validates file syntax

#### Python Specific
- **check-docstring-first**: Ensures docstrings come first
- **debug-statements**: Catches debug statements
- **name-tests-test**: Validates test file naming

#### Documentation
- **interrogate**: Checks docstring coverage (minimum 50%)

#### SQL
- **sqlfluff**: SQL linting and formatting for PostgreSQL

#### Poetry
- **poetry-check**: Validates pyproject.toml
- **poetry-lock**: Ensures lock file is up to date

### Configuration File

Location: `backend/.pre-commit-config.yaml`

### Updating Hooks

Update to the latest hook versions:

```bash
poetry run pre-commit autoupdate
```

### Skip Hooks (Emergency Only)

To skip pre-commit hooks (not recommended):

```bash
git commit --no-verify -m "commit message"
```

---

## Frontend Setup (Node.js)

### 1. Install Dependencies

Install Husky, lint-staged, and commitlint:

```bash
cd frontend
npm install
```

### 2. Initialize Husky

Husky should be automatically initialized when you run `npm install`. If not:

```bash
npm run prepare
```

### 3. Verify Installation

Check that hooks are installed:

```bash
ls -la .husky/
# Should show: pre-commit, commit-msg (both executable)
```

### Frontend Hooks Overview

The following hooks run automatically:

#### Pre-commit Hook (`.husky/pre-commit`)
Runs on staged files using `lint-staged`:
- **ESLint**: JavaScript/TypeScript linting with auto-fix
- **Prettier**: Code formatting
- **TypeScript**: Type checking

#### Commit Message Hook (`.husky/commit-msg`)
- **Commitlint**: Validates commit message format (Conventional Commits)

### Configuration Files

- Husky hooks: `frontend/.husky/`
- lint-staged config: `frontend/package.json` (lint-staged section)
- Commitlint config: `frontend/commitlint.config.js`

### Updating Hooks

Update dependencies:

```bash
npm update husky lint-staged @commitlint/cli @commitlint/config-conventional
```

### Skip Hooks (Emergency Only)

To skip hooks (not recommended):

```bash
git commit --no-verify -m "commit message"
```

---

## Commit Message Format (Conventional Commits)

Both backend and frontend enforce Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

Must be one of:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI configuration changes
- `chore`: Other changes (dependencies, etc)
- `revert`: Revert previous commit

### Examples

```bash
# Good commit messages
git commit -m "feat: add user authentication"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "refactor(auth): simplify JWT validation logic"

# Bad commit messages (will be rejected)
git commit -m "update code"           # Missing type
git commit -m "Feat: add feature"     # Type must be lowercase
git commit -m "add new feature"       # Missing type prefix
git commit -m "feat add feature"      # Missing colon
```

### Scope (Optional)

Scope can specify what part of the codebase is affected:

```bash
git commit -m "feat(api): add new endpoint"
git commit -m "fix(database): resolve migration issue"
git commit -m "test(auth): add unit tests"
```

---

## Workflow

### Normal Commit Workflow

1. Make your changes
2. Stage files: `git add .`
3. Commit: `git commit -m "feat: your message"`
4. **Hooks run automatically:**
   - Backend: Ruff, mypy, Bandit, etc.
   - Frontend: ESLint, Prettier, TypeScript, Commitlint
5. If hooks pass: commit succeeds
6. If hooks fail: fix issues and try again

### When Hooks Fail

#### Backend Example
```bash
$ git commit -m "feat: add new feature"

Ruff linter.............................Failed
- hook id: ruff
- exit code: 1

app/main.py:10:1: E501 Line too long (120 > 100 characters)
```

**Fix**: Edit the file, then:
```bash
git add app/main.py
git commit -m "feat: add new feature"
```

#### Frontend Example
```bash
$ git commit -m "add new feature"

Commitlint..............................Failed
⧗   input: add new feature
✖   subject may not be empty [subject-empty]
✖   type may not be empty [type-empty]
```

**Fix**: Use correct format:
```bash
git commit -m "feat: add new feature"
```

---

## Troubleshooting

### Backend Issues

#### Issue: "pre-commit command not found"
**Solution**:
```bash
poetry install
poetry run pre-commit install
```

#### Issue: "ModuleNotFoundError" in mypy
**Solution**: Install additional dependencies
```bash
poetry run pre-commit install --install-hooks
```

#### Issue: Hooks take too long
**Solution**: Skip slow hooks for local development (edit `.pre-commit-config.yaml`):
```yaml
repos:
  - repo: ...
    hooks:
      - id: slow-hook
        stages: [manual]  # Only run manually
```

Then run manually when needed:
```bash
poetry run pre-commit run slow-hook --all-files
```

### Frontend Issues

#### Issue: "husky command not found"
**Solution**:
```bash
npm install
npm run prepare
```

#### Issue: Hooks not executing
**Solution**: Check if hooks are executable:
```bash
ls -la .husky/
chmod +x .husky/pre-commit .husky/commit-msg
```

#### Issue: "lint-staged not found"
**Solution**:
```bash
npm install lint-staged --save-dev
```

---

## CI Integration

Pre-commit hooks are also configured to run in CI:

### Backend CI
File: `.github/workflows/backend-ci.yml`
- Runs same checks as pre-commit hooks
- Enforces on all pull requests

### Frontend CI
File: `.github/workflows/frontend-ci.yml`
- Runs ESLint, Prettier, TypeScript checks
- Enforces on all pull requests

### PR Checks
File: `.github/workflows/pr-checks.yml`
- Validates commit message format
- Checks PR title and description

---

## Best Practices

### 1. Commit Often
Pre-commit hooks run fast. Commit small, logical changes frequently.

### 2. Fix Issues Immediately
Don't skip hooks to "fix later". Address issues before committing.

### 3. Run Manual Checks
Before pushing, run full checks:
```bash
# Backend
cd backend
poetry run pre-commit run --all-files

# Frontend
cd frontend
npm run lint
npm run type-check
npm run test
```

### 4. Keep Hooks Updated
Update hooks monthly:
```bash
# Backend
poetry run pre-commit autoupdate

# Frontend
npm update husky lint-staged @commitlint/cli
```

### 5. Document Exceptions
If you must skip a hook, document why in the commit message:
```bash
git commit -m "feat: emergency fix" --no-verify
# Include explanation in PR description
```

---

## Configuration Customization

### Backend: Disable Specific Hooks

Edit `backend/.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.8
    hooks:
      - id: ruff
        exclude: ^(tests/|scripts/)  # Skip for these directories
```

### Frontend: Customize lint-staged

Edit `frontend/package.json`:

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
      // Add more commands here
    ]
  }
}
```

### Commitlint: Customize Rules

Edit `frontend/commitlint.config.js`:

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 150],  // Increase max length
    'scope-enum': [2, 'always', ['api', 'ui', 'db']]  // Enforce scopes
  }
};
```

---

## FAQ

### Q: Do hooks run on `git commit --amend`?
**A**: No, hooks don't run on amend by default. Run manually if needed:
```bash
# Backend
poetry run pre-commit run --all-files
# Then amend
git commit --amend
```

### Q: Can I run specific hooks only?
**A**: Yes:
```bash
# Backend
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files

# Frontend (run specific npm script)
npm run lint
npm run type-check
```

### Q: How do I test hooks without committing?
**A**:
```bash
# Backend
poetry run pre-commit run --all-files

# Frontend
npx lint-staged
npm run type-check
```

### Q: What if hooks fail in CI but pass locally?
**A**: Usually due to:
1. Different versions of tools
2. Unstaged changes committed
3. Environment differences

**Solution**: Update tools and run full checks locally:
```bash
# Backend
poetry update
poetry run pre-commit run --all-files

# Frontend
npm update
npm run lint && npm run type-check
```

---

## Support

For issues or questions:
- Create an issue in the repository
- Check GitHub Actions logs for CI failures
- Review `.pre-commit-config.yaml` (backend) or `.husky/` (frontend)

---

**Last Updated**: 2026-06-17
**Maintained by**: DevOps Team
