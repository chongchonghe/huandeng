# Themes — the ten starting points

**Every talk starts by copying one of these folders.** Each is a complete, self-contained deck: `cd themes/paper && make` renders it with nothing but Quarto, and it goes on rendering years later on a machine that has never seen this repository.

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

Six of them take their colour and typographic character from [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) (MIT, by lewis), a pure HTML/CSS deck builder. `signal`, `monochrome` and `cobalt` take theirs from [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates) (MIT, by zarazhangrui), by way of the [frontend-slides](https://github.com/zarazhangrui/frontend-slides) skill. Nothing is imported or vendored in either case; the palettes and the ideas are the borrowed part, rebuilt as Quarto SCSS against this repo's own classes.

## Start a talk

```bash
cp -r themes/paper talks/2027-my-talk     # pick any row above
cd talks/2027-my-talk
mv template.qmd talk.qmd                  # one .qmd per deck; the name is yours
make preview
```

Fill in the YAML block at the top of the `.qmd` first: title, author, institute, the `footer` line, which is the only place the short forms appear, and `density:` — `speaker-led` if you will talk over it, `reading-first` if it will be read alone. That last one decides what goes on every slide; the **quarto-academic-style** skill says how. Then write. **Never edit a `themes/` folder to write a talk** — copy it first, or you change what everybody starts from.

## What is in a deck

| | |
| --- | --- |
| `talk.qmd` | your slides — normally the only file you touch |
| `_quarto.yml` | slide size, slide level, and every deck-wide option |
| `theme.scss` | the look: colours, type, the layout classes |
| `fonts.html` | ships Fira Sans with the deck; see the note inside |
| `guides.html` | the **X** key: draws the 1280 × 720 slide boundary while you write |
| `attach/` | images and video, referenced as `attach/foo.png` |
| `fonts/` | Fira Sans, so the deck renders the same anywhere |
| `ref.bib` | citations, if the talk has any |

All of it is a copy. No deck reads anything outside its own directory, which is what makes a finished talk frozen.

## Building

```bash
make            # render out/talk.html — Quarto alone, nothing else needed
make preview    # the same, in a browser that reloads as you save
make check      # render, then look at every slide
make all        # HTML, PDF and PPTX
make standalone # one self-contained .html to email
make themes     # the looks available, by name
make gallery    # ...and by sight: every one rendered into out/gallery.html
make theme THEME=nord   # copy one of them over this deck's
```

`make pdf` writes two files, printed from the built deck in headless Chromium — no LaTeX anywhere:

| | |
| --- | --- |
| `out/talk.pdf` | one page per **step**, so builds and flip-books survive; present from this |
| `out/talk-one-page-per-slide.pdf` | one page per slide, fully built; the handout |

A `<video>` prints as one still frame. For an animation that survives on paper, use an `.r-stack` of image frames with `::: {.fragment .fade-in-then-out}` on each after the first — every frame then gets its own PDF page.

`make pptx` rasterises that PDF into `out/talk.pptx`, one full-bleed image per slide at 3840 px wide — a source pixel behind every pixel of a 4K projector. Nothing is editable in PowerPoint; in exchange the deck arrives looking like itself, which Pandoc's native writer cannot manage because the layout is CSS. For a different size, run the tool directly with `--width 5120` or `--width 1920`.

## The classes you get

`##` starts a slide, `#` starts a section, `. . .` reveals the rest of it on the next keypress. Layout comes from classes in `theme.scss`, the same set in every theme:

| | |
| --- | --- |
| `::: {.fig}` + `[..]{.credit}` | figure with a source credit; `.caption` above it, `.below` under it |
| `::: {.columns}` | a 50/50 split — prefer this one, it is the class Pandoc understands, so PPTX gets real columns |
| `::: {.columns-3-2}` | other ratios; also `-2-1`, `-1-2`, `-2-3`, `-1-1-1` |
| `::: {.media-row}` | a labelled strip of images, on one line |
| `::: {.highlight}` | the callout for the one sentence a slide is about |
| `::: {.card}` | a box round a group; `[..]{.pill}` for an inline tag |
| `[..]{.alert}`, `.small`, `.tiny`, `.center`, `.muted` | inline emphasis and sizing |
| `<video class="r-stretch" …>` | video, sized to whatever height the slide has left |

Reveal.js brings `.incremental`, `.fragment`, `.absolute`, `.r-stack` and `{background-color=".."}` on top of that.

## Changing your mind later

```bash
cd talks/2027-my-talk
make themes                       # what there is
make theme THEME=nord             # put that look on this deck
make check                        # then look at it
```

Commit before you run it. The command overwrites `theme.scss` and rewrites one line of `_quarto.yml`, so `git diff` is how you read what happened and `git checkout` is how you undo it. `make theme THEME=university` takes a deck back to the default.

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

The hard offset shadow, the card and the pill are the ideas worth taking from html-ppt-skill; they are rebuilt here rather than copied.

## What a theme owns, and what it does not

A theme is `theme.scss` plus one line of `_quarto.yml`: `highlight-style`, which sets the colours inside a code block. That one cannot live in the SCSS, because it is a Pandoc theme rather than a stylesheet.

No theme puts a field of colour behind the title slide or the closing slide. Both stand on the deck's own ground, with the type and a hairline under the title doing the work. To turn a colour field back on, uncomment `title-slide-attributes` in your deck's `_quarto.yml` and set the four title-slide colours in `theme.scss` to something that reads on it. That has to be YAML rather than CSS: reveal paints slide backgrounds on a layer outside the slide's own margin, where a stylesheet cannot reach.

The one thing switching cannot reach is a colour you wrote into a slide yourself. No deck here ships one, but if you add one:

```markdown
## Results {background-color="#0a6ebd"}
```

it stays azure on a deck that has just gone dark grey. It has to: reveal reads that attribute as a literal colour, and writing `var(--deck-primary)` there would defeat the brightness test it uses to decide whether the type on that slide turns white. So a colour in a slide belongs to the talk, not the theme — `make theme` prints a note when it finds one.

## Dark themes and scientific figures

Almost every plot comes out of matplotlib, IDL or IRAF on a white canvas. On `nord` or `blueprint` that figure is a bright rectangle punched into the slide, and the axis labels stay black on white while everything around them is light on dark. There is no CSS fix — inverting an image also inverts the colour map, which changes what the figure says.

So a dark theme is a decision about your figures first. Either save them with a transparent or dark background (`savefig(..., transparent=True)` plus light axis colours), or use one of the eight light themes. `make png` and looking at the result is the only way to know.

## How each theme file is built

`themes/university/theme.scss` is the source. Every other `theme.scss` in here has three parts:

1. a header — the SCSS defaults and the `:root` custom properties, which is where the colours and the typeface live;
2. the shared body, byte-identical to `themes/university/theme.scss` from `.reveal {` onwards — every local class, unchanged;
3. an appendix under a marked banner, which is what makes the theme that theme.

To carry a fix from `university` into a theme, replace part 2. To change a theme, edit parts 1 and 3. The split exists so those two operations never collide.

Two custom properties appear in the other nine that `university` does not have, because it writes both as literals: `--deck-accent`, the second colour a theme uses for emphasis, and `--deck-code-bg`. A theme may add its own on top — `signal` carries a second gold for type on navy, `cobalt` the colour of its ruling and the opaque stock it cuts cards from.

## Fonts

Every theme ships the same `fonts/` — Fira Sans, seven faces — and every theme uses it somewhere: as the body face in eight of them, and in `paper` for the running foot, the captions and the figure credits, which is how a printed paper sets its metadata against a serif text.

The other families are named, not shipped: Helvetica Neue in `swiss`, Charter and Palatino in `paper`, an old-style serif — Iowan, Palatino, Charter, Georgia — for the titles of `signal` and `cobalt`, and the system monospace in `whiteprint`, `blueprint`, `signal` and `cobalt`. `monochrome` names nothing at all beyond the shipped Fira Sans, so it is the one theme here that is pixel-identical anywhere. Each falls back through a stack that ends in something every machine has. A deck in one of those themes therefore renders very close on a machine that is not yours, rather than pixel-identical — which is the trade for not putting another 2 MB of licensed type in the repository. Only Fira Sans is guaranteed.

## One rule

After any slide edit, run `make check`. A reveal.js slide that holds too much does not error and does not shrink — the surplus hangs into the margin and is then cut off by the window edge, and a 16:10 laptop shows about 57 slide-px of it where a 16:9 projector shows 15. So a slide can look merely tight while you write it and be cut on stage. Press **X** to see the boundary while you work.

## Where to look next

- **[`../demo/`](../demo/)** — every class above working, with commentary. The reference deck.
- **[`../demo/README.md`](../demo/README.md)** — the figure and video details, what `make check` looks for, and the Quarto traps worth knowing before you hit them.
