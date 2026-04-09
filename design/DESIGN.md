# Design System Specification: The Culinary Concierge

## 1. Overview & Creative North Star
**Creative North Star: "The Modern Bistro Editorial"**

This design system rejects the clinical, "tech-first" aesthetic of typical AI assistants in favor of a warm, tactile, and high-end editorial experience. It is designed to feel like a premium printed menu—airy, intentional, and appetizing. 

We break the "standard app" template by moving away from rigid grids and boxy containers. Instead, we use **intentional asymmetry**, **exaggerated corner radii**, and **fluid typography scales** to create an interface that breathes. The goal is to make the user feel like they are interacting with a helpful human concierge, not a database. This is achieved through "Soft Minimalism": removing all unnecessary structural lines and letting the hierarchy be defined by tonal depth and generous whitespace.

---

## 2. Colors & Visual Soul
The palette is rooted in appetizing, "sun-drenched" tones that evoke warmth and freshness.

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders to section off content. Physical boundaries must be defined solely through background color shifts. For example, a `surface-container-low` section should sit directly on a `surface` background. The transition between these two tones is the only "line" allowed.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like fine linen paper stacked on a cream tabletop. 
- **Base Layer:** `surface` (#fffbff)
- **Nested Content:** Use `surface-container-low` (#fdf9f2) for large secondary areas.
- **Interactive Cards:** Use `surface-container-lowest` (#ffffff) to make elements pop off a tinted background.
- **High Importance:** Use `primary-container` (#ff7a2f) for "hero" moments to draw the eye immediately.

### Signature Textures (The Glass & Gradient Rule)
To avoid a flat "Material" look, apply a subtle linear gradient to main CTAs: 
*From `primary` (#aa4500) to `primary-container` (#ff7a2f) at a 135-degree angle.*
For floating overlays (like a "Currently Ordering" bar), use **Glassmorphism**: 
*Background: `surface` at 80% opacity | Backdrop Blur: 12px.*

---

## 3. Typography
The typography is the voice of the assistant: friendly, confident, and highly legible.

*   **Display & Headlines:** We use **Plus Jakarta Sans**. Its geometric yet soft curves feel modern and approachable. The `display-lg` (3.5rem) should be used for welcoming "hero" moments, often with intentional asymmetric placement.
*   **Body & Titles:** We use **Be Vietnam Pro**. It is an ultra-readable workhorse that maintains a friendly tone even at smaller sizes.
*   **The Hierarchy:** Use `display-md` for food category titles and `title-lg` for dish names. Never crowd the text; allow at least 1.5x line height for body copy to ensure accessibility for all age groups.

---

## 4. Elevation & Depth
Depth in this system is organic, not artificial. We mimic natural light hitting a physical surface.

*   **The Layering Principle:** Avoid shadows for static elements. If an element needs to feel "higher," shift its token from `surface-container` to `surface-container-highest`.
*   **Ambient Shadows:** For floating elements (Modals/FABs), use a "Whisper Shadow":
    *   `Box-shadow: 0 12px 32px rgba(57, 56, 52, 0.06);` (A tint of the `on-surface` color).
*   **The "Ghost Border" Fallback:** If a container requires definition against a similar background (e.g., a white card on a cream surface), use the `outline-variant` token at **15% opacity**. This creates a soft edge that is felt rather than seen.
*   **Corner Radii:** Apply the `xl` scale (3rem/48px) to main containers and the `lg` scale (2rem/32px) to interactive cards. This "over-rounding" creates the playful, accessible character required.

---

## 5. Components

### Buttons
*   **Primary:** Gradient of `primary` to `primary-container`. `xl` roundedness. No shadow unless hovered.
*   **Secondary:** `surface-container-highest` background with `primary` text.
*   **Tertiary:** Bold `primary` text, no background, 10% `primary` tint on hover.

### Cards & Lists
*   **No Dividers:** Forbid the use of horizontal lines. Use `1.5rem` to `2rem` of vertical whitespace to separate list items.
*   **Layered Cards:** Place a `surface-container-lowest` card on top of a `surface-container` background to create a "tabbed" or "nested" feel.

### Input Fields
*   **Style:** `surface-container-high` background, `xl` roundedness. 
*   **Focus:** Transition background to `surface-container-lowest` and add a `2px` "Ghost Border" using `primary`.

### Specialized Component: The "Chef's Kiss" Recommendation Card
An asymmetric card using a `secondary-container` (#ffc3bc) background, with the dish image overlapping the top edge of the card by 24px, breaking the container boundary to create a high-end editorial feel.

---

## 6. Do's and Don'ts

### Do:
*   **Do** use extreme whitespace. If a layout feels "full," it is likely too crowded.
*   **Do** use `primary` and `secondary` accents to guide the user's eye toward the "Next Step."
*   **Do** ensure all touch targets are at least 56px tall for accessibility.

### Don't:
*   **Don't** use pure black (#000000) for text. Always use `on-surface` (#393834) to maintain the warm, organic feel.
*   **Don't** use 90-degree sharp corners. Everything must feel "soft to the touch."
*   **Don't** use traditional grid-locked layouts. Allow images to bleed off the edge of the screen or sit slightly offset from text blocks to create visual rhythm.