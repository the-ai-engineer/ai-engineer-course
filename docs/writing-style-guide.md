# Writing Style Guide

This guide defines how we write lessons for the course.

## Voice

Write like you're explaining something to a smart friend. Not a textbook. Not a tutorial. A conversation with someone who's capable and wants to get things done.

**Do this:**
> Agents are just loops. The model picks a tool, you run it, feed the result back, repeat until done. That's it.

**Not this:**
> It's important to understand that agents are fundamentally based on an iterative loop pattern. The model determines which tool to invoke, the system executes the tool, and the result is provided back to the model for further processing.

## Principles

### 1. Short paragraphs
One idea per paragraph. Two to three sentences max. White space is your friend.

### 2. Show first, explain second
Don't spend three paragraphs explaining what something is before showing it. Show the code, then explain the interesting parts.

### 3. No hedging
Say what to do. Don't say "you might want to consider" or "it can be useful to think about."

**Do:** "Use streaming for chat interfaces."
**Don't:** "You might want to consider using streaming when building chat interfaces."

### 4. Assume competence
Readers are developers. They know what a function is. They know what JSON is. Don't explain things they already know.

### 5. Be direct about what matters
Not everything is equally important. Say what matters most. Skip the completeness for the sake of being complete.

### 6. Personal voice is fine
"I've found that..." or "This is the part that trips people up" is good. It's a course, not documentation.

### 7. Casual asides work
"Hand this off and go get coffee" or "You're going to debug this a lot" keeps it human.

### 8. Clear, not clever
Use the simplest word that works. Don't impress. Communicate.

| Instead of | Write |
|------------|-------|
| utilize | use |
| leverage | use |
| facilitate | help |
| implement | build |
| functionality | feature |
| in order to | to |
| due to the fact that | because |
| at this point in time | now |
| a large number of | many |
| enables you to | lets you |

### 9. Speak like you're teaching
You're not writing documentation. You're teaching someone. There's a person on the other side trying to learn this. Talk to them.

### 10. One concept at a time
Don't explain three things in one paragraph. Finish one idea before starting the next. If you're stringing concepts together with commas, break them apart.

## Structure

Each lesson should flow naturally, but roughly:

```
# Lesson Title

[2-3 sentence opener - what this is, why you care]

## The Core Idea
[Brief explanation, short paragraphs]

## In Practice
[Code with explanation woven in, not before]

## What Matters
[Key patterns or principles, often numbered]

## Watch Out
[2-3 things that bite people, with fixes inline]

## Go Deeper (optional)
[Links for those who want more]
```

Don't force every lesson into this exact structure. Let the content guide it.

## Formatting

- **Headings:** Use sparingly. H2 for major sections only.
- **Lists:** Keep items short. Not paragraphs disguised as bullets.
- **Code blocks:** Show real code that runs. Keep them focused.
- **Bold:** For key terms on first use. Don't overdo it.
- **Diagrams:** Mermaid when it actually clarifies. Skip when it doesn't add value.

## What to Avoid

- Em dashes (—). Use periods, commas, or rewrite the sentence.
- "It's important to note that..."
- "Let's take a moment to understand..."
- "In this section, we will explore..."
- Long introductions before getting to the point
- Explaining things twice
- Comprehensive coverage of every edge case
- Separate "Common Mistakes" sections (weave them in naturally)
- Academic tone

## Examples

### Good opener
> The Gemini SDK is how you talk to Google's models. One package, a few lines of code, and you're generating text. Let's get it running.

### Bad opener
> In this lesson, we will explore the fundamentals of the Gemini SDK. The SDK provides a comprehensive interface for interacting with Google's large language models. Understanding these fundamentals is essential for building AI applications.

### Good explanation
> Streaming sends text to the user as it's generated instead of waiting for the whole response. For chat interfaces, this is the difference between feeling instant and feeling broken.

### Bad explanation
> Streaming is a technique whereby the response from the language model is transmitted to the client incrementally as tokens are generated, rather than waiting for the complete response to be generated before transmission. This approach has significant implications for user experience, particularly in conversational interfaces.

### Good code section
> Here's the simplest call:
> ```python
> response = client.models.generate_content(
>     model="gemini-2.0-flash",
>     contents="Explain APIs in one sentence."
> )
> print(response.text)
> ```
> That's it. Three lines after setup.

### Bad code section
> Before we look at the code, it's important to understand the structure of an API call. The call requires a model identifier, which specifies which model to use, and contents, which contains the prompt. Let's examine a basic example:
> [code block]
> As you can see in the above example, we first specify the model...

## The Test

Before publishing, read your lesson out loud. If it sounds like a textbook, rewrite it. If it sounds like you're explaining something to a colleague, ship it.
