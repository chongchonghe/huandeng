# Slide geometry, and why things do not fit

## There is a frame, and it is exactly 1280 × 720

`width` and `height` in `_quarto.yml` define a fixed coordinate space. Reveal lays every slide out
in that box and then scales the whole box uniformly to the window. That is the determinism
guarantee: `{width="385px"}` is 385/1280 of the screen on any display, at any resolution, and
nothing re-flows when the window changes size.

Press **X** to draw the box while you write.

## margin

`margin: 0.04` removes 4% of the window **in total** — half on each side — before the scale:

```
scale = min(windowWidth / 1280, windowHeight / 720) × (1 − margin)
```

Measured on this configuration:

| window | scale | slide box | empty border each side |
| --- | --- | --- | --- |
| 1920 × 1080 (16:9) | 1.44 | 1843 × 1037 | 38 px · 22 px (= **15 slide-px**) |
| 2560 × 1440 (16:9) | 1.92 | 2458 × 1382 | 51 px · 29 px (= **15 slide-px**) |
| 1600 × 1000 (16:10) | 1.20 | 1536 × 864 | 32 px · 68 px (= **57 slide-px**) |
| 1512 × 982 (MacBook, 3:2) | 1.13 | 1452 × 816 | 30 px · 83 px (= **73 slide-px**) |

## Overflow is silent, and asymmetric

Reveal does **not** clip content to the box and does **not** shrink it. The surplus is drawn into
that border and then cut off by the window edge.

The vertical figure above is the trap. On a 16:9 projector only **15 slide-px** of overflow survive;
on the 16:10 or 3:2 laptop you are writing on, 57 to 73 do. **A slide that looks merely tight while
you write it is cut on stage.** The numbers depend only on aspect ratio, not resolution — a 4K
projector is no more forgiving than a 1080p one.

Sideways is worse: `.media-items` is `flex-wrap: nowrap`, so one image too many slides off the right
with no visual cue at all.

Printed, an over-full slide does not cut — it **splits across two PDF pages**, title alone on one
and body on the next.

## What `make check` measures

It walks the built deck slide by slide in headless Chromium and reports:

- content past **any** edge of the 1280 × 720 box, in slide-px, naming the slide;
- images and videos drawn more than 2% off their own pixel aspect ratio;
- images that never loaded;
- stray `<section>` elements inside a slide, which reveal counts as slides of their own;
- the slide count, against `--expect N` if you pin one.

Two categories of false alarm are suppressed deliberately, and both matter if you extend it: MathJax
lays equations out with spans whose boxes reach well above the ink, and anything inside an ancestor
that clips its own overflow — a numbered code block, most obviously — cannot be seen sticking out of
it anyway.

## When the deck does not fill the screen

Three different things look identical. Press **X** and read the label:

```
1280 × 720 · window 1512 × 982 · ar 1.54 · scale 1.13 · fill 41%
```

1. **`fill` is low** — the box fills the screen; the *slide* is half empty. Much the commonest case,
   and no reveal setting touches it. Put more on the slide, make the figures bigger, or raise
   `$presentation-font-size-root`.
2. **`ar` is not 1.78** — a 16:9 deck on a 16:10 or 3:2 laptop letterboxes. Unavoidable, and
   invisible on a white slide because the page behind is white too.
3. **`CAPPED by max-scale`** — reveal refuses to scale past 2× by default, so past about 2560 CSS px
   the deck stops growing. `max-scale: 5` in `_quarto.yml` lifts it; nothing here is a bitmap.

## Fixing something that does not fit

Change the slide before the theme. A `.small` on that one block, a narrower figure, one less
bullet — that is one slide's problem and it belongs in one slide.

Reach for `theme.scss` or `_quarto.yml` only when the default is wrong for *any* deck, or when the
same fix would otherwise be repeated slide after slide.

**Within the slide, shrinking text is the last lever, not the first.** Reach for the layout first:
join a wrapped equation onto one line, turn two stacked rows into two columns, cut words. Text below
about 0.7em stops being readable from the back of a room, so a slide that only fits at 0.62em is not
a slide that fits — it is a slide with too much on it.

There is no automatic rescue. `auto-stretch` is off and reveal will not shrink an over-full slide.
