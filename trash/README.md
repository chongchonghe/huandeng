# Roads not taken

Dead ends, kept because knowing *why* they are dead ends is worth more than the disk they cost. Nothing here is part of the build; nothing here is committed except this file. Delete the folder whenever you like — the commands below regenerate all of it.

The question these answer: **can a Quarto deck be turned into a PDF by something other than a browser?** Every attempt below says no, for the same underlying reason — the layout here is CSS, and neither LaTeX nor Typst can read CSS.

| file | what made it | verdict |
| --- | --- | --- |
| *(not kept)* | `quarto render talk.qmd --to pdf` — Pandoc → LuaLaTeX | 2 pages, US Letter **portrait**. An article. The deck is gone. |
| `talk-typst-letter.pdf` | `--to typst`, Quarto's stock Typst format | 2 pages, US Letter portrait. Same as above, without the LaTeX. |
| `talk-typst-16x9.pdf` | `--to typst` with `papersize: presentation-16-9` | 4 pages at 841.89 × 473.56 pt. 16:9 paper, but the content is still one continuous flow — 6 slides did not become 6 pages. |
| `talk-typst-source.typ` | the same run with `keep-typ: true` | The evidence. **Zero `pagebreak` calls**, and the `::: notes` block emitted as body text at line 444. Pandoc has no idea those headings were slides. |
| `talk-touying.pdf` | `quarto add kazuyanagimoto/quarto-clean-typst`, then `--to clean-typst` | Real slides — title slide, section dividers, slide numbers, one page per `##`. But the two-column slide lost its columns, stacked, split across two pages, and stranded the figure credit alone under a repeated title. |
| `demo-touying.pdf` | the same, on `demo/` | The full picture: **34 slides → 58 pages**, and Touying's own counter reads 53. See below. |

## What the Touying bridge does to this deck

It is the closest of the three, and worth understanding rather than dismissing — [`kazuyanagimoto/quarto-clean-typst`](https://github.com/kazuyanagimoto/quarto-clean-typst) wrapping the [`touying-quarto-clean`](https://typst.app/universe/package/touying-quarto-clean/) Typst package. Run on `demo/`:

- **survives** — headings, bullets, tables, highlighted code, ordinary maths, citations, and Mermaid (Quarto renders it to an image Typst embeds)
- **silently lost** — video renders as *nothing*, leaving "Gas density around an accreting black hole" as a caption over blank space
- **silently broken** — the `\class{fragment}{..}` equation falls through as raw LaTeX, printing `$$ \underbrace{\frac{1}{c}...` verbatim across the slide. Ordinary maths on the neighbouring slide typesets fine, so it is that construct alone.
- **re-flowed** — every `.columns-*` collapses and the slide splits two to four ways
- **dropped** — `.highlight`, `.fig`, `.media-row`, `.absolute`, `.r-stack`, the footer, and `theme.scss` entirely
- **leaked** — `::: notes` printed into the body, where an audience reads it

None of that is a bug in the extension. It is a different deck built from the same Markdown, not an exporter for this one. If you want slides genuinely built by Typst, write [Touying](https://github.com/touying-typ/touying) by hand — its full API beats whatever survives a Markdown round trip.

## Pandoc's own PowerPoint writer

`demo-pandoc-styled.pptx` and `make-reference-pptx.py` are the second dead end, and they are here for the same reason: to save the next person the afternoon.

Pandoc has a real PPTX writer, and it can be styled — not by CSS but by a *reference document*, which supplies the slide masters, layouts, theme fonts and theme colours. The script rebuilds Pandoc's own default with the deck's palette, and patches `<p:titleStyle>` on the master so titles come out primary blue and left aligned rather than centred black. It works, as far as it goes:

- `.columns` (not `.columns-1-1` — Pandoc only knows the former) becomes a real two-column **Two Content** slide
- theme colours travel inside the file, so they always arrive
- fonts do **not** travel: PowerPoint embeds fonts on Windows only and Pandoc does not do it at all, so the reference doc used Aptos rather than the deck's Fira Sans

And it still looked like a Pandoc outline rather than the deck, because everything that gives a slide its shape here — the columns beyond 50/50, `.fig` and its credits, `.media-row`, `.highlight`, `.absolute`, the footer, fragments — is CSS, and PowerPoint has never heard of CSS.

**The conclusion is the same as the Typst one, and it is the same conclusion twice: only a browser can render this deck.** So `--pptx` now rasterises the PDF and ships one full-bleed image per slide. Nothing is editable in PowerPoint, and in exchange the deck arrives looking like itself.

## Regenerating any of this

```bash
cp -r template /tmp/scratch && cd /tmp/scratch

quarto render talk.qmd --to pdf                       # LuaLaTeX
quarto render talk.qmd --to typst -M keep-typ:true    # stock Typst

quarto add kazuyanagimoto/quarto-clean-typst
quarto render talk.qmd --to clean-typst               # Touying
```

## The conclusion that stuck

`make pdf` prints the built deck in headless Chromium, through reveal's own `?print-pdf` layout. It is the only route that renders the deck you actually wrote, because it is the only one that renders CSS — and it has never involved LaTeX at any point. See **Slide geometry** in [`../demo/README.md`](../demo/README.md).
