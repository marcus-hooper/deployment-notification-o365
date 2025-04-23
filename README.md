# Deployment Notification O365

A GitHub Action and Python-based solution for sending deployment notifications via email using Microsoft Graph API and Azure Active Directory.

## Features

- Sends deployment notifications via email.
- Integrates with Microsoft Graph API for email delivery.
- Uses Azure Active Directory for secure authentication.
- Supports environment variable configuration for flexibility.

## Prerequisites

1. **Azure Active Directory Application**:
   - Register an application in Azure Active Directory.
   - Grant the application the `Mail.Send` permission for Microsoft Graph API.
   - Note the `Tenant ID`, `Client ID`, and `Client Secret`.

2. **Python Environment**:
   - Python 3.8 or higher installed.
   - Install dependencies using `pip install -r requirements.txt`.

3. **Environment Variables**:
   - Set the following environment variables:
     - `AZURE_TENANT_ID`: Your Azure AD Tenant ID.
     - `AZURE_CLIENT_ID`: Your Azure AD Application Client ID.
     - `AZURE_CLIENT_SECRET`: Your Azure AD Application Client Secret.
     - `GITHUB_ENVIRONMENT`: The deployment environment (e.g., production, staging).
     - `NOTIFICATION_TO`: Comma-separated list of recipient email addresses.
     - `NOTIFICATION_FROM`: The sender's email address.
