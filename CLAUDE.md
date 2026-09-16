# Skeletal System Flashcard Review App — Claude Code Context

## What this is

A single-page flashcard review app for an A&P (Anatomy & Physiology) Unit 2
skeletal system lab exam. Built for Josiah, a nursing-prereq student, from
his own Anki deck (`Type-In Occlusion+` and `Basic (type in the answer with
image)` note types). Meant to be shared with classmates too.

It compiles down to **one self-contained HTML file** — all 227 cards and all
images are embedded inline (JSON + base64 data URIs), so it needs no server,
no database, and no build step at runtime. It can be opened directly from
disk or hosted as a static file anywhere (Netlify, GitHub Pages, a subdomain
via a CNAME record, etc.).

## Repo layout

```
anatomy-flashcards/
├── CLAUDE.md            — this file
├── ETYMOLOGY.md         — human-readable etymology reference, by category
├── build.py             — assembles index.html
├── template.html        — the HTML/CSS/JS shell (edit THIS for feature work)
├── cards.json           — all 227 cards (edit THIS for content changes)
├── images/              — 50 source images referenced by cards.json
├── CNAME                — GitHub Pages custom domain (anatomy.josiahmooreart.com)
└── index.html            — build OUTPUT + the file GitHub Pages serves at the
                             repo root; do not hand-edit
```

This repo IS the GitHub Pages site — `index.html` at the root is both the
build output and the deployed file, so **every content/design change needs a
rebuild + commit + push to actually go live**, not just a local edit.

**Workflow: edit `template.html` and/or `cards.json` and/or `images/`, then
run `python3 build.py`, then commit and push `index.html` (and whatever
source files changed).** The build script has no dependencies beyond the
Python standard library. It reads every image in `images/`, base64-encodes
it, JSON-dumps `cards.json`, and substitutes both into `template.html`'s two
placeholders (`__CARDS_JSON__` and `__IMAGES_JSON__`), writing the result to
`index.html`.

The build script also warns (not errors) if `cards.json` references an image
that isn't in `images/`, or if `images/` has files no card uses — useful
after adding/removing cards.

## Data model — `cards.json`

An array of card objects. Two `type`s exist, mirroring the two Anki note
types the deck was originally built from:

### `type: "occlusion"` (199 of 227 cards)

