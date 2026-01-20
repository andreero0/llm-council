# SSE Event Contracts: Stage 2.5 Events

**Feature Branch**: `001-peer-critique-self-correction`  
**Date**: 2026-01-20

---

## Overview

This document defines the Server-Sent Events (SSE) contract for the new Stage 2.5 events. These events integrate into the existing streaming endpoint.

---

## Existing Event Sequence (Reference)

```
stage1_start → stage1_complete → 
stage2_start → stage2_complete → 
stage3_start → stage3_complete → 
title_complete (optional) → 
complete
```

---

## Updated Event Sequence

```
stage1_start → stage1_complete → 
stage2_start → stage2_complete → 
stage2_5_start → stage2_5_complete →  ← NEW
stage3_start → stage3_complete → 
title_complete (optional) → 
complete
```

---

## New Events

### stage2_5_start

Signals that Stage 2.5 (self-correction) processing has begun.

**Event Format**:
```json
{
  "type": "stage2_5_start"
}
```

**Triggered When**: Stage 2 has completed and Stage 2.5 processing begins.

**Frontend Action**: Display loading indicator for Stage 2.5 section.

---

### stage2_5_complete

Signals that Stage 2.5 processing has completed with results.

**Event Format**:
```json
{
  "type": "stage2_5_complete",
  "data": [
    {
      "model": "openai/gpt-4",
      "original_response": "The capital of France is Paris...",
      "peer_critiques": "Peer evaluation from anthropic/claude-3-opus:\n...",
      "corrected_response": "The capital of France is Paris, which has served..."
    },
    {
      "model": "anthropic/claude-3-opus",
      "original_response": "Paris is the capital of France...",
      "peer_critiques": "Peer evaluation from openai/gpt-4:\n...",
      "corrected_response": "Paris is the capital of France and has been since..."
    }
  ]
}
```

**Triggered When**: All Stage 2.5 model queries have completed (or fallen back to Stage 1).

**Frontend Action**: 
- Hide Stage 2.5 loading indicator
- Display Stage 2.5 results with tabbed interface
- Each tab shows original and corrected response

---

## Data Field Specifications

### stage2_5_complete.data[]

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | OpenRouter model identifier |
| `original_response` | string | Yes | Model's Stage 1 response |
| `peer_critiques` | string | Yes | Formatted peer feedback text |
| `corrected_response` | string | Yes | Model's refined response |

---

## Error Handling

### Partial Failure

If some models fail Stage 2.5 but others succeed:
- Failed models use Stage 1 response as `corrected_response`
- `peer_critiques` still populated with available feedback
- Event still fires with mixed results

**Example (one model failed)**:
```json
{
  "type": "stage2_5_complete",
  "data": [
    {
      "model": "openai/gpt-4",
      "original_response": "...",
      "peer_critiques": "...",
      "corrected_response": "..." // Actual corrected response
    },
    {
      "model": "anthropic/claude-3-opus",
      "original_response": "...",
      "peer_critiques": "...",
      "corrected_response": "..." // Falls back to original_response value
    }
  ]
}
```

### Complete Failure

If Stage 2.5 fails entirely:
- Event still fires with fallback data
- All `corrected_response` values equal `original_response`
- Processing continues to Stage 3

---

## Frontend State Machine

```
                    ┌─────────────────┐
                    │  stage2_5: null │
                    │  loading: false │
                    └────────┬────────┘
                             │
                   stage2_5_start
                             │
                             ▼
                    ┌─────────────────┐
                    │  stage2_5: null │
                    │  loading: true  │
                    └────────┬────────┘
                             │
                  stage2_5_complete
                             │
                             ▼
                    ┌─────────────────┐
                    │  stage2_5: data │
                    │  loading: false │
                    └─────────────────┘
```

---

## Integration Notes

1. **Endpoint**: `POST /api/conversations/{id}/message/stream`
2. **Media Type**: `text/event-stream`
3. **Event Prefix**: All events prefixed with `data: ` per SSE spec
4. **Termination**: Stream ends with `complete` event (unchanged)
