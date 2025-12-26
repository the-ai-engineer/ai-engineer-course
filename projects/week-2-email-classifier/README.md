# Email Triage

Classify emails and apply labels using a conditional AI workflow.

## Quick Start

```bash
cd projects/week-2-email-classifier
uv sync

# Run with sample emails (no setup needed)
uv run python pipeline.py

# Run with real Gmail
uv run python pipeline.py --gmail --dry-run  # Preview without changes
uv run python pipeline.py --gmail            # Apply labels for real
```

## What It Does

- Triages emails into two categories: respond or skip
- Drafts responses for emails that need them
- Only processes unread emails (won't reprocess the same email twice)
- Marks emails as read after processing
- Applies "Needs Response" label to emails that need a reply
- Use `--dry-run` to preview without modifying your inbox

## Gmail Setup (Optional)

**1. Create a Google Cloud project**
- Go to https://console.cloud.google.com
- Click the project dropdown → "New Project"
- Name it "Email Triage" (or anything you like)

**2. Enable Gmail API**
- Go to "APIs & Services" → "Library"
- Search for "Gmail API" → Click it → "Enable"

**3. Configure OAuth consent screen**
- Go to "APIs & Services" → "OAuth consent screen"
- User type: External → Create
- App name: "Email Triage"
- User support email: your email
- Developer contact: your email
- Save and continue through the scopes (no changes needed)
- Add your email as a test user
- Save

**4. Create credentials**
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth client ID"
- Application type: "Desktop app"
- Name: "Email Triage CLI"
- Click "Create"

**5. Download and configure**
- Click the download icon next to your new credential
- Save as `credentials.json` in this folder
- Copy `.env-sample` to `.env` and add your OpenAI API key

**6. Run**
```bash
uv run python pipeline.py --gmail --dry-run
```

First run opens a browser for Gmail authorization. After that, a `token.json` is saved so you won't need to re-authorize.

## Files

- `pipeline.py` - Triage logic, drafting, and CLI
- `gmail.py` - Gmail API authentication, fetching, and labeling
