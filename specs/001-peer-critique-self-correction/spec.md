# Feature Specification: Peer Critique Self-Correction (Stage 2.5)

**Feature Branch**: `001-peer-critique-self-correction`  
**Created**: 2026-01-20  
**Status**: Clarified  
**Input**: User description: "I would like to add a new feature that allows models to correct themselves after seeing peer critics. Logic Flow feeds each model its own initial answer plus the specific critics written by its peers. Prompt: Here is your original answer and how your peers critiqued it. Based on their feedback, provide a final corrected version of your response. Use internet tools where required. The Chairman now receives the stage 2.5 corrected answer instead of stage 1 drafts. We need a separate back-end update as well as a front-end that can accommodate showing the user the update based on the critique."

---

## Overview

This feature introduces a new **Stage 2.5** in the LLM Council deliberation pipeline. After Stage 2 (peer rankings/critiques), each model receives its own original answer along with the specific criticisms written by its peers. Models then produce a **corrected/refined response** based on this feedback. The Chairman (Stage 3) receives these corrected Stage 2.5 responses instead of the original Stage 1 drafts, enabling higher-quality final synthesis.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Self-Corrected Responses (Priority: P1)

As a user, I want to see how each model refined its answer after receiving peer feedback, so I can understand how critique improves response quality.

**Why this priority**: This is the core value proposition—users gain transparency into the self-improvement process and can evaluate whether models meaningfully incorporated peer feedback.

**Independent Test**: Can be fully tested by submitting a question and verifying that a new "Stage 2.5" section appears showing each model's corrected response alongside their original answer.

**Acceptance Scenarios**:

1. **Given** a user has submitted a query and Stage 2 has completed, **When** Stage 2.5 processing finishes, **Then** the user sees a new section displaying each model's corrected response.
2. **Given** Stage 2.5 results are displayed, **When** the user views a model's corrected response, **Then** they can also see the original Stage 1 response for comparison.
3. **Given** Stage 2.5 is in progress, **When** the user is waiting, **Then** they see a loading indicator specific to Stage 2.5.

---

### User Story 2 - Compare Original vs Corrected Responses (Priority: P2)

As a user, I want to easily compare a model's original response with its corrected version, so I can evaluate the quality of self-correction.

**Why this priority**: Comparison capability enhances the transparency value by making improvements (or lack thereof) immediately visible.

**Independent Test**: Can be tested by verifying that the UI provides a clear mechanism to view original and corrected responses side-by-side or in sequence.

**Acceptance Scenarios**:

1. **Given** Stage 2.5 results are displayed, **When** the user selects a model tab, **Then** they see both the original response and the corrected response clearly labeled.
2. **Given** a model's responses are displayed, **When** the user reads them, **Then** the distinction between "Original" and "Corrected" is visually clear.

---

### User Story 3 - Chairman Uses Corrected Responses (Priority: P1)

As a user, I want the Chairman's final synthesis to be based on the improved Stage 2.5 responses rather than the original drafts, so the final answer incorporates peer-reviewed improvements.

**Why this priority**: This directly impacts output quality—the Chairman should synthesize from the best available responses.

**Independent Test**: Can be verified by checking that the Chairman prompt includes Stage 2.5 corrected responses instead of Stage 1 responses.

**Acceptance Scenarios**:

1. **Given** Stage 2.5 has completed, **When** Stage 3 (Chairman) runs, **Then** the Chairman receives the corrected responses from Stage 2.5 as input.
2. **Given** the Chairman is synthesizing, **When** the Chairman prompt is constructed, **Then** it references "corrected responses" rather than "initial responses."

---

### User Story 4 - Progressive Loading for Stage 2.5 (Priority: P2)

As a user, I want to see Stage 2.5 results appear progressively as they complete, so I have visibility into the ongoing process.

**Why this priority**: Maintains the existing UX pattern of progressive stage loading, ensuring consistency.

**Independent Test**: Can be tested by observing that Stage 2.5 loading indicator appears after Stage 2 completes and before Stage 3 begins.

**Acceptance Scenarios**:

1. **Given** Stage 2 has completed, **When** Stage 2.5 begins processing, **Then** a loading indicator for Stage 2.5 is displayed.
2. **Given** Stage 2.5 is processing, **When** it completes, **Then** the loading indicator is replaced with the actual results.

