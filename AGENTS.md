# Working in this repo

Plain-text slide decks in two flavours: **Typst + Touying** at the root, and **Quarto + reveal.js**
under `quarto/`. Each has its own shared build tool.

```
Makefile                repo-wide: make check verifies every deck, both flavours
tools/build-slides.py   the Typst toolchain — shared, never copied into a deck
template/               the Typst starting point: copy it, never edit it in place
demo/                   every Typst feature, working, as a reference deck
quarto/                 the Quarto flavour: tools/, template/, demo/, its own README
talks/                  the user's own decks, either flavour — gitignored, never commit anything here
.agents/skills/         the agent skills; .claude/skills symlinks here, as CLAUDE.md does to this file
```

**The flavours are siblings, not versions.** Neither is deprecated. Pick per talk, and never convert
a deck from one into the other unless asked to. A talk in `talks/` is Typst if it has a `main.typ`
and Quarto if it has a `_quarto.yml`; each toolchain finds only its own.

A Typst deck is `main.typ` + `globals.typ` + `content.typ` + `attach/`. A Quarto deck is
`talk.qmd` + `_quarto.yml` + `theme.scss` + `fonts.html` + `attach/`. Both carry a `Makefile` that
only wraps the commands below and holds no build logic of its own.

Full detail lives in `README.md`, `demo/README.md`, `quarto/README.md` and `quarto/demo/README.md`.
For slide authoring invoke **slide-deck** (Typst) or **quarto-deck** (Quarto); to convert an existing
PowerPoint or Keynote deck invoke **pptx-to-typst**; for Touying itself, the vendored docs are in
`.agents/skills/touying-author/`.

## Rules that prevent silent breakage

These fail without an error, so they cannot be left to a lookup:

1. **After ANY slide edit, run `make check`.** Overflow is silent in both flavours, in different
   ways, and neither raises anything. Exit 1 means look. `make check` from inside the deck, or
   `make check` at the repository root to verify every deck of both flavours at once.
   - *Typst*: an overflowing slide is quietly broken across two pages. `--check` counts the pages
     the source should produce, compares with the built PDF, and names the slide that spilled.
     From the root: `uv run python tools/build-slides.py <deck> --check`.
   - *Quarto*: an over-full reveal.js slide neither errors nor shrinks — the surplus hangs into the
     margin around the 1280x720 slide box and is then cut by the window edge, and a 16:10 laptop
     shows about 57 slide-px of that where a 16:9 projector shows 15, so it can look merely tight
     while you write it and be cut on stage. Printed, it splits across two PDF pages. A
     `.media-items` row runs off the right with no visual cue at all. `--check` walks the built deck
     in a headless browser and reports content past any edge; press **X** in the deck to see the
     boundary. From the root:
     `uv run --extra quarto python quarto/tools/build-slides.py <deck> --check`.
2. **Each flavour has a font trap, and both are silent.**
   - *Typst*: `typst compile` needs `--font-path fonts`. Without it the deck still compiles, falls
     back to another font, and repaginates. The deck's `make` target passes it for you.
   - *Quarto*: the `@font-face` rules live in `fonts.html`, not `theme.scss`, because Quarto
     compiles the theme five directories deep and a relative `url()` resolves against the
     stylesheet. Move them into the SCSS and the deck falls back to another typeface and re-flows.
3. **Edit the content file.** `content.typ` for Typst, `talk.qmd` for Quarto. `globals.typ` and
   `theme.scss` are shared API; `main.typ` and `_quarto.yml` are configuration. Changing any of
   those affects every slide.
