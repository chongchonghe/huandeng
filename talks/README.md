# Your talks go here

This folder is yours. Everything in it is gitignored except this file, so you can work inside a clone of huandeng without your decks becoming part of it, and without `git pull` ever conflicting with what you wrote.

```bash
cp -r template talks/2027-my-talk
cd talks/2027-my-talk
make preview
```

Then edit `talk.qmd`. From inside the deck, `make` renders it and `make check` verifies it; from the repository root:

```bash
uv run python tools/build-slides.py talks/2027-my-talk          # HTML, PDFs and PPTX
uv run python tools/build-slides.py talks/2027-my-talk --check  # after every slide edit
```

`make check` at the root picks up anything here with a `_quarto.yml`, so your talks are verified along with the template and the demo.

## If you want your talks in version control

They should be, eventually — but not in this repository, because a `git pull` here would then have to merge someone else's toolkit changes into your slides. Two ways to keep them separate:

- **A second repository, with huandeng as a submodule.** Your talks are the repository; huandeng is a pinned dependency you update deliberately. This is how the author uses it.
- **A second repository, and copy what you need.** Copy one of `themes/` into it once and forget about huandeng until you want a newer version. Slower to update, but there is nothing to go wrong.

Either way, remember the rule the rest of this repo is built on: **a deck is self-contained.** `theme.scss`, `_quarto.yml`, `fonts.html`, `guides.html`, the fonts and every asset are copies that live inside the deck folder. Nothing imports from outside it. That is what lets a talk you gave in 2026 still render in 2030, after huandeng has moved on without it.

A deck copied out of here keeps `make` and `make preview`, which need only Quarto. The targets that need the shared tool — `check`, `pdf`, `png`, `pptx`, `standalone` — look for it up the directory tree and say so plainly when it is not there.
