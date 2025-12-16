# Project Specification Template

Use this format for all course projects. It's designed to be executable by AI agents while remaining clear for humans.

---

```markdown
# Project: [Name]

## Overview

[2-3 sentences: What you're building and why it matters. Get the reader excited.]

## User Stories

- As a user, I can [action] so that [benefit]
- As a user, I can [action] so that [benefit]
- As a user, I can [action] so that [benefit]

## Technical Constraints

- Language: [Python version]
- SDK: [specific libraries with versions if needed]
- Must use: [patterns, tools, or approaches required]
- Must NOT: [boundaries and restrictions]

## Implementation Tasks

1. [ ] [Specific, verifiable task]
2. [ ] [Task that depends on #1]
3. [ ] [Another task]
4. [P] [Task that can be parallelized]

Use `[P]` to mark tasks that can be done in parallel.

## Verification

Run command:
\`\`\`bash
[exact command to run the project]
\`\`\`

Test queries/inputs:
- [Specific test case 1]
- [Specific test case 2]
- [Edge case to verify]

Expected behavior:
- [What success looks like]
- [Specific output or behavior to verify]

## Out of Scope

- [Feature explicitly NOT included]
- [Complexity to avoid]
- [Future enhancement, not for now]

## Your Task

Build it yourself using what you learned in this module. Reference the code examples from earlier lessons.

When ready, check out the solution: [link to solution]
```

---

## Why This Format

**User Stories** frame capabilities from the user's perspective. They make acceptance criteria testable: "Can the user do X?" is a yes/no question.

**Technical Constraints** prevent ambiguity. AI agents need explicit boundaries or they'll make assumptions.

**Implementation Tasks** provide a checklist. Ordered tasks show dependencies. `[P]` marks parallelizable work.

**Verification** makes success concrete. Exact commands, specific test cases, expected outputs.

**Out of Scope** prevents scope creep. Explicitly stating what NOT to build is as important as stating what to build.

## Tips

- Keep user stories to 3-5. More than that and the project is too big.
- Tasks should be small enough to verify independently.
- Include at least one edge case in verification.
- Be specific about versions and tools. "Use Python" is vague. "Python 3.11+" is clear.
