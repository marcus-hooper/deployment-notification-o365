# Changelog

All notable changes to deployment-notification-o365 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-18

### Added

- CONTRIBUTING.md with development setup, coding standards, and PR guidelines
- Pull request template with checklist and structured sections
- Issue template chooser with security vulnerability and documentation links
- Repository labels configuration file with type, priority, status, and area labels
- Label sync workflow to automatically apply labels from configuration
- Dependency review configuration with license allow-list for supply chain security
- CHANGELOG validation job in CI workflow
- Concurrency groups to cancel redundant workflow runs
- Path filters to CI workflow to skip runs for docs-only changes
- Pip caching in CI workflow for faster dependency installation
- Timeout settings to all workflow jobs
- Dependency grouping in Dependabot to batch related updates

### Changed

- Issue templates converted from Markdown to YAML form-based format
- Dependabot configuration enhanced with timezone, rebase strategy, and major version ignore rules
- All workflow checkout actions now use `persist-credentials: false`

### Security

- Added step-security/harden-runner with egress blocking to all workflows
- Network egress restricted to only required endpoints per workflow
- Added objects.githubusercontent.com to CodeQL workflow allowed endpoints

## [1.0.2] - 2026-01-16

### Fixed

- Use pwsh shell for cross-platform compatibility on Windows runners

## [1.0.1] - 2026-01-16

### Added

- CI/CD workflows (linting, type checking, tests, security scanning)
- CodeQL workflow for SAST analysis
- OSSF Scorecard workflow for security analysis
- Test suite with pytest and code coverage
- SECURITY.md with vulnerability reporting guidelines
- Dependabot configuration for automated dependency updates
- Test results upload to CI artifacts

### Changed

- Pin all GitHub Actions to commit SHAs for supply chain security
- Pin Python dependencies with hashes for supply chain security
- Add explicit least-privilege permissions to all workflows
- Updated actions/checkout from v4 to v6
- Updated actions/setup-python from v5 to v6
- Updated actions/upload-artifact from v4 to v6
- Updated github/codeql-action from v3 to v4
- Updated ossf/scorecard-action from 2.4.0 to 2.4.3

### Fixed

- Linting errors and action.yml branding quotes
- Import line wrapping for ruff line length compliance
- Include production dependencies in dev requirements for CI tests

### Security

- Remove unpinned pip upgrade commands from workflows
- Pin dependencies with hashes for supply chain security

## [1.0.0] - 2025-04-23

### Added

- Initial release
- GitHub Action for sending deployment notifications via Microsoft Graph API
- Azure AD authentication using client credentials
- Email notifications with repository, environment, actor, and timestamp
- Support for including recent commit messages from file
- Composite action definition for easy integration
- README with usage instructions and prerequisites

---

<!--
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality
- **BREAKING**: Description of breaking change

### Deprecated
- Features to be removed in future versions

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements or vulnerability fixes
-->

[Unreleased]: https://github.com/marcus-hooper/deployment-notification-o365/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/marcus-hooper/deployment-notification-o365/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/marcus-hooper/deployment-notification-o365/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/marcus-hooper/deployment-notification-o365/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/marcus-hooper/deployment-notification-o365/releases/tag/v1.0.0
