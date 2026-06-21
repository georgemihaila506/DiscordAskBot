# Architecture Decision Records

Each file records one decision: the context, what was decided, and the
consequences — so the reasoning survives even when the code changes. 0001–0011
were made during the v1 design session; 0012–0014 added the v2 features
(follow-ups + ops bundle). All on 2026-06-21.

| # | Decision |
|---|----------|
| [0001](0001-open-general-qa.md) | Open general Q&A — no RAG |
| [0002](0002-slash-command-only.md) | `/ask` slash command is the only interface |
| [0003](0003-stateless.md) | Stateless / one-shot — no conversation memory |
| [0004](0004-python-stack.md) | Python + discord.py + anthropic SDK |
| [0005](0005-defer-and-stream.md) | Defer, then stream via throttled edits |
| [0006](0006-cost-controls.md) | Cost controls: max_tokens + daily token budget |
| [0007](0007-local-first-no-docker.md) | Local-first env-var config; no Docker in v1 |
| [0008](0008-chunk-long-answers.md) | Auto-split long answers at ~2000 chars |
| [0009](0009-haiku-default-configurable.md) | Haiku 4.5 default, model via env |
| [0010](0010-public-replies.md) | Public (non-ephemeral) replies |
| [0011](0011-inflight-guard.md) | One-in-flight-per-user guard |
| [0012](0012-reply-to-continue-memory.md) | Multi-turn follow-ups via reply-to-continue |
| [0013](0013-persistent-budget.md) | Persist the daily budget across restarts |
| [0014](0014-access-controls.md) | Access controls: guild allowlist + per-user cooldown |
