# Deployment Notification O365

[![CI](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/ci.yml/badge.svg)](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/marcus-hooper/deployment-notification-o365)](https://github.com/marcus-hooper/deployment-notification-o365/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![CodeQL](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/codeql.yml/badge.svg)](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/codeql.yml)
[![Security](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/security.yml/badge.svg)](https://github.com/marcus-hooper/deployment-notification-o365/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/marcus-hooper/deployment-notification-o365/badge)](https://scorecard.dev/viewer/?uri=github.com/marcus-hooper/deployment-notification-o365)

A GitHub Action that sends deployment notifications via email using Microsoft Graph API and Azure Active Directory.

## Features

- Sends deployment notification emails when deployments complete
- Integrates with Microsoft Graph API for email delivery
- Uses Azure Active Directory for secure authentication
- Includes repository, environment, timestamp, and recent commit messages
- Cross-platform (runs on Linux, macOS, and Windows runners)

## Quick Start

```yaml
- name: Send Deployment Notification
  uses: marcus-hooper/deployment-notification-o365@v1
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    NOTIFICATION_TO: team@example.com
    NOTIFICATION_FROM: notifications@example.com
```

## Usage

```yaml
- name: Send Deployment Notification
  uses: marcus-hooper/deployment-notification-o365@v1
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    GITHUB_ACTOR: ${{ github.actor }}
    GITHUB_ENVIRONMENT: production
    NOTIFICATION_TO: team@example.com, lead@example.com
    NOTIFICATION_FROM: notifications@example.com
```

### With Commit Messages

To include recent commit messages in the notification, create a `commit_message.txt` file before calling the action:

```yaml
- name: Get recent commits
  run: git log --oneline -5 > commit_message.txt

- name: Send Deployment Notification
  uses: marcus-hooper/deployment-notification-o365@v1
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    GITHUB_ACTOR: ${{ github.actor }}
    GITHUB_ENVIRONMENT: production
    NOTIFICATION_TO: team@example.com, lead@example.com
    NOTIFICATION_FROM: notifications@example.com
```

### Complete Workflow Example

Here's a complete deployment workflow with notification:

```yaml
name: Deploy and Notify

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy Application
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 5

      - name: Deploy to production
        run: |
          # Your deployment steps here
          echo "Deploying application..."

      - name: Capture recent commits
        run: git log --oneline -5 > commit_message.txt

      - name: Send Deployment Notification
        uses: marcus-hooper/deployment-notification-o365@v1
        env:
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_ACTOR: ${{ github.actor }}
          GITHUB_ENVIRONMENT: ${{ github.environment }}
          NOTIFICATION_TO: ${{ vars.NOTIFICATION_TO }}
          NOTIFICATION_FROM: ${{ vars.NOTIFICATION_FROM }}
```

### Sample Email Output

The action sends a plain text email with the following format:

**Subject:**
```
Deployment Successful: owner/repo to production on 2025-01-15 14:30:45
```

**Body:**
```
Repository: owner/repo
Environment: production
Deployment Time: 2025-01-15 14:30:45
Status: Successful
Started by: username
Repository URL: https://github.com/owner/repo

Recent Commit Messages:
abc1234 Fix authentication bug
def5678 Add new feature
```

## Prerequisites

### Azure Active Directory Application

1. **Register an application** in [Azure Portal](https://portal.azure.com) > Azure Active Directory > App registrations > New registration
   - Name: `GitHub Deployment Notifications` (or your preference)
   - Supported account types: Single tenant
   - Redirect URI: Leave blank

2. **Add API permissions**
   - Go to API permissions > Add a permission > Microsoft Graph
   - Select **Application permissions** (not Delegated)
   - Search for and add `Mail.Send`
   - Click **Grant admin consent** (requires admin privileges)

3. **Create a client secret**
   - Go to Certificates & secrets > New client secret
   - Set an expiration (recommend 12-24 months)
   - Copy the secret value immediately (shown only once)

4. **Note your credentials**
   - **Tenant ID**: Found in Overview
   - **Client ID**: Found in Overview (Application ID)
   - **Client Secret**: The value you copied above

### GitHub Secrets

Add the following secrets to your repository (Settings > Secrets and variables > Actions):

| Secret | Description |
|--------|-------------|
| `AZURE_TENANT_ID` | Azure AD Tenant ID |
| `AZURE_CLIENT_ID` | Azure AD Application Client ID |
| `AZURE_CLIENT_SECRET` | Azure AD Application Client Secret |

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `AZURE_TENANT_ID` | Azure AD Tenant ID |
| `AZURE_CLIENT_ID` | Azure AD Application Client ID |
| `AZURE_CLIENT_SECRET` | Azure AD Application Client Secret |
| `GITHUB_REPOSITORY` | Repository name (owner/repo) |
| `GITHUB_ACTOR` | User who triggered the deployment |
| `GITHUB_ENVIRONMENT` | Deployment environment (e.g., production) |
| `NOTIFICATION_TO` | Comma-separated recipient email addresses |
| `NOTIFICATION_FROM` | Sender email address (must have a mailbox in your tenant) |

### Optional

| Input | Description |
|-------|-------------|
| `commit_message.txt` | File containing recent commit messages to include |

## How It Works

1. Loads Azure credentials from environment variables
2. Reads `commit_message.txt` if present in the working directory
3. Formats email with repository, environment, timestamp, and commits
4. Authenticates via Azure AD using client credentials flow
5. Sends email via Microsoft Graph API (`/users/{sender}/sendMail`)

## Limitations

- **Plain text emails only** - HTML formatting is not supported
- **US/Eastern timezone** - Timestamps use US/Eastern timezone; not configurable
- **No retry logic** - Email send is attempted once; fails immediately on error
- **Environment variables only** - Uses `env:` rather than `with:` inputs

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AADSTS7000215: Invalid client secret` | Client secret is incorrect or expired | Regenerate the client secret in Azure Portal |
| `AADSTS700016: Application not found` | Wrong Client ID or Tenant ID | Verify IDs in Azure Portal > App registrations |
| `Authorization_RequestDenied` | Missing `Mail.Send` permission | Add permission and grant admin consent |
| `ErrorItemNotFound` / `MailboxNotFound` | `NOTIFICATION_FROM` email doesn't exist | Use an email with a valid mailbox in your tenant |
| `Missing required environment variable` | Env var not set or empty | Check secrets are correctly configured in GitHub |

### Debug Tips

1. **Check workflow logs** - Expand the "Send notification" step for detailed error messages
2. **Verify Azure AD setup** - Ensure admin consent is granted (green checkmark in API permissions)
3. **Test sender email** - The `NOTIFICATION_FROM` address must be a valid mailbox, not just an alias
4. **Check secret expiration** - Client secrets expire; regenerate if needed

## Development

### Requirements

- Python 3.11+

### Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy send_deployment_notification.py --ignore-missing-imports
```

### Project Structure

```
deployment-notification-o365/
├── .github/
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
│       ├── ci.yml              # Linting, type checking, tests
│       ├── codeql.yml          # CodeQL SAST analysis
│       ├── security.yml        # Security scanning
│       ├── validate.yml        # action.yml validation
│       ├── release.yml         # Version tag management
│       └── ...
├── tests/                      # Unit tests
├── action.yml                  # GitHub Action definition
├── send_deployment_notification.py
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── pyproject.toml              # Tool configuration
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick start:

1. Check existing [issues](https://github.com/marcus-hooper/deployment-notification-o365/issues) or open a new one
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/my-feature`)
4. Make your changes and add tests if applicable
5. Ensure CI passes (lint, format, and test)
6. Submit a pull request

See the issue templates for [bug reports](.github/ISSUE_TEMPLATE/bug_report.yml) and [feature requests](.github/ISSUE_TEMPLATE/feature_request.yml).

## Security

See [SECURITY.md](SECURITY.md) for security policy and best practices.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
