# 0007 — Local-first, env-var config; no Docker in v1

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

The bot needs to run somewhere and handle secrets (Discord token, Anthropic key).
Options ranged from running locally to deploying on an always-on host, and
whether to containerize with Docker now or later.

## Decision

Run locally on the author's machine for v1, with all configuration via
environment variables loaded from a gitignored `.env` (`python-dotenv`). Keep the
config deploy-ready (no hardcoded paths) so moving to a host later needs no code
change. **Do not** add Docker in v1.

## Consequences

- Zero hosting cost; simplest possible start. The bot is offline when the machine
  is off — fine for personal use.
- Secrets stay out of git (`.env` is ignored); `.env.example` documents them.
- **On Docker:** not worth it for a single long-running process with no database.
  Add a `Dockerfile` only at the cloud-deploy increment, where it pays off (most
  hosts — Railway, Fly.io, a VPS — take a Dockerfile directly). Contrast a
  database-centric project, where Docker shines for spinning up a throwaway DB;
  this bot has no such need.
