# Branch Strategy

> Git branch management rules for AI SEO Agency

## Branch Types

### Main Branches

| Branch | Purpose | Protected | Direct Push |
|--------|---------|-----------|-------------|
| `main` | Production-ready code | Yes | No |
| `develop` | Integration branch for next release | Yes | No |

### Feature Branches

```
feature/{ticket-id}-{short-description}
```

- Branch from: `develop`
- Merge back to: `develop`
- Naming: Use kebab-case

**Examples:**
```
feature/AUD-001-site-audit-workflow
feature/agent-new-local-seo
feature/docs-api-reference
```

### Bugfix Branches

```
bugfix/{ticket-id}-{short-description}
```

- Branch from: `develop` or `main` (for hotfixes)
- Merge back to: `develop` or `main`

**Examples:**
```
bugfix/AUD-002-fix-handoff-timeout
bugfix/hotfix-security-patch
```

### Release Branches

```
release/{version}
```

- Branch from: `develop`
- Merge back to: `main` and `develop`
- Version format: `v1.2.0`

### Hotfix Branches

```
hotfix/{ticket-id}-{short-description}
```

- Branch from: `main`
- Merge back to: `main` and `develop`
- Use for critical production fixes

## Branch Lifecycle

```
main ──────────────────────────────────────────────────────►
  │       ▲                    ▲
  │       │                    │
  │   hotfix/001          release/v1.1
  │       │                    │
  │       ▼                    ▼
develop ───► feature/001 ─────────────► merge
              │
              ▼
         feature/002 ───────► merge
```

## Workflow

### Feature Development

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/AUD-001-new-workflow

# 3. Work and commit
git add .
git commit -m "feat: add new workflow"

# 4. Push and create PR
git push -u origin feature/AUD-001-new-workflow
# Create PR to develop via GitHub UI
```

### Release Process

```bash
# 1. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0

# 2. Final testing and fixes
# (No new features after this point)

# 3. Merge to main
git checkout main
git merge release/v1.1.0
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main --tags

# 4. Merge back to develop
git checkout develop
git merge release/v1.1.0
git push origin develop

# 5. Delete release branch
git branch -d release/v1.1.0
```

### Hotfix Process

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/security-fix

# 2. Fix and commit
git commit -m "fix: resolve security issue"

# 3. Merge to main
git checkout main
git merge hotfix/security-fix
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin main --tags

# 4. Merge to develop
git checkout develop
git merge hotfix/security-fix
git push origin develop
```

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{id}-{description}` | `feature/AUD-001-site-audit` |
| Bugfix | `bugfix/{id}-{description}` | `bugfix/AUD-002-fix-timeout` |
| Release | `release/{version}` | `release/v1.1.0` |
| Hotfix | `hotfix/{id}-{description}` | `hotfix/security-patch` |
| Experiment | `experiments/{description}` | `experiments/new-agent-pattern` |

## Rules

1. **Never commit directly to main**
2. **Always branch from the correct source**
3. **Use meaningful branch names** with ticket IDs
4. **Delete branches after merge**
5. **Keep branches short-lived** (max 1-2 weeks)
6. **Sync with upstream** before creating PRs

## Commit Messages

Follow [Conventional Commits](https://conventionalcommits.org):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code restructuring |
| `test` | Tests |
| `chore` | Maintenance |

### Examples

```
feat(agents): add local SEO agent
fix(workflow): resolve handoff timeout issue
docs: update QUICKSTART.md
refactor(state): simplify ledger format
test: add unit tests for task protocol
```

## Pull Request Guidelines

### PR Title

Use conventional commit format:
```
feat(agents): add local SEO agent
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Related Issue
Closes #XXX

## Testing
- [ ] Tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Requirements

- At least 1 approval required
- All CI checks must pass
- No merge conflicts

---

**Questions?** Open a discussion or ask in the team channel.
