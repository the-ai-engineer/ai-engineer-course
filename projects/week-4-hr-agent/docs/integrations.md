# Integrations

Zen HR connects with your favorite tools to streamline your HR workflows.

## Payroll Integrations

### Gusto

Sync employee data and time-off with Gusto.

**What syncs:**
- Employee profiles (name, email, department, job title)
- Time-off balances and requests
- New hire information
- Termination dates

**Setup:**
1. Go to **Settings > Integrations > Payroll**
2. Click "Connect Gusto"
3. Log in to your Gusto account
4. Authorize Zen HR
5. Choose sync direction (one-way or bidirectional)
6. Map fields between systems

**Sync frequency:** Every 4 hours (automatic) or on-demand

### ADP Workforce Now

Integrate with ADP for enterprise payroll.

**What syncs:**
- Employee demographics
- Compensation data (read-only in Zen HR)
- Time-off accruals
- Department and position changes

**Setup:**
1. Go to **Settings > Integrations > Payroll**
2. Click "Connect ADP"
3. Enter your ADP company code
4. Complete OAuth authorization in ADP
5. Configure field mappings

**Requirements:** ADP API access (contact your ADP representative)

### Paychex

Connect Paychex Flex for payroll synchronization.

**What syncs:**
- Employee profiles
- Pay schedules
- Time-off data

**Setup:**
1. Go to **Settings > Integrations > Payroll**
2. Click "Connect Paychex"
3. Enter your Paychex client ID
4. Authorize the connection
5. Test sync with a few employees first

### Rippling

Bidirectional sync with Rippling.

**What syncs:**
- Employee data
- Time-off requests
- Documents
- Onboarding workflows

**Setup:**
1. Go to **Settings > Integrations > Payroll**
2. Click "Connect Rippling"
3. Follow the OAuth flow
4. Select sync preferences

## Communication Integrations

### Slack

Get Zen HR notifications in Slack.

**Features:**
- Time-off request notifications
- Approval reminders
- Birthday and anniversary announcements
- New hire announcements

**Setup:**
1. Go to **Settings > Integrations > Communication**
2. Click "Add to Slack"
3. Choose your Slack workspace
4. Select the channel for notifications
5. Configure which notifications to send

**Slash commands:**
- `/zenhr whoami` - View your profile
- `/zenhr pto` - Check your time-off balance
- `/zenhr request-pto [dates]` - Request time off
- `/zenhr directory [name]` - Search employee directory

### Microsoft Teams

Bring Zen HR into Teams.

**Features:**
- Approval notifications in Teams
- Time-off request cards
- Employee directory tab

**Setup:**
1. Go to **Settings > Integrations > Communication**
2. Click "Connect Microsoft Teams"
3. Install the Zen HR app in Teams Admin Center
4. Configure notification channels

## Calendar Integrations

### Google Calendar

Sync time-off to Google Calendar.

**What syncs:**
- Approved time-off as calendar events
- Company holidays
- Team member absences (optional)

**Setup:**
1. Go to **Profile > Integrations**
2. Click "Connect Google Calendar"
3. Authorize access
4. Choose calendars to sync

### Outlook Calendar

Sync with Microsoft Outlook.

**What syncs:**
- Time-off events
- Out-of-office status (automatic)
- Meeting conflicts with time-off

**Setup:**
1. Go to **Profile > Integrations**
2. Click "Connect Outlook"
3. Sign in with Microsoft account
4. Grant calendar permissions

## API Access

Available on Professional and Enterprise plans.

### Getting Started

1. Go to **Settings > API**
2. Click "Generate API Key"
3. Copy your API key (shown only once)
4. Store securely

### Authentication

Include your API key in request headers:

```
Authorization: Bearer YOUR_API_KEY
```

### Rate Limits

| Plan | Rate Limit |
|------|------------|
| Starter | Not available |
| Professional | 1,000 requests/hour |
| Enterprise | 10,000 requests/hour |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time until limit resets (Unix timestamp)

### API Endpoints

**Employees**
- `GET /api/v1/employees` - List all employees
- `GET /api/v1/employees/{id}` - Get employee by ID
- `POST /api/v1/employees` - Create new employee
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Deactivate employee

**Time Off**
- `GET /api/v1/time-off/requests` - List time-off requests
- `POST /api/v1/time-off/requests` - Create time-off request
- `GET /api/v1/time-off/balances/{employee_id}` - Get balances

**Departments**
- `GET /api/v1/departments` - List departments
- `POST /api/v1/departments` - Create department

Full API documentation: docs.zenhr.com/api

### Webhooks

Receive real-time notifications when events occur.

**Available events:**
- `employee.created`
- `employee.updated`
- `employee.deactivated`
- `time_off.requested`
- `time_off.approved`
- `time_off.denied`

**Setup:**
1. Go to **Settings > API > Webhooks**
2. Click "Add Webhook"
3. Enter your endpoint URL
4. Select events to subscribe to
5. Save and test

Webhook payloads include:
- Event type
- Timestamp
- Full resource data
- Signature for verification

## Applicant Tracking Systems

### Greenhouse

Import new hires from Greenhouse.

**What syncs:**
- Candidate becomes employee on start date
- Job title, department, manager
- Offer letter details

**Setup:**
1. Go to **Settings > Integrations > ATS**
2. Click "Connect Greenhouse"
3. Enter your Greenhouse API key
4. Map fields

### Lever

Connect Lever for recruiting-to-onboarding flow.

**Setup:**
1. Go to **Settings > Integrations > ATS**
2. Click "Connect Lever"
3. Authorize via OAuth
4. Configure when to create employees (offer accepted, start date, etc.)

## Identity Providers

See [Accounts > Single Sign-On](accounts.md#single-sign-on-sso) for SSO setup with:
- Google Workspace
- Microsoft Entra ID
- Okta
- OneLogin
- Custom SAML 2.0

## Building Custom Integrations

For integrations not listed here:

1. Use our REST API to build custom connections
2. Set up webhooks for real-time data
3. Use Zapier for no-code integrations

**Zapier:**
- Go to zapier.com
- Search for "Zen HR"
- Create zaps with 3,000+ apps

**Need help?** Contact integrations@zenhr.com for custom integration support.
