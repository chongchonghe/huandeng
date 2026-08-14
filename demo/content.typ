#import "globals.typ": *

= Getting started

== Quick start

This deck is three files: `globals.typ` holds shared imports and helpers, `main.typ` holds every
`config-*` call, and `content.typ` — this file — holds the slides. The theme is Touying's built-in
#link("https://touying-typ.github.io/docs/themes/university")[University].

=== Live preview

Install the `tinymist` VS Code extension and open `main.typ`; it re-renders the slide under the
cursor as you type. From a terminal:

```bash
typst watch --font-path fonts main.typ out/talk.pdf
```

== Exporting

`tools/build-slides.py` compiles through the `typst` Python package, so a separate Typst install
is optional.

#side-by-side(columns: (1fr, 1fr))[
  *What you get*

  - `out/<deck>.pdf` — the deck itself
  - `out/<deck>.html` — self-contained, vector, arrow-key navigation
  - `out/<deck>.pptx` — one full-bleed slide image per page
][
  *Commands*

  ```bash
  build-slides.py <deck>         # all three
  build-slides.py <deck> --pdf
  build-slides.py <deck> --html
  build-slides.py <deck> --pptx
  ```
]

PowerPoint has no Typst-native path, so every slide ships as a high-resolution image. Faithful, but
not editable in PowerPoint — treat PPTX as a delivery format, not a source format.

== The rules of the file

- *New section*: a `=` heading; University inserts a section slide automatically
- *New slide*: a `==` heading, set by `config-common(slide-level: 2)`
- *Another slide, same title*: `#pagebreak()`, or a bare `---`
- *Global options*: arguments to `#show: university-theme.with(..)` in `main.typ`
- *Custom layout*: call a slide function instead of writing a bare heading

```typst
#empty-slide[A slide with no chrome]
#slide(composer: (2fr, 1fr))[Left][Right]
#focus-slide[One big statement]
```

== What is Touying?

*Touying* is a presentation package for #link("https://typst.app/")[Typst]. Slides are plain text,
compiled to PDF by a single fast binary.

- Version-controls as cleanly as Markdown, but the markup is a real language
- Themes are functions, so layout helpers are functions too — no CSS escape hatch
- Math is native to Typst: no KaTeX, no MathJax, no browser
- Incremental reveals come for free

#pause

- ...like this line, which becomes its own page in the exported PDF

#speaker-note[
  Speaker notes live next to the slide they belong to. They are invisible in the deck unless you
  enable `config-common(show-notes-on-second-screen: right)`, and they are exported to pdfpc.
]

= Text, code and tables

== Lists and formatting

#side-by-side(columns: (1fr, 1fr))[
  - Ordinary Typst markup
    - `*Bold text*` for emphasis
    - `_Italic text_` for subtle emphasis
    - `` `Inline code` `` for technical terms
  - `#alert[..]` paints text in the theme's accent colour, like #alert[this]
][
  *Nested lists*

  - Main point 1
    - Sub-point A
    - Sub-point B
  - Main point 2
    - Sub-point C
    - Sub-point D
]

== Code highlighting

```python
def hello_world():
    print("Hello, Touying!")
    return True

if __name__ == "__main__":
    hello_world()
```

Typst highlights fenced blocks natively; `main.typ` adds the tinted background with a `show raw`
rule.

== Blockquotes and links

#quote(block: true, attribution: [Alan Kay])[
  The best way to predict the future is to invent it.
]

- #link("https://typst.app/")[Typst official website]
- #link("https://github.com/touying-typ/touying")[Touying GitHub repository]
- #link("https://touying-typ.github.io/")[Touying documentation]

== Tables

// The header table needs the wider column: three prose columns wrap at 1fr, and the wrapped rows
// then push its rule into the headerless table beside it. A real gutter keeps the pair reading as
// two tables rather than one six-column block.
#side-by-side(columns: (1.45fr, 1fr), gutter: 2.2em)[
  *With a header row*

  #head-table(
    columns: 3,
    [Method], [Advantages], [Disadvantages],
    [Method A], [Fast, simple], [Less accurate],
    [Method B], [Accurate], [Slow, complex],
    [Method C], [Balanced], [Moderate],
  )
][
  *Headerless*

  #plain-table(
    columns: 3,
    [Data A], [Data B], [Data C],
    [1.23], [4.56], [7.89],
    [2.34], [5.67], [8.90],
    [3.45], [6.78], [9.01],
  )
]

