# The theme

## What a deck is made of

| file | role |
| --- | --- |
| `talk.qmd` | the slides, and this talk's title/author/date/footer |
| `_quarto.yml` | every option that shapes the whole deck |
| `theme.scss` | the look, and every layout class |
| `fonts.html` | seven `@font-face` rules, injected into `<head>` |
| `guides.html` | the **X** key overlay |
| `fonts/`, `attach/`, `ref.bib` | the deck's own copies of everything it needs |

All of it is a **copy**. No deck imports anything from outside its own directory, so a talk given in
2026 still renders in 2030 after the template has moved on. The cost is that a fix in `template/`
reaches an existing deck only if you carry it there by hand. That trade is deliberate.

## theme.scss structure

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
`--deck-*` custom properties on `:root` so the rules and `guides.html` can read them at runtime.

## Specificity: Quarto fights back

Quarto ships CSS for revealjs that neutralises classes its HTML formats use. The one that matters:

```css
div.columns { display: initial; gap: initial }
```

That is one class **plus an element**, which outranks a bare `.columns`. Every column rule in
`theme.scss` is therefore prefixed `.reveal` — two classes beat one class and an element. Forget it
and both columns land on top of each other at full width.

When adding a rule for anything Quarto also styles, check the compiled output rather than assuming:

```bash
grep -o 'div\.columns[^}]*}' demo/out/demo_files/libs/revealjs/dist/theme/quarto-*.css
```

## Fonts live in fonts.html, not theme.scss

`@font-face` cannot go in `theme.scss`. Quarto compiles the theme into
`<deck>_files/libs/revealjs/dist/theme/` — five directories deep — and a relative `url()` inside a
stylesheet resolves against *the stylesheet*, so `fonts/FiraSans-Regular.otf` written there is looked
for beside reveal's own theme files and quietly 404s.

A `<style>` element in the document resolves against *the document*, which is `out/<deck>.html`, and
`out/fonts/` is exactly where `_quarto.yml`'s `resources:` puts them. Hence `fonts.html` and
`include-in-header`.

The failure is silent: the deck still renders, in whatever sans-serif the machine has, at different
metrics, with every line breaking somewhere else.

## The title slide

Quarto 1.9 emits it as `section.quarto-title-block`. The older `.title-slide` class now belongs to
the **section divider** slides (`section.level1`), so do not reach for it here — that is a rename
that silently restyles the wrong thing.

Its background is set by `title-slide-attributes` in `_quarto.yml`, not by CSS, because reveal paints
backgrounds on a layer outside the slide margin. See `geometry.md`.

## guides.html

Press **X**, or load the deck with `?guides`, to draw the 1280 × 720 boundary, a 24 px keep-clear
inset, and a live readout of window size, aspect ratio, scale and how full the slide is. Bound
through `Reveal.addKeyBinding`, so it appears in reveal's own `?` help and cannot collide with
navigation — `X` because `G` is already reveal's jump-to-slide.

## Adding a class

Add it to the deck's own `theme.scss` and rebuild. To give an *existing* deck a class the template
gained later, copy the rule into that deck's `theme.scss`. Never by making one deck import another —
that is the rule the whole layout rests on.

`template/theme.scss` and `demo/theme.scss` are separate files that happen to be identical today.
Fix one and copy it across; do not symlink them.
