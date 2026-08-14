---
name: pptx-to-typst
description: Convert an existing PowerPoint or Keynote deck into a Typst + Touying deck in this repo. Use when asked to port, convert, migrate or import a .pptx/.key/.pdf presentation into Typst, or to reuse slides from an old talk. Covers extracting media with PowerPoint's own crop rectangles, correcting video pixel aspect ratio, and re-typesetting text as real Typst rather than importing screenshots.
---

# PowerPoint or Keynote to Typst

The goal is a deck you can **edit afterwards**. That rules out the easy path — exporting each
slide as an image and placing it — because the result is a PDF wearing a Typst costume: no text to
fix, no figure to resize, nothing an assistant can help with later. Extract the assets, then
re-typeset the words as Typst.

Keynote has no direct route. Export to `.pptx` from Keynote first and treat it as PowerPoint. The
export is lossy in ways that matter — see **Traps**.

## Ask first: what is the deck for?

Reproducing the old talk page for page is usually the wrong goal, and it is worth confirming before
spending an hour on it. Most people converting a deck want *material they can reuse*, not a replica.
When that is the case:

- **Drop slides that repeat something the audience already has.** Duplicate slides, hidden slides,
  and slides that are screenshots of a previous version of the same talk.
- **Drop screenshots of other people's slides or of LaTeX output.** They cannot be re-typeset and
  they will look wrong beside real Typst.
- Keep the figures, the data, the structure, the equations.

## Survey before extracting

```bash
python -m markitdown talk.pptx                 # all the text, in slide order
mkdir -p /tmp/pptx && cd /tmp/pptx && unzip -q ~/talk.pptx
ls ppt/media/                                  # every image and video, unnamed
ls ppt/slides/                                 # slide1.xml ... slideN.xml
```

`markitdown` gives you the words and speaker notes. The XML gives you everything else: which media
appears on which slide, where, at what size, and **cropped how**.

## Extract media the way the deck actually shows it

This is where a naive conversion goes wrong, silently.

### Crops — `<a:srcRect>`

PowerPoint stores a cropped image uncropped, plus a crop rectangle. Copy `ppt/media/image7.png`
straight out and you get the *whole* figure — often a two-panel plot where the slide showed one
panel, or a chart with someone else's axis labels still attached.

```xml
<a:blipFill>
  <a:blip r:embed="rId3"/>
  <a:srcRect l="48957" t="0" r="0" b="12500"/>
</a:blipFill>
```

Values are **thousandths of a percent of inset from that edge**. Here: cut 48.957% off the left and
12.5% off the bottom. Audit every image on every slide for a `srcRect` before you extract anything —
grep the whole slide directory at once rather than checking slides one at a time, because the ones
you miss look like plausible figures.

One image can appear twice with different crops. That is a two-panel figure split across a slide,
and it needs to become two files.

### Videos — the pixel aspect ratio

A video's stored frame is often not its displayed frame. A non-square sample aspect ratio (SAR)
means the player stretches it on the way out, so extracting frames at their stored size distorts
every one of them. Keynote and PowerPoint round trips produce these routinely — in one real
ten-video deck, three were affected, the worst by 2.5x.

`--add-movie` handles this: it asks ffprobe for the displayed size and squares the pixels on
extraction.

```bash
uv run python tools/build-slides.py <deck> --add-movie ppt/media/media3.mp4 --name bondi-zoom
uv run python tools/build-slides.py <deck> --add-movie clip.mp4 --frame-format jpg   # dense renders
```

Use `--frame-format jpg` for simulation output and photographs; PNG is roughly ten times the size
for a turbulent colour field. Keep PNG for line plots and screen captures.

If you ever extract frames by hand, the correction is `ffmpeg -vf scale=iw*sar:ih,setsar=1`.

### Baked-in titles

Figures exported from another tool often carry their own title text. Once the slide has a Typst
heading saying the same thing, that title is a duplicate — crop it off, do not write a caption that
repeats it.

## Re-typeset, do not transcribe

Work slide by slide from the `markitdown` output, and write Typst that *means* what the slide meant:

- A PowerPoint table of nested coloured cells becomes a Typst function that draws it, not a
  screenshot. If the original is a diagram, `fletcher` will usually redraw it in fewer lines than
  it took to describe.
- Equations become real Typst maths. This is the single largest win of the conversion, and the
  reason to do it at all.
- A slide-wide statement is body text; a caption describes only its panel. See the house style in
  the **slide-deck** skill.
- Bullet lists that were pasted prose should become bullet lists.

Put helpers the deck needs in its own `globals.typ` — never import from outside the deck.

## Verify, then look

```bash
uv run python tools/build-slides.py <deck> --check
```

Then **render the pages to PNG and read them**. `--check` proves nothing spilled and no figure is
stretched; it cannot tell you that a figure is the wrong figure, that a caption contradicts the
plot, or that text is too small to read from the back. Every conversion I have seen had at least
one mis-mapped figure that only a human eye caught.

## Traps

- **`#set text(size: ..)` at slide-body level leaks into every later slide.** Converting a deck
  means writing a lot of size adjustments, and unscoped ones compound: five of them leave the last
  slides at half size, which reads as "the theme is small" rather than as a bug. Wrap each in
  `#[ .. ]`. Worse, the leak *hides* overflow — shrunken slides fit, so `--check` stays green until
  you scope them and several slides overflow at once.
- **Shrinking text is the last lever, not the first.** A converted slide that only fits at 0.62em
  has too much on it; change the layout instead.
- **Keynote's PPTX export rasterises what it cannot represent.** Equations, some shapes and any
  Keynote-specific effect arrive as images. Those are the slides to re-typeset by hand, and the
  reason to check the original Keynote file rather than trusting the export's text layer.
- **Hidden and duplicate slides survive the export.** `<p:sld show="0">` marks a hidden slide; it
  will not be in the presentation you remember giving.
- **Speaker notes are in `ppt/notesSlides/`,** not in the slide XML, and `markitdown` may or may not
  surface them depending on version. Check before assuming the talk had none.
- **Media filenames carry no meaning.** `ppt/media/image23.png` tells you nothing; build the mapping
  from the slide XML and rename on extraction, or you will lose track by slide 20.
