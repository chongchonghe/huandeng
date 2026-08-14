// Entry file: all configuration lives here, all content lives in `content.typ`.
//
//   typst watch --font-path fonts main.typ out/template.pdf
//   uv run python tools/build-slides.py <deck>     # PDF + HTML + PPTX

#import "globals.typ": *

// Fira Sans ships in fonts/; the rest of the list are fallbacks if it is ever removed.
#set text(font: ("Fira Sans", "Helvetica Neue", "Helvetica", "Arial"))
#show math.equation: set text(font: ("Fira Math", "New Computer Modern Math"))

#show: university-theme.with(
  aspect-ratio: "16-9",
  // The logo belongs on the title slide, not in the header of every slide.
  header-right: none,
  // Speaker · talk · date and page number, in grey with no fill — see `uni-slide` in globals.typ.
  footer-a: self => [#self.info.author (#self.store.short-institution)],
  footer-b: self => utils.call-or-display(self, self.info.short-title),
  footer-c: self => context {
    utils.slide-counter.display() + " / " + utils.last-slide-number
  },
  config-colors(
    // Brighter than the theme's default navy (#04364A): a clear azure that still reads on a
    // projector, with two lighter steps for section slides and accents.
    primary: rgb("#0A6EBD"),
    secondary: rgb("#2E97DB"),
    tertiary: rgb("#6FC2E8"),
    neutral-lightest: rgb("#ffffff"),
    neutral-darkest: rgb("#1A1A1A"),
  ),
  // The theme's default top margin is 2em with `header-ascent: 0`, so the running title sits
  // directly on the body, hard against the top edge. Buy room above and below it.
  config-page(margin: (top: 3.4em, bottom: 1.9em, x: 2em)),
  // Our slide function, for the quiet footer.
  config-common(slide-fn: uni-slide),
  // Short forms used by the footer.
  config-store(short-institution: [Your Institute]),
  config-info(
    title: [Huandeng: a Typst + Touying deck, feature by feature],
    subtitle: [Every helper in this repo, working],
    author: [Your Name],
    short-title: [Huandeng demo],
    date: datetime.today(),
    institution: [Your Institute],
    logo: image("attach/placeholder-logo.png", width: 2.5cm),
  ),
  config-common(
    // `=` starts a section, `==` starts a slide.
    slide-level: 2,
    datetime-format: "[day] [month repr:short] [year]",
  ),
)

// University sets 25pt, which is generous for a slide with a figure and a caption on it. This
// `set` comes after the theme's show rule, so it wins.
#set text(size: 20pt)

// Number sections `1.`, slides `1.1`.
#set heading(numbering: numbly("{1}.", default: "1.1"))

// Code blocks read better with a tinted background.
#show raw.where(block: true): it => block(
  width: 100%,
  fill: luma(245),
  inset: 8pt,
  radius: 3pt,
  text(size: 0.8em, it),
)
#show raw.where(block: false): it => box(
  fill: luma(240),
  inset: (x: 3pt),
  outset: (y: 3pt),
  radius: 2pt,
  it,
)

#title-slide()

= Outline <touying:hidden>

#components.adaptive-columns(outline(title: none, indent: 1em, depth: 1))

#include "content.typ"
