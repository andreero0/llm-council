# Storage Schema Contract: Stage 2.5 Extension

**Feature Branch**: `001-peer-critique-self-correction`  
**Date**: 2026-01-20

---

## Overview

This document defines the storage schema changes for persisting Stage 2.5 results in conversation JSON files.

---

## File Location

```
data/conversations/{conversation_id}.json
```

---

## Schema Changes

### Before (Current Schema)

```json
{
  "id": "uuid",
  "created_at": "ISO8601",
  "title": "string",
  "messages": [
    {
      "role": "user",
      "content": "string"
    },
    {
      "role": "assistant",
      "stage1": [...],
      "stage2": [...],
      "stage3": {...}
    }
  ]
}
```

### After (Extended Schema)

```json
{
  "id": "uuid",
  "created_at": "ISO8601",
  "title": "string",
  "messages": [
    {
      "role": "user",
      "content": "string"
    },
    {
      "role": "assistant",
      "stage1": [...],
      "stage2": [...],
      "stage2_5": [...],  // ← NEW FIELD
      "stage3": {...}
    }
  ]
}
```

---

## Stage 2.5 Field Specification

### Assistant Message Extension

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `stage2_5` | array | No | `undefined` | Array of Stage2_5Result objects |

**Note**: Field is optional for backward compatibility with existing conversations.

### Stage2_5Result Object

```json
{
  "model": "string",
  "original_response": "string",
  "peer_critiques": "string",
  "corrected_response": "string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | OpenRouter model identifier |
| `original_response` | string | Yes | Model's Stage 1 response (copied) |
| `peer_critiques` | string | Yes | Formatted peer feedback text |
| `corrected_response` | string | Yes | Model's refined response |

---

## Complete Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-20T10:30:00.000Z",
  "title": "Capital of France",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    },
    {
      "role": "assistant",
      "stage1": [
        {
          "model": "openai/gpt-4",
          "response": "The capital of France is Paris."
        },
        {
          "model": "anthropic/claude-3-opus",
          "response": "Paris is the capital of France."
        },
        {
          "model": "google/gemini-pro",
          "response": "France's capital is Paris."
        }
      ],
      "stage2": [
        {
          "model": "openai/gpt-4",
          "ranking": "All responses correctly identify Paris...\n\nFINAL RANKING:\n1. Response B\n2. Response A\n3. Response C",
          "parsed_ranking": ["Response B", "Response A", "Response C"]
        },
        {
          "model": "anthropic/claude-3-opus",
          "ranking": "Each response provides the correct answer...\n\nFINAL RANKING:\n1. Response A\n2. Response B\n3. Response C",
          "parsed_ranking": ["Response A", "Response B", "Response C"]
        },
        {
          "model": "google/gemini-pro",
          "ranking": "The responses are all accurate...\n\nFINAL RANKING:\n1. Response B\n2. Response A\n3. Response C",
          "parsed_ranking": ["Response B", "Response A", "Response C"]
        }
      ],
      "stage2_5": [
        {
          "model": "openai/gpt-4",
          "original_response": "The capital of France is Paris.",
          "peer_critiques": "Peer evaluation from anthropic/claude-3-opus:\nThe response is correct but could benefit from additional context...\n\nPeer evaluation from google/gemini-pro:\nAccurate but brief...",
          "corrected_response": "The capital of France is Paris, which has served as the nation's capital since 987 CE. Paris is not only the political center but also the cultural and economic heart of France, with a population of over 2 million in the city proper."
        },
        {
          "model": "anthropic/claude-3-opus",
          "original_response": "Paris is the capital of France.",
          "peer_critiques": "Peer evaluation from openai/gpt-4:\nCorrect identification but lacks historical context...\n\nPeer evaluation from google/gemini-pro:\nSimple and accurate...",
          "corrected_response": "Paris is the capital of France and has been since the late 10th century. As the nation's largest city, it serves as the center of government, commerce, and culture, hosting major institutions like the Élysée Palace and the National Assembly."
        },
        {
          "model": "google/gemini-pro",
          "original_response": "France's capital is Paris.",
          "peer_critiques": "Peer evaluation from openai/gpt-4:\nVery brief response that could be expanded...\n\nPeer evaluation from anthropic/claude-3-opus:\nAccurate but minimal detail...",
          "corrected_response": "France's capital is Paris, a city of approximately 2.1 million residents that has served as the nation's capital for over a millennium. Beyond its political role, Paris is renowned as a global center for art, fashion, gastronomy, and culture."
        }
      ],
      "stage3": {
        "model": "google/gemini-2.5-flash",
        "response": "Based on the corrected responses from the council members, the capital of France is Paris. This historic city has served as France's capital since 987 CE and is home to over 2 million residents..."
      }
    }
  ]
}
```

---

## Backward Compatibility

### Reading Old Conversations

When loading a conversation without `stage2_5`:
- Field will be `undefined` or missing
- Frontend must handle gracefully (don't render Stage 2.5 section)
- Backend passes `None`/`null` to storage functions

### Migration

No migration required:
- New field is optional
- Old conversations work without modification
- Stage 2.5 only appears for new messages after feature deployment

---

## Storage Function Changes

### add_assistant_message() Signature Update

**Before**:
```python
def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage3: Dict[str, Any]
)
```

**After**:
```python
def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage2_5: List[Dict[str, Any]],  # ← NEW PARAMETER
    stage3: Dict[str, Any]
)
```

---

## Validation Rules

1. **Model Consistency**: Each `model` in `stage2_5` must exist in `stage1`
2. **Response Match**: `original_response` must match corresponding `stage1[].response`
3. **Non-Empty**: `corrected_response` must be non-empty string
4. **Peer Count**: `peer_critiques` should contain feedback from N-1 models (all except self)
