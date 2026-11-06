# Design

<!-- impeccable:design-schema 1 -->

## World

Citadel is a **sovereign control-room terminal** — an instrumented enclosure, not a
dark-themed chat app. Strict monochrome. The interface reads like instrumentation:
hairline-divided panels, corner registration crosshairs, an engineering dot-grid field
behind the conversation, and uppercase tracked mono labels for all metadata. The world
earns its character from structure and typography, never from color or ornament.

Mode: **Operate** (a working tool). Controls stay standard; the world lends only type,
density, and one signature move.

## Palette

Monochrome only — no hue anywhere.

| Token | Value | Role |
|---|---|---|
| `--color-ground` | `#0a0b0d` | app ground (control-room dark, low glare) |
| `--color-panel` | `#0e1013` | rails, composer, modals |
| `--color-line` | `#1e2227` | hairline seams (1px) |
| `--color-line-bright` | `#2b3037` | active seams, crosshairs, scrollbar |
| `--color-ink` | `#e8eaed` | primary text, active state |
| `--color-ink-dim` | `#8a9099` | secondary text, user turns |
| `--color-ink-faint` | `#565c63` | metadata, placeholders, idle icons |

Dark chosen from the use scene: confidential industrial operators, often low-light
control rooms; dark reduces glare and signals instrumentation.

## Type

Self-hosted (no CDN — the product is air-gapped).

- **Inter Variable** — UI and reading text. 13–14px body.
- **IBM Plex Mono** (400/500) — all metadata, labels, timestamps, status, coordinates,
  and document bodies. Mono is used only for data/measurement/identifiers, never as a
  "technical" costume.
- `.label` utility: 10px, `letter-spacing: 0.18em`, uppercase, `ink-faint`.

## Signature move

**Engineering dot-grid field** (`.dotfield`, 22px radial dots at ~5% white) behind the
transcript, plus **corner registration crosshairs** (`.crosshairs`) on the app frame.
The retrieval state is a **scan hairline** sweeping a 1px rule, not a spinner or bouncing
dots. Status is a single blinking 1.5px square (`.live-dot`).

## Structure

Three vertical zones split by 1px hairlines:
- **Left rail (240px)** — wordmark lockup, New session, session log with mono timestamps,
  air-gap footer.
- **Center** — status strip (ONLINE · LOCAL · model), transcript on the dot-grid with
  `USER` / `NODE` gutter labels, composer with `>` prompt pinned bottom.
- **Right rail (288px)** — Corpus header + count, Upload, file list, format footer.

## Components

- **Icons:** authored SVG, single 1.5 stroke, `currentColor` (`src/icons.jsx`). No emoji,
  no icon font.
- **Buttons/controls:** flat, hairline-bordered, text + optional icon; hover lifts ink
  from dim→full or adds `bg-white/[0.03]`.
- **Inputs:** transparent on panel, 1px border, border brightens on focus; global
  `:focus-visible` = 1px ink outline.
- **Modal (DocViewer):** bordered panel, mono body, line count in header.

## Browser surfaces

Themed from the palette: `::selection` inverts (ink ground / dark text); scrollbars use
`--color-line-bright`; focus ring is 1px ink; placeholders are `ink-faint`.

## Bans honored

No gradients, no glass/blur decoration, no color, no emoji icons, no kicker/eyebrow, no
same-size card grids, no colored border-left, no CDN fonts.
