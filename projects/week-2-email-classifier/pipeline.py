"""
Email Triage

Classify emails and take different actions based on category.
Demonstrates: conditional workflows, structured output.

Usage:
    uv run python pipeline.py                       # Run with sample emails
    uv run python pipeline.py --gmail --dry-run     # Preview Gmail triage
    uv run python pipeline.py --gmail               # Apply labels for real
    uv run python pipeline.py --gmail --limit 5     # Process only 5 emails
"""

import argparse
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Models
# =============================================================================


class TriageResult(BaseModel):
    category: str  # respond, skip
    reason: str


class ProcessedEmail(BaseModel):
    subject: str
    sender: str
    category: str
    reason: str
    draft: str | None = None


# =============================================================================
# Sample Emails
# =============================================================================

SAMPLE_EMAILS = [
    {
        "id": "1",
        "subject": "Meeting follow-up from Sarah",
        "sender": "sarah@company.com",
        "body": "Hi! Thanks for the meeting today. Could you send me the slides you mentioned? Also, are you free next Tuesday for a follow-up?",
    },
    {
        "id": "2",
        "subject": "Q3 Board Report",
        "sender": "cfo@company.com",
        "body": "Please find attached the Q3 financial report. Key highlights: 15% revenue growth, new enterprise clients, and expanded APAC presence. Full details in the PDF.",
    },
    {
        "id": "3",
        "subject": "Your weekly digest from Medium",
        "sender": "noreply@medium.com",
        "body": "Top stories this week: How AI is changing everything, 10 productivity hacks, and more...",
    },
    {
        "id": "4",
        "subject": "50% off sale ends today!",
        "sender": "deals@store.com",
        "body": "Don't miss out! Our biggest sale of the year ends at midnight. Use code SAVE50 at checkout.",
    },
    {
        "id": "5",
        "subject": "Your Uber receipt",
        "sender": "noreply@uber.com",
        "body": "Thanks for riding with Uber. Your trip cost $23.50. View full receipt online.",
    },
    {
        "id": "6",
        "subject": "Quick question about the API",
        "sender": "dev@client.com",
        "body": "Hey, we're integrating your API and hit a snag. Getting 403 errors on the /users endpoint. Any idea what might be wrong? Happy to jump on a call if easier.",
    },
    {
        "id": "7",
        "subject": "AI clone for your YouTube channel",
        "sender": "mark@socialbrew.studio",
        "body": "Owain, saw your AI-focused YouTube channel around software engineers. We can create an AI clone of yourself that's identical in look and voice, so you don't need to record yourself anymore. Want me to send a few AI-made videos? Think you could spot the difference?",
    },
]


# =============================================================================
# Triage
# =============================================================================


def triage_email(email: dict) -> TriageResult:
    """Classify email into respond/skip."""
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": """Triage this email into exactly one category:

- respond: Someone asking a question, making a request, or presenting an opportunity that deserves a reply (even if just to decline politely)
- skip: Newsletters, automated emails, receipts, or low-quality outreach that doesn't warrant a response""",
            },
            {
                "role": "user",
                "content": f"""From: {email['sender']}
Subject: {email['subject']}

{email['body'][:500]}""",
            },
        ],
        text_format=TriageResult,
        temperature=0.0,
    )
    return response.output_parsed


# =============================================================================
# Response Drafting
# =============================================================================


def draft_response(email: dict) -> str:
    """Draft a response for emails that need a reply."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""Draft a brief, professional response to this email.

From: {email['sender']}
Subject: {email['subject']}

{email['body']}""",
    )
    return response.output_text


# =============================================================================
# Workflow
# =============================================================================


def process_email(email: dict) -> ProcessedEmail:
    """Process a single email through the triage workflow."""
    print(f"Processing: {email['subject'][:40]}...")

    # Step 1: Triage
    triage = triage_email(email)
    print(f"  -> {triage.category}")

    # Step 2: Draft response if needed
    draft = None
    if triage.category == "respond":
        print("  -> Drafting response...")
        draft = draft_response(email)

    print()
    return ProcessedEmail(
        subject=email["subject"],
        sender=email["sender"],
        category=triage.category,
        reason=triage.reason,
        draft=draft,
    )


def process_batch(emails: list[dict]) -> list[ProcessedEmail]:
    """Process a batch of emails."""
    return [process_email(email) for email in emails]


# =============================================================================
# Output
# =============================================================================


def print_results(results: list[ProcessedEmail]):
    """Print triage results grouped by category."""
    print("=" * 60)
    print("TRIAGE RESULTS")
    print("=" * 60)

    respond = [r for r in results if r.category == "respond"]
    skip = [r for r in results if r.category == "skip"]

    if respond:
        print(f"\nRESPOND ({len(respond)})")
        print("-" * 40)
        for email in respond:
            print(f"  {email.subject}")
            print(f"    From: {email.sender}")
            print(f"    Why: {email.reason}")
            if email.draft:
                preview = email.draft[:100].replace("\n", " ")
                print(f"    Draft: {preview}...")
            print()

    if skip:
        print(f"\nSKIP ({len(skip)})")
        print("-" * 40)
        for email in skip:
            print(f"  {email.subject}")
            print(f"    Why: {email.reason}")


# =============================================================================
# Gmail Integration
# =============================================================================


def run_with_gmail(dry_run: bool = False, limit: int = 10):
    """
    Run the triage pipeline with real Gmail emails.

    - Only processes unread emails
    - Marks emails as read after processing
    - Applies "Needs Response" label to emails that need a reply
    """
    from gmail import (
        get_gmail_service,
        fetch_emails,
        get_or_create_needs_response_label,
        apply_label,
        mark_as_read,
    )

    print("Connecting to Gmail...")
    service = get_gmail_service()

    # Set up the label
    print("Setting up labels...")
    needs_response_label_id = get_or_create_needs_response_label(service)

    # Fetch unread emails only
    print(f"Fetching up to {limit} unread emails...")
    emails = fetch_emails(service, max_results=limit, unread_only=True)
    print(f"Found {len(emails)} unread emails\n")

    if not emails:
        print("No unread emails to triage.")
        return

    # Process each email
    results = []
    for email in emails:
        result = process_email(email)
        results.append(result)

        if dry_run:
            if result.category == "respond":
                print(f"  -> [DRY RUN] Would apply 'Needs Response' label")
            print(f"  -> [DRY RUN] Would mark as read")
        else:
            # Apply label for emails needing response
            if result.category == "respond":
                apply_label(service, email["id"], needs_response_label_id)
                print(f"  -> Applied 'Needs Response' label")
            # Mark as read so we don't process again
            mark_as_read(service, email["id"])

    print_results(results)


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Email triage pipeline")
    parser.add_argument(
        "--gmail",
        action="store_true",
        help="Use real Gmail emails instead of samples",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of emails to process (default: 10)",
    )
    args = parser.parse_args()

    if args.gmail:
        run_with_gmail(dry_run=args.dry_run, limit=args.limit)
    else:
        # Run with sample emails (always a dry run)
        print("Running with sample emails...\n")
        results = process_batch(SAMPLE_EMAILS)
        print_results(results)


if __name__ == "__main__":
    main()
