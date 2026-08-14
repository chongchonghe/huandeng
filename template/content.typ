#import "globals.typ": *

= First section

== A slide

Start each slide with `==`. A `=` heading opens a section and gets its own divider slide.

- Bullets, *bold*, _italic_, `inline code`
- `#alert[..]` picks up the theme colour, like #alert[this]

#pause

- `#pause` reveals the rest of the slide on the next page

#speaker-note[
  Notes live next to the slide they belong to and never appear in the deck.
]

== A figure with its source

Academic slides credit every borrowed figure. `#fig` puts the credit tight under the image,
right-aligned, at 60% size:

#fig(
  "attach/placeholder.png",
  width: 40%,
  credit: [He et al. 2025],
)

Add `caption:` for a description above the figure, or `below:` for one under it.

== Two columns

#side-by-side(columns: (3fr, 2fr))[
  `#side-by-side` splits the body of a slide. The column ratio is yours to choose.

  Maths is native:

  $ (partial E) / (partial t) + nabla dot bold(F) = 4 pi rho j $
][
  #head-table(
    columns: 2,
    [Method], [Cost],
    [A], [low],
    [B], [high],
  )
]

= Second section

== Wrapping up

Delete these slides and write your own. What is worth keeping:

- `main.typ` — title, theme, colours, footer
- `globals.typ` — the helpers (`fig`, `movie`, `side-by-side`, `head-table`, ...)
- `fonts/` — so the deck renders the same on any machine

#focus-slide[
  Thank you
]
