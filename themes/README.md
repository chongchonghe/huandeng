# Themes

Six alternative looks, adapted from [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) (MIT, by lewis) — that project is a pure HTML/CSS deck builder, and what carried over is its colour and typography, rebuilt as Quarto SCSS. Nothing in it is imported or vendored; the palettes and the typographic character are the borrowed part.

The default look — azure on white, Fira Sans — is not in here. It lives in `template/theme.scss` and `demo/theme.scss` and is untouched by any of this.

| theme | ground | reads as | good for |
| --- | --- | --- | --- |
| `paper` | warm cream | a printed journal page: serif text, navy heads, crimson emphasis, hairline rules | a seminar where the slides should feel like the paper |
| `swiss` | white | the international style: black, one red, heavy rules, tight headings, nothing decorative | a talk that wants to look deliberate and modern |
| `whiteprint` | white | an engineering drawing: navy ink, square corners, monospace on everything that labels rather than states | methods and instrument talks |
| `solarized` | cream | Ethan Schoonover's light palette — nothing at full black or full white | a long talk, or a bright room where full contrast is tiring |
| `nord` | dark blue-grey | arctic, muted, frost-blue accents | a dark room, if your figures suit it — read the note below |
| `blueprint` | deep blue | a drawing sheet in reverse: monospace headings, amber for anything that matters | the same, with more of a statement |

Each directory is a complete deck. `cd themes/paper && make` renders it; `make check` verifies it, and the repository's own `make check` walks all six.

## What varies, beyond the colours

A theme that only recoloured the default would not be worth switching to, so these differ in shape as well.

| | |
| --- | --- |
| **Progress bar** | `paper`, `whiteprint` and `solarized` have none — they read as documents, and the slide number already says how far in you are. `swiss` has a flat 6px red one, `nord` a 3px frost line, `blueprint` a 3px amber line, the default a gradient. |
| **Slide title** | a hairline in `paper`, a 3px rule in `swiss`, capitals under a hairline in `whiteprint`, a dashed construction line in `blueprint`. |
| **Subhead (`####`)** | italic serif in `paper`; tracked-out capitals in `swiss`, `solarized` and `nord`; monospace capitals in `whiteprint` and `blueprint`. |
| **`.card`** | a ruled box in `paper`, a hard 6px offset shadow in `swiss`, a square navy outline in `whiteprint`, a soft rounded surface in `solarized`, a raised rounded one in `nord`, dashed in `blueprint`. |
| **Line height** | 1.28 in `swiss` up to 1.42 in `solarized`, the theme for a long talk in a bright room. |
| **Section divider** | centred in most, flush left under a full-measure red bar in `swiss`, capitals in `whiteprint`. |

The hard offset shadow, the card and the pill are the ideas worth taking from html-ppt-skill; they are rebuilt here rather than copied.

## Starting a talk in a theme

```bash
cp -r themes/paper talks/2027-my-talk
cd talks/2027-my-talk
mv template.qmd talk.qmd          # one .qmd per deck; the name is yours
make preview
```

That is the same move as `cp -r template talks/...`, with a different look already in place.

## Changing the theme of a deck you have already written

```bash
cd talks/2027-my-talk
make themes                       # what there is
make theme THEME=nord             # put that look on this deck
make check                        # then look at it
```

Commit before you run it. The command overwrites `theme.scss` and rewrites one line of `_quarto.yml`, so `git diff` is how you read what happened and `git checkout` is how you undo it.

## What a theme owns, and what it does not

A theme is `theme.scss` plus one line of `_quarto.yml`: `highlight-style`, which sets the colours inside a code block. That one cannot live in the SCSS, because it is a Pandoc theme rather than a stylesheet.

No theme puts a field of colour behind the title slide or the closing slide. Both stand on the deck's own ground, with the type and a hairline under the title doing the work. To turn a colour field back on, uncomment `title-slide-attributes` in your deck's `_quarto.yml` and set the four title-slide colours in `theme.scss` to something that reads on it. That has to be YAML rather than CSS: reveal paints slide backgrounds on a layer outside the slide's own margin, where a stylesheet cannot reach.

The one thing switching cannot reach is a colour you wrote into a slide yourself. No deck here ships
one, but if you add one:

```markdown
## Results {background-color="#0a6ebd"}
```

it stays azure on a deck that has just gone dark grey. It has to: reveal reads that attribute as a literal colour, and writing `var(--deck-primary)` there would defeat the brightness test it uses to decide whether the type on that slide turns white. So a colour in a slide belongs to the talk, not the theme — `make theme` prints a note when it finds one.

## Dark themes and scientific figures

Almost every plot comes out of matplotlib, IDL or IRAF on a white canvas. On `nord` or `blueprint` that figure is a bright rectangle punched into the slide, and the axis labels stay black on white while everything around them is light on dark. There is no CSS fix — inverting an image also inverts the colour map, which changes what the figure says.

So a dark theme is a decision about your figures first. Either save them with a transparent or dark background (`savefig(..., transparent=True)` plus light axis colours), or use one of the four light themes. `make png` and looking at the result is the only way to know.

## How each theme file is built

Every `theme.scss` in here has three parts:

1. a header — the SCSS defaults and the `:root` custom properties, which is where the colours and the typeface live;
2. the shared body, byte-identical to `template/theme.scss` from `.reveal {` onwards — every local class, unchanged;
3. an appendix under a marked banner, which is what makes the theme that theme.

To carry a fix from `template/theme.scss` into a theme, replace part 2. To change a theme, edit parts 1 and 3. The split exists so those two operations never collide.

Two custom properties appear here that `template/theme.scss` does not have, because it writes both as literals: `--deck-accent`, the second colour a theme uses for emphasis, and `--deck-code-bg`.

## Fonts

Every theme ships the same `fonts/` — Fira Sans, seven faces — and every theme uses it somewhere: as the body face in four of them, and in `paper` for the running foot, the captions and the figure credits, which is how a printed paper sets its metadata against a serif text.

The other families are named, not shipped: Helvetica Neue in `swiss`, Charter and Palatino in `paper`, the system monospace in `whiteprint` and `blueprint`. Each falls back through a stack that ends in something every machine has. A deck in one of those themes therefore renders very close on a machine that is not yours, rather than pixel-identical — which is the trade for not putting another 2 MB of licensed type in the repository. Only Fira Sans is guaranteed.
