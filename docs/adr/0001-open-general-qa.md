# 0001 — Open general Q&A (no RAG)

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

The bot needs to "answer questions." That hides a fork: answer from the model's
own knowledge, or answer grounded in a supplied knowledge base (RAG) with
ingestion, embeddings, and retrieval.

## Decision

Answer from Claude's own knowledge — a straight pass-through: message in →
Claude → message out. No data ingestion, vector store, or retrieval.

## Consequences

- Ships fastest; the smallest possible moving-parts surface.
- Answers are general-purpose, not authoritative about any private corpus, and
  not citable.
- Adding RAG later is a clean, separate increment (a retrieval step before the
  Claude call) — nothing here blocks it.
