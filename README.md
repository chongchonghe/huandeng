# 幻灯 Huandeng

**Academic slide decks in plain text — built on [Touying](https://github.com/touying-typ/touying) and [Typst](https://typst.app), with agent skills so an LLM can help without taking the wheel.**

[中文说明](README.zh-CN.md)

One source file becomes a PDF you present from, an HTML page you can send to anyone, and a PPTX for the conference that insists on it. Videos play in all three. A checker catches the mistakes that would otherwise reach the room.

幻灯 (huàndēng) is the Chinese word for a slide, from 幻灯片 — literally "magic lantern". Touying (投影) is the projection; huandeng is what gets projected.

## Why this exists

Keynote and PowerPoint are fast until the moment you want a language model to help. Then the deck is a binary blob: the model cannot read it, cannot diff it, and cannot edit one word without rewriting a file it does not understand. LaTeX Beamer is plain text but slow to compile and painful to lay out. Typst fixes the compile and the layout; Touying makes it a presentation framework. What was still missing is the part around it — the export formats a real talk needs, the video pipeline, and a way to let an assistant work on the deck without silently breaking it.

That last point is the design goal. **Every part of a deck here is text you can edit by hand, and every part is text a model can edit for you.** You are never locked out of either mode. The build tool exists to make the model's edits safe: it checks that no slide overflowed, that no figure got stretched, and that the page count is what the source says it should be.

## Quick start

Two ways in. They are the same deck either way — files you can open, read and edit yourself.

### By hand

```bash
brew install typst                                  # or see typst.app for your system
git clone https://github.com/chongchonghe/huandeng.git
cd huandeng
cp -r template talks/my-talk                        # your copy — leave template/ alone
cd talks/my-talk
make
```

That writes `out/my-talk.pdf`. Open it: a finished deck, ready to present. Now edit `content.typ`, run `make` again, and it is your deck.

`make` is the only command you need day to day. Three others when you want them:

| | |
| --- | --- |
| `make` | build the PDF |
| `make watch` | rebuild every time you save, so you can leave the PDF open beside the text |
| `make check` | build, then confirm nothing quietly overflowed a slide |
| `make all` | also write an HTML page and a PowerPoint file |

**What `make` actually runs** is one line:

```bash
typst compile --font-path fonts main.typ out/my-talk.pdf
```

Type that yourself if you prefer — nothing is hidden. The reason to use `make` is `--font-path fonts`: leave it off and Typst quietly swaps in a different font and re-flows the whole deck. `make` cannot forget it.

`make` and `make watch` need only Typst. `make check` and `make all` also need Python — see [Requirements](#requirements).

### By LLM

Open the folder in [Claude Code](https://claude.com/claude-code) or Codex and ask for what you want, in plain words. The skills in `.agents/skills/` already tell it how this repo works, so you do not have to explain any of it.

> Convert my slides in `~/Desktop/group-meeting.pptx` into a new deck under `talks/`.

> Write a deck about the Kelvin–Helmholtz instability, using the figures in `~/figs/` and the notes in `notes.md`.

> Slide 12 is too crowded. Fix it without making the text smaller.

It runs `make check` on its own work, so a slide it accidentally overflowed comes back to it as an error to fix, rather than to you as a surprise on stage.

You are not locked in. Everything it writes is the same plain text you would have written, in the same files, and you can take over with `make watch` at any point.

Read `demo/` for every feature working at once, and [`demo/README.md`](demo/README.md) for the detail.

## What you get

| | |
| --- | --- |
| **One source, three formats** | PDF, a self-contained HTML page, and PPTX — from the same `content.typ` |
| **Video that survives the format** | real `<video>` in HTML and a movie shape in PPTX, a sampled flip-book in the PDF, all from one `#movie("name")` |
| **A checker for silent failures** | an overflowing slide does not error in Typst — it quietly splits across two pages. `--check` catches that, and catches figures drawn at the wrong aspect ratio |
| **Figures with academic credits** | `#fig("x.png", caption: [..], credit: [He et al. 2025])` — the credit hugs the figure's own edge, not the slide's |
| **Agent skills** | `slide-deck` for authoring, `pptx-to-typst` for converting a deck you already have, `touying-author` for Touying itself |
| **Decks that do not rot** | every deck owns its copies of the helpers, the fonts and the assets, so it still renders years later, moved anywhere |

## Working with an LLM

Three skills live in `.agents/skills/`, with `.claude/skills` symlinked to it — and `AGENTS.md` is the real instruction file, with `CLAUDE.md` symlinked to that. The agent-neutral name is the canonical one in both cases, so Claude Code and Codex read the same files and any other agent needs at most one more symlink. (On Windows, clone with `git config --global core.symlinks true` set, or those two links arrive as ordinary text files.)

- **`slide-deck`** — how to write slides here: the local helpers that are not part of stock Touying, the house style, and the traps that fail without an error message.
- **`pptx-to-typst`** — convert a PowerPoint or Keynote deck you already have. Not a screenshot import: it extracts the media, reads PowerPoint's own crop rectangles so figures come out cropped the way you cropped them, corrects the pixel aspect ratio of videos, and re-typesets the text as real Typst so you can edit it afterwards.
- **`touying-author`** — the upstream Touying documentation, vendored, so the model does not have to guess at the API.

The reason this combination works is the checker. An assistant editing slides will occasionally write one line too many, and Typst will not complain — it will just push the overflow onto a second page that looks almost right. `--check` turns that into an error with a slide name, so the model can find and fix its own mistake before you ever see it.

## Requirements

- **Typst** for the PDF. Nothing else is needed if the PDF is all you want.
- **Python 3.13 and [uv](https://docs.astral.sh/uv/)** for HTML, PPTX and `--check`. Dependencies are pinned in `uv.lock`.
- **ffmpeg**, only if your deck has video.

## Layout

```
tools/build-slides.py   the toolchain — shared by every deck, copied into none
template/               the starting point. Copy it; never edit it in place.
demo/                   every feature, working, as a reference deck
talks/                  yours — gitignored, so your decks stay out of this repo
.agents/skills/         the agent skills (.claude/skills is a symlink to it)
```

A deck is `main.typ` + `globals.typ` + `content.typ` + `attach/`, and contains no build script of its own.

## A design decision worth knowing about

**Every deck is self-contained, and that duplication is deliberate.** `globals.typ`, `main.typ` and the fonts are *copies*, not imports. No deck reads anything outside its own directory.

The cost is real: improving `template/` does not reach a talk you already copied, and carrying a fix across means copying it in by hand. What you buy is that a finished talk is frozen. A deck you gave in 2026 renders identically in 2030, on a different machine, after the template has moved on — because nothing it depends on can change underneath it. For conference talks and lecture notes that get reused and re-sent for years, that trade is worth making.

## Credits

Built on [Touying](https://github.com/touying-typ/touying) by the touying-typ authors, and [Typst](https://typst.app). Fonts are [Fira Sans](https://github.com/mozilla/Fira) and [Fira Math](https://github.com/firamath/firamath), SIL OFL.

MIT licensed. See [LICENSE](LICENSE).
