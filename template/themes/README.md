# The ten looks this deck can wear

Every stylesheet here travels with the deck, so changing the look is one line of `_quarto.yml` and nothing else — no tool, no copying, and undo is undo.

```yaml
    theme: [default, themes/paper.scss]
```

That is the whole of it, code blocks included: each stylesheet colours Pandoc's syntax tokens from its own palette, so there is no second setting to keep in step. `make gallery` renders all ten side by side into `out/gallery.html` with that line printed under each name — the easy way to choose.

| theme | ground | reads as | good for |
| --- | --- | --- | --- |
| `university` | white | azure on white, Fira Sans, a rule under every title — the plain institutional look | the default. Start here if you have no reason not to |
| `paper` | warm cream | a printed journal page: serif text, navy heads, crimson emphasis, hairline rules | a seminar where the slides should feel like the paper |
| `swiss` | white | the international style: black, one red, heavy rules, tight headings, nothing decorative | a talk that wants to look deliberate and modern |
| `whiteprint` | white | an engineering drawing: navy ink, square corners, monospace on everything that labels rather than states | methods and instrument talks |
| `solarized` | cream | Ethan Schoonover's light palette — nothing at full black or full white | a long talk, or a bright room where full contrast is tiring |
| `nord` | dark blue-grey | arctic, muted, frost-blue accents | a dark room, if your figures suit it — read the note below |
| `blueprint` | deep blue | a drawing sheet in reverse: monospace headings, amber for anything that matters | the same, with more of a statement |
| `signal` | warm cream | a briefing paper: serif titles in deep navy, one antique gold, monospace on every label, section dividers inverted to a navy band | a talk that should read as considered and institutional rather than loud |
| `monochrome` | ivory | ledger paper and black type, and no colour at all: emphasis is weight, rule and space | any deck whose figures carry the colour, and any room where you cannot predict the projector |
| `cobalt` | near-white | squared paper — a faint 40px grid over the whole sheet, italic cobalt serif titles, hairlines everywhere else | working notes, methods, anything that suits a physicist's pad |

Six take their colour and typographic character from [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) (MIT, by lewis). `signal`, `monochrome` and `cobalt` take theirs from [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates) (MIT, by zarazhangrui), by way of the [frontend-slides](https://github.com/zarazhangrui/frontend-slides) skill. Nothing is imported or vendored in either case; the palettes and the ideas are the borrowed part, rebuilt as Quarto SCSS against this deck's own classes.

## What varies, beyond the colours

A theme that only recoloured the default would not be worth switching to, so these differ in shape as well.

| | |
| --- | --- |
| **Progress bar** | `paper`, `whiteprint` and `solarized` have none — they read as documents, and the slide number already says how far in you are. `swiss` has a flat 6px red one, `nord` a 3px frost line, `blueprint` a 3px amber line, `signal` a 3px gold one, `cobalt` a 3px cobalt one, `monochrome` a 2px black one, `university` a gradient. |
| **Slide title** | a hairline in `paper`, a 3px rule in `swiss`, capitals under a hairline in `whiteprint`, a dashed construction line in `blueprint`. |
| **Subhead (`####`)** | italic serif in `paper`; tracked-out capitals in `swiss`, `solarized` and `nord`; monospace capitals in `whiteprint` and `blueprint`. |
| **`.card`** | a ruled box in `paper`, a hard 6px offset shadow in `swiss`, a square navy outline in `whiteprint`, a soft rounded surface in `solarized`, a raised rounded one in `nord`, dashed in `blueprint`, a gold-topped clipping in `signal`, an unfilled ruled box in `monochrome`, and in `cobalt` an opaque white sheet laid on the grid so the ruling does not read through the text. |
| **Line height** | 1.28 in `swiss` up to 1.42 in `solarized`, the theme for a long talk in a bright room. |
| **Section divider** | centred in most, flush left under a full-measure red bar in `swiss`, capitals in `whiteprint`, and in `signal` a full-measure navy band with the heading knocked out of it — as close to a dark slide as a stylesheet can get, since a real slide background has to be an attribute. |

## What switching cannot reach

No theme puts a field of colour behind the title slide or the closing slide. Both stand on the deck's own ground, with the type and a hairline under the title doing the work. To turn a colour field back on, uncomment `title-slide-attributes` in `_quarto.yml` and set the four title-slide colours in the stylesheet to something that reads on it. That has to be YAML rather than CSS: reveal paints slide backgrounds on a layer outside the slide's own margin, where a stylesheet cannot reach.

The other thing switching cannot reach is a colour you wrote into a slide yourself:

```markdown
## Results {background-color="#0a6ebd"}
```

That stays azure on a deck that has just gone dark grey. It has to: reveal reads the attribute as a literal colour, and writing `var(--deck-primary)` there would defeat the brightness test it uses to decide whether the type on that slide turns white. So a colour in a slide belongs to the talk, not the theme — grep for `background-color="#` after switching.

## Dark themes and scientific figures

Almost every plot comes out of matplotlib, IDL or IRAF on a white canvas. On `nord` or `blueprint` that figure is a bright rectangle punched into the slide, and the axis labels stay black on white while everything around them is light on dark. There is no CSS fix — inverting an image also inverts the colour map, which changes what the figure says.

So a dark theme is a decision about your figures first. Either save them with a transparent or dark background (`savefig(..., transparent=True)` plus light axis colours), or use one of the eight light themes. `make png` and looking at the result is the only way to know.

## How each file is built

`university.scss` is the source. Every other stylesheet here has three parts:

1. a header — the SCSS defaults and the `:root` custom properties, which is where the colours and the typeface live, including the five `--deck-code-*` values the code tokens are drawn in;
2. the shared body, byte-identical to `university.scss` from `.reveal {` onwards — every local class, unchanged;
3. an appendix under a marked banner, which is what makes the theme that theme.

To carry a fix from `university` into a theme, replace part 2. To change a theme, edit parts 1 and 3. The split exists so those two operations never collide.

Two custom properties appear in the other nine that `university` does not have, because it writes both as literals: `--deck-accent`, the second colour a theme uses for emphasis, and `--deck-code-bg`. A theme may add its own on top — `signal` carries a second gold for type on navy, `cobalt` the colour of its ruling and the opaque stock it cuts cards from.

## Fonts

The deck ships `fonts/` — Fira Sans, seven faces — and every theme uses it somewhere: as the body face in eight of them, and in `paper` for the running foot, the captions and the figure credits, which is how a printed paper sets its metadata against a serif text.

The other families are named, not shipped: Helvetica Neue in `swiss`, Charter and Palatino in `paper`, an old-style serif — Iowan, Palatino, Charter, Georgia — for the titles of `signal` and `cobalt`, and the system monospace in `whiteprint`, `blueprint`, `signal` and `cobalt`. Each falls back through a stack that ends in something every machine has, so a deck in one of those themes renders very close on a machine that is not yours rather than pixel-identical. `monochrome` names nothing beyond the shipped Fira Sans, so it is the one theme that is pixel-identical anywhere.

## After switching, look

`make check` after any change — a slide that fits in one theme can overflow in another, because the line heights and the type scales are not the same. `make png` writes one PNG per slide if you want to read them.
