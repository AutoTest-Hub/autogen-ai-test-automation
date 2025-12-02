# ADR-001: LLM Provider Chain Architecture

## Status
Accepted

## Date
2025-11-29

## Context

The platform needs LLM capabilities for intelligent test generation, code review, and analysis. However:

1. **Cost**: Cloud LLM APIs (OpenAI, Anthropic) are expensive for high-volume usage
2. **Latency**: Network calls add latency to every agent operation
3. **Privacy**: Some customers may not want test data sent to external APIs
4. **Availability**: External APIs can have outages or rate limits

We need a flexible architecture that can use multiple LLM providers with graceful fallback.

## Decision

We implement a **provider chain** architecture with the following priority:

```
Local AI (Ollama) → OpenAI → Anthropic → Error
```

### Implementation

```python
# In agents/base_agent.py

async def generate_llm_response(self, prompt: str, ...) -> Dict[str, Any]:
    """Generate response using configured LLM provider chain."""

    # 1. Try Local AI first (fastest, cheapest, most private)
    if self.local_ai_provider and self.local_ai_provider.is_available():
        return await self._call_local_ai(prompt, ...)

    # 2. Fall back to OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        return await self._call_openai(prompt, ...)

    # 3. Fall back to Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        return await self._call_anthropic(prompt, ...)

    raise LLMProviderError("No LLM provider available")
```

### Response Caching

To reduce costs and latency, responses are cached with TTL:

```python
self._response_cache: Dict[str, Dict[str, Any]] = {}
self._cache_ttl = 300  # 5 minutes
```

### Retry Logic

Each provider call includes exponential backoff:

```python
for attempt in range(max_retries):
    try:
        return await self._make_api_call(...)
    except RateLimitError:
        await asyncio.sleep(2 ** attempt)
```

## Consequences

### Positive
- **Cost optimization**: Local AI handles most requests at zero marginal cost
- **Privacy**: Sensitive data can stay on-premises with local AI
- **Resilience**: Automatic failover if one provider is unavailable
- **Flexibility**: Easy to add new providers to the chain

### Negative
- **Complexity**: More code to maintain than single-provider
- **Quality variance**: Local models may produce lower quality than GPT-4
- **Configuration**: Users must set up Ollama for best experience

### Mitigations
- Quality-critical tasks (code review) can force cloud providers
- Clear documentation for Ollama setup
- Monitoring to track which providers are being used

## Related Files
- `agents/base_agent.py` - Provider chain implementation
- `models/local_ai_provider.py` - Local AI (Ollama) integration
- `config/settings.py` - LLM configuration

---

*Decision made by: Claude (AI Assistant)*
*Reviewed by: [Pending]*
