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
- Regular updates on the progress of addressing the vulnerability
- Credit in the security advisory (unless you prefer to remain anonymous)

### Scope

The following are considered security vulnerabilities:
- Authentication or authorization bypasses
- Credential exposure or leakage
- Injection vulnerabilities in the script
- Issues that could compromise email content or recipients
- Issues that could compromise the CI/CD pipeline

Out of scope:
- Vulnerabilities in upstream dependencies (report to the respective project)
- Issues requiring physical access or social engineering

### Security Notifications

Security fixes are announced via:
- [GitHub Security Advisories](https://github.com/marcus-hooper/deployment-notification-o365/security/advisories)
- Release notes for patched versions

Dependencies are monitored automatically via Dependabot.

## Security Considerations

This action handles sensitive credentials:

- **Azure AD credentials** (tenant ID, client ID, client secret)
- **Email addresses** (sender and recipients)

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

### Permissions Required

The Azure AD application requires:
- `Mail.Send` - To send emails via Microsoft Graph API

No other permissions are required or requested.
