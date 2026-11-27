# Project Agent Rules (Fictional-Bands)

> Inherits the global NEXUS L1–L6 Constitution from [`nexus-swarm-core/AGENTS.base.md`](https://github.com/jezehelfranca-svg/nexus-swarm-core/blob/main/AGENTS.base.md).
> Global Plugin / Skills: `nexus-swarm-core` (`multi-model-advisor`, `nexus-sob-gate`, `nexus-attach`).
> Core Swarm Rule: *"Swarm only work that splits into non-colliding lanes, and let a separate verifier check every claim."*

## Default NEXUS Activation Tier
- **Default Tier:** `Tier 1` (override any task explicitly with `[Tier 1]`, `[Tier 2]`, or `[Tier 3]`).
- **Tier 1 (Routine Fixes):** Native Antigravity `/swarm` (Gemini 4 Neon + Hydrogen + Carbon) — 0 external MCP quota burn.
- **Tier 2 (New Features / Schema Changes):** Pre-split `claude-advisor` (`claude_advise`, Sage/Judge) + `@verifier` with `codex-worker` (`sandbox: "read-only"`, Guardian).
- **Tier 3 (New Projects / Major Architecture):** Full 4-archetype SOB deliberation + GATO Alignment Scorecard via `nexus-sob-gate` before L4 lane decomposition.

## Suggested Non-Colliding RBAC Worker Lanes
*(Auto-detected from top-level structure in `Fictional-Bands` — refine paths and verification commands as needed.)*

| Lane | Owned Paths (RBAC) | Verification Command |
| :--- | :--- | :--- |
| `#1` Band Catalog / Assets | `*` (scoped per band folder/file) | Verify band metadata & links |
| `#2` Documentation / Workflows | `README.md`, `.github/**` | Validate markdown & workflow syntax |

## Project-Specific Guardrails
- Workers **MUST NOT** edit files outside their assigned RBAC lane. Escalate cross-lane dependencies via `[question]` to `@coordinator`.
- Use isolated `git worktree` copies whenever parallel edits risk overlapping builds or shared configs.
- External MCP servers (`claude-advisor`, `codex-worker`) stay idle unless triggered by Tier 2/3 or explicit user request. On rate-limit or `Killed` state, pause immediately and fall back to native Gemini 4 tiers (no retry loops).