Both helpers live in `globals.typ`; they are thin wrappers over Typst's `#table`.

= Figures

== One figure with a source credit

Every figure in a talk needs to say where it came from. `#fig` puts that credit tight against the
image's bottom-right corner, at 60% size, so it costs almost no vertical space.

#side-by-side(columns: (1fr, 1fr))[
  ```typst
  #fig(
    "attach/x.png",
    width: 70%,
    credit: [He et al. 2025],
  )
  ```
][
  #fig("attach/placeholder-image.png", width: 52%, credit: [He et al. 2025])
]

== Caption above, a label below, or both

`caption` goes above the figure — the house default, since a slide is read top to bottom. `below`
is the exception, for the second half of a paired label. Both are optional, and so is `credit`.
The first argument may be a path or any content, so a diagram takes a credit the same way.

#side-by-side(columns: (1fr, 1fr, 1fr))[
  #fig(
    "attach/placeholder-image.png",
    width: 76%,
    caption: [Above the figure],
    credit: [Smith 2024],
  )
][
  #fig(
    "attach/placeholder-image.png",
    width: 76%,
    below: [Below the figure],
    credit: [Lee & Park 2023],
  )
][
  #fig(
    "attach/placeholder-image.png",
    width: 76%,
    caption: [Setup],
    below: [Result],
    credit: [He et al. 2025],
  )
]

== A row of figures

#img-row(
  box(width: 4em)[Image 1:],
  image("attach/placeholder-image.png", width: 5cm),
  image("attach/placeholder-image.png", width: 5cm),
  image("attach/placeholder-image.png", width: 5cm),
)

#v(0.5em)

#img-row(
  box(width: 4em)[Image 2:],
  image("attach/slide-fld/shadow-labeled.png", width: 5cm),
  image("attach/slide-m1-quokka/shadow-quokka.png", width: 5cm),
)

#caption[Give the images absolute widths — a percentage inside an `auto` grid column has nothing to
resolve against.]

== Figure beside text

#side-by-side(columns: (3fr, 2fr))[
  Marp docks a background image with `![bg right:40%](..)`. Touying has no background-image syntax;
  you compose the slide instead:

  - `#side-by-side(columns: (3fr, 2fr))[..][..]` splits the page
  - the image is an ordinary `#image(..)` in the right column
  - any ratio works: `(1fr, 1fr)`, `(2fr, 3fr)`, `(1fr, 1fr, 1fr)`

  The figure takes part in the layout rather than floating behind it, so text never collides with
  it.
][
  #image("attach/placeholder-image.png", width: 100%)
]

== A grid of figures

#plain-table(
  columns: 4,
  align: horizon,
  [*Exact Eddington tensor:*],
  image("attach/placeholder-image.png", width: 100%),
  image("attach/placeholder-image.png", width: 100%),
  image("attach/placeholder-image.png", width: 100%),

  [*M1 closure:*],
  image("attach/slide-m1-quokka/shadow-quokka.png", width: 100%),
  image("attach/slide-m1-quokka/shadow-quokka.png", width: 100%),
  image("attach/slide-m1-quokka/shadow-quokka.png", width: 100%),

  [*FLD:*],
  image("attach/slide-fld/shadow-labeled.png", width: 100%),
  image("attach/slide-fld/shadow-labeled.png", width: 100%),
  image("attach/slide-fld/shadow-labeled.png", width: 100%),
)

#caption[Time evolution under three radiation transport methods]

#let zoom = "compressed-BH-accretion-rbh50-zoom"
#let mdot = "compressed-BH-accretion-rbh50-mdot-vs-time"

== Video

PDF has no portable video support, so `#movie` gives each format the best it can do: a flip-book in
the PDF, a real `<video>` in the HTML, a playable movie in the PPTX.