4. **Never edit `template/` or `quarto/template/` to write a talk.** Copy it into `talks/` first.
5. **`out/` is not committed** and never needs to be.
6. **Never change the aspect ratio of an image or a video.** These are scientific figures: the
   aspect ratio carries meaning. Stretch one and equal axes stop being square, a circle becomes an
   ellipse, an edge-on disk looks face-on — and it still looks like a plausible figure, so nobody
   catches it. Give an image a width *or* a height, never both, and never `fit: "stretch"`. (Both
   dimensions with Typst's default `fit: "cover"` silently *crops* instead, which is its own way
   to lose data; in the browser they *stretch*.) `--check` audits every drawn image against its own
   pixel dimensions in both flavours and fails on any disagreement past 2%.

   The Quarto flavour has one source of this that is nobody's mistake: reveal.js caps every image
   at 95% of its container, so inside a shrink-to-fit box — an `.r-stack` cell, a flex item, a
   `.fig` — the cap squeezes the width by 5% while an explicit `height` holds firm. `theme.scss`
   raises the cap to 100%; a deck copied from an older template may not have that fix.

   The trap that is not your fault: a video's stored frame is not always its displayed frame. A
   non-square sample aspect ratio (SAR) means the player stretches it back on the way out, and
   anything through a Keynote or PowerPoint round trip routinely carries one — in one real ten-video
   deck, three did, the worst by 2.5x. `--add-movie` reads the *displayed* size with ffprobe and
   squares the pixels on extraction. If you ever extract frames by hand,
   `ffmpeg -vf scale=iw*sar:ih,setsar=1` is the correction.

## Fix fitting problems in the slide, not the theme

When something overflows or does not fit, change the content file first — a smaller font on that
slide, a narrower figure, tighter text, a `#text(size: ..)` wrapper or a `.small` on one block.
That is one slide's problem and it belongs in one slide.

Reach for `globals.typ` / `main.typ`, or `theme.scss` / `_quarto.yml`, only when either is true:

- it is a real flaw in the template — the default is wrong for any deck, not just this content, or
- the same fix would otherwise be repeated on slide after slide.

A worked example of each: University pads section slides 20% a side, leaving 60% of the width, so a
43-character section title wraps — that is a template flaw and `uni-section-slide` fixes it once for
everyone. Its `focus-slide` sets 2em, which is correct for "Wake up!" and too big for a four-line
sentence — that is one slide's content, and `#focus-slide[#text(size: 0.62em)[..]]` is the fix.

**Within the slide, shrinking text is the last lever, not the first.** Reach for the layout before
the font: join a wrapped equation onto one line, turn two stacked rows into two columns, drop a
`#v()`, cut words. Text below about 0.7em stops being readable from the back of a room, so a slide
that only fits at 0.62em is not a slide that fits — it is a slide with too much on it. A worked
example: a two-column slide of IMEX equations went from 0.62em to 0.72em with no content cut, paid
for by collapsing an equations-row-then-plots-row layout into two columns and unwrapping the
equation continuations. See the house style in the **slide-deck** and **quarto-deck** skills for the
rest. Reveal.js gives no rescue at all here: it does not shrink an over-full slide, and
`auto-stretch` is off, so what does not fit simply hangs off the edge.

## Every deck is self-contained

A deck must render correctly when copied anywhere, on its own, years later.

- **Never factor shared code out into a library at the repo root.** No deck may import from outside
  its own directory. `globals.typ`, `main.typ`, `theme.scss`, `_quarto.yml`, `fonts.html`, `fonts/`
  and every asset are *copies*, and that duplication is the point.
- **A finished talk is frozen.** Improving either `template/` must not change a single page of a
  talk already given. That is only guaranteed if the talk owns its copy of everything.
- **Propagate by copying, deliberately.** To give an existing deck a new helper or a new class, copy
  it into that deck's own `globals.typ` or `theme.scss` and rebuild. Never by making it import one.
- The cost is real — a fix in `template/` reaches old decks only if you carry it there — and it is
  accepted knowingly, in exchange for talks that never rot.
- **This applies across flavours too.** `quarto/template/theme.scss` and `quarto/demo/theme.scss`
  are separate files that happen to be identical today. Fix one and copy it; do not symlink them.

## Verifying

Read the rendered pages and **look at them**. For Typst, render the PDF to PNG with PyMuPDF; for
Quarto, `make png` writes one PNG per slide to `out/png/`. "It compiled" and "it rendered" are not
evidence that a slide is legible or that content did not spill.
