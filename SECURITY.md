# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Use [GitHub's private vulnerability reporting](https://github.com/marcus-hooper/deployment-notification-o365/security/advisories/new) to submit a report
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Disclosure Timeline

- Acknowledgment of your report within 48 hours
- Initial assessment within 7 days
- Target resolution within 90 days for critical vulnerabilities
- Weekly updates on the progress of addressing the vulnerability
- Credit in the security advisory (unless you prefer to remain anonymous)

### Safe Harbor

We consider security research conducted in accordance with this policy to be:

- Authorized concerning any applicable anti-hacking laws
- Authorized concerning any relevant anti-circumvention laws
- Exempt from restrictions in our Terms of Service that would interfere with conducting security research

We will not pursue civil action or initiate a complaint to law enforcement for accidental, good-faith violations of this policy. We consider security research conducted consistent with this policy to be "authorized" conduct under the Computer Fraud and Abuse Act.

We understand that many systems and services interconnect with third-party systems. While researching this project, ensure you do not access or modify third-party systems without authorization.

### Scope

The following are considered security vulnerabilities:
- Authentication or authorization bypasses
- Credential exposure or leakage
- Injection vulnerabilities in the script
- Issues that could compromise email content or recipients
- Issues that could compromise the CI/CD pipeline

Out of scope:
- Vulnerabilities in upstream dependencies (report to the respective project). However, if you notice we're using a vulnerable version, please let us know and we'll update our pinned dependencies promptly.
- Issues requiring physical access or social engineering

### Security Notifications

Security fixes are announced via:
- [GitHub Security Advisories](https://github.com/marcus-hooper/deployment-notification-o365/security/advisories)
- Release notes for patched versions

Dependencies are monitored automatically via Dependabot.

## Security Infrastructure

This project employs multiple layers of automated security:

| Measure | Description |
|---------|-------------|
| **CodeQL** | Static analysis for security vulnerabilities |
| **OSSF Scorecard** | Supply chain security assessment published to OpenSSF |
| **Bandit** | Python-specific security linter |
| **pip-audit** | Scans for known vulnerabilities in Python dependencies |
| **Secret Scanning** | Detects hardcoded credentials in code |
| **Pinned Actions** | All GitHub Actions pinned to full commit SHAs |
| **Dependabot** | Automated dependency updates |
| **Least Privilege Workflows** | Workflows use minimal `contents: read` permissions by default |

## Security Considerations

This action performs the following operations:

1. **Authenticates to Azure AD** using client credentials (tenant ID, client ID, secret)
2. **Sends HTTP requests** to Microsoft Graph API to send emails
3. **Reads local files** (commit_message.txt) if present
4. **Handles sensitive data** including Azure AD credentials and email addresses

### Network Endpoints

If you have firewall or egress restrictions, allow these endpoints:

| Endpoint | Port | Purpose |
|----------|------|---------|
| `login.microsoftonline.com` | 443 | Azure AD authentication |
| `graph.microsoft.com` | 443 | Microsoft Graph API (email sending) |

### Best Practices for Users

1. **Never hardcode credentials** - Always use GitHub Secrets
2. **Use environment-level secrets** - Scope secrets to specific environments when possible
3. **Rotate credentials regularly** - Update Azure AD client secrets periodically
4. **Limit permissions** - Grant the Azure AD application only the minimum required permissions (Mail.Send)
5. **Review access logs** - Monitor Azure AD sign-in logs for unusual activity
6. **Pin to a specific version** - Use a tagged release (e.g., `@v1`) rather than `@main`
7. **Use isolated runners** - Consider ephemeral runners for sensitive pipelines

### Data Handling

This action:

- Does **not** log or expose Azure credentials or email addresses
- Does **not** store any data beyond the workflow execution
- Does **not** send data to any service other than Microsoft Graph API
- Processes commit messages from local files (ensure you trust the source)
- Credentials passed via GitHub Secrets are automatically masked in workflow logs by GitHub Actions

### Permissions Required

The Azure AD application requires:
- `Mail.Send` - To send emails via Microsoft Graph API

No other permissions are required or requested.
