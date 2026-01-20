# Tasks: Peer Critique Self-Correction (Stage 2.5)

**Input**: Design documents from `/specs/001-peer-critique-self-correction/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Manual testing only (no automated test framework in codebase per research.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (React/Vite)
- **Storage**: `data/conversations/` (JSON files)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup needed—extending existing codebase

- [x] T001 Verify backend server runs without errors at http://localhost:8001
- [x] T002 Verify frontend dev server runs without errors at http://localhost:5173
- [x] T003 Review existing Stage 1, Stage 2, Stage 3 code patterns in `backend/council.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Core Functions

- [x] T004 Add `format_peer_critiques()` helper function in `backend/council.py` - extracts and formats peer feedback from Stage 2 results, excluding self-evaluation
- [x] T005 Add `build_correction_prompt()` helper function in `backend/council.py` - builds the Stage 2.5 prompt per research.md template
- [x] T006 Add `stage2_5_collect_corrections()` async function in `backend/council.py` - orchestrates parallel model queries for corrections

### Storage Extension

- [x] T007 Update `add_assistant_message()` signature in `backend/storage.py` - add `stage2_5` parameter between `stage2` and `stage3`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Self-Corrected Responses (Priority: P1) 🎯 MVP

**Goal**: Users see a new Stage 2.5 section showing each model's corrected response after peer feedback

**Independent Test**: Submit a question and verify Stage 2.5 section appears with corrected responses

### Backend Implementation for US1

- [x] T008 [US1] Add `stage2_5_start` SSE event in `backend/main.py` streaming endpoint - emit after stage2_complete
- [x] T009 [US1] Call `stage2_5_collect_corrections()` in `backend/main.py` streaming endpoint - between Stage 2 and Stage 3
- [x] T010 [US1] Add `stage2_5_complete` SSE event in `backend/main.py` streaming endpoint - emit with results data
- [x] T011 [US1] Update storage call in `backend/main.py` - pass `stage2_5_results` to `add_assistant_message()`

### Frontend Implementation for US1

- [x] T012 [P] [US1] Create `frontend/src/components/Stage2_5.jsx` - tabbed component showing corrected responses per model
- [x] T013 [P] [US1] Create `frontend/src/components/Stage2_5.css` - styles matching existing Stage components
- [x] T014 [US1] Add `stage2_5` to assistant message initial state in `frontend/src/App.jsx` - add `stage2_5: null` and `loading.stage2_5: false`
- [x] T015 [US1] Add `stage2_5_start` event handler in `frontend/src/App.jsx` - set `loading.stage2_5 = true`
- [x] T016 [US1] Add `stage2_5_complete` event handler in `frontend/src/App.jsx` - store data and set `loading.stage2_5 = false`
- [x] T017 [US1] Import and render Stage2_5 component in `frontend/src/components/ChatInterface.jsx` - between Stage 2 and Stage 3
- [x] T018 [US1] Add loading indicator for Stage 2.5 in `frontend/src/components/ChatInterface.jsx` - show when `loading.stage2_5` is true

**Checkpoint**: User Story 1 complete - Stage 2.5 section visible with model corrections

---

## Phase 4: User Story 2 - Compare Original vs Corrected (Priority: P2)

**Goal**: Users can easily compare original and corrected responses within the same view

**Independent Test**: Select a model tab and verify both original and corrected responses are visible with clear labels

### Frontend Implementation for US2

- [x] T019 [US2] Add "Original Response" section with header in `frontend/src/components/Stage2_5.jsx` - display `original_response` with ReactMarkdown
- [x] T020 [US2] Add "Corrected Response" section with header in `frontend/src/components/Stage2_5.jsx` - display `corrected_response` with ReactMarkdown
- [x] T021 [US2] Style stacked layout in `frontend/src/components/Stage2_5.css` - original above, corrected below with visual distinction
- [x] T022 [US2] Add visual indicators in `frontend/src/components/Stage2_5.css` - different background colors or borders for original vs corrected sections

**Checkpoint**: User Story 2 complete - clear comparison between original and corrected responses

---

## Phase 5: User Story 3 - Chairman Uses Corrected Responses (Priority: P1)

**Goal**: Chairman's synthesis is based on Stage 2.5 corrected responses instead of Stage 1 drafts

**Independent Test**: Verify Chairman prompt references "corrected responses" and uses Stage 2.5 data

### Backend Implementation for US3

