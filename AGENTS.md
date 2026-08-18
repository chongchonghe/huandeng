# Working in this repo

Plain-text slide decks: **Quarto + reveal.js**, built by one shared Python tool.

```
Makefile                repo-wide: make check verifies every deck
tools/build-slides.py   the toolchain — shared, never copied into a deck
themes/                 the ten starting points, each a complete deck of its own.
                        Copy one into talks/; never edit one in place. themes/README.md
demo/                   every feature, working, as a reference deck
talks/                  the user's own decks — gitignored, never commit anything here
trash/                  dead ends, with a README recording why. Read it before
                        proposing LaTeX, Typst or Pandoc's PPTX writer again.
.agents/skills/         the agent skills; .claude/skills symlinks here, as CLAUDE.md does to this file
```

A talk starts as `cp -r themes/<name> talks/<my-talk>`, then `mv template.qmd talk.qmd` — the tool
takes the deck's single `.qmd` and refuses to run if it finds two. A deck is `talk.qmd` +
`_quarto.yml` + `theme.scss` + `fonts.html` + `guides.html` + `fonts/` + `ref.bib` + `attach/`,
plus a `Makefile` that only wraps these — it holds no build logic of its own:

```
make            render out/talk.html
make preview    the same, in a browser that reloads as you save
make check      render, then look at every slide — after ANY slide edit
make png        one PNG per slide, so you can read them
make all        HTML, PDF and PPTX
make standalone one self-contained .html to email
make theme THEME=nord    another look on this deck; make themes lists them
make gallery    every theme side by side, as out/gallery.html
```

`make` and `make preview` need nothing but Quarto, which is why a deck copied anywhere still builds.
The rest drive a headless Chromium, so once per clone:
`uv sync && uv run playwright install chromium`.

Full detail lives in `README.md` and `demo/README.md`. Two skills, separate on purpose:
**quarto-deck** for the machinery — the local classes, the build, the traps — with its reference
docs bundled in `.agents/skills/quarto-deck/docs/`, so it needs no web lookup; and
**quarto-academic-style** for the words, the maths and the house preferences. Skills do not load
each other, so writing a talk usually wants both, asked for by name. Nothing here depends on a
skill installed outside the repository.

## Rules that prevent silent breakage

These fail without an error, so they cannot be left to a lookup:

1. **After ANY slide edit, run `make check`.** An over-full reveal.js slide neither errors nor
   shrinks — the surplus hangs into the margin around the 1280x720 slide box and is then cut by the
   window edge, and a 16:10 laptop shows about 57 slide-px of that where a 16:9 projector shows 15,
   so it can look merely tight while you write it and be cut on stage. Printed, it splits across two
   PDF pages. A `.media-items` row runs off the right with no visual cue at all. `--check` walks the
   built deck in a headless browser and reports content past any edge; press **X** in the deck to
   see the boundary. Exit 1 means look. `make check` from inside the deck, or `make check` at the
   repository root to verify every deck at once. From the root:
   `uv run python tools/build-slides.py <deck> --check`.
2. **The `@font-face` rules live in `fonts.html`, not `theme.scss`.** Quarto compiles the theme five
   directories deep and a relative `url()` resolves against the stylesheet, so moving them into the
   SCSS makes the deck fall back to another typeface and re-flow every line. Silently.
3. **Edit `talk.qmd`.** `theme.scss` is shared API and `_quarto.yml` is configuration; changing
   either affects every slide.
4. **Never edit a `themes/` directory to write a talk.** Copy it into `talks/` first — those ten
   are what everybody starts from, and editing one in place changes every talk written after it.
