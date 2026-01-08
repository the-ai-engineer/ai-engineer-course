"""
Prompt Patterns

Core patterns: extraction, classification, few-shot, and delimiters.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# =============================================================================
# Extraction (Unstructured to Structured)
# =============================================================================

email_text = """
Hi there,

Thanks for reaching out! My name is Sarah Chen and I'm the product manager
at TechCorp. You can reach me at sarah.chen@techcorp.com or call my office
at (555) 123-4567.

Best,
Sarah
"""

response = client.responses.create(
    model="gpt-5-mini",
    input=f"""Extract contact information from this email.

<email>
{email_text}
</email>

Return in this format:
Name: [name]
Email: [email]
Phone: [phone]
Company: [company]""",
)

response.output_text

# =============================================================================
# Classification with Few-Shot
# =============================================================================

# Few-shot produces more consistent results than zero-shot.
# Output prefixes (Sentiment:) signal the expected format.

few_shot_prompt = """Classify the sentiment of product reviews.

Review: "Fast shipping and the product works great!"
Sentiment: POSITIVE

Review: "Stopped working after a week. Very disappointed."
Sentiment: NEGATIVE

Review: "It's fine. Nothing special but does the job."
Sentiment: NEUTRAL

Review: "{review}"
Sentiment:"""

review = "This product is amazing! Best purchase I've ever made."

response = client.responses.create(
    model="gpt-5-mini",
    input=few_shot_prompt.format(review=review),
)

response.output_text

# =============================================================================
# Using Delimiters
# =============================================================================

article = """
Apple announced its Q4 2024 earnings yesterday, reporting revenue of $94.9
billion, up 6% year over year. CEO Tim Cook highlighted strong growth in
emerging markets, particularly India where sales grew 30%.
"""

response = client.responses.create(
    model="gpt-5-mini",
    input=f"""Summarize the following article.

<article>
{article}
</article>

<instructions>
- One sentence only
- Include the key number
</instructions>""",
)

response.output_text
