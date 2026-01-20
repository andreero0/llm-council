# Quickstart Guide: Peer Critique Self-Correction (Stage 2.5)

**Feature Branch**: `001-peer-critique-self-correction`  
**Date**: 2026-01-20

---

## Overview

This guide provides a quick reference for implementing the Stage 2.5 feature. It covers the key changes needed in both backend and frontend.

---

## Implementation Summary

| Component | Files to Modify | New Files |
|-----------|-----------------|-----------|
| Backend | `council.py`, `main.py`, `storage.py` | None |
| Frontend | `App.jsx`, `ChatInterface.jsx` | `Stage2_5.jsx`, `Stage2_5.css` |

---

## Backend Implementation

### 1. Add Stage 2.5 Function to `council.py`

```python
async def stage2_5_collect_corrections(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Stage 2.5: Each model corrects its response based on peer feedback.
    """
    # Build correction prompts for each model
    correction_tasks = []
    
    for stage1_result in stage1_results:
        model = stage1_result['model']
        original_response = stage1_result['response']
        
        # Collect peer critiques (exclude self-evaluation)
        peer_critiques = format_peer_critiques(model, stage2_results)
        
        # Build correction prompt
        prompt = build_correction_prompt(user_query, original_response, peer_critiques)
        
        correction_tasks.append({
            'model': model,
            'original_response': original_response,
            'peer_critiques': peer_critiques,
            'messages': [{"role": "user", "content": prompt}]
        })
    
    # Query all models in parallel
    results = await query_models_parallel(
        [task['model'] for task in correction_tasks],
        [task['messages'] for task in correction_tasks]
    )
    
    # Format results with fallback
    stage2_5_results = []
    for task in correction_tasks:
        model = task['model']
        response = results.get(model)
        
        stage2_5_results.append({
            'model': model,
            'original_response': task['original_response'],
            'peer_critiques': task['peer_critiques'],
            'corrected_response': response.get('content', task['original_response']) if response else task['original_response']
        })
    
    return stage2_5_results
```

### 2. Update `main.py` Streaming Endpoint

Add Stage 2.5 events between Stage 2 and Stage 3:

```python
# After stage2_complete...

# Stage 2.5: Collect corrections
yield f"data: {json.dumps({'type': 'stage2_5_start'})}\n\n"
stage2_5_results = await stage2_5_collect_corrections(
    request.content, stage1_results, stage2_results
)
yield f"data: {json.dumps({'type': 'stage2_5_complete', 'data': stage2_5_results})}\n\n"

# Stage 3: Synthesize (now uses stage2_5_results)
yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
stage3_result = await stage3_synthesize_final(
    request.content, stage2_5_results, stage2_results  # Changed from stage1_results
)
```

### 3. Update `storage.py`

Add `stage2_5` parameter to `add_assistant_message`:

```python
def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage2_5: List[Dict[str, Any]],  # NEW
    stage3: Dict[str, Any]
):
    conversation["messages"].append({
        "role": "assistant",
        "stage1": stage1,
        "stage2": stage2,
        "stage2_5": stage2_5,  # NEW
        "stage3": stage3
    })
```

---

## Frontend Implementation

### 1. Create `Stage2_5.jsx` Component

```jsx
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage2_5.css';

export default function Stage2_5({ corrections }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!corrections || corrections.length === 0) {
    return null;
  }

  return (
    <div className="stage stage2-5">
      <h3 className="stage-title">Stage 2.5: Self-Corrections</h3>
      <p className="stage-description">
        Each model revised its answer based on peer feedback.
      </p>

      {/* Tab bar */}
      <div className="tabs">
        {corrections.map((corr, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {corr.model.split('/')[1] || corr.model}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="tab-content">
        <div className="response-section original">
          <h4>Original Response</h4>
          <div className="markdown-content">
            <ReactMarkdown>{corrections[activeTab].original_response}</ReactMarkdown>
          </div>
        </div>
        
        <div className="response-section corrected">
          <h4>Corrected Response</h4>
          <div className="markdown-content">
            <ReactMarkdown>{corrections[activeTab].corrected_response}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 2. Update `App.jsx` Event Handling

Add handlers for Stage 2.5 events:

```jsx
case 'stage2_5_start':
  setCurrentConversation((prev) => {
    const messages = [...prev.messages];
    const lastMsg = messages[messages.length - 1];
    lastMsg.loading.stage2_5 = true;
    return { ...prev, messages };
  });
  break;

case 'stage2_5_complete':
  setCurrentConversation((prev) => {
    const messages = [...prev.messages];
    const lastMsg = messages[messages.length - 1];
    lastMsg.stage2_5 = event.data;
    lastMsg.loading.stage2_5 = false;
    return { ...prev, messages };
  });
  break;
```

### 3. Update `ChatInterface.jsx`

Add Stage 2.5 component between Stage 2 and Stage 3:

```jsx
{/* Stage 2.5 */}
{message.loading?.stage2_5 && (
  <div className="stage-loading">Loading self-corrections...</div>
)}
{message.stage2_5 && (
  <Stage2_5 corrections={message.stage2_5} />
)}
```

---

## Testing Checklist

- [ ] Submit a query and verify Stage 2.5 section appears
- [ ] Verify loading indicator shows during Stage 2.5 processing
- [ ] Check that original and corrected responses display correctly
- [ ] Verify tabs work to switch between models
- [ ] Confirm Stage 3 synthesis references corrected responses
- [ ] Test with model failure (should fall back to Stage 1)
- [ ] Verify old conversations still load without Stage 2.5

---

## Key Files Reference

```
backend/
├── council.py      # Add stage2_5_collect_corrections()
├── main.py         # Add SSE events, update stage3 call
└── storage.py      # Add stage2_5 to add_assistant_message()

frontend/src/
├── App.jsx                    # Add stage2_5 event handlers
├── components/
│   ├── ChatInterface.jsx      # Render Stage2_5 component
│   ├── Stage2_5.jsx           # NEW: Stage 2.5 UI component
│   └── Stage2_5.css           # NEW: Stage 2.5 styles
```
