# Accounts and User Management

Zen HR provides flexible user management with role-based access control.

## User Roles

### Admin

Full access to all Zen HR features:

- Manage all employees and their data
- Access billing and subscription settings
- Configure company-wide settings
- Add and remove users
- Manage integrations
- View all reports and analytics
- Create custom workflows

Every Zen HR account must have at least one Admin.

### HR Manager

Access to HR functions without billing control:

- View and edit all employee records
- Manage time-off policies and requests
- Run performance reviews
- Generate reports
- Approve document requests
- Cannot access billing or subscription settings

### Manager

Limited access focused on direct reports:

- View profiles of direct reports only
- Approve time-off requests for their team
- Conduct performance reviews for direct reports
- View team reports
- Cannot edit company-wide settings

### Employee

Self-service access for individual users:

- View and update their own profile
- Submit time-off requests
- Access personal documents
- View company directory
- Participate in performance reviews
- View their own reports

## Inviting Users

### Single User Invite

1. Go to **People > Add Employee**
2. Enter their email and basic information
3. Select their role
4. Check "Send invite email"
5. Click Save

### Bulk Invites

1. Go to **Settings > Data > Import**
2. Include email addresses in your CSV
3. After import, go to **People > Pending Invites**
4. Click "Send All Invites"

## Single Sign-On (SSO)

Zen HR supports SSO with major identity providers:

### Google Workspace

1. Go to **Settings > Security > SSO**
2. Click "Connect Google Workspace"
3. Authorize Zen HR in your Google Admin console
4. Enable "Require SSO for all users" (optional)

### Microsoft Entra ID (Azure AD)

1. Go to **Settings > Security > SSO**
2. Click "Connect Microsoft"
3. Enter your Entra ID tenant information
4. Complete authorization in Azure portal

### Okta

1. Go to **Settings > Security > SSO**
2. Click "Connect Okta"
3. Enter your Okta domain
4. Add Zen HR as an application in Okta

### OneLogin

1. Go to **Settings > Security > SSO**
2. Click "Connect OneLogin"
3. Follow the setup wizard

### SAML 2.0 (Custom)

For other identity providers:

1. Go to **Settings > Security > SSO**
2. Click "Configure SAML"
3. Enter your IdP metadata URL or upload metadata file
4. Configure attribute mappings

## Two-Factor Authentication (2FA)

Zen HR supports 2FA for additional security:

### Enabling 2FA for Your Account

1. Go to **Profile > Security**
2. Click "Enable 2FA"
3. Scan the QR code with an authenticator app (Google Authenticator, Authy, 1Password)
4. Enter the verification code
5. Save your backup codes securely

### Requiring 2FA Company-Wide

Admins can require 2FA for all users:

1. Go to **Settings > Security**
2. Enable "Require 2FA for all users"
3. Set a grace period for users to enable 2FA
4. Users without 2FA will be prompted on next login

## Password Requirements

Default password policy:

- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character

Admins can customize password requirements in **Settings > Security**.

## Session Management

### Session Timeout

Sessions expire after 24 hours of inactivity by default. Admins can adjust this in **Settings > Security**.

### Active Sessions

Users can view and terminate active sessions:

1. Go to **Profile > Security**
2. View "Active Sessions"
3. Click "Sign out" next to any session to terminate it

### Sign Out Everywhere

To terminate all sessions:

1. Go to **Profile > Security**
2. Click "Sign out of all devices"
3. Confirm the action

## Account Deactivation

### Deactivating an Employee

When an employee leaves:

1. Go to **People > [Employee Name]**
2. Click "Deactivate Account"
3. Choose whether to:
   - Immediately revoke access
   - Schedule deactivation for a future date
4. Select data retention preferences
5. Reassign any pending approvals

Deactivated accounts:
- Cannot log in
- Are hidden from the active directory
- Retain historical data for reporting
- Can be reactivated if needed

### Reactivating an Account

1. Go to **People > Inactive**
2. Find the employee
3. Click "Reactivate"
4. Send a new invite email if needed

## Data Privacy

### Viewing Your Data

Employees can export their personal data:

1. Go to **Profile > Privacy**
2. Click "Download My Data"
3. Receive a ZIP file with all personal information

### Right to Deletion

For GDPR compliance, users can request data deletion:

1. Contact your company Admin
2. Admin goes to **People > [Employee] > Privacy**
3. Click "Process Deletion Request"
4. Confirm after the required retention period
