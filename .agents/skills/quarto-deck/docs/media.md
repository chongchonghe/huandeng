# Video, GIFs and animation

The deck is a browser, so video needs no pipeline: put an `.mp4` in `attach/` and write a tag.
There is no frame extraction, no manifest, no encoding step.

## Video

```html
<video class="r-stretch video-center" src="attach/clip.mp4"
       controls data-autoplay muted loop></video>
```

| attribute | why |
| --- | --- |
| `data-autoplay` | reveal starts it when the slide arrives and rewinds it on the way out |
| `controls` | a scrub bar, for when someone asks you to go back |
| `muted` | what browsers require before they will autoplay anything |
| `loop` | optional; drop it if the clip should stop on its last frame |

This is one of the few places raw HTML beats Markdown — `data-autoplay` has no Pandoc spelling.

### Sizing

**`r-stretch` first.** Reveal measures what height the slide has left and fits the video to it. Two
conditions, both easy to break:

- it must be the **last element on the slide**;
- it must **not** be wrapped in a div. Putting it inside `::: {.center}` silently breaks the
  sizing. Use the `.video-center` class on the video itself instead.

When it cannot be last — a video beside text, say — drop `r-stretch` and give it an explicit
height:

```html
<video src="attach/clip.mp4" style="height: 330px; display: block; margin: 0 auto;"
       controls data-autoplay muted loop></video>
```

Height only, never both dimensions: a stretched simulation frame is a wrong figure and nothing
warns you. `make check` compares `videoWidth`/`videoHeight` against the drawn box.

### Two clips at their true relative scale

```html
::: {.video-pair style="width: 800px"}
<video src="attach/zoom.mp4" style="flex: 1080" controls data-autoplay muted loop></video>
<video src="attach/mdot.mp4" style="flex: 720" controls data-autoplay muted loop></video>
:::
```

Give each clip `flex: <its own pixel width>`. The row then shows them at one common scale factor
rather than forcing them to equal widths. Set a width on the row itself so the taller clip stays on
the slide, and let `make check` confirm it.

### A video's stored frame is not always its displayed frame

A non-square sample aspect ratio (SAR) means the player stretches the frame back on the way out, and
anything through a Keynote or PowerPoint round trip routinely carries one. If you extract or
re-encode by hand, square the pixels:

```bash
ffmpeg -i in.mp4 -vf "scale=iw*sar:ih,setsar=1" out.mp4
```

## GIF

A GIF is an image — no player, no attributes, works everywhere:

```markdown
![](attach/clip.gif){height="330px"}
```

It also cannot be paused, scrubbed or muted, and it is usually far larger than the equivalent mp4.
Prefer mp4 for anything you might want to stop and talk over.

## An animation that survives the PDF

**A `<video>` prints as one still frame.** A page cannot play anything, and nothing can be done
about that.

When the animation has to survive on paper, use a **flip-book**: an `.r-stack` of image frames, each
one after the first wrapped in a fragment.

```markdown
::: {.r-stack}
![](attach/frames/frame-01.jpg){height="320px"}

::: {.fragment .fade-in-then-out}
![](attach/frames/frame-02.jpg){height="320px"}
:::
::: {.fragment .fade-in-then-out}
![](attach/frames/frame-03.jpg){height="320px"}
:::
:::
```

Live it steps in place like a movie. In the per-step PDF **each frame takes its own page**, so
twelve frames come out as twelve consecutive pages you can hold an arrow key down through. Worked
example: the demo's "A flip-book, in place" slide, twelve frames of a black-hole accretion clip.

### Extracting frames

```bash
ffmpeg -i clip.mp4 -vf "fps=6,scale=780:-1,setsar=1" -q:v 3 attach/frames/frame-%02d.jpg
```

- **JPEG, not PNG,** for dense simulation output — measured at 436 KB against 1.7 MB for the same
  twelve frames of a turbulent colour field. PNG is right for line plots and terminal captures.
- Render at about 2× the displayed size. Frames shown at 320 px tall want roughly 780 px wide.
- A dozen frames reads as motion; sixty makes a large deck for little gain.
