"""Anthropic client wrapper.

Uses the async client so it never blocks discord.py's event loop.
- ``ask``    : single non-streaming call -> full answer string (step 3).
- ``stream`` : async generator yielding text deltas as they arrive (step 4).
"""

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from src import config

_client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)


async def ask(question: str) -> str:
    """Send a question to Claude and return the full answer text."""
    message = await _client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        system=config.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    # The response content is a list of blocks; collect the text ones.
    return "".join(block.text for block in message.content if block.type == "text")


async def stream(
    question: str,
    history: list[dict] | None = None,
    usage: dict[str, int] | None = None,
) -> AsyncIterator[str]:
    """Stream Claude's answer, yielding text fragments as they're generated.

    ``history`` (prior {role, content} turns) is prepended for multi-turn
    follow-ups. If ``usage`` is provided, it's populated with ``input_tokens``
    and ``output_tokens`` once the stream completes (for budget accounting).
    """
    messages = list(history or []) + [{"role": "user", "content": question}]
    async with _client.messages.stream(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        system=config.SYSTEM_PROMPT,
        messages=messages,
    ) as response:
        async for text in response.text_stream:
            yield text
        if usage is not None:
            final = await response.get_final_message()
            usage["input_tokens"] = final.usage.input_tokens
            usage["output_tokens"] = final.usage.output_tokens
