---
name: slide-style
description: House style for writing academic talk slides in this repo — concise slides, narrative in speaker notes, readable equations, citations, acronyms, figure placeholders. Use when drafting or revising the prose and maths of a .qmd, or reviewing a deck for readability before a talk. Covers what to write; quarto-deck covers the machinery that renders it.
---

# Slide style

**quarto-deck** covers the *mechanics* — the layout classes, the build, the traps that raise no
error. This skill covers *style*: how to write slides that read from the back row.

**Core principle:** slides are terse and telegraphic; the narrative lives in the speaker notes.
Equations are written for a reader, not a typesetter.

## 1. Slides are terse; notes carry the narrative

- One idea per slide. Each bullet at most about two lines.
- If a bullet *explains* or *narrates*, move that prose into `::: notes` and shorten the bullet to a
  claim plus its key symbol.
- End a content slide with a one-sentence takeaway in `::: {.highlight}`.
- Speaker notes are full spoken paragraphs, written to be read aloud, **ending with a transition
  into the next slide**.

```markdown
<!-- the bullet narrates -->
- **Virial equilibrium** — gravity is balanced by turbulent and thermal
  support, which we can quantify using the virial parameter alpha-vir,
  and observations of giant molecular clouds place them at around one
  to two, meaning they are bound but not collapsing everywhere...

<!-- the bullet states; the notes narrate -->
- **Virial equilibrium** — gravity balanced by turbulent + thermal support,
  $2E_{\rm kin}+E_{\rm grav}=0$; virial parameter
  $\alpha_{\rm vir}\equiv 2E_{\rm kin}/|E_{\rm grav}|$, with GMCs near
  $\alpha_{\rm vir}\sim 1\text{--}2$
```

## 2. Write readable equations

Prefer the **physics-meaningful form** over the algebraically expanded one. A reader should grasp
the meaning without parsing the algebra. Keep the full prefactor only when its value is the point.

| readable | over-expanded |
| --- | --- |
| $\alpha_{\rm vir}\equiv 2E_{\rm kin}/\|E_{\rm grav}\|$ | $\alpha_{\rm vir}\equiv 5\sigma_v^2 R/(GM)$ |
| $M_J\propto c_s^3/\sqrt{\rho}$ | $M_J=\frac{\pi^{5/2}}{6}\frac{c_s^3}{G^{3/2}\rho^{1/2}}$, unless the constant is the point |
| $t_{\rm ff}\sim 1/\sqrt{G\rho}$ | $t_{\rm ff}=\sqrt{3\pi/(32G\rho)}$ on a dense slide |

**Maths hygiene:**

- Roman subscripts: `M_{\rm J}`, `t_{\rm ff}`, `\alpha_{\rm vir}`, `\Gamma_{\rm IMF}`.
- Thin space in units: `$\sim 0.03\,M_\odot$`, `$M_\odot\,{\rm pc}^{-2}$`.
- `$\sim$` is "of order" (one value); `$\approx$` is "approximately equal" (relates two expressions).
- Numeric ranges: `\text{--}` inside one maths span, or a literal en dash in prose. Never `-` inside
  maths — that is subtraction.
- Colour: `\color{red}{..}`, never `\textcolor` — the web maths renderer does not define it and
  prints it as literal red error text.
- Inline maths for short expressions. At most **one** display `$$..$$` per dense column; more risks
  running off the bottom.
- `\class{fragment}{..}` builds an equation up one term per keypress, and the whole equation stays
  one slide.

## 3. Layout per slide

- Bullets left, figure right: `::: {.columns-3-2}`. For a balanced split use `::: {.columns}` — that
  is the class Pandoc recognises, so the PPTX export gets real columns rather than one flattened
  text box.
- Use a **placeholder** until the real asset exists: `![](attach/placeholder.png)` plus an HTML
  comment naming the intended figure and where it comes from.
- Size images in `px` or `pt`, never `%` inside `.fig` — see quarto-deck.

## 4. Citations and claims

- `bibliography: ref.bib` in the YAML; cite with `[@Key]`.
- If anything is cited, add a References slide — `::: {#refs} :::` — or Pandoc drops the bibliography
  outside every `<section>` and reveal.js paints it over every slide in the deck.
- **Verify every number and claim against its source before stating it.** Record claim → source →
  line number in a `talk-writing-log.md` beside the `.qmd`. A wrong number on a slide is repeated by
  everyone who photographs it.

## 5. Acronyms

Expand on first use: "the initial mass function (IMF)". Field-common acronyms (IMF, GMC, MHD, SFR)
may stay abbreviated for a specialist audience.

## 6. Render discipline

- Rebuild and check after edits: `make check` from the deck. Overflow here is silent and is *not*
  signalled by a `.scrollable` or `.smaller` class — reveal.js neither shrinks nor scrolls an
  over-full slide, it lets the surplus hang off the edge. Only the checker sees it.
- Do **not** run `make clean` after working — leave the built HTML for the author to look at.
- Read the slides: `make png` writes one PNG per slide to `out/png/`.

## 7. What you may change without asking

These are someone's slides, and a talk is an argument with a shape. Fix mechanics freely; leave the
argument alone.

**Without asking:** obvious typos; capitalisation in headings; awkward punctuation replaced with
plain punctuation where it reads better; missing blank lines around Markdown blocks; a bullet that
narrates moved into `::: notes`.

**Ask first:** reordering slides; removing or changing a citation; changing an equation; collapsing
or expanding a scientific claim; splitting one slide into two. Any of those changes what the talk
argues, and only the speaker knows whether that is right.

Keep comments that record intent or preserve recoverable material — `<!-- Keep this derivation
hidden unless the backup slide is restored. -->`. Delete empty ones and conversion artefacts.

## Common mistakes

| mistake | fix |
| --- | --- |
| a multi-line bullet that narrates | shorten to claim + symbol; move the prose to `::: notes` |
| `\textcolor{red}{..}` | `\color{red}{..}` |
| `$\alpha_{\rm vir}=5\sigma_v^2R/(GM)$` as the on-slide form | `$\alpha_{\rm vir}\equiv 2E_{\rm kin}/\|E_{\rm grav}\|$` |
| `$~100$`, or a bare `~` in text | `$\sim 100$` |
| `1-2` inside maths | `1\text{--}2` |
| `[@cite]` used with no References slide | add `::: {#refs} :::` |
| a slide that overflows | trim bullets, move prose to notes — then `make check` |
| an unverified number stated as fact | check the source, log it in `talk-writing-log.md` |
| `.columns-1-1` for a 50/50 split | `.columns`, so the PPTX keeps the two columns |
