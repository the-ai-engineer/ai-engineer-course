# Troubleshooting Guide

Common issues and how to resolve them.

## Login Issues

### "Invalid credentials" Error

**Symptoms:** You enter your email and password but see "Invalid credentials."

**Solutions:**
1. Verify you're using the correct email address (the one you received your invite on)
2. Check for typos in your password
3. Ensure Caps Lock is off
4. Try resetting your password (see below)

### Forgot Password

1. Go to app.zenhr.com/login
2. Click "Forgot password?"
3. Enter your email address
4. Check your inbox for a reset link (also check spam)
5. Click the link and set a new password
6. Password reset links expire after 1 hour

### SSO Login Failed

**Error code: E401**

**Symptoms:** "Authentication failed" when using Google, Microsoft, or other SSO.

**Solutions:**
1. Verify your company has SSO enabled (ask your Admin)
2. Ensure you're using your work email, not a personal account
3. Try logging out of your identity provider and back in
4. Clear your browser cookies for zenhr.com
5. Contact your IT administrator if the issue persists

### Account Locked

**Symptoms:** "Your account has been locked" message.

**Cause:** Too many failed login attempts (5 attempts within 15 minutes).

**Solutions:**
1. Wait 15 minutes for automatic unlock
2. Or contact your Admin to manually unlock your account
3. Or reset your password to unlock immediately

### "Account not found" Error

**Symptoms:** "We couldn't find an account with that email."

**Solutions:**
1. Verify you're using the email that received the invite
2. Check if you have multiple email addresses
3. Contact your Admin to verify your account exists
4. Check if your account was deactivated

## Two-Factor Authentication Issues

### Lost Access to 2FA Device

1. Use one of your backup codes to log in
2. Go to **Profile > Security**
3. Click "Reset 2FA"
4. Set up 2FA with your new device

**No backup codes?** Contact your Admin to reset 2FA for your account.

### 2FA Code Not Working

**Solutions:**
1. Ensure your device's clock is synchronized (2FA is time-based)
2. Wait for the next code (they refresh every 30 seconds)
3. Try a backup code
4. Regenerate the 2FA setup in your authenticator app

## Time-Off Issues

### Time-Off Request Not Submitting

**Symptoms:** Click "Submit" but nothing happens.

**Solutions:**
1. Check all required fields are filled
2. Ensure end date is after start date
3. Verify you have sufficient balance
4. Try a different browser
5. Check for JavaScript errors (open browser console)

### Incorrect Time-Off Balance

**Symptoms:** Your balance doesn't match what you expect.

**Possible causes:**
1. Pending requests reduce available balance
2. Accruals may not have processed yet
3. Policy changes mid-year

**Solutions:**
1. Go to **Time Off > My Balance**
2. Click "View History" to see all transactions
3. Check for pending requests that are holding balance
4. Contact your HR Admin if discrepancies persist

### Can't See Time-Off Request Option

**Symptoms:** The "Request Time Off" button is missing.

**Possible causes:**
1. No time-off policy assigned to you
2. You're in a probationary period
3. Your manager hasn't been set

**Solutions:**
Contact your HR Admin to verify your time-off policy assignment.

## Performance Issues

### Slow Page Load

**Symptoms:** Pages take more than 5 seconds to load.

**Solutions:**
1. Check your internet connection
2. Try a different browser (Chrome recommended)
3. Clear browser cache and cookies
4. Disable browser extensions
5. Check status.zenhr.com for service issues

### Features Not Loading

**Symptoms:** Buttons don't work, forms don't submit, pages are blank.

**Solutions:**
1. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Try incognito/private browsing mode
4. Try a different browser
5. Check if JavaScript is enabled

### Mobile App Issues

**Symptoms:** App crashes, won't load, or shows errors.

**Solutions:**
1. Force close and reopen the app
2. Check for app updates in your app store
3. Ensure you have a stable internet connection
4. Log out and log back in
5. Uninstall and reinstall the app

## Integration Issues

### Payroll Sync Not Working

**Error code: E503**

**Symptoms:** Employee data not syncing with Gusto/ADP/etc.

**Solutions:**
1. Go to **Settings > Integrations**
2. Click "Test Connection" for your payroll provider
3. If test fails, try "Reconnect"
4. Verify your payroll provider credentials haven't expired
5. Check that required fields are mapped

### Slack Notifications Not Arriving

**Solutions:**
1. Verify Slack integration is connected in **Settings > Integrations**
2. Check the notification channel still exists
3. Ensure the Zen HR bot hasn't been removed from the channel
4. Try disconnecting and reconnecting Slack

### Calendar Sync Issues

**Symptoms:** Time-off not appearing in Google/Outlook calendar.

**Solutions:**
1. Go to **Profile > Integrations**
2. Verify calendar is connected
3. Check which calendar is selected for sync
4. Try disconnecting and reconnecting
5. Wait up to 15 minutes for sync to complete

## Data Issues

### Missing Employee Data

**Symptoms:** Employee records are incomplete or missing fields.

**Solutions:**
1. Check if the employee completed their profile
2. Verify data import was successful
3. Check user permissions to view the data
4. Contact your Admin to investigate

### Export Failed

**Error code: E500**

**Symptoms:** "Export failed" when trying to download data.

**Solutions:**
1. Try exporting a smaller date range
2. Try a different export format (CSV vs XLSX)
3. Check your browser's download permissions
4. Try again in a few minutes (may be a temporary issue)

### Report Not Loading

**Symptoms:** Reports show "Error loading data" or spin indefinitely.

**Solutions:**
1. Try a smaller date range
2. Apply fewer filters
3. Try a different report
4. Clear browser cache
5. Check for service issues at status.zenhr.com

## Error Codes Reference

| Code | Meaning | Solution |
|------|---------|----------|
| E400 | Bad request | Check your input data is valid |
| E401 | Authentication failed | Re-login or reset password |
| E403 | Permission denied | Contact Admin for access |
| E404 | Resource not found | Check the URL or resource exists |
| E429 | Rate limit exceeded | Wait 1 hour or upgrade plan |
| E500 | Server error | Try again; contact support if persists |
| E502 | Gateway error | Service temporarily unavailable |
| E503 | Service unavailable | Check status.zenhr.com |

## Browser Compatibility

### Supported Browsers

- Google Chrome (recommended) - latest 2 versions
- Mozilla Firefox - latest 2 versions
- Safari - latest 2 versions
- Microsoft Edge - latest 2 versions

### Not Supported

- Internet Explorer (any version)
- Opera Mini
- Browsers with JavaScript disabled

## Getting More Help

If your issue isn't resolved by this guide:

### Live Chat
Click the chat icon in the bottom right of any Zen HR page. Available Monday-Friday, 9am-6pm ET.

### Email Support
Send details to support@zenhr.com. Include:
- Your email address
- Company name
- Screenshot of any error
- Steps to reproduce the issue

Response times:
- Starter: Within 24 hours
- Professional: Within 4 hours
- Enterprise: Within 1 hour

### Phone Support (Enterprise only)
Call 1-800-ZENHR-01, available 24/7.

### Status Page
Check status.zenhr.com for:
- Current service status
- Planned maintenance
- Incident history
