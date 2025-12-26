"""
Gmail API Integration

Connect to Gmail, authenticate, and fetch emails.
"""

import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scopes - need modify to add labels
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    """
    Authenticate with Gmail API and return the service object.

    First run will open a browser for OAuth consent.
    Subsequent runs use the saved token.
    """
    creds = None

    # Check for existing token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json not found. "
                    "Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_emails(service, max_results: int = 10, unread_only: bool = True) -> list[dict]:
    """
    Fetch recent emails from the inbox.

    Args:
        service: Gmail API service object
        max_results: Maximum number of emails to fetch
        unread_only: Only fetch unread emails (for incremental processing)

    Returns:
        List of email dictionaries with id, subject, sender, snippet, body
    """
    # Only fetch unread emails to avoid reprocessing
    label_ids = ["INBOX"]
    if unread_only:
        label_ids.append("UNREAD")

    # Get list of messages
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=label_ids, maxResults=max_results)
        .execute()
    )

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        # Get full message details
        message = (
            service.users().messages().get(userId="me", id=msg["id"]).execute()
        )

        # Extract headers
        headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

        # Get body text
        body = extract_body(message["payload"])

        emails.append(
            {
                "id": msg["id"],
                "subject": headers.get("Subject", "(No Subject)"),
                "sender": headers.get("From", "Unknown"),
                "snippet": message.get("snippet", ""),
                "body": body[:2000],  # Truncate for LLM context
            }
        )

    return emails


def extract_body(payload: dict) -> str:
    """Extract plain text body from email payload."""
    body = ""

    if "body" in payload and payload["body"].get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    elif "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and part["body"].get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
            elif "parts" in part:
                body = extract_body(part)
                if body:
                    break

    return body


# =============================================================================
# Labels
# =============================================================================


def get_or_create_label(service, label_name: str) -> str:
    """
    Get a label by name, or create it if it doesn't exist.

    Returns the label ID.
    """
    # Check if label already exists
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    for label in labels:
        if label["name"] == label_name:
            return label["id"]

    # Create the label
    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    created = service.users().labels().create(userId="me", body=label_body).execute()
    print(f"Created label: {label_name}")
    return created["id"]


def apply_label(service, message_id: str, label_id: str):
    """Apply a label to an email message."""
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def mark_as_read(service, message_id: str):
    """Mark an email as read by removing the UNREAD label."""
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def get_or_create_needs_response_label(service) -> str:
    """Create the 'Needs Response' label if it doesn't exist."""
    return get_or_create_label(service, "Needs Response")


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    service = get_gmail_service()
    emails = fetch_emails(service, max_results=5)

    for email in emails:
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Snippet: {email['snippet'][:100]}...")
        print("-" * 40)
