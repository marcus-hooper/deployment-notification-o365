# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email the maintainer directly or use GitHub's private vulnerability reporting feature
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment of your report within 48 hours
- Regular updates on the progress of addressing the vulnerability
- Credit in the security advisory (unless you prefer to remain anonymous)

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

### Permissions Required

The Azure AD application requires:
- `Mail.Send` - To send emails via Microsoft Graph API

No other permissions are required or requested.