#side-by-side(columns: (3fr, 2fr))[
  ```typst
  #movie("seq")            // 24 pages
  #movie("seq", every: 10) // every 10th
  #movie("seq", every: 1)  // all
  ```

  Drop a folder of PNGs into `movie-frames/`, or run `--add-movie clip.mp4` (or `clip.gif`).
  `every` affects only the PDF; HTML and PPTX always play the whole sequence.
][
  #align(center, movie(zoom, width: 74%))

  // Broken by hand: at this column width the line otherwise orphans "hole" on a line of its own.
  #caption[Gas density around an \ accreting black hole]
]

== Two sequences on one timeline

// The `fr` ratio fixes the relative scale; the outer width keeps the pair inside one page.
#align(center, box(width: 72%, side-by-side(columns: (1080fr, 720fr))[
  #movie(zoom, width: 100%)
][
  #movie(mdot, width: 100%)
]))

#caption[
  Column widths `(1080fr, 720fr)` are the two sequences' pixel widths, so both render at their
  native relative scale. Equal page budgets keep them in lockstep whatever their lengths.
]

= Math and diagrams

== Math

Inline: the equation $E = m c^2$ sets in the surrounding text without a separate renderer.

Display:

$ (partial E) / (partial t) + nabla dot bold(F) = 4 pi rho j - rho kappa c E $

Aligned:

$
  (partial E_nu) / (partial t) + nabla dot bold(F)_nu &= 4 pi rho j_nu - rho kappa_(nu,a) c E_nu \
  1 / c (partial bold(F)_nu) / (partial t) + c nabla dot bb(P)_nu &= -rho kappa_(nu,a) bold(F)_nu
$

== Math that builds up

Touying's `#pause` works inside `$ ... $`, so an equation can arrive one term at a time:

$
  underbrace(1 / c (partial bold(F)) / (partial t), "time dependence")
  #pause
  + underbrace(c nabla dot bb(P), "transport")
  #pause
  = underbrace(-rho kappa_a bold(F), "absorption")
$

#pause

Each `#pause` costs one extra page in the PDF and nothing in the source.

== Diagrams

Mermaid needs a `<script>` tag from a CDN. Typst draws the diagram itself with
#link("https://typst.app/universe/package/fletcher")[fletcher], offline and as vectors.

#align(center)[
  #diagram(
    node-stroke: 0.6pt,
    spacing: (26mm, 12mm),
    node((0, 0), [Start], corner-radius: 2pt),
    edge("-|>"),
    node((0, 1), [Decision?], shape: fletcher.shapes.diamond),
    edge((0, 1), (-1, 2), "-|>", label: [Yes], label-pos: 0.6, label-side: left),
    node((-1, 2), [Process 1], corner-radius: 2pt),
    edge((0, 1), (1, 2), "-|>", label: [No], label-pos: 0.6, label-side: right),
    node((1, 2), [Process 2], corner-radius: 2pt),
    edge((-1, 2), (0, 3), "-|>"),
    node((0, 3), [End], corner-radius: 2pt),
    edge((1, 2), (0, 3), "-|>"),
  )
]

#caption[Flowchart drawn with fletcher]

= Wrapping up

== Reference

- *Theme*: `#import themes.university: *`, then `#show: university-theme.with(..)` in `main.typ`
- *Assets*: keep images under the deck's `attach/`, reference them as `attach/foo.png`
- *Slide functions*: `#slide(..)`, `#title-slide()`, `#focus-slide[..]`, `#new-section-slide(..)`
- *Helpers in `globals.typ`*: `fig` (figure + source credit), `movie`, `side-by-side`, `caption`, `img-row`, `head-table`, `plain-table`
- *Splitting the deck further*: move `content.typ` into `sections/` and `#include` several files
- *Animation*: `#pause`, `#meanwhile`, `#uncover`, `#only`, `#alternatives`
- *Presenter tools*: `#speaker-note[..]` exports to #link("https://pdfpc.github.io/")[pdfpc] and
  Pympress with `config-common(enable-pdfpc: true)`

#focus-slide[
  Thanks!

  #v(0.4em)

  #text(size: 0.5em)[
    Questions? Comments? Feedback welcome! \
    your.email\@university.edu
  ]
]