Ported from the **"Type-In Occlusion+"** Anki note type. The image has
*every* label on it covered by a colored box (`Blockers`), and the box
covering the specific label this card is testing is recolored and marked
with a badge (`termCss`) so the learner knows which blank to answer. The
box is **never actually removed** — even after "revealing" the answer, the
image stays fully occluded. The answer comes from the `term` text shown
below the image, not from uncovering the label. This was a deliberate
design choice carried over from the original deck (so repeated review
doesn't just pattern-match on label position).

```json
{
  "id": 1788641641865,
  "type": "occlusion",
  "category": "Types of Bones (Shape)",
  "definition": "Bones that are longer than they are wide, with a shaft and two ends; e.g. the femur and humerus.",
  "image": "lab_2__0002_bone_types_axial.png",
  "term": "long bones",
  "mnemonic": "",
  "blockers": "<div style=\"position:absolute; left:81.3%; top:8.3%; width:6.9%; height:5.4%; background:#ffeb3b;\"></div>...",
  "whiteout": "",
  "termCss": "<div style=\"position:absolute; left:85.9%; top:24%; width:11.7%; height:4.6%; background:#4caf50;\"></div><div class=\"term-star\" style=\"position:absolute; left:90.7%; top:24.9%; width:2.2%; height:2.8%;\"></div>"
}
```

- `blockers` / `whiteout` / `termCss` are raw HTML strings — a series of
  `position:absolute` `<div>`s with **percentage-based** coordinates,
  meant to sit inside a `position:relative` wrapper the same size as the
  displayed `<img>`. Percentages make them resolution/display-size
  independent. Rendered via `innerHTML`, not escaped — this is trusted
  data (Josiah's own deck), not user input.
  - `blockers`: yellow (`#ffeb3b`) boxes over every label on the image.
  - `whiteout`: white (`#ffffff`) boxes permanently covering irrelevant
    baked-in text on the source image (unrelated to any card's answer).
    Shown on every card that uses this image, front and back.
  - `termCss`: the box highlighting *this* card's target label
    (background `#4caf50` — green, changed from the original Anki
    orange `#ff8a3d` at Josiah's request) plus a `.term-star` div — a
    small badge. **This is currently a green circle with a white "?"**
    rendered via an inline SVG data URI in `.term-star`'s CSS
    (originally a gold star shape via `clip-path`; changed per request).
    Shown on the front only; dropped on the "revealed" back state.
  - Some cards have *two* target boxes in `termCss` (e.g. "atlas" appears
    labeled twice in one image) — don't assume exactly one box per card.

### `type: "marker"` (28 of 227 cards)

Ported from **"Basic (type in the answer with image)"**. Simpler: the
image is shown with a single always-visible SVG marker (a `rect` or
`line`, red stroke via the `--rust` CSS variable) pointing at/outlining
the structure in question. No occlusion — the marker doesn't hide
anything, it just points.

```json
{
  "id": 1788505591976,
  "type": "marker",
  "category": "Divisions of the Skeleton",
  "definition": "The division of the skeleton consisting of the skull, vertebral column, ribs, and sternum — the bones along the body's central axis.",
  "image": "paste-bca7f8cf8a2d4497ec6f1dba82b4353e3861188b.jpg",
  "term": "Axial",
  "mnemonic": "",
  "marker": "<rect x=\"50.0\" y=\"1.5\" width=\"43.1\" height=\"98.1\"></rect>"
}
```

- `marker` is raw SVG markup (percentage coordinates, `viewBox="0 0 100
  100"`), inserted inside an `<svg class="overlay-svg">` sitting over the
  image. Can be empty string (a few cards have no marker — plain
  definition + image + answer, e.g. "hyaline cartilage" originally).

### Common fields
- `id` — original Anki note ID. Stable; used as the card's identity for
  easy/hard marks and localStorage. **Don't reuse an id for a different
  card** — anyone's saved marks would silently apply to the wrong card.
- `category` — one of 43 exact strings (see below). Case- and
  spelling-sensitive; `template.html`'s `BUCKET_DEFS` matches against
  these exact strings.
- `definition`, `mnemonic` — trusted HTML (may contain `<span
  style="color:...">`, `<b>`, etc.), rendered unescaped.
- `image` — filename, must exist in `images/` (or be `null`/omitted for
  a card with no image, though currently every card has one).

## Category buckets (`template.html`)

The 43 raw categories are grouped into 6 toggleable "buckets" shown in the
sidebar (each bucket expandable to reveal/toggle its individual
categories). This mapping is **hardcoded** in `template.html` as
`BUCKET_DEFS`:

- **Vertebral Column and Thorax** (6 categories)
- **Cranium (Skull)** (11 categories)
- **General Osteology** (5 categories)
- **Pectoral Girdle & Upper Limb** (6 categories)
- **Pelvic Girdle & Lower Limb** (9 categories)
- **Histology** — catch-all: computed as *every category not explicitly
  listed above*, not a hardcoded list. Currently the 6
  `Histology - *` categories land here automatically.

**If you add a card with a brand-new category string**, it will silently
fall into "Histology" unless you add it to one of the `BUCKET_DEFS` arrays
in `template.html`. There's a dev-time sanity check you can run in a JS
console (see `BUCKETS` construction in the script) but no automated test
for this currently — worth adding if the deck grows much more.

## Study modes (`template.html`)

Four modes, switched via the "Study Mode" dropdown, all reading from the
same `cards.json`:

1. **Type In Answer** (default) — text input, checked against `term`
   (case-insensitive, whitespace-normalized exact match — no fuzzy
   matching/typo tolerance currently).
2. **Quick Study** — flip-to-reveal, no typing.
3. **Multiple Choice** — 4 options (1 correct + 3 distractors). Distractors
   are pulled from **other cards in the same bucket** first (via
   `findBucketForCategory`), falling back to the whole deck only if the
   bucket doesn't have 3 other unique terms (e.g. "Hyoid Bone" is a
   1-card category). No "Hide Answer" in this mode — selecting an option
   locks it in; move on via Next.
4. **Image Only** — same as Quick Study but the `definition` text is
   hidden.

Easy/hard marks, hide-easy, review-tough-only, active categories, expanded
buckets, and the chosen mode all persist to `localStorage` under the key
`apSkeletalLabGuide.state.v2`, guarded with try/catch (works fine if
storage is unavailable — just doesn't persist).

## Design system

- Fonts: **Fraunces** (display/headers) + **Source Sans 3** (body/UI), via
  Google Fonts `<link>` tags.
- Palette: warm parchment/atlas-plate aesthetic (`--paper`, `--ink`,
  `--rust`, `--verdigris`, `--gold`, `--green`/`--red` for marks and
  feedback), with a dark-mode variant via `prefers-color-scheme` and a
  `data-theme` attribute override.
- No JS framework, no build tooling, no external runtime dependencies
  beyond the two Google Fonts. Vanilla HTML/CSS/JS by design, since the
  whole point is a single portable file.

## Known constraints / gotchas

- **`</script` inside embedded JSON** would break the page if left
  unescaped (e.g. a definition containing that literal string) — `build.py`
  guards against this by replacing `</script` with `<\/script` in both the
  cards and images JSON blobs before injection. If you build the HTML any
  other way, keep that guard.
- **Image size budget**: images are pre-compressed to JPEG (quality ~82,
  capped at 900px on the long edge) before going in `images/`. The current
  50 images total ~2.9MB raw / ~3.9MB base64. Total output file is ~4.3MB.
  Claude.ai's Artifact publish tool caps at 16MB — plenty of headroom, but
  don't paste in full-resolution scans without compressing first.
- **No spaced repetition** — deliberately out of scope per the original
  request. This is flip/type/quiz review only, no scheduling.
- **Not synced across devices** — study marks are per-browser
  (`localStorage`), by design (no backend). See "Hosting" below.

## Hosting

No database or backend needed — see above, it's fully static. Live at
**anatomy.josiahmooreart.com** via GitHub Pages, decided with Josiah:
- This repo's `main` branch, root folder, is the Pages source. `index.html`
  at the root (the build output) is what's actually served.
- `CNAME` file at the repo root holds the custom domain
  (`anatomy.josiahmooreart.com`) — GitHub Pages requires this to keep the
  custom domain configured on every deploy; don't delete it.
- The subdomain points here via a DNS **CNAME record** (`anatomy` →
  `<github-username>.github.io`) at Josiah's DNS provider — separate from,
  and requiring no changes to, his main Jekyll portfolio site/repo.
- If cross-device sync of study marks is ever wanted, that's the trigger
  to add a backend (e.g. Supabase) — additive, not a rewrite, since the
  static core wouldn't change.

## Provenance

Originally built from `A_P__Unit_2__Skeletal_System_Lab_Exam_Guide.apkg`
(Josiah's own Anki export). The `.apkg` format needed some unpacking not
worth re-documenting in depth here since `cards.json`/`images/` are now
the source of truth going forward — but briefly, for reference: modern
`.apkg` files are a zip containing a zstd-compressed SQLite DB
(`collection.anki21b`) plus zstd-compressed media files individually
numbered (`0`, `1`, `2`...) with a separate zstd-compressed protobuf
(`media`) mapping those numbers to real filenames. If Josiah exports a
*new* `.apkg` later with more/changed cards, that whole extraction dance
would need to be redone (decompress `media` → protobuf-parse the name
mapping → decompress each numbered file with a zstd streaming reader →
read `notes`/`fields`/`templates` from the decompressed SQLite → rebuild
`cards.json` entries per the schema above). Ask Josiah if he still has the
`.apkg` if this comes up.