---

### Edge Cases

- What happens when a model fails to produce a corrected response? **Assumption**: The system falls back to the original Stage 1 response for that model.
- What happens when no peer critiques are available for a model (e.g., all other models failed)? **Assumption**: The model is prompted to review its own response without peer feedback.
- How does the system handle very long critique text that might exceed context limits? **Assumption**: Critiques are summarized or truncated if they exceed a reasonable threshold.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a new Stage 2.5 that runs after Stage 2 and before Stage 3.
- **FR-002**: System MUST feed each model its own Stage 1 response along with the critiques/evaluations written by peer models in Stage 2.
- **FR-003**: System MUST prompt each model to produce a corrected/refined response based on peer feedback.
- **FR-004**: System MUST pass the Stage 2.5 corrected responses (instead of Stage 1 responses) to the Chairman in Stage 3.
- **FR-005**: System MUST display Stage 2.5 results in the frontend with a dedicated UI section.
- **FR-006**: System MUST show both original (Stage 1) and corrected (Stage 2.5) responses for comparison.
- **FR-007**: System MUST stream Stage 2.5 progress events to the frontend (stage2_5_start, stage2_5_complete).
- **FR-008**: System MUST persist Stage 2.5 results in conversation storage.
- **FR-009**: System MUST handle model failures gracefully by falling back to Stage 1 responses.
- **FR-010**: System MUST maintain the existing tabbed UI pattern for Stage 2.5, showing each model's corrected response in a separate tab.

### Key Entities

- **Stage 2.5 Result**: Contains model identifier, original response reference, peer critiques received, and corrected response text.
- **Peer Critique**: The evaluation/criticism text written by one model about another model's response (extracted from Stage 2 results).
- **Corrected Response**: The refined answer produced by a model after reviewing peer feedback.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view Stage 2.5 corrected responses within 30 seconds of Stage 2 completion (parallel processing of all models).
- **SC-002**: 100% of Chairman syntheses use Stage 2.5 corrected responses as input when available.
- **SC-003**: Users can distinguish between original and corrected responses with no additional clicks (both visible in the same view).
- **SC-004**: Stage 2.5 loading state is visible to users, maintaining the progressive disclosure pattern.
- **SC-005**: System gracefully handles model failures, with fallback to Stage 1 responses occurring in under 1 second.

---

## Clarified Decisions

The following decisions were clarified during specification review:

### CD-001: Critique Extraction Method
**Decision**: Full evaluation text with peer attribution (Option C)
- Each model receives the complete Stage 2 evaluation text from each peer
- Critiques are clearly labeled with which peer model wrote them
- This maintains full context while making attribution clear

### CD-002: UI Layout for Comparison
**Decision**: Stacked layout - original above, corrected below (Option A)
- Original response displayed first with clear "Original Response" header
- Corrected response displayed below with clear "Corrected Response" header
- Works well on all screen sizes and follows existing UI patterns
- No additional clicks required to see both versions

### CD-003: Chairman Input
**Decision**: Stage 2.5 responses + Stage 2 rankings (Option B)
- Chairman receives the corrected Stage 2.5 responses (not Stage 1 drafts)
- Chairman also receives the Stage 2 peer rankings to weigh responses by consensus
- This maintains the existing pattern where rankings inform synthesis quality

---

## Assumptions

1. **Parallel Processing**: Stage 2.5 queries all models in parallel (same pattern as Stage 1 and Stage 2) to minimize latency.
2. **Critique Extraction**: Peer critiques include the full Stage 2 evaluation text with clear peer attribution (per CD-001).
3. **Prompt Structure**: The Stage 2.5 prompt follows the pattern: "Here is your original answer and how your peers critiqued it. Based on their feedback, provide a final corrected version of your response."
4. **No Self-Critique**: Models do not see their own Stage 2 evaluation of themselves—only peer evaluations.
5. **Existing Models**: Stage 2.5 uses the same council models as Stage 1 and Stage 2 (no new model configuration needed).
6. **Storage Schema**: Stage 2.5 results are stored in the same conversation JSON structure, adding a `stage2_5` field to assistant messages.
7. **Chairman Context**: Chairman receives Stage 2.5 corrected responses plus Stage 2 rankings (per CD-003).
