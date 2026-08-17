# Citations

Declare the bibliography in the deck's YAML:

```yaml
bibliography: ref.bib
csl: mnras.csl        # optional; a journal's own style
```

Cite with Pandoc syntax:

```markdown
@Rosdahl2013 implemented RAMSES-RT              <!-- narrative -->
M1 closure methods [e.g., @Rosdahl2013; @Kannan2019]   <!-- parenthetical -->
[-@Rosdahl2013]                                  <!-- year only -->
```

## The trap: you must add a References slide

If `bibliography` is declared **and anything is cited**, add:

```markdown
## References

::: {#refs}
:::
```

Without it Pandoc has nowhere to put the generated bibliography, so it appends the `#refs` div
*outside every `<section>`* — and reveal.js then paints the whole reference list on top of every
slide in the deck. It is immediately obvious once it happens and mystifying until you know why.

Skip the slide entirely if the deck cites nothing. Declaring `bibliography` alone is harmless.

## Placement

The References slide is conventionally last, before any closing slide. `#refs` styling is in
`theme.scss` (0.62em, spaced entries); a long list will overflow, and `make check` will say so —
split it across two slides with a second `::: {#refs}` is *not* possible, so either trim the
bibliography or put it on a `{.smaller}` slide.

## Getting the .bib

Any BibTeX file works. For astronomy, NASA ADS exports one per paper or per library. Keep it in the
deck folder as `ref.bib` — like everything else in a deck, it is a copy, so the talk still builds in
five years when your reference manager has moved on.

## Claims

Verifying that a cited number is actually the number in the paper is a *writing* concern, not a
mechanical one — see the **quarto-academic-style** skill.
