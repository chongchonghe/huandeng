// Shared imports and small content helpers.
// Both `main.typ` and `content.typ` import this file, so it must not import either of them.

#import "@preview/touying:0.6.1": *
#import themes.university: *

#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "@preview/numbly:0.1.0": numbly

// --------------------------------------------------------------------- theme --

// University's own `slide` hardcodes a three-cell footer filled with the theme colours. To get a
// quiet Metropolis-style footer we have to replace the slide function itself; everything else in
// the theme (title-slide, focus-slide, section slides, colours) is untouched.
#let footer-grey = luma(120)

#let uni-slide(
  config: (:),
  repeat: auto,
  setting: body => body,
  composer: auto,
  align: auto,
  ..bodies,
) = touying-slide-wrapper(self => {
  if align != auto { self.store.align = align }

  let header(self) = {
    set std.align(top)
    grid(
      rows: (auto, auto),
      // The theme uses 3mm; more air between the progress bar and the running title.
      row-gutter: 8mm,
      if self.store.progress-bar {
        components.progress-bar(height: 2pt, self.colors.primary, self.colors.tertiary)
      },
      block(
        inset: (x: .5em),
        components.left-and-right(
          text(
            fill: self.colors.primary,
            weight: "bold",
            size: 1.2em,
            utils.call-or-display(self, self.store.header),
          ),
          text(
            fill: self.colors.primary.lighten(65%),
            utils.call-or-display(self, self.store.header-right),
          ),
        ),
      ),
    )
  }

  // Grey text, no fill: speaker · talk · date and page number.
  let footer(self) = {
    set std.align(bottom)
    set text(size: .8em, fill: footer-grey)
    block(
      width: 100%,
      inset: (x: .5em, bottom: .2em),
      grid(
        columns: (auto, 1fr, auto),
        align: (left + horizon, center + horizon, right + horizon),
        utils.call-or-display(self, self.store.footer-a),
        utils.call-or-display(self, self.store.footer-b),
        utils.call-or-display(self, self.store.footer-c),
      ),
    )
  }

  let self = utils.merge-dicts(self, config-page(header: header, footer: footer))
  let new-setting = body => {
    show: std.align.with(self.store.align)
    show: setting
    body
  }
  touying-slide(self: self, config: config, repeat: repeat, setting: new-setting, composer: composer, ..bodies)
})

// ------------------------------------------------------------------ helpers --

// Split the *body* of a slide into columns, without starting a new slide.
// (`#slide(composer: ..)` also splits into columns, but always begins a new slide.)
// University already aligns slide bodies to the top, so this only guards against a theme or a
// caller that sets `horizon`.
#let side-by-side(..args) = {
  set align(top)
  components.side-by-side(gutter: 1em, ..args)
}

// A standalone caption line, rendered wherever it is written — for tables and other things `fig`
// does not wrap. For a figure use `fig(caption: ..)`, which places it above.
#let caption(body) = align(center, text(size: 0.8em, fill: luma(90), body))

// Source credit under a figure: tiny, grey, right-aligned to the image's own edge.
#let credit-size = 0.6em
#let credit-fill = luma(110)

/// A figure with an academic source credit, and an optional caption.
///
///   #fig("attach/x.png", width: 70%, credit: [He et al. 2025])
///   #fig("attach/x.png", caption: [What it shows], credit: [He et al. 2025])
///   #fig("attach/x.png", caption: [Setup], below: [Result], credit: [He et al. 2025])
///
/// `caption` sits *above* the figure. That is the house default and the reason the argument is
/// not called `above`: a slide is read top to bottom, so the caption should say what the panel
/// is before the eye reaches it. `below` remains for the genuine exception — a second label
/// under a paired figure, or a note that belongs to the image rather than to the slide.
///
/// The first argument is a path, or any content (a diagram, a grid of images). The credit hugs
/// the right edge of the figure itself, not the slide, so it stays put at any width.
#let fig(
  body,
  width: 100%,
  caption: none,
  below: none,
  credit: none,
  gap: 0.45em,
  credit-gap: 0.15em,
) = layout(container => {
  let w = if type(width) == ratio { container.width * width } else { width }
  let art = if type(body) == str { image(body, width: 100%) } else { body }
  let desc(it) = align(center, text(size: 0.8em, fill: luma(90), it))
  align(center, block(width: w, {
    // Every gap here is placed by hand, so the credit can sit tight under the image.
    set par(spacing: 0pt)
    if caption != none { desc(caption); v(gap) }
    art
    if credit != none {
      v(credit-gap)
      align(right, text(size: credit-size, fill: credit-fill, credit))
    }
    if below != none { v(gap); desc(below) }
  }))
})

