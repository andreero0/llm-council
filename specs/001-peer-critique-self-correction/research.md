# Research: Peer Critique Self-Correction (Stage 2.5)

**Feature Branch**: `001-peer-critique-self-correction`  
**Date**: 2026-01-20

---

## Technical Context Findings

### 1. Existing Architecture Analysis

**Decision**: Extend existing patterns rather than introduce new architecture.

**Rationale**: 
- Backend uses FastAPI with async/await pattern for parallel model queries
- Frontend uses React with progressive SSE (Server-Sent Events) streaming
- Storage is JSON-based with simple file persistence
- All stages follow the same pattern: parallel query → aggregate results → stream to frontend

**Alternatives Considered**:
- WebSocket-based streaming (rejected: SSE already works well, lower complexity)
- Database storage (rejected: JSON files sufficient for current scale)

---

### 2. Critique Extraction Strategy

**Decision**: Extract full Stage 2 evaluation text with peer attribution labels.

**Rationale** (per CD-001):
- Stage 2 evaluations contain both positive and negative feedback
- Full context helps models understand nuanced criticism
- Attribution prevents confusion about who said what

**Implementation Approach**:
```
For each council model M:
  1. Get M's original Stage 1 response
  2. Collect all Stage 2 evaluations from other models (not M's own evaluation)
  3. Format as:
     "Peer evaluation from [Model A]:
      [Full evaluation text]
      
      Peer evaluation from [Model B]:
      [Full evaluation text]"
  4. Prompt M to correct based on this feedback
```

**Alternatives Considered**:
- Parse and extract only criticism sections (rejected: loses context, parsing unreliable)
- Include self-evaluation (rejected: per spec assumption #4, models shouldn't see their own evaluation)

---

### 3. Stage 2.5 Prompt Design

**Decision**: Use clear, structured prompt that mirrors existing Stage 2/3 patterns.

**Rationale**:
- Consistency with existing prompts improves maintainability
- Clear structure helps models produce focused corrections

**Prompt Template**:
```
You previously answered a question, and your peers have provided feedback on your response.

Original Question: {user_query}

Your Original Answer:
{model_original_response}

Peer Feedback:

{formatted_peer_critiques}

Based on this feedback from your peers, please provide a corrected and improved version of your response. Address the valid criticisms and incorporate any useful suggestions while maintaining the strengths of your original answer.

Corrected Response:
```

**Alternatives Considered**:
- Shorter prompt without original question (rejected: context helps)
- Asking model to explain what it changed (rejected: adds complexity, user can compare)

---

### 4. Chairman Prompt Modification

**Decision**: Chairman receives Stage 2.5 corrected responses + Stage 2 rankings (per CD-003).

**Rationale**:
- Rankings still provide valuable consensus signal
- Corrected responses are higher quality than Stage 1 drafts
- Maintains existing pattern where rankings inform synthesis

**Modified Chairman Context**:
```
STAGE 2.5 - Corrected Responses (after peer review):
{stage2_5_results}

STAGE 2 - Peer Rankings:
{stage2_rankings}
```

---

### 5. Frontend Integration Strategy

**Decision**: Add new Stage2_5.jsx component following existing Stage patterns.

**Rationale**:
- Maintains consistency with Stage1.jsx, Stage2.jsx, Stage3.jsx
- Tabbed interface already proven for multi-model display
- Stacked layout (original above, corrected below) per CD-002

**Component Structure**:
```
Stage2_5.jsx
├── Stage title: "Stage 2.5: Self-Corrections"
├── Description text explaining the stage
├── Tab bar (one tab per model)
└── Tab content:
    ├── "Original Response" section (from Stage 1)
    └── "Corrected Response" section (from Stage 2.5)
```

---

### 6. SSE Event Stream Extension

**Decision**: Add `stage2_5_start` and `stage2_5_complete` events.

**Rationale**:
- Follows existing pattern (stage1_start/complete, stage2_start/complete, etc.)
- Enables progressive loading UI for Stage 2.5
- Minimal changes to existing event handling

**Event Sequence**:
```
stage1_start → stage1_complete →
stage2_start → stage2_complete →
stage2_5_start → stage2_5_complete →  // NEW
stage3_start → stage3_complete →
complete
```

---

### 7. Storage Schema Extension

**Decision**: Add `stage2_5` field to assistant messages.

**Rationale**:
- Follows existing pattern (stage1, stage2, stage3)
- No migration needed—old conversations work without stage2_5
- Simple JSON structure matches existing patterns

**Schema**:
```json
{
  "role": "assistant",
  "stage1": [...],
  "stage2": [...],
  "stage2_5": [
    {
      "model": "openai/gpt-4",
      "original_response": "...",
      "peer_critiques": "...",
      "corrected_response": "..."
    }
  ],
  "stage3": {...}
}
```

---

### 8. Error Handling Strategy

**Decision**: Fall back to Stage 1 response if Stage 2.5 fails for a model.

**Rationale** (per FR-009):
- Graceful degradation maintains system reliability
- Chairman can still synthesize with mixed Stage 1/Stage 2.5 responses
- Follows existing pattern of continuing with successful responses

**Fallback Logic**:
```python
if stage2_5_response is None:
    # Use Stage 1 response as fallback
    corrected_response = stage1_response
    log_warning(f"Model {model} failed Stage 2.5, using Stage 1 fallback")
```

---

## Technology Stack Confirmation

| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Backend | Python + FastAPI | 3.11+ | Existing |
| Frontend | React + Vite | 19.x / 7.x | Existing |
| API Pattern | REST + SSE | N/A | Existing |
| Storage | JSON files | N/A | Existing |
| Markdown | react-markdown | 10.x | Existing |
| Testing | Manual | N/A | No automated tests in codebase |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Stage 2.5 adds latency | Medium | Medium | Parallel processing (same as Stage 1/2) |
| Token limits exceeded | Low | Medium | Truncate critiques if needed |
| Models ignore feedback | Medium | Low | Accept—this is model behavior, not system issue |
| UI becomes cluttered | Low | Medium | Stacked layout keeps it manageable |

---

## Resolved Unknowns

All technical unknowns have been resolved:

1. ✅ Critique extraction method → Full text with attribution
2. ✅ UI layout → Stacked (original above, corrected below)
3. ✅ Chairman input → Stage 2.5 + rankings
4. ✅ Prompt design → Structured template following existing patterns
5. ✅ Event streaming → New stage2_5_start/complete events
6. ✅ Storage schema → Add stage2_5 field to assistant messages
7. ✅ Error handling → Fall back to Stage 1 response
