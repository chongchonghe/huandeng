# The theme

## What a deck is made of

| file | role |
| --- | --- |
| `talk.qmd` | the slides, and this talk's title/author/date/footer |
| `_quarto.yml` | every option that shapes the whole deck |
| `themes/*.scss` | ten looks, one per file; `_quarto.yml` picks one. Every layout class is in each |
| `head.html` | injected into `<head>`: seven `@font-face` rules, and the **X** key overlay |
| `fonts/`, `attach/`, `ref.bib` | the deck's own copies of everything it needs |

All of it is a **copy**. No deck imports anything from outside its own directory, so a talk given in
2026 still renders in 2030 after its theme has moved on. The cost is that a fix in `themes/` reaches
an existing deck only if you carry it there by hand. That trade is deliberate.

## Stylesheet structure

Quarto's SCSS convention, two labelled regions in one file:

```scss
/*-- scss:defaults --*/
// SCSS variables, read before Quarto's own defaults. Fonts, colours, sizes.
$presentation-font-size-root: 30px !default;
$primary: #0a6ebd !default;

/*-- scss:rules --*/
// Ordinary CSS, appended after reveal's theme.
.reveal h2 { color: var(--deck-primary); }
```

Variables in `defaults` must carry `!default` so Quarto can override them. Anything that is plain
CSS goes in `rules`.

The palette is declared twice on purpose: as SCSS variables for Quarto's own machinery, and as
`--deck-*` custom properties on `:root` so the rules and the guides script in `head.html` can read them at runtime.

## Specificity: Quarto fights back

Quarto ships CSS for revealjs that neutralises classes its HTML formats use. The one that matters:

```css
div.columns { display: initial; gap: initial }
```

That is one class **plus an element**, which outranks a bare `.columns`. Every column rule in
Each stylesheet is therefore prefixed `.reveal` — two classes beat one class and an element. Forget it
and both columns land on top of each other at full width.

When adding a rule for anything Quarto also styles, check the compiled output rather than assuming:

```bash
grep -o 'div\.columns[^}]*}' demo/out/demo_files/libs/revealjs/dist/theme/quarto-*.css
```

## Fonts live in head.html, not the stylesheet

`@font-face` cannot go in a stylesheet. Quarto compiles the theme into
`<deck>_files/libs/revealjs/dist/theme/` — five directories deep — and a relative `url()` inside a
stylesheet resolves against *the stylesheet*, so `fonts/FiraSans-Regular.otf` written there is looked
for beside reveal's own theme files and quietly 404s.

A `<style>` element in the document resolves against *the document*, which is `out/<deck>.html`, and
`out/fonts/` is exactly where `_quarto.yml`'s `resources:` puts them. Hence `head.html` and
`include-in-header`.

The failure is silent: the deck still renders, in whatever sans-serif the machine has, at different
metrics, with every line breaking somewhere else.

**The same trap catches every other `url()` in a stylesheet**, not just `@font-face`. A slide logo
written as `background-image: url("attach/logo.png")` 404s for exactly this reason, and the deck
renders perfectly with no logo on it. Use Quarto's own `logo:` in `_quarto.yml`, which writes an
`<img class="slide-logo">` into the page — that path resolves against the document. `theme.scss`
positions it top right and pins the slide number back to the bottom, because Quarto moves the number
up as soon as a logo exists.

## The slide title

`.reveal h2` is `width: fit-content; max-width: 100%`, so its rule stops where the words stop rather
than running the width of the slide. Two things follow. A title too long for one line wraps, fills
the measure, and its rule goes back to spanning the whole way — there is nothing else it could do.
And the heading box is *narrow*: anything you position against its right edge lands beside the text,
not at the slide's edge. `section.focus h2` sets `width: auto` back for exactly that reason, since a
shrink-wrapped box gives `text-align: center` nothing to centre inside.

## The title slide

Quarto 1.9 emits it as `section.quarto-title-block`. The older `.title-slide` class now belongs to
the **section divider** slides (`section.level1`), so do not reach for it here — that is a rename
that silently restyles the wrong thing.

It stands on the deck's own background, like every other slide: the title takes `--deck-primary` and
a hairline under it does the work a colour field used to. To put a field back, uncomment
`title-slide-attributes` in `_quarto.yml` and change the four title-slide colours to suit. It has to
be set there rather than in CSS, because reveal paints backgrounds on a layer outside the slide
margin. See `geometry.md`.

## The layout guides, also in head.html

Press **X**, or load the deck with `?guides`, to draw the 1280 × 720 boundary, a 24 px keep-clear
inset, and a live readout of window size, aspect ratio, scale and how full the slide is. Bound
through `Reveal.addKeyBinding`, so it appears in reveal's own `?` help and cannot collide with
navigation — `X` because `G` is already reveal's jump-to-slide.

## Changing the whole look

Every deck carries all ten stylesheets in its own `themes/`, and `_quarto.yml` picks one.
`university` is the plain one and the source of the shared body; `themes/README.md` inside the deck
says what each of the ten is.

```bash
cp -r template talks/2027-my-talk         # start a new talk
cd talks/2027-my-talk && make gallery     # all ten, rendered, to choose by eye
```

Then switching is a text edit — two adjacent lines in the deck's own `_quarto.yml`, and `make check`
afterwards because a slide that fits in one theme can overflow in another:

```yaml
    theme: [default, themes/nord.scss]
```

One line, and nothing else to set. Pandoc marks up code with `<span class="kw">` and friends
whatever happens, and Quarto would normally colour them from a `highlight-style:` chosen in the
YAML; here the shared body colours them from five `--deck-code-*` custom properties instead, so a
theme owns its code block along with the rest of its look. There is no command for any of this and
nothing is copied, so undo is undo. Nothing else changes: no theme here puts a colour field behind
the
title slide or the closing slide, so there is no background left to carry across.

Three things switching cannot do, all worth saying out loud before an author is surprised by them:

- **A `background-color="#0a6ebd"` written into a slide stays azure.** Reveal parses that attribute
  as a literal colour; `var(--deck-primary)` there would render but would defeat the brightness test
  reveal uses to decide whether that slide's type turns white. So it belongs to the talk. `make
  theme` prints a note when it finds one.
- **A dark theme is a decision about the figures.** A plot saved on a white canvas is a bright
  rectangle punched into a dark slide, with black axis labels in the middle of a light-on-dark deck.
  Inverting the image inverts the colour map too, which changes what the figure says. Either the
  figures are re-saved transparent, or the deck stays light.
- **Only Fira Sans is shipped.** The other families a theme names — Helvetica Neue, Charter, the
  system monospace — fall back through a stack, so those decks render *close* on someone else's
  machine rather than identically.

Each stylesheet is a header (defaults and `:root`, including the five `--deck-code-*` values), then the shared
body byte-identical to `university.scss` from `.reveal {` on, then an appendix under a marked
banner. Carry a fix across by replacing the middle; change the theme by editing the two ends.

## Adding a class

Add it to the deck's own stylesheets and rebuild. To give an *existing* deck a class its starting
point gained later, copy the rule in. Never by making one deck import another — that is the rule the
whole layout rests on.

A new class belongs in the shared body, so it goes into `template/themes/university.scss` first and
then into the other nine and into `demo/themes/` — twenty separate files that happen to be identical
through that stretch. Fix one and copy it across; do not symlink them.
