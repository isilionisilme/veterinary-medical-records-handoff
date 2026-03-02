# Lean Design System (Tokens + Primitives)

## Purpose
This document defines the minimal design-system contract for the internal Claims Review UI.

Goals:
- prevent ad-hoc styling drift,
- provide a consistent base for editable structured fields,
- keep UI implementation lightweight and maintainable.

This is an implementation-facing UI contract. It does not redefine workflow behavior from UX/Product docs.

---

## Token strategy

The project uses **CSS variables as canonical tokens** in `frontend/src/index.css`, then maps those tokens into Tailwind in `frontend/tailwind.config.cjs`.

Rule:
- Define/adjust token values in CSS variables.
- Consume tokens through Tailwind utility names (not ad-hoc hex values in components).

All new user-visible UI must use tokens instead of scattered hard-coded values.

### Color tokens

> Brand-level color decisions (accent, page bg, text hierarchy, semantic status) are defined in
> [brand-guidelines.md](../shared/brand-guidelines.md). This table reflects **actual implementation values**
> from `frontend/src/index.css`. When brand and implementation diverge, this table tracks the code.

| Token | Value | Usage |
|---|---|---|
| `--app-bg` | `#ebf5ff` | outer page background |
| `--canvas-bg` | `#ffffff` | main app canvas/container |
| `--card-bg` | `#ffffff` | cards/panels (inner surfaces) |
| `--app-frame` | `var(--canvas-bg)` | canvas alias |
| `--surface` | `var(--card-bg)` | card alias |
| `--surface-muted` | `#f2f5f8` | subtle inner surfaces / toolbar blocks |
| `--border-subtle` | `#cfd8e3` | subtle separators and panel borders |
| `--shadow-soft` | `none` | soft elevation for frame/cards |
| `--color-page-bg` | `var(--app-bg)` | app/page background alias |
| `--color-surface` | `var(--surface)` | cards/panels alias |
| `--color-surface-muted` | `var(--surface-muted)` | muted surface alias |
| `--color-text` | `#1f2933` | primary text |
| `--color-text-secondary` | `#4b5563` | secondary text |
| `--color-text-muted` | `#6b7280` | metadata/helper text |
| `--text-title` | `var(--color-text)` | panel/section title text |
| `--text-body` | `var(--color-text)` | default body text |
| `--text-muted` | `var(--color-text-secondary)` | secondary metadata |
| `--color-border` | `#d7dee7` | default borders |
| `--color-border-subtle` | `var(--border-subtle)` | subtle separators alias |
| `--color-accent` | `#e5603d` | primary accent |
| `--color-accent-foreground` | `#ffffff` | text on accent |
| `--shadow-subtle` | `none` | gentle elevation alias |

### Surface levels (L0–L3)

- **L0 (`--app-bg`)**: page background outside the app frame.
- **L1 (`--canvas-bg`)**: main application canvas/frame.
- **L2 (`--card-bg` / `--surface`)**: primary panels/cards (sidebar, viewer, data panel).
- **L3 (`--surface-muted`)**: inner controls/toolbar blocks/secondary containers.

Rule:
- Prefer alternating levels to avoid flat “same color everywhere” composition.
- Use one logical boundary per block; avoid unnecessary nested frames.

### Semantic/status tokens

| Token | Value | Usage |
|---|---|---|
| `--status-success` | `#3f9e86` | semantic success / ready |
| `--status-warn` | `#c99645` | semantic warning / processing |
| `--status-error` | `#c45f5c` | semantic error / failure |
| `--confidence-low` | `var(--status-error)` | low-confidence indicator |
| `--confidence-med` | `var(--status-warn)` | medium-confidence indicator |
| `--confidence-high` | `var(--status-success)` | high-confidence indicator |
| `--status-critical` | `var(--status-error)` | critical badge border/text accent |
| `--status-missing` | `#9ca3af` | missing/placeholder state tone |
| `--status-success-bg` | `#e7f4ef` | success background fill |
| `--status-info-bg` | `#f3f6f9` | info background fill |
| `--status-error-bg` | `#f9eceb` | error background fill |

Brand constraint:
- Barkibu Orange (see [BRAND_GUIDELINES](../shared/brand-guidelines.md)) is used as accent/CTA only.
- Semantic status colors stay muted and never use orange.

### Spacing scale

`4, 8, 12, 16, 20, 24, 32` px

### Radius scale

`--radius-frame: 14px`, `--radius-card: 10px`, `--radius-control: 8px`

Guideline:
- Frame uses `radius-frame`.
- Cards and major panels use `radius-card`.
- Controls (buttons/inputs/toggles/chips) use `radius-control`.

### Text hierarchy

- **Section titles**: stronger size/weight (`text-lg`, `font-semibold`).
- **Body text**: default readable text tokens (`text-text`).
- **Metadata/help**: compact muted hierarchy (`text-xs`, `text-textSecondary`/`text-muted`).

### Focus ring & accent usage

- Focus ring token uses `accent` (`focus-visible:outline-accent`) for keyboard visibility.
- Accent is reserved for primary actions, selected states, and key highlights.
- Accent must not be used as a background wash for all surfaces.

---

## Primitives (shadcn/ui + Radix)

