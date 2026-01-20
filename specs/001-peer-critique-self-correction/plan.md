# Implementation Plan: Peer Critique Self-Correction (Stage 2.5)

**Branch**: `001-peer-critique-self-correction` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-peer-critique-self-correction/spec.md`

---

## Summary

Add a new **Stage 2.5** to the LLM Council pipeline where each model receives its original answer plus peer critiques, then produces a corrected response. The Chairman (Stage 3) uses these improved responses instead of Stage 1 drafts. Implementation extends existing patterns: parallel async queries, SSE streaming, JSON storage, and React tabbed UI.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript/React 19.x (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, asyncio (backend); React, Vite 7.x, react-markdown (frontend)  
**Storage**: JSON files in `data/conversations/`  
**Testing**: Manual testing (no automated test framework in codebase)  
**Target Platform**: Web application (localhost development)  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: Stage 2.5 completes within 30 seconds (parallel model queries)  
**Constraints**: Must maintain SSE streaming pattern, backward compatible with existing conversations  
**Scale/Scope**: Single-user development tool, 3-5 council models

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (No constitution violations)

The project constitution (`constitution.md`) contains placeholder template content only. No specific architectural constraints or gates are defined. The implementation follows existing codebase patterns:

- ✅ Extends existing module structure (no new architectural patterns)
- ✅ Uses established async/parallel query pattern
- ✅ Follows existing SSE streaming contract
- ✅ Maintains backward compatibility with storage schema
- ✅ Reuses existing UI component patterns

---

## Project Structure

### Documentation (this feature)

```text
specs/001-peer-critique-self-correction/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/           # Phase 1 output (complete)
│   ├── sse-events.md    # SSE event contracts
│   └── storage-schema.md # Storage schema extension
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── __init__.py
├── config.py           # Council/Chairman model configuration
├── council.py          # MODIFY: Add stage2_5_collect_corrections()
├── main.py             # MODIFY: Add SSE events, update streaming endpoint
├── openrouter.py       # OpenRouter API client (no changes)
└── storage.py          # MODIFY: Add stage2_5 to add_assistant_message()

frontend/
├── src/
│   ├── api.js          # API client (no changes needed)
│   ├── App.jsx         # MODIFY: Add stage2_5 event handlers
│   ├── App.css
│   ├── components/
│   │   ├── ChatInterface.jsx  # MODIFY: Render Stage2_5 component
│   │   ├── ChatInterface.css
│   │   ├── Stage1.jsx
│   │   ├── Stage1.css
│   │   ├── Stage2.jsx
│   │   ├── Stage2.css
│   │   ├── Stage2_5.jsx       # NEW: Stage 2.5 UI component
│   │   ├── Stage2_5.css       # NEW: Stage 2.5 styles
│   │   ├── Stage3.jsx
│   │   └── Stage3.css
│   └── ...
└── ...

data/
└── conversations/      # JSON storage (schema extended)
```

**Structure Decision**: Web application structure (Option 2) - matches existing codebase layout with separate `backend/` and `frontend/` directories.

---

## Complexity Tracking

> No constitution violations to justify. Implementation follows existing patterns with minimal complexity.

| Aspect | Approach | Rationale |
|--------|----------|-----------|
| New stage | Follows Stage 1/2/3 pattern | Consistency, maintainability |
| Parallel queries | Reuses `query_models_parallel` | Proven pattern, minimizes latency |
| SSE events | Extends existing event stream | No new infrastructure needed |
| Storage | Adds optional field | Backward compatible |
| UI component | Mirrors Stage1/Stage2 components | Consistent UX |

---

## Phase 0 Artifacts

- ✅ `research.md` - Technical decisions documented
- ✅ All unknowns resolved (critique extraction, UI layout, Chairman input)

## Phase 1 Artifacts

- ✅ `data-model.md` - Stage2_5Result entity defined
- ✅ `contracts/sse-events.md` - New SSE events specified
- ✅ `contracts/storage-schema.md` - Storage schema extension
- ✅ `quickstart.md` - Implementation guide

---

## Next Steps

Run `/speckit.tasks` to generate the implementation task list in `tasks.md`.
