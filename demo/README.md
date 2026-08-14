# Demo deck

Every feature of this repo's Typst + Touying setup, working, with commentary. **Read it; do not start from it** — start from [`template/`](../template/), which is the same machinery with the sample assets stripped out.

Built on [Typst](https://typst.app/) + [Touying](https://touying-typ.github.io/) with Touying's built-in **University** theme. It began as a port of `inbox/marp-template/`.

## Files

| File | Purpose |
| --- | --- |
| `main.typ` | Entry point. Every `config-*` call, the theme, and the title/outline slides. |
| `content.typ` | The slides. This is the file you edit day to day. |
| `globals.typ` | Shared imports and small helpers (`fig`, `movie`, `side-by-side`, `caption`, `img-row`, `head-table`, `plain-table`). Imported by both of the above, so it must not import either. |
| `attach/` | Images. Reference them as `attach/foo.png`. |
| `movie-frames/` | One directory of PNGs per movie, plus the generated `manifest.json`. See [Movies and animations](#movies-and-animations). |
| `fonts/` | Optional. Any `.otf`/`.ttf` here is passed to the compiler, which is how you make the deck render identically off this machine. |

The deck holds no build script: exports come from the shared `tools/build-slides.py` at the repository root.

This is the three-file layout Touying recommends for decks that outgrow a single file: separating `globals.typ` from `main.typ` lets both `main.typ` and `content.typ` import it without a circular reference. When `content.typ` gets long, move it to `sections/` and `#include` several files from `main.typ`.

## Writing slides

- `=` starts a section and emits a section slide automatically
- `==` starts a slide (`config-common(slide-level: 2)` in `main.typ`)
- `#pagebreak()` or a bare `---` adds a page under the same title
- `#pause` reveals the rest of the slide on the next page
- `#slide(..)`, `#focus-slide[..]`, `#empty-slide[..]` for custom layouts
- `#side-by-side(columns: (3fr, 2fr))[left][right]` splits the *body* of a slide into columns; `#slide(composer: ..)` also gives columns but always begins a new slide

## Figures and source credits

Academic slides need a source on every borrowed figure. `#fig` puts it tight against the image's
bottom-right corner at 60% size, so it costs almost no vertical space:

```typst
#fig("attach/shock.png", width: 70%, credit: [He et al. 2025])
```

A caption goes **above** the figure: a slide is read top to bottom, so it should say what the panel
is before the eye reaches it. `below` is there for the exception — the second half of a paired
label, or a note that belongs to the image rather than to the slide.

```typst
#fig("attach/a.png", caption: [Initial condition],   credit: [Smith 2024])
#fig("attach/b.png", below: [After 10 Myr],          credit: [Lee & Park 2023])
#fig("attach/c.png", caption: [Setup], below: [Result], credit: [He et al. 2025])
```

| argument | default | |
| --- | --- | --- |
| first | — | image path, **or any content** — a diagram, a grid, a table |
| `width` | `100%` | of the container, so it works inside `side-by-side` columns |
| `credit` | `none` | 60% size, grey, right-aligned to the figure's own edge |
| `caption` / `below` | `none` | 80% size, grey, centred; `caption` above, `below` under |
| `credit-gap` | `0.15em` | space between image and credit |
| `gap` | `0.45em` | space around the descriptions |

The credit aligns to the **figure's** right edge, not the slide's, so it stays put whatever `width`
you give. Because the first argument accepts content, a `fletcher` diagram or an `img-row` takes a
credit exactly the same way.

## Movies and animations

Everything animated comes from **a folder of PNG frames** in `movie-frames/`. One call plays it:

```typst
#movie("zoom")              // sampled to 24 PDF pages
#movie("zoom", every: 10)   // every 10th frame
#movie("zoom", every: 1)    // all of them
#movie("zoom", width: 90%)
```

`every` and `budget` affect **only the PDF flip-book**. The mp4 is always encoded from *every*
frame, so HTML and PPTX always play the whole sequence at full rate.

### 1. You already have a folder of frames

Drop it in and tell the build about it:

```bash
cp -r /path/to/my-frames talks/my-talk/movie-frames/zoom
uv run python tools/build-slides.py talks/my-talk --sync-frames
```

Then `#movie("zoom")`. The directory name is the movie name — nothing else to configure.

### 2. You have a movie file

```bash
uv run python tools/build-slides.py talks/my-talk --add-movie ~/sim/render.mp4
```

Frames are extracted into `movie-frames/render/`, the source frame rate is probed and recorded, and
the command prints the line to paste. Options: `--name`, `--fps`, `--max-width` (default 1280),
`--force` to replace an existing sequence. The source file is not copied into the repository.

### 3. You have a GIF

The same command — `--add-movie clip.gif`. There is no GIF-specific path and cannot be: PDF has no
animation, and **Typst loads GIFs but renders them static**. Extracting frames is the only way to
show motion. `ffmpeg`'s `fps` filter also resamples a GIF's variable per-frame delays onto a
constant rate, so the timing survives.

### What each format gets

| Format | What you get |
| --- | --- |
| PDF | a flip-book — one sampled frame per subslide |
| HTML | a real `<video>` with controls, inlined as a data URI |
| PPTX | a PowerPoint movie shape, playable in the slideshow |

Typst has no idea what it is being compiled into, so the branch is driven from outside:

1. `build-slides.py` compiles each export with a different `sys.inputs.target`, which `globals.typ` reads into `#let target`.
2. For `pdf`, `#movie` renders a flip-book. Otherwise it draws only the poster frame and emits `#metadata((src, poster, page, x, y, w, h)) <video-rect>` recording the rectangle it occupies.
3. `build-slides.py` queries those rectangles and covers each one: a percentage-positioned `<video>` over the inline SVG in the HTML, `shapes.add_movie(...)` at the same coordinates in the PPTX.
4. The mp4s are encoded from the frames into `out/media/`, so only frames live in the repository.

### The manifest

Typst **cannot list a directory** ([typst#2123](https://github.com/typst/typst/issues/2123)), so
`movie-frames/manifest.json` records what exists and `#movie` reads it with `#json()`. It is
regenerated at the start of every build and committed, so a bare `typst compile main.typ` works
without Python. `--sync-frames --check` exits non-zero if it is stale — the CI hook.

### Consequences worth knowing

- **`ffmpeg` is required** for `--add-movie`, and for the HTML and PPTX targets. A PDF-only build does not need it.
- **The PDF and the HTML/PPTX have different page counts** — a flip-book spends a page per frame, a video spends one. That is the point of the branch, not a bug.
- **Every flip-book frame is a PDF page.** The 24-page budget is the guard; `every: 1` opts out of it. After each PDF build the tool prints what every movie cost:

  ```
  movies:
    zoom  250 frames → 24 PDF pages
  ```

- **A slide that overflows does not error** — Typst just breaks it across two pages. Sometimes the extra page repeats the slide counter (a movie reporting 24 pages but occupying 47), sometimes it advances it, so the safest check is the deck's total page count against what you expect. Either way the fix is the same: shrink the image or the surrounding text.
- **`--link-video`** references `out/media/*.mp4` from the HTML instead of inlining them. Much smaller file, but no longer self-contained.
- **`--html-frames`** picks the other way to put a movie in the HTML. The default embeds one real `<video>` per sequence; this flag instead stacks the sequence's own PNG frames and reveals one at a time with a generated `@keyframes` rule. It is pure CSS — no player, no codec, no `ffmpeg` at all. It behaves like the `<video>` it replaces: parked on its first frame until the slide's first `space`, then playing through once and holding on the last frame rather than looping, and rewound when you leave the slide so returning re-arms that `space`. The cost is weight: the frames embed roughly twice the mp4 (the demo goes from 5.8 MB to 11.9 MB), so reach for it when a browser will not play your codec or when `ffmpeg` is unavailable. Combines with `--link-video`, which then points at `../movie-frames/` instead of inlining. The PDF and PPTX are unaffected.

## Live preview

Install the `tinymist` VS Code extension and open `main.typ`. It re-renders the slide under your cursor as you type. From a terminal, if you have the Typst CLI:

```bash
typst watch --font-path fonts main.typ out/talk.pdf
```

## Export

```bash
# From the repository root. `typst compile main.typ talk.pdf` needs none of this if you only want the PDF.
uv run python tools/build-slides.py demo
uv run python tools/build-slides.py demo --pdf
uv run python tools/build-slides.py demo --html
uv run python tools/build-slides.py demo --pptx --dpi 300
uv run python tools/build-slides.py demo --html --link-video
uv run python tools/build-slides.py demo --html --html-frames
```

Python dependencies (`typst`, `pymupdf`, `python-pptx`) are declared in the `pyproject.toml` at the repository root; `uv run` installs them on first use, so no separate Typst install is needed.

What each target is:

- **PDF** — the deck, straight from the Typst compiler. One page per `#pause` step.
- **HTML** — a single self-contained file: one inline SVG per slide, any videos inlined as data URIs, plus a small viewer (arrow keys or click to navigate, `f` for fullscreen, `#7` in the URL jumps to slide 7). Space keeps one rhythm across the whole deck: on a slide with video the first press starts every video on it at once and the next press moves on; on any other slide it just advances. Leaving a slide rewinds its videos, so coming back re-arms the first press. The slide always scales to the largest 16:9 box the window allows, so it is full-bleed on a projector without zooming; the page counter fades out when idle. Vector, no CDN, no network access. Typst numbers SVG ids per page, so `build-slides.py` namespaces them before inlining, otherwise glyphs from different slides would collide.
- **PPTX** — one full-bleed rendered image per slide, plus real movie shapes where the deck has video. PowerPoint has no Typst import path, so this is a delivery format, not a source format; nothing but the videos is live.

## Reproducing this from scratch

Everything needed is in the repository. On a clean checkout:

```bash
brew install typst
cd template && typst compile --font-path fonts main.typ out/talk.pdf   # PDF only, no Python

brew install ffmpeg                                # for the other two targets
uv run python tools/build-slides.py demo
```

`uv` reads `pyproject.toml` + `uv.lock` at the repository root and installs exact versions; the Typst compiler itself arrives as the `typst` wheel, so there is nothing to install by hand. The `@preview` packages (`touying`, `fletcher`, `numbly` and their transitive `cetz`, `oxifmt`) are version-pinned in the source and fetched into Typst's own cache on first build — verified against a cold cache, so a fresh machine resolves all five.

**Two clean builds are byte-identical**, verified by hashing `out/` after deleting it and rebuilding — PDF, HTML, PPTX and the encoded mp4s. Two things had to be fixed to get there, and both are worth knowing if you change the pipeline:

- python-pptx stamps each zip member with the current time, so `build-slides.py` rewrites the archive with a fixed timestamp. The member contents were already identical.
- x264 is deterministic for the same version and flags, so the mp4s — and therefore the HTML that inlines them — are stable. A different ffmpeg build may produce different bytes for the same frames.

### Fonts are shipped with the deck

University is set in **Fira Sans**, which is not installed on most machines. Rather than
depend on that, every deck carries its own copy: `fonts/` holds Fira Sans and Fira Math (both
[OFL](https://openfontlicense.org/), redistributable), about 2.2 MB.

`build-slides.py` passes that directory to the compiler automatically. The bare CLI does not, so
tell it:

```bash
typst compile --font-path fonts main.typ out/talk.pdf
# or: export TYPST_FONT_PATHS=fonts
```

Without it you get `warning: unknown font family: fira sans` and Typst falls back — to Helvetica
Neue on macOS, and all the way to its serif default on Linux, CI or Windows, where the deck no
longer looks like this one. `build-slides.py` also inspects the fonts actually embedded in the PDF
and warns if none of the intended families made it in, so a silent fallback cannot go unnoticed.

Copying the fonts into each deck rather than sharing one directory is deliberate: it is what lets a
talk folder be copied, archived or emailed and still render identically. The cost is 2.2 MB per
talk.

Maths is unaffected either way: `New Computer Modern Math` ships with Typst itself.
