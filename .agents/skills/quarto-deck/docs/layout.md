# Layout

Every class here is defined in the deck's own `theme.scss`. A deck copied from an older template
may not have all of them — check that deck's `theme.scss` before using one.

## Columns

```markdown
:::: {.columns}
::: {.column}
left
:::
::: {.column}
right
:::
::::
```

| class | split |
| --- | --- |
| `.columns` | 50 / 50 — **prefer this one for a balanced split** |
| `.columns-1-1` | the same thing; kept so older decks still render |
| `.columns-2-1`, `.columns-1-2` | 2:1 and 1:2 |
| `.columns-3-2`, `.columns-2-3` | 3:2 and 2:3 — the usual "bullets left, figure right" |
| `.columns-1-1-1` | three equal |

Use `.columns` rather than `.columns-1-1` when the split is even: Pandoc recognises that one class
and maps it to PowerPoint's *Two Content* layout, so the PPTX keeps two real columns instead of one
flattened text box. They are identical in the browser.

They are CSS grid, `align-items: start`, so columns of unequal height hang from a common top edge.
A slide is read top to bottom; centring them makes a short column float.

**Do not reach for a bare `.columns` selector in new CSS.** Quarto ships
`div.columns { display: initial }` for revealjs, which outranks a one-class selector and lays both
columns on top of each other. Every column rule in `theme.scss` is prefixed `.reveal` for exactly
this reason.

## Anywhere on the slide

`.absolute` plus `top`/`left`/`bottom`/`right`/`width`/`height` places an element at a fixed spot in
the 1280 × 720 coordinate space. Quarto injects the `position: absolute` for you.

```markdown
![](attach/inset.png){.absolute bottom="90" left="120" width="200"}
```

### Centring an absolute box without arithmetic

Do not compute `left = (1280 - width) / 2`. The standard CSS idiom centres at *any* width, and stays
centred when you change it:

```markdown
::: {.absolute .center style="left:50%; top:50%; transform:translate(-50%,-50%); width:360px;"}
Dead centre, no maths.
:::
```

`left/top: 50%` puts the box's own top-left corner at the slide centre; `translate(-50%, -50%)`
pulls it back by half its own size. Horizontal only: `left:50%; transform:translateX(-50%)`.

This is static positioning, so it does not fight `.fragment` — fragments animate opacity and
visibility, not transform.

## Stacking things in one spot

`.r-stack` overlays its children on the same spot, sized to the largest.

```markdown
::: {.r-stack}
![](attach/f1.png){height="320px"}

::: {.fragment .fade-in-then-out}
![](attach/f2.png){height="320px"}
:::
::: {.fragment .fade-in-then-out}
![](attach/f3.png){height="320px"}
:::
:::
```

Keep the **first child bare** — no fragment — so something is visible when the slide opens. This is
also how a flip-book animation is built; see `media.md`.

## Emphasis and sizing

| | |
| --- | --- |
| `::: {.highlight}` | the callout block for the one sentence a slide is about |
| `::: {.card}` | a box round a group — carries no emphasis, just a boundary |
| `[..]{.pill}` | an inline tag: `[N = 512]{.pill}`, `[preprint]{.pill}` |
| `[..]{.alert}` | inline, in the theme's accent colour |
| `[..]{.muted}` | inline, grey |
| `.small` / `.tiny` | 0.78em / 0.62em, on a block or a span |
| `.center` | centre the text of a block — **and** reveal's own vertical centring when put on a slide heading |
| `.focus` | the one-big-statement slide; pair with `.center` and a `background-color` |

`.center` does double duty: on a `:::` block it is `text-align: center`; on a `##` heading it is
reveal's per-slide vertical centring, which is why the focus slide needs both classes.

`.card` and `.highlight` do different jobs. A highlight is the one sentence the slide is about and
says so in the theme's colour; a card is a container that draws a boundary and nothing else. Three
cards across a `.columns-1-1-1` is the usual shape, and it is the widest difference between the
themes on a slide that has no figure on it — hairline boxes in `paper`, a hard offset shadow in
`swiss`, dashed construction lines in `blueprint`, a raised rounded surface in `nord`.

### Two traps when nesting divs

**Fences of the same length do not nest.** Pandoc closes the innermost open fence at the first
matching `:::`, so a card inside a column inside a row needs three lengths, longest outside:

```markdown
::::: {.columns-1-1-1}
:::: {.column}
::: {.card}
**Setup**

Shear layer, two fluids
:::
::::
:::::
```

**Never start a fenced div with a heading.** Pandoc writes a div whose first block is a heading out
as a `<section>` carrying the div's class, and reveal's slide selector is `.slides section` — a
*descendant* selector — so it becomes a slide of its own, with a blank entry in the progress bar and
an arrow press that goes nowhere. `::: {.card}` followed by `#### Setup` costs three phantom slides
and no error. Lead with `**bold text**` instead. `.column` is the exception, because Quarto rewrites
those divs itself before Pandoc gets there. `make check` reports any stray section it finds.

## Tables

Ordinary Markdown tables. The theme styles them: a rule under the header, thin rules between rows,
0.62em.

```markdown
::: {.no-header}
| | | |
|---|---|---|
| Data A | Data B | Data C |
| 1.23 | 4.56 | 7.89 |
:::
```

`.no-header` hides the header row, for a table that is really a grid of numbers. The empty header
cells are still required — Pandoc needs them to parse the table.

## Everything at once

`demo/demo.qmd` has a worked slide for each of these, and `make check` verifies them on every
commit. That is the example to copy from.