// A horizontal strip of items (images, labels, ...), aligned on their tops. Figures of unequal
// height hang from a common line that way, which is how the slide is read; centring them makes
// a short panel float and its caption drift out of line with its neighbours'.
#let img-row(..items, gutter: 6pt) = grid(
  columns: items.pos().len(),
  column-gutter: gutter,
  align: top,
  ..items.pos()
)

// Escape hatch: play an explicit list of image paths, one per subslide. Prefer `#movie` below,
// which takes the list from the manifest. Useful for hand-picked frames under `attach/`.
#let flip-book(paths, ..args) = {
  for (i, path) in paths.enumerate() {
    only(i + 1, image(path, ..args))
  }
}

// --------------------------------------------------------------------- video --

// Which format is being exported. `build.py` passes this in; a bare `typst compile` sees "pdf".
#let target = sys.inputs.at("target", default: "pdf")

// Draw the poster frame at its final size and record exactly where it landed, so `build.py` can
// lay a real video over that rectangle. Typst never opens `src` — only the poster.
#let video-box(src, poster, width: 100%) = layout(container => {
  let w = if type(width) == ratio { container.width * width } else { width }
  let frame = image(poster, width: w)
  let h = measure(frame).height
  box(width: w, height: h)[
    #place(top + left)[#context {
      let p = here().position()
      [#metadata((
        src: src,
        poster: poster,
        page: p.page,
        x: p.x.pt(),
        y: p.y.pt(),
        w: w.pt(),
        h: h.pt(),
      )) <video-rect>]
    }]
    #frame
  ]
})

#let movie-root = "movie-frames/"

// PDF pages one `#movie` spends when no cadence is given. A 250-frame sequence would otherwise be
// 250 pages.
#let flip-book-budget = 24

// Choose which frames the PDF flip-book shows. `every: auto` samples evenly to `budget`, always
// keeping the first and last frame; `every: n` takes every nth and pins the last.
#let movie-select(files, every: auto, budget: flip-book-budget) = {
  let n = files.len()
  if every == auto {
    let k = calc.min(budget, n)
    if k <= 1 { return (files.first(),) }
    range(k).map(i => files.at(int(calc.round(i * (n - 1) / (k - 1)))))
  } else {
    let idx = range(0, n, step: every)
    if idx.last() != n - 1 { idx.push(n - 1) }
    idx.map(i => files.at(i))
  }
}

/// Play the image sequence `movie-frames/<name>/`, the best way each format allows: a flip-book in
/// the PDF, a real playable video in HTML and PPTX.
///
/// `every` and `budget` affect ONLY the PDF. The mp4 is always encoded from every frame, so HTML
/// and PPTX always play the whole sequence.
///
///   #movie("zoom")            // sampled to `budget` pages
///   #movie("zoom", every: 10) // every 10th frame
///   #movie("zoom", every: 1)  // all of them
#let movie(name, every: auto, width: 100%, budget: flip-book-budget) = {
  // Read the manifest HERE, not at the top of the file: `json()` on a missing file is a hard
  // error, and a deck with no movies has no manifest to read.
  let sequences = json(movie-root + "manifest.json").sequences
  assert(
    name in sequences,
    message: "movie: no sequence \"" + name + "\" in " + movie-root + "manifest.json"
      + " — add frames and run: build-slides.py <deck> --sync-frames",
  )
  let files = sequences.at(name).frames
  let chosen = movie-select(files, every: every, budget: budget)
  let paths = chosen.map(f => movie-root + name + "/" + f)
  // Derived, never typed by the author: this is where `encode_movies()` puts the mp4.
  let src = "media/" + name + ".mp4"

  [#metadata((name: name, total: files.len(), used: chosen.len())) <movie-cost>]
  if target == "pdf" {
    flip-book(paths, width: width)
  } else {
    video-box(src, paths.first(), width: width)
  }
}

#let table-inset = (x: 0.6em, y: 0.4em)

// Table with a bold header row.
#let head-table(..args) = {
  show table.cell.where(y: 0): set text(weight: "bold")
  table(
    stroke: (_, y) => (bottom: if y == 0 { 0.8pt + luma(60) } else { 0.4pt + luma(200) }),
    inset: table-inset,
    ..args,
  )
}

// Borderless table with no header row.
#let plain-table(..args) = table(stroke: none, inset: table-inset, ..args)
