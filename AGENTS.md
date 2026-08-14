# Working in this repo

Plain-text slide decks: Typst + Touying, built by one shared Python tool.

```
Makefile                repo-wide: make check verifies every deck
tools/build-slides.py   the toolchain — shared, never copied into a deck
template/               the starting point: copy it, never edit it in place
demo/                   every feature, working, as a reference deck
talks/                  the user's own decks — gitignored, never commit anything here
.agents/skills/         the agent skills; .claude/skills symlinks here, as CLAUDE.md does to this file
```

A deck is `main.typ` + `globals.typ` + `content.typ` + `attach/`, plus a `Makefile` that only
wraps the two commands below — it holds no build logic of its own.
Full detail lives in `README.md` and `demo/README.md`. For slide authoring invoke the
**slide-deck** skill; to convert an existing PowerPoint or Keynote deck invoke **pptx-to-typst**;
for Touying itself, the vendored docs are in `.agents/skills/touying-author/`.

## Rules that prevent silent breakage

These fail without an error, so they cannot be left to a lookup:

1. **After ANY slide edit, run `--check`.** An overflowing slide does not error — Typst silently
   breaks it across two pages. `--check` counts the pages the source should produce, compares that
   with the built PDF, and names the slide that spilled. Exit 1 means look.
   `make check` from inside the deck, or `uv run python tools/build-slides.py <deck> --check`
   from the repo root; `make check` at the root verifies every deck at once.
2. **`typst compile` needs `--font-path fonts`.** Without it the deck still compiles, falls back to
   another font, and repaginates. The deck's `make` target passes it for you, which is the reason
   to prefer it over a hand-typed `typst compile`.
3. **Edit `content.typ`.** `globals.typ` is shared API and `main.typ` is configuration; changing
   them affects every slide.
4. **Never edit `template/` to write a talk.** Copy it into `talks/` first.
5. **`out/` is not committed** and never needs to be. It is byte-reproducible.
6. **Never change the aspect ratio of an image or a video.** These are scientific figures: the
   aspect ratio carries meaning. Stretch one and equal axes stop being square, a circle becomes an
   ellipse, an edge-on disk looks face-on — and it still looks like a plausible figure, so nobody
   catches it. Give `image` a width *or* a height, never both, and never `fit: "stretch"`. (Both
   dimensions with Typst's default `fit: "cover"` silently *crops* instead, which is its own way
   to lose data.) `--check` audits every drawn image against its own pixel dimensions and fails on
   any disagreement past 2%.

   The trap that is not your fault: a video's stored frame is not always its displayed frame. A
   non-square sample aspect ratio (SAR) means the player stretches it back on the way out, and
   anything through a Keynote or PowerPoint round trip routinely carries one — in one real ten-video
   deck, three did, the worst by 2.5x. `--add-movie` reads the *displayed* size with ffprobe and
   squares the pixels on extraction. If you ever extract frames by hand,
   `ffmpeg -vf scale=iw*sar:ih,setsar=1` is the correction.

## Fix fitting problems in the slide, not the theme

When something overflows or does not fit, change `content.typ` first — a smaller font on that
slide, a narrower figure, tighter text, a `#text(size: ..)` wrapper. That is one slide's problem
and it belongs in one slide.

Reach for `globals.typ` or `main.typ` only when either is true:

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
equation continuations. See the house style in the **slide-deck** skill for the rest.

## Every deck is self-contained

A deck must render correctly when copied anywhere, on its own, years later.

- **Never factor shared code out into a library at the repo root.** No deck may import from outside
  its own directory. `globals.typ`, `main.typ`, `fonts/` and every asset are *copies*, and that
  duplication is the point.
- **A finished talk is frozen.** Improving `template/` must not change a single page of a talk
  already given. That is only guaranteed if the talk owns its copy of everything.
- **Propagate by copying, deliberately.** To give an existing deck a new helper, copy that helper
  into the deck's own `globals.typ` and rebuild it. Never by making it import one.
- The cost is real — a fix in `template/` reaches old decks only if you carry it there — and it is
  accepted knowingly, in exchange for talks that never rot.

## Verifying

Read the rendered pages — render to PNG with PyMuPDF and look at them. "It compiled" is not
evidence that a slide is legible or that content did not spill.
