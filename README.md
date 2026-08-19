# 幻灯 Huandeng

**Academic slide decks in plain text — built on [Quarto](https://quarto.org/) and [reveal.js](https://revealjs.com/), with a checker for the failures that raise no error, and agent skills so an LLM can help without taking the wheel.**

[中文说明](README.zh-CN.md)

One Markdown file becomes a web page you present from, a self-contained page you can send to anyone, PDFs that keep your builds, and a PowerPoint for the conference that insists on one. Video plays. A checker catches the mistakes that would otherwise reach the room.

幻灯 (huàndēng) is the Chinese word for a slide, from 幻灯片 — literally "magic lantern".

## Why this exists

Keynote and PowerPoint are fast until the moment you want a language model to help. Then the deck is a binary blob: the model cannot read it, cannot diff it, and cannot edit one word without rewriting a file it does not understand. LaTeX Beamer is plain text but slow to compile and painful to lay out. Quarto gives you Markdown; reveal.js gives you CSS, which means any layout you can imagine. What was still missing is the part around it — the export formats a real talk needs, and a way to let an assistant work on the deck without silently breaking it.

That last point is the design goal. **Every part of a deck here is text you can edit by hand, and every part is text a model can edit for you.** You are never locked out of either mode. The build tool exists to make the model's edits safe: it checks that no slide overflowed, that no figure got stretched, and that every image actually loaded.

## Quick start

```bash
brew install --cask quarto                  # or see quarto.org
git clone <this repo>
cd huandeng
cp -r template talks/my-talk
cd talks/my-talk
mv template.qmd talk.qmd
make preview
```

A browser opens on the deck and reloads every time you save. Edit `talk.qmd`, and it is your deck.

Every talk starts as a copy of [`template/`](template/). It arrives wearing `university`, the plain one; ten looks travel inside it in [`template/themes/`](template/themes/), and changing to another is two lines of `_quarto.yml`. `make gallery` renders all ten side by side so you can pick by looking.

| | |
| --- | --- |
| `make` | render `out/talk.html` |
| `make preview` | the same, reloading as you save |
| `make check` | render, then look at every slide for the things that fail silently |
| `make all` | also write the PDFs and a PowerPoint of slide images |
| `make standalone` | one self-contained `.html` you can email |
| `make png` | one PNG per slide, so you can read them |
| `make gallery` | every theme side by side, so you can pick one by looking |

`make` and `make preview` need nothing but Quarto. The rest need Python and a headless browser — see [Requirements](#requirements).

Read [`demo/`](demo/) for every feature working at once, and [`demo/README.md`](demo/README.md) for the detail.

### By LLM

Open the folder in [Claude Code](https://claude.com/claude-code) or Codex and ask for what you want, in plain words. The skills in `.agents/skills/` already tell it how this repo works, so you do not have to explain any of it — **`quarto-deck`** for the machinery (the local classes, the build, the traps that raise no error) and **`quarto-academic-style`** for the writing (terse bullets, narrative in speaker notes, readable equations). `quarto-deck` bundles its own reference docs, so an agent can work without searching the web. Both travel with the repository, so a collaborator who clones it gets the same guidance you do.

> Write a deck about the Kelvin–Helmholtz instability, using the figures in `~/figs/` and the notes in `notes.md`.

> Slide 12 is too crowded. Fix it without making the text smaller.

It runs `make check` on its own work, so a slide it accidentally overflowed comes back to it as an error to fix, rather than to you as a surprise on stage.

## What you get

| | |
| --- | --- |
| **One source, five outputs** | HTML, a single self-contained HTML, two PDFs and a PPTX of slide images — from the same `talk.qmd` |
| **A PDF that keeps the builds** | `make pdf` writes one page per *step* to present from, and one page per slide to hand out. Printed from the real deck in headless Chromium, so it is what the room sees — no LaTeX anywhere |
| **Video that needs no pipeline** | an `.mp4` in `attach/` and one `<video>` tag; reveal starts it on the slide and rewinds it on the way out. For an animation that survives the PDF too, a flip-book of frames steps in place live and takes one page per frame on paper |
| **A checker for silent failures** | a reveal.js slide that holds too much does not error and does not shrink — it hangs off the edge, and how much of that the room sees depends on the screen's aspect ratio. `make check` catches it, catches figures drawn at the wrong aspect ratio, and catches images that never loaded |
| **A visible slide boundary** | every slide is laid out in exactly 1280 &times; 720 and scaled to the screen; press **X** to draw that box while you write. See [Slide geometry](demo/README.md#slide-geometry) |
| **Figures with academic credits** | `::: {.fig}` puts the credit against the figure's own edge, not the slide's |
| **A PowerPoint that looks like the deck** | one full-bleed slide image per page at 4K, because the layout is CSS and no PowerPoint writer can read CSS. Not editable, and pixel-identical |
| **Ten looks, none of them locked in** | the default plus nine — `paper`, `swiss`, `whiteprint`, `solarized`, `nord`, `blueprint`, `signal`, `monochrome`, `cobalt`. All ten travel inside every deck, so switching is one line of `_quarto.yml`; `make gallery` renders them side by side so you can pick by looking. [`template/themes/README.md`](template/themes/README.md) |
| **Decks that do not rot** | every deck owns its copies of the theme, the fonts and the assets, so it still renders years later, moved anywhere |

## Layout

```
tools/build-slides.py   the toolchain — shared by every deck, copied into none
template/               the deck you copy to start a talk. themes/ inside it
                        holds ten looks; _quarto.yml picks one
demo/                   every feature, working, as a reference deck
talks/                  yours — gitignored, so your decks stay out of this repo
trash/                  dead ends, with a README recording why they are dead
.agents/skills/         the agent skills (.claude/skills is a symlink to it)
Makefile                make check verifies every deck at once
```

A deck is `talk.qmd` + `_quarto.yml` + `themes/` + `fonts.html` + `guides.html` + `attach/`, plus a `Makefile` that wraps the commands above and holds no build logic of its own.

## Themes

A talk starts as a copy of one of these. Each is a complete deck you can render and look at before you commit to it.

| | |
| --- | --- |
| `university` | azure on white, Fira Sans, a rule under every title — the plain institutional look |
| `paper` | a printed journal page: warm stock, serif text, navy heads, crimson emphasis |
| `swiss` | white, black, one red; heavy rules and tight headings |
| `whiteprint` | an engineering drawing — navy ink on white, monospace on every label |
| `solarized` | low contrast, cream and teal, for a bright room or a long talk |
| `nord` | dark blue-grey with frost accents |
| `blueprint` | deep blue with monospace headings and amber accents |
| `signal` | a briefing paper: warm cream, deep navy, one antique gold; serif titles, monospace labels |
| `monochrome` | ivory and black, and no colour at all — the only colour on the slide is the one in your figure |
| `cobalt` | squared paper: a faint grid over the whole sheet, italic cobalt serif titles |

All ten travel inside every deck, so switching is one line of `_quarto.yml` — no tool, no copying, and undo is undo:

```yaml
    theme: [default, themes/paper.scss]
```

Code blocks come with it: each stylesheet colours the syntax tokens from its own palette, so there is nothing else to set. `make gallery` renders all ten side by side into `out/gallery.html` with that line printed under each name. `make check` afterwards: a slide that fits in one theme can overflow in another.

They differ in shape, not only in colour: `paper`, `whiteprint` and `solarized` carry no progress bar at all, line height runs from 1.28 to 1.42, and `::: {.card}` comes out as a ruled box, a hard offset shadow, a dashed construction line or a raised rounded surface depending on where you are.

Two dark themes are in there because people ask for them, but a figure saved on a white canvas is a bright rectangle on a dark slide and no stylesheet can fix that. [`template/themes/README.md`](template/themes/README.md) has the detail.

## Requirements

- **[Quarto](https://quarto.org/docs/get-started/)** for the HTML. Nothing else is needed if that is all you want.
- **Python 3.13, [uv](https://docs.astral.sh/uv/), and Chromium** for `make check`, `make pdf`, `make png` and `make pptx`:

  ```bash
  uv sync
  uv run playwright install chromium
  ```

  A browser is not an optional extra here: the deck's layout is CSS, so nothing else can print it faithfully or tell you where a slide's content actually landed.
- **ffmpeg**, only if you need to convert a video into something a browser will play.

There is no Node.js requirement and no LaTeX requirement. The usual way to get a PDF out of reveal.js is `decktape`, which needs npm; driving reveal's own `?print-pdf` layout through Playwright does the same job with a dependency the checker needs anyway.

## Every deck is self-contained

A deck must render correctly when copied anywhere, on its own, years later. `themes/`, `_quarto.yml`, `fonts.html`, `guides.html`, `fonts/` and every asset are **copies**, not imports, and no deck reads anything outside its own directory. That is why every theme travels with every deck rather than being looked up in a shared folder: a talk that pointed at `../../themes/paper.scss` would stop rendering the day you emailed it to someone.

The cost is real: improving a theme does not reach a talk you already copied, and carrying a fix across means copying it in by hand. What you buy is that a finished talk is frozen. A deck you gave in 2026 renders identically in 2030, on a different machine, after the template has moved on — because nothing it depends on can change underneath it. For conference talks and lecture notes that get reused and re-sent for years, that trade is worth making.

`out/` is not committed and never needs to be.

## Credits

Built on [Quarto](https://quarto.org/) and [reveal.js](https://revealjs.com/). Fonts are [Fira Sans](https://github.com/mozilla/Fira), SIL OFL. Six of the themes in `template/themes/` take their palettes and typographic character from [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) by lewis, MIT; `signal`, `monochrome` and `cobalt` take theirs from [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates) by zarazhangrui, MIT, by way of [frontend-slides](https://github.com/zarazhangrui/frontend-slides). Nothing is vendored — the palettes and the ideas are the borrowed part, rebuilt here as Quarto SCSS.

MIT licensed. See [LICENSE](LICENSE).
