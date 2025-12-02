# AutoGen AI QA Platform - Documentation

## Overview

This directory contains architecture documentation, design decisions, and implementation guides for the AutoGen AI QA Platform.

## Documentation Structure

```
docs/
├── architecture/           # Detailed design per phase
│   ├── overview.md        # System architecture overview
│   ├── phase-0-*/         # Application Context & Onboarding
│   ├── phase-1-*/         # Core Intelligence (LLM Integration)
│   ├── phase-2-*/         # Agent Collaboration
│   └── phase-3-*/         # Agent Personalities
├── decisions/             # Architecture Decision Records (ADRs)
│   └── ADR-NNN-*.md      # Individual decisions
└── guides/               # How-to guides
    ├── onboarding.md     # Onboarding new applications
    └── developer-setup.md # Development environment
```

## Quick Links

### Architecture
- [System Overview](./architecture/overview.md)
- [Phase 0: Application Context](./architecture/phase-0-application-context/README.md)
- [Phase 1: Core Intelligence](./architecture/phase-1-core-intelligence/README.md)
- [Phase 2: Agent Collaboration](./architecture/phase-2-agent-collaboration/README.md)

### Decisions
- [ADR Index](./decisions/README.md)
- [ADR-001: LLM Provider Chain](./decisions/ADR-001-llm-provider-chain.md)
- [ADR-002: Message Protocol](./decisions/ADR-002-message-protocol.md)
- [ADR-003: Application Context](./decisions/ADR-003-application-context.md)

### Guides
- [Onboarding New Applications](./guides/onboarding.md)
- [Developer Setup](./guides/developer-setup.md)

## Implementation Status

| Phase | Status | Documentation |
|-------|--------|---------------|
| Phase 0: Application Context | 🔴 Not Started | [Design](./architecture/phase-0-application-context/) |
| Phase 1: Core Intelligence | 🟡 88% Complete | [Design](./architecture/phase-1-core-intelligence/) |
| Phase 2: Agent Collaboration | 🟡 96% Complete | [Design](./architecture/phase-2-agent-collaboration/) |
| Phase 3: Agent Personalities | 🔴 Not Started | [Design](./architecture/phase-3-agent-personalities/) |

## Contributing to Documentation

When adding new features or making architectural changes:

1. **Create/Update ADR** - Document the decision in `decisions/ADR-NNN-*.md`
2. **Update Phase Docs** - Add implementation details to the relevant phase folder
3. **Update This Index** - Keep the quick links current

---

*Last Updated: 2025-12-01*
