# Your talks go here

This folder is yours. Everything in it is gitignored except this file, so you can work inside a clone of huandeng without your decks becoming part of it, and without `git pull` ever conflicting with what you wrote.

Both flavours live here side by side. A Typst talk has a `main.typ`, a Quarto talk has a `_quarto.yml`, and each toolchain finds only its own.

```bash
cp -r template talks/2027-my-talk          # Typst + Touying
cp -r quarto/template talks/2027-my-talk   # Quarto + reveal.js
```

Then edit `content.typ` or `talk.qmd`, and build — from inside the deck, `make` is the same word in either:

```bash
# Typst
typst compile --font-path talks/2027-my-talk/fonts talks/2027-my-talk/main.typ talks/2027-my-talk/out/talk.pdf
uv run python tools/build-slides.py talks/2027-my-talk          # PDF, HTML and PPTX
uv run python tools/build-slides.py talks/2027-my-talk --check  # after every slide edit

# Quarto
uv run --extra quarto python quarto/tools/build-slides.py talks/2027-my-talk
uv run --extra quarto python quarto/tools/build-slides.py talks/2027-my-talk --check
```

## If you want your talks in version control

They should be, eventually — but not in this repository, because a `git pull` here would then have to merge someone else's toolkit changes into your slides. Two ways to keep them separate:

- **A second repository, with huandeng as a submodule.** Your talks are the repository; huandeng is a pinned dependency you update deliberately. This is how the author uses it.
- **A second repository, and copy what you need.** Copy `template/` into it once and forget about huandeng until you want a newer version. Slower to update, but there is nothing to go wrong.

Either way, remember the rule the rest of this repo is built on: **a deck is self-contained.** `globals.typ` and `main.typ` — or `theme.scss` and `_quarto.yml` — the fonts and every asset are copies that live inside the deck folder. Nothing imports from outside it. That is what lets a talk you gave in 2026 still render in 2030, after huandeng has moved on without it.