- [x] T023 [US3] Modify `stage3_synthesize_final()` signature in `backend/council.py` - accept `stage2_5_results` instead of `stage1_results`
- [x] T024 [US3] Update Chairman prompt in `stage3_synthesize_final()` in `backend/council.py` - reference "STAGE 2.5 - Corrected Responses" instead of "STAGE 1"
- [x] T025 [US3] Update `stage3_synthesize_final()` call in `backend/main.py` streaming endpoint - pass `stage2_5_results` instead of `stage1_results`
- [x] T026 [US3] Update `stage3_synthesize_final()` call in `backend/main.py` non-streaming endpoint - pass `stage2_5_results` instead of `stage1_results`

**Checkpoint**: User Story 3 complete - Chairman synthesizes from improved responses

---

## Phase 6: User Story 4 - Progressive Loading (Priority: P2)

**Goal**: Users see Stage 2.5 loading state during processing

**Independent Test**: Observe loading indicator appears after Stage 2 completes and before Stage 2.5 results display

### Frontend Implementation for US4

- [x] T027 [US4] Style loading indicator in `frontend/src/components/Stage2_5.css` - match existing stage loading styles
- [x] T028 [US4] Verify loading state transitions in `frontend/src/App.jsx` - ensure smooth transition from loading to results

**Checkpoint**: User Story 4 complete - progressive loading works correctly

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, backward compatibility, and cleanup

### Error Handling

- [x] T029 [P] Add fallback logic in `stage2_5_collect_corrections()` in `backend/council.py` - use Stage 1 response if model fails
- [x] T030 [P] Handle missing `stage2_5` in `frontend/src/components/ChatInterface.jsx` - gracefully skip rendering for old conversations

### Backward Compatibility

- [x] T031 Verify old conversations load correctly without `stage2_5` field
- [x] T032 Verify new conversations save with `stage2_5` field in `data/conversations/`

### Validation

- [ ] T033 Run full end-to-end test: submit query → verify all 4 stages complete
- [ ] T034 Run quickstart.md testing checklist validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US3 are both P1 priority - US1 should complete first (provides UI for US3 verification)
  - US2 and US4 are P2 priority - can proceed after US1
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (T004-T007)
        │
        ▼
┌───────────────────┐
│  User Story 1     │  ← MVP: Core Stage 2.5 functionality
│  (T008-T018)      │
└───────┬───────────┘
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ User Story 2  │  │ User Story 3  │  │ User Story 4  │
│ (T019-T022)   │  │ (T023-T026)   │  │ (T027-T028)   │
│ Comparison UI │  │ Chairman Fix  │  │ Loading State │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Polish (T029-  │
                  │ T034)          │
                  └────────────────┘
```

### Within Each User Story

- Backend tasks before frontend tasks (data must flow)
- Component creation before integration
- Core functionality before styling

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T004, T005 can run in parallel (helper functions, no dependencies)

**Phase 3 (US1)**:
- T012, T013 can run in parallel (new files, no dependencies)

**Phase 4 (US2)**:
- T019, T020 can run in parallel (different sections of same component)

**Phase 7 (Polish)**:
- T029, T030 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes...

# Backend tasks (sequential - same file):
Task T008: Add stage2_5_start SSE event
Task T009: Call stage2_5_collect_corrections()
Task T010: Add stage2_5_complete SSE event
Task T011: Update storage call

# Frontend tasks (parallel where marked):
Task T012 [P]: Create Stage2_5.jsx
Task T013 [P]: Create Stage2_5.css
# Then sequential:
Task T014: Add stage2_5 to state
Task T015: Add stage2_5_start handler
Task T016: Add stage2_5_complete handler
Task T017: Import and render Stage2_5
Task T018: Add loading indicator
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: User Story 1 (T008-T018)
4. **STOP and VALIDATE**: Test Stage 2.5 appears with corrections
5. Deploy/demo if ready - basic Stage 2.5 functionality works

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Complete!**
3. Add User Story 3 → Test Chairman uses corrections → Core feature complete
4. Add User Story 2 → Test comparison UI → Enhanced UX
5. Add User Story 4 → Test loading states → Polished UX
6. Polish phase → Production ready

### Recommended Order

Given both US1 and US3 are P1 priority:
1. **US1 first** - Creates the visible Stage 2.5 UI
2. **US3 second** - Makes Chairman use the corrections (invisible but critical)
3. **US2 and US4** - Polish the user experience

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | T001-T003 | N/A (verification) |
| Foundational | T004-T007 | T004, T005 |
| US1 (P1) 🎯 MVP | T008-T018 | T012, T013 |
| US2 (P2) | T019-T022 | T019, T020 |
| US3 (P1) | T023-T026 | None |
| US4 (P2) | T027-T028 | None |
| Polish | T029-T034 | T029, T030 |

**Total Tasks**: 34  
**MVP Scope**: T001-T018 (18 tasks)  
**Full Feature**: All 34 tasks

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No automated tests - use quickstart.md testing checklist for manual validation
