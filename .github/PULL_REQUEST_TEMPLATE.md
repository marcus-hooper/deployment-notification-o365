## Summary

<!-- Brief description of what this PR does -->

## Related Issues

<!-- Link to related issues: Fixes #123, Relates to #456 -->

## Changes

<!-- List the key changes made -->

-
-
-

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Security fix
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CI/CD changes
- [ ] Dependency update

### Breaking Change Details

<!-- If breaking change, describe migration steps for users -->

## Testing

<!-- Describe how this was tested -->

- [ ] Unit tests added/updated
- [ ] All tests pass (`pytest`)
- [ ] Manual testing performed

## Security Considerations

<!-- If this PR modifies Azure authentication, email handling, or external dependencies -->

- [ ] N/A - No changes to authentication or email logic
- [ ] Verified no credentials are logged or exposed
- [ ] Reviewed for supply chain security implications
- [ ] No new external services or endpoints added without validation

## Checklist

- [ ] My code follows the project's coding standards
- [ ] I have run `ruff check .` and there are no linting issues
- [ ] I have run `ruff format --check .` and code is properly formatted
- [ ] I have run `mypy send_deployment_notification.py --ignore-missing-imports` (if applicable)
- [ ] I have run `bandit -r . -x ./tests` and there are no security issues
- [ ] I have updated documentation if needed
- [ ] I have updated README.md if action inputs/outputs changed
- [ ] I have checked for breaking changes and documented them
- [ ] Commit messages use conventional prefixes (`fix:`, `feat:`, `docs:`, `security:`, etc.)
- [ ] Any new GitHub Actions dependencies are pinned to full commit SHAs

### Dependency Updates

<!-- Check if this PR modifies dependencies -->

- [ ] N/A - No dependency changes
- [ ] `requirements.txt` updated with pinned versions
- [ ] `pip-audit` shows no new vulnerabilities

## Output

<!-- Optional: Add relevant command output, logs, or test results -->
