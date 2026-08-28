# Visual thesis — The Data Limited

## Direction and rationale

`tabular-file-diff` uses an **art-deco transit poster** system. Large datasets are
treated as express trains: two snapshots enter on parallel tracks, the primary
key is the junction, and additions, removals, and modifications leave on clearly
signed routes. The metaphor makes a technical, terminal-first tool feel fast and
legible without pretending that data comparison is effortless or cloud-based.

This is intentionally a single dark treatment, like a night-platform enamel
sign. It paints every surface explicitly and does not depend on the browser's
color scheme.

## Palette

All colors are CSS tokens and were checked against the midnight background.

| Token | Value | Use |
| --- | --- | --- |
| `--night` | `#101A25` | page background |
| `--platform` | `#172534` | raised surfaces |
| `--paper` | `#F5EBD3` | primary text (13.7:1 on night) |
| `--paper-muted` | `#C6BDA8` | secondary text (9.0:1 on night) |
| `--brass` | `#F2C14E` | primary accent and focus (9.8:1 on night) |
| `--brass-ink` | `#17140C` | text on brass (11.1:1) |
| `--signal` | `#EF6A57` | removals/errors; always paired with a label |
| `--jade` | `#62C6A5` | additions/success; always paired with a label |
| `--sky` | `#72B6D9` | modifications/info; always paired with a label |
| `--line` | `#425366` | structural rules, never body text |

## Typography

- **Display:** `Arial Narrow`, `Avenir Next Condensed`, `Liberation Sans Narrow`,
  sans-serif. Uppercase, slightly tracked, geometric station-poster voice.
- **Utility and prose:** `Inter`, `Avenir Next`, `Segoe UI`, sans-serif. A local
  system stack avoids font downloads and keeps the initial payload small.
- **Code and figures:** `ui-monospace`, `SFMono-Regular`, `Cascadia Code`,
  monospace with tabular figures.
- Scale: 14 / 16 / 20 / 28 / clamp(44–84) px. Body never falls below 16 px.
  Reading measure is capped at 70 characters.

## Layout and spacing

An 8 px base rhythm with 4 px for micro-alignment. Major sections use 80–128 px
vertical spacing on desktop and 56–80 px on mobile. Thin parallel rules evoke
rail tracks; octagonal labels and clipped corners recall enamel wayfinding.
Content groups use proximity first, with borders reserved for genuinely
independent panels. The 390 px layout stacks the route diagram under the copy,
reduces ornamental track lines, and turns comparison metrics into a two-column
grid.

## Interaction grammar

- Primary actions are brass, rectangular with small clipped corners, and begin
  with verbs.
- File inputs read as station platforms: file name is the state, the button is
  the destination marker.
- Results follow one stable order: added / removed / modified / schema.
- The playground's outlined engine ticket names the exact wheel, DuckDB, and
  PyArrow versions after the worker loads. It uses the same enamel-sign shape
  language as the route labels, so implementation proof is part of the visual
  system rather than a generic status badge.
- Focus is a 3 px brass outline with a 3 px offset. Hover never carries meaning
  on its own. Targets are at least 44 px.
- The demo exposes loading, empty, invalid-key, duplicate-key, no-change, and
  offline states with an `aria-live` status line and a concrete recovery action.

## Motion policy

On first view, route lines draw from their source and independent result counts
rise 8 px into place over 220–360 ms. Buttons and tabs use 160 ms opacity,
background, and transform feedback. Nothing loops. Under
`prefers-reduced-motion: reduce`, line drawing and transforms are removed and
state changes are instant opacity swaps. The design's depth remains through
scale, overlap, and color.

## Asset plan and provenance

- `site/public/data-limited-hero.webp`: original AI-generated, text-free
  editorial illustration showing two stylized data trains meeting at a keyed
  junction. Generated for this repository with
  `/opt/fleet/lib/gen-image.sh`, deployment `factory-image`, then downscaled and
  encoded to WebP at ≤300 KB. No reference images; no third-party marks.
- Product mark, route lines, key glyph, and tiny UI icons are hand-authored in
  HTML/CSS or inline SVG. They are simple interface geometry, not stock assets.
- `site/public/og-image.png` and `site/public/apple-touch-icon.png` are
  hand-composed crops of the repository's original `data-limited-hero.webp`.
  They introduce no third-party imagery.

Final generation prompt:

> Use case: stylized-concept. Asset type: landing-page hero illustration.
> Primary request: an original 1930s art-deco transit poster metaphor for a fast
> local tabular data diff tool. Scene: two streamlined abstract trains made from
> neat rows of rectangular data cells approach a precise central brass key-shaped
> junction, then separate into three clearly distinct colored rail routes. Style:
> screen-printed gouache poster, crisp geometric forms, subtle paper grain, deep
> midnight navy, warm ivory, brass gold, signal coral, jade and pale blue.
> Composition: landscape, strong diagonal rails, centered junction, no people.
> Constraints: absolutely no text, letters, numbers, logos, brands, watermarks,
> gradients, photorealism, interface mockups, or illegible signage.
