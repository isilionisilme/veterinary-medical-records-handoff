---
title: "Barkibu — Brand Guidelines (Project Canonical)"
type: reference
status: active
audience: all
last-updated: 2026-03-02
---

# Barkibu — Brand Guidelines (Project Canonical)

> **Canonical source of truth.** This file is a canonical document maintained by humans.
> Derived router files are auto-generated from this canonical source. Flow is **canonical → router only**.
> Router files MUST NOT be edited directly.

**Breadcrumbs:** [Docs](../../README.md) / Shared / 01-product

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Purpose](#purpose)
- [Scope & precedence](#scope--precedence)
- [Brand character](#brand-character)
- [Color system (exact values)](#color-system-exact-values)
  - [Primary accent](#primary-accent)
  - [Backgrounds & surfaces](#backgrounds--surfaces)
  - [Text](#text)
  - [Borders/dividers](#bordersdividers)
  - [Semantic support colors (muted)](#semantic-support-colors-muted)
- [Typography](#typography)
- [Layout & density rules (productivity UI)](#layout--density-rules-productivity-ui)
  - [Header](#header)
  - [Surfaces](#surfaces)
  - [Accent usage](#accent-usage)
- [Components](#components)
  - [Buttons](#buttons)
  - [Links](#links)
  - [Cards](#cards)
  - [Confidence/status pills](#confidencestatus-pills)
- [Tokenization (implementation requirement)](#tokenization-implementation-requirement)
- [Tone of voice (UI copy)](#tone-of-voice-ui-copy)
  - [General](#general)
  - [Preferred product naming (internal tool)](#preferred-product-naming-internal-tool)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Purpose

Single source of truth for **visual identity** (colors/typography/layout primitives) and **UI copy tone** used by Codex
and contributors. This document is normative for shared brand tokens and UI tone decisions.

## Scope & precedence

- Applies to: **UI styling** and **user-facing text** only.
- Does not define: product behavior, UX flows, business rules.
- If there is conflict: **UX/requirements docs > this file**.

---

## Brand character

The UI must feel:

- Calm, trustworthy, healthcare-adjacent
- Modern, restrained, productivity-oriented

Avoid:

- Marketing "hero" aesthetics inside the tool
- Flashy gradients, heavy shadows, playful/experimental UI
- Overly corporate or legalistic copy

---

## Color system (exact values)

Use **only** these values unless explicitly instructed otherwise.

### Primary accent

- **Barkibu Orange:** `#FC4E1B`

Use for:

- Primary CTA buttons
- Key highlights
- Main page title (H1)

Do not use orange as semantic status (error/warn/success).

### Backgrounds & surfaces

- **Page background:** `#EBF5FF`
- **Card/surface background:** `#FFFFFF`

Rule: default = **light-blue page background + white cards**.

### Text

- Primary text: `#1F2933`
- Secondary text: `#6B7280`
- Muted/metadata: `#9CA3AF`

Avoid pure black (`#000000`).

### Borders/dividers

- Default border/divider: `#E5E7EB`
- Subtle separators: `#EEF1F4`

### Semantic support colors (muted)

Use only for meaning (status, confidence). Keep them subtle.

- Success: `#4CAF93`
- Warning/uncertainty: `#E6B566`
- Error: `#D16D6A`

---

## Typography

- Primary font: **Inter**
- Fallback stack:

```css
font-family:
  "Inter",
  system-ui,
  -apple-system,
  "Segoe UI",
  Roboto,
  sans-serif;
```

Recommended weights:

- Body: 400-500
- Headings: 600

---

## Layout & density rules (productivity UI)

### Header

- Keep it **compact** (app header), not a marketing hero.
- Avoid large white blocks behind the title.
- Prefer minimal vertical space to maximize the working area.

### Surfaces

- Prefer white cards with gentle borders.
- Padding inside cards: comfortable but not wasteful (aim for clarity).

### Accent usage

- Orange is an **accent**, not the primary UI color.
- Most structure should be neutral (grays/white).

---

## Components

### Buttons

- Primary: background `#FC4E1B`, text `#FFFFFF`
- Secondary: neutral outline or light fill; neutral text

### Links

- Evidence/source links can use orange when they are meaningful actions.
- Utility links can remain neutral.

### Cards

- White background, subtle border.
- Shadows (if used) must be soft; avoid heavy elevation.

### Confidence/status pills

- Use semantic colors (success/warn/error).
- Never use orange as a "warning/low confidence" color.

---

## Tokenization (implementation requirement)

Avoid scattering hex codes across components.

Preferred (Tailwind): extend theme with:

- `brand.accent = #FC4E1B`
- `brand.bg = #EBF5FF`

Alternative: CSS variables:

- `--brand-accent: #FC4E1B;`
- `--brand-bg: #EBF5FF;`

---

## Tone of voice (UI copy)

### General

- Clear, calm, professional
- Short, task-oriented
- Prefer concrete verbs; avoid marketing slogans

### Preferred product naming (internal tool)

Use language aligned with claims/reimbursements:

- **"Revisión de reembolsos veterinarios"** (recommended H1)
- "Revisión de reclamaciones"
- "Documentos"
- "Datos estructurados"
- "Fuente"

Avoid:

- "Carga asistiva de documentos"
- "Revisión asistida editorial veterinario"
- Over-explaining obvious actions with long helper sentences
