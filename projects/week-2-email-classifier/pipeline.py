"""
Email Classifier

Fetch emails from Gmail and classify them using structured output.
Demonstrates: structured output, working with APIs, simple workflows.
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


# =============================================================================
# Classification Schema
# =============================================================================


class EmailClassification(BaseModel):
    """Structured output for email classification."""

    category: str  # support, sales, spam, newsletter, personal
    confidence: str  # high, medium, low
    reason: str  # Brief explanation


# =============================================================================
# Sample Emails (for testing without Gmail)
# =============================================================================

SAMPLE_EMAILS = [
    {
        "id": "1",
        "subject": "Can't login to my account",
        "sender": "frustrated.user@gmail.com",
        "body": "Hi, I've been trying to login for the past hour but keep getting an error. Can someone help?",
    },
    {
        "id": "2",
        "subject": "Enterprise pricing inquiry",
        "sender": "cto@bigcorp.com",
        "body": "We're evaluating your platform for our team of 500. What are your enterprise options?",
    },
    {
        "id": "3",
        "subject": "You've won a FREE iPhone!!!",
        "sender": "deals@totallylegit.xyz",
        "body": "CONGRATULATIONS! Click here to claim your prize. Limited time offer!!!",
    },
    {
        "id": "4",
        "subject": "Weekly Tech Digest",
        "sender": "newsletter@techblog.com",
        "body": "This week in tech: AI updates, new frameworks, and industry news...",
    },
    {
        "id": "5",
        "subject": "Lunch tomorrow?",
        "sender": "friend@gmail.com",
        "body": "Hey! Want to grab lunch tomorrow? There's a new place I want to try.",
    },
]


# =============================================================================
# Classification
# =============================================================================


def classify_email(email: dict) -> EmailClassification:
    """Classify an email using structured output."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""Classify this email.

Categories:
- support: Customer needs help with a problem
- sales: Business inquiry or sales opportunity
- spam: Unsolicited, suspicious, or promotional junk
- newsletter: Regular updates, digests, subscriptions
- personal: From someone you know, not business-related

From: {email['sender']}
Subject: {email['subject']}

{email['body'][:500]}""",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EmailClassification,
        ),
    )

    return EmailClassification.model_validate_json(response.text)


# =============================================================================
# Pipeline
# =============================================================================


def process_emails(emails: list[dict]) -> list[dict]:
    """Process a list of emails and return classifications."""
    results = []

    for email in emails:
        print(f"Classifying: {email['subject'][:40]}...")
        classification = classify_email(email)

        results.append({
            "id": email["id"],
            "subject": email["subject"],
            "sender": email["sender"],
            "category": classification.category,
            "confidence": classification.confidence,
            "reason": classification.reason,
        })

        print(f"  -> {classification.category} ({classification.confidence})")

    return results


def print_results(results: list[dict]):
    """Print classification results."""
    print("\n" + "=" * 60)
    print("CLASSIFICATION RESULTS")
    print("=" * 60)

    # Group by category
    by_category = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)

    for category, emails in sorted(by_category.items()):
        print(f"\n{category.upper()} ({len(emails)})")
        print("-" * 40)
        for email in emails:
            print(f"  {email['subject'][:50]}")
            print(f"    From: {email['sender']}")
            print(f"    Reason: {email['reason']}")


# =============================================================================
# Gmail Integration (Optional)
# =============================================================================


def run_with_gmail(max_emails: int = 10):
    """Run classifier on real Gmail emails."""
    from gmail import get_gmail_service, fetch_emails

    print("Connecting to Gmail...")
    service = get_gmail_service()
    emails = fetch_emails(service, max_results=max_emails)
    print(f"Fetched {len(emails)} emails\n")

    results = process_emails(emails)
    print_results(results)

    return results


def run_with_samples():
    """Run classifier on sample emails (no Gmail needed)."""
    print("Using sample emails\n")
    results = process_emails(SAMPLE_EMAILS)
    print_results(results)

    return results


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":
    import sys

    if "--gmail" in sys.argv:
        run_with_gmail()
    else:
        run_with_samples()