5. **Never change the aspect ratio of an image or a video.** These are scientific figures: the
   aspect ratio carries meaning. Stretch one and equal axes stop being square, a circle becomes an
   ellipse, an edge-on disk looks face-on — and it still looks like a plausible figure, so nobody
   catches it. Give an image a width *or* a height, never both. `--check` audits every drawn image
   against its own pixel dimensions and fails on any disagreement past 2%.

   One source of this is nobody's mistake: reveal.js caps every image at 95% of its container, so
   inside a shrink-to-fit box — an `.r-stack` cell, a flex item, a `.fig` — the cap squeezes the
   width by 5% while an explicit `height` holds firm. `theme.scss` raises the cap to 100%; a deck
   copied from an older template may not have that fix.

   The trap that is not your fault: a video's stored frame is not always its displayed frame. A
   non-square sample aspect ratio (SAR) means the player stretches it back on the way out, and
   anything through a Keynote or PowerPoint round trip routinely carries one. If you extract frames
   by hand, `ffmpeg -vf scale=iw*sar:ih,setsar=1` is the correction.
6. **A `.gitignore` glob can eat a source file.** `fonts.html`, `guides.html` and `reference.pptx`
   all share a suffix with something the ignore rules are meant to catch. `guides.html` was missing
   from the repository for several commits because of exactly this, invisible until someone cloned
   it fresh. Negations are in `.gitignore`; add one for any new source file whose extension
   collides, and verify with a clone before believing a deck is portable.

## Fix fitting problems in the slide, not the theme

When something overflows or does not fit, change `talk.qmd` first — a `.small` on that one block, a
narrower figure, tighter text, one less bullet. That is one slide's problem and it belongs in one
slide.

Reach for `theme.scss` or `_quarto.yml` only when either is true:

- it is a real flaw in the template — the default is wrong for any deck, not just this content, or
- the same fix would otherwise be repeated on slide after slide.

**Within the slide, shrinking text is the last lever, not the first.** Reach for the layout before
the font: join a wrapped equation onto one line, turn two stacked rows into two columns, cut words.
Text below about 0.7em stops being readable from the back of a room, so a slide that only fits at
0.62em is not a slide that fits — it is a slide with too much on it. See the house style in the
**quarto-deck** skill for the rest. Reveal.js gives no rescue at all here: it does not shrink an
over-full slide, and `auto-stretch` is off, so what does not fit simply hangs off the edge.

## Every deck is self-contained

A deck must render correctly when copied anywhere, on its own, years later.

- **Never factor shared code out into a library at the repo root.** No deck may import from outside
  its own directory. `theme.scss`, `_quarto.yml`, `fonts.html`, `guides.html`, `fonts/` and every
  asset are *copies*, and that duplication is the point.
- **A finished talk is frozen.** Improving a theme must not change a single page of a talk already
  given. That is only guaranteed if the talk owns its copy of everything.
- **Propagate by copying, deliberately.** To give an existing deck a new class, copy it into that
  deck's own `theme.scss` and rebuild. Never by making it import one.
- `themes/university/theme.scss` is where the shared body lives, and `demo/theme.scss` is a separate
  file that happens to be identical to it today. Fix one and copy it; do not symlink them.
- The cost is real — a fix in a theme reaches old decks only if you carry it there — and it is
  accepted knowingly, in exchange for talks that never rot.
- **`themes/` is not an exception.** `make theme THEME=nord` *copies* that theme's `theme.scss` in
  and rewrites the one line of `_quarto.yml` a theme owns; afterwards the deck owns its look and
  renders with `themes/` deleted. Nothing links, and no deck may start linking. `themes/README.md`.

`out/` is not committed and never needs to be: it is rebuilt from the deck's own source.

## Only a browser can render this deck

The layout is CSS. Three separate attempts to get a PDF or a PPTX out of it by another route all
failed the same way, and they are recorded in `trash/README.md` with measurements:

- `--to pdf` renders the Markdown as a **LaTeX article** and throws the deck away
- `--to typst` does the same without the LaTeX
- the Touying bridge makes real slides but drops the columns, the credits, the callouts, the video
  and the theme, and prints `::: notes` into the body
- Pandoc's PPTX writer, even with a styled reference document, reaches the fonts and colours and no
  further

So `--pdf` prints the built deck in headless Chromium through reveal's own `?print-pdf` layout, and
`--pptx` rasterises that PDF into one full-bleed image per slide. **Read `trash/README.md` before
suggesting any of the above again.**

## Verifying

Read the rendered pages and **look at them**. `make png` writes one PNG per slide to `out/png/`.
"It rendered" is not evidence that a slide is legible or that content did not spill.
