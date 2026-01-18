# Contributing to deployment-notification-o365

Thank you for your interest in contributing to deployment-notification-o365!

## Development Setup

### Prerequisites

- Python 3.13+
- Git

### Clone and Install

```bash
git clone https://github.com/marcus-hooper/deployment-notification-o365.git
cd deployment-notification-o365
pip install -r requirements-dev.txt
```

### Verify Setup

```bash
pytest
```

## Running CI Locally

Before pushing, run the same checks as CI:

```bash
# Lint check (must pass)
ruff check .

# Format check (must pass)
ruff format --check .

# Type check (must pass)
mypy send_deployment_notification.py --ignore-missing-imports

# Unit tests (must pass)
pytest
```

### Quick CI Script

```bash
# All-in-one CI check
ruff check . && ruff format --check . && mypy send_deployment_notification.py --ignore-missing-imports && pytest
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `ci` | CI/workflow changes |
| `deps` | Dependency updates |
| `security` | Security improvements |

### Examples

```
feat: Add CC recipient support

fix: Handle missing commit_message.txt gracefully

docs: Update environment variable documentation

ci: Add CodeQL security scanning

deps: Update msgraph-sdk to 1.5.0
```

### Breaking Changes

For breaking changes, use `!` after the type or add a `BREAKING CHANGE:` footer:

```
feat!: Change email body format to HTML

Email bodies now use HTML content type instead of plain text.
```

Or with a footer:

```
feat: Change email body format to HTML

BREAKING CHANGE: Email bodies now use HTML content type instead of plain text.
```

## Pull Request Process

### Before Opening a PR

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Run CI locally** (see above)

3. **Add tests** for new functionality

4. **Update README.md** if adding new environment variables or changing behavior

### PR Requirements

All PRs must pass these checks before merge:

| Check | Command | Threshold |
|-------|---------|-----------|
| Lint | `ruff check .` | No errors |
| Format | `ruff format --check .` | No changes |
| Type Check | `mypy send_deployment_notification.py --ignore-missing-imports` | No errors |
| Tests | `pytest` | All pass |
| Security | `bandit -r . -x ./tests` | No high-severity issues |

### PR Description

Include in your PR description:

- Summary of changes
- Related issue (if any)
- Type of change (bug fix, feature, refactor, etc.)
- Testing performed

### Code Review

- All PRs require at least one approval
- Address review feedback promptly
- Resolve all conversations before merge
- Squash merge to `main`

## Test Requirements

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=term-missing
```

### Adding Tests

| Change Type | Test Requirement |
|-------------|------------------|
| New function | Add unit tests covering happy path and error cases |
| Bug fix | Add regression test that fails without the fix |
| Refactor | Ensure existing tests still pass |

Tests are located in `tests/`. See [Test Mocking](#test-mocking) for important details about the mocking setup.

## Coding Standards

- **Formatter**: Ruff (line length 100)
- **Linter**: Ruff with pycodestyle, Pyflakes, isort, bugbear rules
- **Type hints**: Optional but encouraged for new code
- **Imports**: Sorted alphabetically, stdlib first, then third-party

Auto-fix issues before committing:

```bash
ruff check . --fix  # Lint and auto-fix
ruff format .       # Format code
```

## Project-Specific Guidelines

### Important Notes

| Topic | Details |
|-------|---------|
| **Timezone** | Hardcoded to US/Eastern in `prepare_email_content()` |
| **Email format** | Plain text only; HTML content type is not supported |
| **Windows compatibility** | `msgraph-sdk` has path length issues on Windows; tests mock it entirely |
| **Async pattern** | All Graph API calls are async; `main()` uses `asyncio.run()` |

### Test Mocking

Tests mock the entire `msgraph` SDK to avoid Windows path length issues and enable testing without Azure credentials. See `tests/conftest.py` for the mocking setup. When adding new tests, follow the existing mocking patterns.

## Issue Guidelines

### Bug Reports

Use the bug report template. Include:

- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages

### Feature Requests

Use the feature request template. Include:

- Problem statement
- Proposed solution
- Alternatives considered

## Release Process

Releases are managed by maintainers:

1. All CI checks pass on `main`
2. Tag created: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. Tag pushed: `git push origin v1.0.0`
4. GitHub Actions updates the major version tag (`v1` → points to `v1.0.0`)

Users referencing `@v1` automatically get the latest `v1.x.x` release.

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/marcus-hooper/deployment-notification-o365/discussions)
- **Bugs**: Open an [Issue](https://github.com/marcus-hooper/deployment-notification-o365/issues)
- **Security**: See [SECURITY.md](SECURITY.md)

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
