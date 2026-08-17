# Slide structure

## Headings make slides

`slide-level: 2` is set in `_quarto.yml`. **Do not change it** — every deck in this repo, the
theme's `section.level1` styling, and the checker all assume it.

| you write | you get |
| --- | --- |
| `# Results` | a section divider slide (big centred title, gradient rule) |
| `## The shock front` | a content slide |
| `---` on its own line | another slide, with no title |

`---` between two `##` headings is redundant — the heading already starts a slide. Avoid it there.
And **never write an em dash as `---` in prose**: it silently cuts the slide in half.

## Per-slide attributes

Everything in braces on the heading applies to that slide only.

```markdown
## A dense slide {.smaller}
## One big statement {.focus .center background-color="#0a6ebd"}
## Over a photo {background-image="attach/galaxy.jpg" background-size="cover"}
## No footer here {footer=false}
## Slides in {transition="fade"}
```

Reveal's background attributes are the only way to paint outside the 4% margin — see
`geometry.md`. `background-color` also flips reveal into dark-slide mode, which the theme picks up
to turn type white.

`transition` takes `none` (the deck default), `fade`, `slide`, `convex`, `concave`, `zoom`.

## Revealing content step by step

```markdown
. . .                       <!-- everything after this waits for a keypress -->

::: {.incremental}
- one at a time
- like this
:::

::: {.fragment}              plain: appears
::: {.fragment .fade-in}     fades in
::: {.fragment .fade-up}     drifts up
::: {.fragment .fade-left}   drifts in from the right
::: {.fragment .highlight-red}    turns red on its step
::: {.fragment .strike}      gets struck through
::: {.fragment .fade-in-then-out} appears, then hides on the next step
::: {.fragment .fade-in-then-semi-out} appears, then dims
```

A fragment costs a keypress and nothing else — it lives inside one slide. Only the per-step PDF
spends a page on it (`exports.md`).

Order them explicitly with `fragment-index` when the visual order should differ from the source
order:

```markdown
::: {.fragment fragment-index=2}  second
::: {.fragment fragment-index=1}  first
```

## Auto-animate

Two *consecutive* slides both marked `auto-animate="true"`. Reveal matches elements between them by
`data-id` and tweens whatever differs — width, height, position, margin, colour.

```markdown
## Zoom in {auto-animate="true" auto-animate-easing="ease-in-out"}

![](attach/panel.png){data-id="p" width="180px"}

## Zoom in {auto-animate="true" auto-animate-easing="ease-in-out"}

![](attach/panel.png){data-id="p" width="620px"}
```

Repeat the heading text so the title does not appear to change. Worked example: the demo's two
"Auto-animate" slides.

## Speaker notes

```markdown
::: notes
What you actually say. Press S during the talk for the presenter window:
notes, a timer, and the next slide.
:::
```

Notes never render into the deck body. They *do* leak into PPTX and into Pandoc's other writers,
which is one of several reasons this repo does not use them (`exports.md`).

## Verbatim Markdown inside a slide

To show fenced-code syntax without it being interpreted, fence it with more backticks than the
thing you are quoting:

````markdown
```` markdown
``` {.python code-line-numbers="1-2|4"}
```
````
````

For a literal `{{< shortcode >}}` or a live `{mermaid}` fence shown as text, double the braces:
`` ```{{mermaid}} ``.