The frontend uses local shadcn-style wrappers backed by Radix primitives under `frontend/src/components/ui`.

Required primitives:
- `Badge` (status / severity variants)
- `Button` (including ghost/icon variants)
- `Card` (content container with header/footer slots)
- `Dialog` (modal overlay for editing / confirmation)
- `Tooltip` + `TooltipProvider`
- `Tabs`
- `Separator`
- `Input`
- `ToggleGroup`
- `ScrollArea`

Rules:
- `Tooltip` content defaults to top placement and renders through portal.
- Tooltip behavior must remain keyboard-accessible (focus/blur + Escape via Radix behavior).
- Use primitive variants and tokens first; avoid one-off utility-class styling when a primitive exists.

---

## App-level wrappers (`components/app`)

Project wrappers standardize repeated review UI patterns:
- `IconButton`: icon-only button with required accessible name + tooltip.
- `Section` / `SectionHeader`: report-like section container and heading row.
- `FieldRow` / `FieldBlock`: label/value row and grouped field block with right-aligned status cluster.
- `ConfidenceDot`: semantic confidence indicator with tooltip (may include a compact breakdown; adjustment text supports positive/negative/neutral treatment).
- `CriticalBadge`: consistent critical marker.
- `RepeatableList`: list container for repeatable values.
- `DocumentStatusChip` (`DocumentStatusCluster` compatibility alias): compact, reusable status chip for document list/sidebar (primary status signal).

---

## Accessibility rules

- **MUST**: icon-only interactive controls must use `IconButton` with required `label`.
- Raw icon-only `<button>` / `<Button>` are forbidden unless explicitly allow-listed as an approved exception.
- Confidence and critical signals cannot rely on color alone (tooltips/labels remain available).
- Tooltips must be keyboard-accessible and must not clip inside scroll containers.

## Tooltip policy (mandatory)

- Use only `frontend/src/components/ui/tooltip.tsx` for tooltip behavior.
- Default placement is `top`.
- Content is rendered via Radix `Portal` to avoid clipping in overflow/scroll containers.
- Do not implement local tooltip logic with ad-hoc `@radix-ui/react-tooltip` usage outside the shared wrapper.

### Confidence tooltip content (standard)

Tooltip template (Spanish):
- `Confianza: 72% (Media)`
- `Indica qué tan fiable es el valor extraído automáticamente.`
- `Desglose:`
  - `Fiabilidad de la extracción de texto: 65%`
  - `Ajuste por histórico de revisiones: +7%`

Adjustment coloring rule:
- `+` uses success semantic styling, `-` uses error semantic styling, `0` uses muted/neutral styling.
- Reuse existing semantic tokens/classes (for example `status-success`, `status-error`, `text-muted`).
- Do not introduce new hex colors for this tooltip pattern.

Accessibility reminder:
- Confidence tooltips must remain keyboard-accessible and must render through the shared tooltip wrapper defined in `frontend/src/components/ui/tooltip.tsx`.

### Icon-only controls: do / don't

Do:
- `<IconButton label="Cerrar panel">✕</IconButton>`
- `<IconButton label="Actualizar" tooltip="Actualizar"> <RefreshCw /> </IconButton>`

Don't:
- `<button aria-label="Cerrar">&times;</button>`
- `<Button aria-label="Actualizar"><RefreshCw /></Button>`

### Exception process (allowlist)

Use exceptions only when `IconButton` cannot represent the interaction semantics (for example, a non-button resize handle).

Required steps:
1. Add a narrow token-based allowlist entry in `scripts/check_design_system.mjs` (`ICON_ONLY_ALLOWLIST`) scoped to file + unique marker.
2. Add rationale to the PR description (why `IconButton` is not viable).
3. Keep keyboard and screen-reader accessibility equivalent or better than the default `IconButton` contract.

---

## Usage examples

### Example 1 — Viewer toolbar icon action

- Use `IconButton` for page/zoom/view actions.
- Provide `label` and concise tooltip text.

### Example 2 — Structured field row

- Wrap field in `FieldBlock`.
- Use `FieldRow` with:
  - left: field label,
  - right: value,
  - status cluster: `CriticalBadge` + `ConfidenceDot`.

### Example 3 — Layered panel composition

- App shell at L1 (`bg-canvas`) over L0 (`bg-page`).
- Main panels at L2 (`bg-surface`, `rounded-card`).
- Toolbars and control groups at L3 (`bg-surfaceMuted`, `rounded-control`).

---

## Enforcement

Use `npm run check:design-system` in `frontend/`.

Current checks:
- flags hard-coded hex colors outside token/config allowlist,
- flags direct inline Radix tooltip primitive usage outside the shared tooltip wrapper,
- flags inline `style={{...}}` outside allowlist,
- flags `IconButton` usage without `label`,
- flags raw icon-only `<button>` and `<Button>` usage outside explicit allowlist.

## Do / Don't

Do:
- Use tokenized Tailwind classes (`bg-surface`, `text-textSecondary`, `border-border`, etc.).
- Use `IconButton`, `DocumentStatusCluster`, and field/section wrappers in review UI.

Don't:
- Add new ad-hoc hex values in component implementation files.
- Reimplement tooltip primitives inline.
- Introduce one-off status chips when `DocumentStatusCluster` matches the need.
