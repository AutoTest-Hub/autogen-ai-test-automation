# Architecture Decision Records (ADRs)

## What are ADRs?

Architecture Decision Records capture important architectural decisions along with their context and consequences. They help future developers understand **why** decisions were made, not just **what** was built.

## ADR Template

Each ADR follows this structure:

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this change?
```

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-llm-provider-chain.md) | LLM Provider Chain Architecture | Accepted | 2025-11-29 |
| [ADR-002](./ADR-002-message-protocol.md) | Agent Message Protocol | Accepted | 2025-11-30 |
| [ADR-003](./ADR-003-application-context.md) | Application Context Layer | Proposed | 2025-12-01 |

## Creating New ADRs

1. Copy the template above
2. Use the next available number (ADR-NNN)
3. Use present tense ("We decide..." not "We decided...")
4. Keep it concise but complete
5. Link to relevant code/files

---

*Last Updated: 2025-12-01*
