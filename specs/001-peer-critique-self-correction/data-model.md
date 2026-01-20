# Data Model: Peer Critique Self-Correction (Stage 2.5)

**Feature Branch**: `001-peer-critique-self-correction`  
**Date**: 2026-01-20

---

## Entity Overview

This feature introduces one new entity (Stage 2.5 Result) and extends the existing Assistant Message entity.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Assistant Message                             │
├─────────────────────────────────────────────────────────────────────┤
│ role: "assistant"                                                    │
│ stage1: Stage1Result[]                                               │
│ stage2: Stage2Result[]                                               │
│ stage2_5: Stage2_5Result[]  ← NEW                                    │
│ stage3: Stage3Result                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Stage2_5Result (NEW)                           │
├─────────────────────────────────────────────────────────────────────┤
│ model: string              // OpenRouter model identifier            │
│ original_response: string  // Reference to Stage 1 response          │
│ peer_critiques: string     // Formatted peer feedback text           │
│ corrected_response: string // The refined response                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Entities

### Stage2_5Result (New Entity)

Represents a model's self-corrected response after receiving peer feedback.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | OpenRouter model identifier (e.g., "openai/gpt-4") |
| `original_response` | string | Yes | The model's original Stage 1 response |
| `peer_critiques` | string | Yes | Formatted text containing all peer evaluations |
| `corrected_response` | string | Yes | The model's refined response after peer review |

**Validation Rules**:
- `model` must be a valid OpenRouter model identifier
- `original_response` must match the corresponding Stage 1 response for this model
- `peer_critiques` must not include the model's own Stage 2 evaluation
- `corrected_response` must be non-empty (fallback to original if model fails)

**State Transitions**:
```
Stage 1 Complete → Stage 2 Complete → Stage 2.5 Processing → Stage 2.5 Complete
                                            │
                                            ▼
                                      [If model fails]
                                            │
                                            ▼
                                   Fallback to Stage 1 response
```

---

### AssistantMessage (Extended)

The existing assistant message entity is extended to include Stage 2.5 results.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | "assistant" | Yes | Message role identifier |
| `stage1` | Stage1Result[] | Yes | Individual model responses |
| `stage2` | Stage2Result[] | Yes | Peer rankings/evaluations |
| `stage2_5` | Stage2_5Result[] | **New** | Self-corrected responses |
| `stage3` | Stage3Result | Yes | Chairman's final synthesis |

**Backward Compatibility**:
- `stage2_5` is optional for existing conversations
- Frontend must handle missing `stage2_5` gracefully
- Old conversations display without Stage 2.5 section

---

### PeerCritique (Conceptual - Not Persisted)

Represents the formatted peer feedback shown to a model. This is constructed at runtime, not stored separately.

| Field | Type | Description |
|-------|------|-------------|
| `critic_model` | string | Model that wrote the critique |
| `critique_text` | string | Full evaluation text from Stage 2 |

**Formatting Pattern**:
```
Peer evaluation from {critic_model}:
{critique_text}

Peer evaluation from {critic_model_2}:
{critique_text_2}
```

---

## Relationships

```
User Query
    │
    ▼
┌───────────┐     ┌───────────┐     ┌────────────┐     ┌───────────┐
│  Stage 1  │────▶│  Stage 2  │────▶│ Stage 2.5  │────▶│  Stage 3  │
│ Responses │     │ Rankings  │     │ Corrections│     │ Synthesis │
└───────────┘     └───────────┘     └────────────┘     └───────────┘
      │                 │                  │                  │
      │                 │                  │                  │
      ▼                 ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Assistant Message                             │
│   { stage1, stage2, stage2_5, stage3 }                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Flow**:
1. Stage 1 → Stage 2: Responses are anonymized for peer evaluation
2. Stage 2 → Stage 2.5: Each model receives its Stage 1 response + peer critiques
3. Stage 2.5 → Stage 3: Chairman receives corrected responses + rankings

---

## JSON Schema

### Stage2_5Result Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "model": {
      "type": "string",
      "description": "OpenRouter model identifier"
    },
    "original_response": {
      "type": "string",
      "description": "The model's original Stage 1 response"
    },
    "peer_critiques": {
      "type": "string",
      "description": "Formatted peer evaluation text"
    },
    "corrected_response": {
      "type": "string",
      "description": "The model's refined response"
    }
  },
  "required": ["model", "original_response", "peer_critiques", "corrected_response"]
}
```

### Extended Assistant Message Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "role": {
      "type": "string",
      "const": "assistant"
    },
    "stage1": {
      "type": "array",
      "items": { "$ref": "#/definitions/Stage1Result" }
    },
    "stage2": {
      "type": "array",
      "items": { "$ref": "#/definitions/Stage2Result" }
    },
    "stage2_5": {
      "type": "array",
      "items": { "$ref": "#/definitions/Stage2_5Result" },
      "description": "Optional - not present in legacy conversations"
    },
    "stage3": {
      "$ref": "#/definitions/Stage3Result"
    }
  },
  "required": ["role", "stage1", "stage2", "stage3"]
}
```

---

## Example Data

### Stage 2.5 Result Example

```json
{
  "model": "openai/gpt-4",
  "original_response": "The capital of France is Paris. It has been the capital since...",
  "peer_critiques": "Peer evaluation from anthropic/claude-3-opus:\nThe response correctly identifies Paris as the capital but lacks historical context about when it became the capital. The answer could be improved by mentioning...\n\nPeer evaluation from google/gemini-pro:\nThis response is accurate but brief. A more comprehensive answer would include...",
  "corrected_response": "The capital of France is Paris, which has served as the nation's capital since 987 CE when Hugh Capet established it as the seat of the Capetian dynasty. Paris is not only the political capital but also the cultural and economic heart of France, home to over 2 million residents in the city proper..."
}
```

### Complete Assistant Message Example

```json
{
  "role": "assistant",
  "stage1": [
    { "model": "openai/gpt-4", "response": "..." },
    { "model": "anthropic/claude-3-opus", "response": "..." },
    { "model": "google/gemini-pro", "response": "..." }
  ],
  "stage2": [
    { "model": "openai/gpt-4", "ranking": "...", "parsed_ranking": ["Response B", "Response A", "Response C"] },
    { "model": "anthropic/claude-3-opus", "ranking": "...", "parsed_ranking": ["Response A", "Response B", "Response C"] },
    { "model": "google/gemini-pro", "ranking": "...", "parsed_ranking": ["Response B", "Response A", "Response C"] }
  ],
  "stage2_5": [
    { "model": "openai/gpt-4", "original_response": "...", "peer_critiques": "...", "corrected_response": "..." },
    { "model": "anthropic/claude-3-opus", "original_response": "...", "peer_critiques": "...", "corrected_response": "..." },
    { "model": "google/gemini-pro", "original_response": "...", "peer_critiques": "...", "corrected_response": "..." }
  ],
  "stage3": {
    "model": "google/gemini-2.5-flash",
    "response": "Based on the corrected responses and peer consensus..."
  }
}
```
