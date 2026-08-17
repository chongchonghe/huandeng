# Figures

## Never change a figure's aspect ratio

These are scientific figures: the aspect ratio carries meaning. Stretch one and equal axes stop
being square, a circle becomes an ellipse, an edge-on disk looks face-on — and it still looks like a
plausible figure, so nobody catches it.

**Give an image a width *or* a height, never both.** `make check` measures every drawn image and
video against its own pixel dimensions and fails past 2%.

One source of this is nobody's mistake: reveal caps every image at 95% of its container, so inside a
shrink-to-fit box — an `.r-stack` cell, a flex item, a `.fig` — the container is already the image's
own width, and the cap squeezes the width 5% while an explicit `height` holds firm. `theme.scss`
raises the cap to 100%. A deck copied from an older template may not have that fix.

## Sizing

Size in `px` or `pt`. Both map cleanly to the 1280 × 720 coordinate space, and **1 pt ≈ 1.333 px**,
so `{width="200pt"}` draws 267 slide-px — about a fifth of the slide width.

```markdown
![](attach/shock.png){width="420px"}
![](attach/shock.png){height="320px"}
```

Percentages work in ordinary flow but **not inside `.fig`**, which sizes itself to its contents —
a percentage there has nothing to resolve against.

## A figure with a source credit

Every borrowed figure in a talk needs to say where it came from. `.fig` shrink-wraps the image so
the credit lands on the *figure's* bottom-right corner, not the slide's.

```markdown
::: {.fig}
[What it shows]{.caption}

![](attach/shock.png){width="420px"}

[He et al. 2025]{.credit}

[After 10 Myr]{.below}
:::
```

| part | where | how it looks |
| --- | --- | --- |
| `[..]{.caption}` | above the image | 0.8em, grey, centred on the figure |
| `[..]{.credit}` | tight under the image | 0.6em, grey, right-aligned to the figure's edge |
| `[..]{.below}` | under the credit | 0.8em, grey, centred |

All three are optional. Each is its own paragraph inside the `:::`.

Two mechanisms make it work, and both are worth knowing before changing them:

- `.fig` is `width: fit-content`, so it takes the image's width. Hence the px/pt rule above.
- The labels are `width: 0; min-width: 100%`. A zero-width child contributes nothing to the
  parent's intrinsic width, then stretches back to whatever the image settled on — so a long
  caption cannot widen the box and drag the credit away from the image's right edge.

For a caption on something `.fig` does not wrap — a table, a Mermaid diagram, a row of images — use
`::: {.caption-line}`.

## A row of figures

`.media-row` is a two-column grid: a label, then a nowrap flex row of images.

```markdown
:::: {.media-row}
::: {.media-label}
FLD:
:::
::: {.media-items}
![](attach/a.png){height="98px"} ![](attach/b.png){height="98px"}
:::
::::
```

Pandoc puts every image written on **one Markdown line** into a single `<p>`, so that `<p>` has to
be a flex row too or the images line-wrap. `theme.scss` styles `.media-items p` as well as
`.media-items` for exactly this. Images get `flex-shrink: 0` so explicit sizes are respected.

`.media-items` is `flex-wrap: nowrap`, which means **one image too many slides off the right edge
with no visual cue at all**. This is the failure `make check`'s horizontal test exists for.

Add `.no-label` to the row if you want the images without a label column.

## A grid of figures

Three stacked `.media-row`s, not a table — a table would force every panel into the same cell
shape. Each row sizes its own label column, so they only line up if told to share a width. Custom
properties inherit, so a plain wrapper is enough:

```markdown
::: {style="--label-width: 250px"}
… three .media-row blocks …
:::
```

## Placeholders

Before the real asset exists, point at `attach/placeholder.png` and leave an HTML comment naming
what belongs there and where it comes from:

```markdown
![](attach/placeholder.png){width="420px"}
<!-- TODO: Fig. 3 of He et al. 2025, the M1 shadow test at t = 10 Myr -->
```

`make check` will still verify the placeholder's aspect ratio, so the slide's geometry is real even
while its content is not.
