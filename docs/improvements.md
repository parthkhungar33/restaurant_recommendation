# Improvements Roadmap

This document captures the next set of product and system improvements, grouped into practical implementation phases.

Current goal: improve recommendation quality and UX without expanding scope beyond MVP constraints.

---

## Improvement Goals

1. Replace `budget` band (`low/medium/high`) with numeric **max budget** input.
2. Ensure `minimum rating` is strictly capped at `5.0`.
3. Replace free-text `additional_preferences` with a dropdown/multi-select.
4. Improve results UX:
   - remove `fit_score` from cards
   - make explanation tone friendlier
   - prevent duplicate/same-restaurant results in output

---

## Phase A - Input Model and Validation Upgrade

### Scope
- Move from `budget` band to numeric `max_budget` in API and frontend.
- Enforce strict validation for rating (`0.0 <= min_rating <= 5.0`).
- Preserve backward compatibility temporarily where needed.

### Changes
- **API models**
  - Replace `budget` with `max_budget: float | None`.
  - Keep validation bounds:
    - `min_rating` max = 5
    - `max_budget` positive and reasonable upper bound.
- **Retrieval logic**
  - Replace budget-band filter with:
    - `avg_cost_for_two <= max_budget`
  - Maintain existing fallback behavior (if results are sparse).
- **Frontend form**
  - Use number input for budget:
    - label: "Max Budget (for two)"
  - Keep rating input max at 5 and block invalid entry in UI.

### Acceptance Criteria
- Query works with numeric max budget.
- Rating cannot exceed 5 at both API and frontend levels.
- Existing tests updated and passing.

---

## Phase B - Controlled Additional Preferences

### Scope
- Replace open text `additional_preferences` with fixed choices in frontend.
- Keep backend field flexible, but process known values predictably.

### Preferred Dropdown Options (initial set)
- `date`
- `family-friendly`
- `quick service`
- `casual`
- `fine dine`
- `outdoor seating`
- `veg friendly`
- `group friendly`

### Changes
- **Frontend**
  - Use single-select or multi-select dropdown (multi-select recommended).
  - Convert selected items into a normalized list/string before API call.
- **Backend**
  - Add preference normalization map (`date` -> romantic/ambience signal, etc.).
  - Pass normalized preference tags into LLM prompt context.

### Acceptance Criteria
- Users select preferences from dropdown only.
- Preferences are consistently interpreted by retrieval + LLM layers.

---

## Phase C - Result Quality and Duplicate Handling

### Scope
- Prevent duplicate restaurant cards.
- Improve recommendation explanation tone.
- Remove `fit_score` from visible UI.

### Duplicate Problem (Observed)
Example issue:
- Same restaurant (`Church Street Social`) returned multiple times in one response.

Likely causes:
- Duplicate rows in source/canonical data for same restaurant identity.
- LLM returning duplicate candidate IDs.
- Final formatter not deduplicating post-ranking.

### Implementation Plan
1. **Canonical dedup in retrieval pipeline**
   - Define dedup key priority:
     - `restaurant_id` first
     - fallback: normalized `(name + locality + cuisine)` signature
   - Deduplicate before candidate list is passed to LLM.
2. **LLM output dedup guard**
   - After parsing LLM JSON, enforce unique `restaurant_id`.
   - Drop repeats and backfill from remaining candidates if needed.
3. **Final response dedup guard**
   - Final formatter enforces uniqueness again before returning cards.
4. **Optional data-level enhancement**
   - Add one-time data quality report for duplicate signatures in DB.

### Friendly Explanation Upgrade
- Update system/user prompt guidelines to:
  - use natural, warm phrasing
  - avoid robotic "meets criteria" style
  - include concise "why this place works for your need"

Example style:
- Instead of: "Meets location and cuisine criteria."
- Use: "This spot matches your Chinese preference and has strong ratings around Church Street, making it a good date option."

### UI Output Change
- Remove `fit_score` from frontend card layout.
- Keep `fit_score` internal/optional in API only if needed for debugging.

### Acceptance Criteria
- No duplicate restaurants in final response.
- Explanations read naturally and are user-friendly.
- UI cards no longer show fit score.

---

## Phase D - Regression Coverage and Quality Gate

### Scope
- Add targeted regression tests so these improvements remain stable.

### Tests to Add
- Numeric `max_budget` filter behavior.
- `min_rating > 5` rejected by API validation.
- Dropdown preference mapping integration test.
- Dedup tests:
  - duplicate candidates in retrieval input
  - duplicate IDs in LLM output
  - final response uniqueness check.
- Snapshot/contract tests for response shape (without `fit_score` in UI layer).

### Acceptance Criteria
- All new tests pass in CI.
- No known duplicate-result regressions.

---

## Recommended Implementation Order

1. **Phase A** (Input model + validation)
2. **Phase C** (Dedup + friendly explanation + remove fit score)
3. **Phase B** (Dropdown preferences)
4. **Phase D** (Regression gate)

Reason:
- Fixing input model and duplicate quality first gives immediate UX gain and prevents misleading outputs.

---

## Notes

- These changes are fully compatible with current MVP direction.
- They do not require high-scale architecture changes.
- After completion, rerun Phase 5 evaluation to compare:
  - empty-result rate
  - duplicate-result rate (target: 0)
  - explanation quality score improvement.
