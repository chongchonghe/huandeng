---
name: quarto-academic-style
description: The author's house style for academic slides — whether the deck is spoken over or read alone (the `density:` key) and what that changes, how terse a bullet should be, equations written for a reader, figure sizing and captions, verifying claims, acronyms, and what an assistant may change without asking. Use when drafting or revising the words and maths of a .qmd, or reviewing a deck for readability before a talk. Builds on quarto-deck, which covers the machinery.
---

# Academic slide style

Preferences, not mechanics. **quarto-deck** covers how the deck is built — the classes, the build,
the traps that raise no error. This covers what to write, and it is one person's taste, learned from
their corrections to real decks. Read it as house style, not physics.

**Core principle:** a deck is either spoken over or read alone, and the two want opposite things.
Everything in §1 follows from which one this is. Equations are written for a reader either way.

## 1. Which deck is this — spoken over, or read alone?

`talk.qmd` records it in one YAML key, so a later session does not have to guess it back out of the
shape of the slides:

```yaml
density: speaker-led     # someone stands up and talks over it
density: reading-first   # someone reads it by themselves
```

Absent, assume `speaker-led`. If it is neither written down nor obvious from the occasion, ask once,
before drafting — it changes what goes on every slide, so it is a bad thing to discover late.

**Do not invent a middle.** A deck that is half keynote and half handout is bad at both. A live
audience — conference talk, seminar, defence, group meeting you present — is speaker-led. Anything
circulated to be read alone — a handout, slides sent to a collaborator, a deck nobody stands up for,
supplementary material — is reading-first. If it is genuinely both, it is speaker-led, and the
handout is a second pass over the same deck rather than a compromise between the two.

**This is mechanics, not taste: `::: notes` does not print.** Reveal hides the notes in its print
layout, so they reach neither PDF, nor the PPTX. Whatever you move into the notes, a reader never
sees. That one fact is the whole reason the modes differ.

Both modes stop at the same edge. `make check` is the same gate either way, and a reading-first
slide that overflows is cut exactly as hard as any other — split it, do not shrink it.

### speaker-led — the slide states, the notes narrate

- One idea per slide. Each bullet at most about two lines.
- If a bullet *explains* or *narrates*, move that prose into `::: notes` and shorten the bullet to a
  claim plus its key symbol.
- End a content slide with a one-sentence takeaway in `::: {.highlight}`.
- Speaker notes are full spoken paragraphs, written to be read aloud, **ending with a transition
  into the next slide**.

### reading-first — the slide carries itself

- One idea per slide still, but the idea arrives whole. A bullet may run to three or four lines, or
  the slide may carry a short paragraph under the heading. A bare claim plus a symbol is not terse
  here; it is unfinished.
- Prefer fewer, fuller slides to more, thinner ones. Twenty-five slides that each say something
  complete beat sixty that each say a fragment — the reader is paging, not listening.
- Say what to look at in a figure, because nobody is standing there pointing. `.caption` names the
  panel, `.below` says what it shows. §3 otherwise applies unchanged.
- Keep the `::: {.highlight}` takeaway. It is what a reader who skims actually reads.
- Cite more, not less: a reader can follow a reference, a listener cannot.
- Expand every acronym on first use, including the field-common ones §5 lets you leave short — a
  reader may start in the middle.
- `::: notes` is then yours alone: reminders, sources, what you would say if you did present it.
  Nothing load-bearing, because none of it prints.

```markdown
<!-- wrong in both modes: the bullet narrates and finishes nothing -->
- **Virial equilibrium** — gravity is balanced by turbulent and thermal
  support, which we can quantify using the virial parameter alpha-vir,
  and observations of giant molecular clouds place them at around one
  to two, meaning they are bound but not collapsing everywhere...

<!-- speaker-led: the bullet states, and the notes narrate -->
- **Virial equilibrium** — gravity balanced by turbulent + thermal support,
  $2E_{\rm kin}+E_{\rm grav}=0$; virial parameter
  $\alpha_{\rm vir}\equiv 2E_{\rm kin}/|E_{\rm grav}|$, with GMCs near
  $\alpha_{\rm vir}\sim 1\text{–}2$

<!-- reading-first: the same claim, finished, because no one will finish it -->
- **Virial equilibrium** — gravity balanced by turbulent + thermal support,
  $2E_{\rm kin}+E_{\rm grav}=0$. The virial parameter
  $\alpha_{\rm vir}\equiv 2E_{\rm kin}/|E_{\rm grav}|$ says which side wins:
  observed GMCs sit at $\alpha_{\rm vir}\sim 1\text{–}2$, bound but not in
  free fall everywhere.
```

## 2. Write equations for a reader

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
- Numeric ranges: the literal en-dash character inside `\text{}` — `\text{–}`, not `\text{--}` — or a
  literal en dash in prose. MathJax 2.7.9's `\text{}` does not run TeX's ligature substitution, so
  `\text{--}` renders as two literal hyphens, not one en dash; only the actual character works. Never
  a bare `-` inside maths — that is subtraction.
- Inline maths for short expressions. At most **one** display `$$..$$` per dense column.

Colour, multi-line and build-up syntax are mechanics — `quarto-deck/docs/math.md`.

## 3. Figures

- **Figures are drawn too small by default.** In one real review pass every width the author touched
  went *up*: 62→90, 72→90, 42→62, 46→56, 62→82, 92→100. A figure is the content of the slide, not an
  illustration beside it. Start near the width the slide allows and come down only if something
  actually collides.
- **Captions go above the figure.** A slide is read top to bottom, so the caption should say what
  the panel is before the eye reaches it. That is why the class is `.caption` and the exception is
  `.below`.
- **A caption says what the panel shows, and nothing else.** "Linear wave analysis"; "Supercritical
  radiative shock". Provenance goes in `.credit`. A statement about the whole slide goes in the
  slide body.
- **Do not pad around figures.** The images have their own intrinsic margins and `.fig` places its
  own gaps; extra spacers make the layout drift.
- **Left-align prose and panel labels.** Centre titles and the figures themselves, not sentences. A
  label reads as a label when it ends in a colon: "Previous codes, operator-split:".
- Use a **placeholder** until the real asset exists — `![](attach/placeholder.png)` plus an HTML
  comment naming the intended figure and its source.

## 4. Claims and citations

- **Verify every number and claim against its source before stating it.** Record claim → source →
  line number in a `talk-writing-log.md` beside the `.qmd`. A wrong number on a slide is repeated by
  everyone who photographs it.
- Cite with `[@Key]`; the References slide is mandatory once anything is cited — see
  `quarto-deck/docs/citations.md` for why.
- Name people with their affiliation when crediting a collaborator: "A. Researcher (PhD student,
  Some University)", not the bare name.

## 5. Acronyms

Expand on first use: "the initial mass function (IMF)". Field-common acronyms — IMF, GMC, MHD, SFR —
may stay abbreviated for a specialist astronomy audience.

## 6. Typographic habits

- Bold the letter a symbol stands for rather than quoting the word: "a **T**ransport and a
  **S**ource term" beats "a 'transport' and a 'source' term" when the equation above uses $T$ and
  $S$.
- `$\sim 100$`, never `~100`.

## 7. What you may change without asking

These are someone's slides, and a talk is an argument with a shape. Fix mechanics freely; leave the
argument alone.

**Without asking:** obvious typos; capitalisation in headings; awkward punctuation replaced with
plain punctuation where it reads better; missing blank lines around Markdown blocks; in a
**speaker-led** deck, a bullet that narrates moved into `::: notes`.

**Never silently:** changing `density:`, or editing a deck as though it were the other mode. In a
**reading-first** deck, moving prose into `::: notes` deletes it from everything the reader gets.

**Ask first:** reordering slides; removing or changing a citation; changing an equation; collapsing
or expanding a scientific claim; splitting one slide into two. Each of those changes what the talk
argues, and only the speaker knows whether that is right.

## Common mistakes

| mistake | fix |
| --- | --- |
| *(speaker-led)* a multi-line bullet that narrates | shorten to claim + symbol; move the prose to `::: notes` |
| *(reading-first)* a bullet that states a claim and stops | finish it on the slide; the notes do not print |
| a deck written without knowing which mode it is | read `density:` in `talk.qmd`; ask if it is not there |
| `$\alpha_{\rm vir}=5\sigma_v^2R/(GM)$` as the on-slide form | `$\alpha_{\rm vir}\equiv 2E_{\rm kin}/\|E_{\rm grav}\|$` |
| `$~100$`, or a bare `~` in text | `$\sim 100$` |
| `1-2` inside maths | `1\text{–}2` |
| `1\text{--}2` inside maths (renders as literal `1--2`) | `1\text{–}2`, the actual en-dash character |
| a figure sized to fit beside the text | size it to the slide; cut the text instead |
| a caption carrying provenance | move it to `.credit` |
| an unverified number stated as fact | check the source, log it in `talk-writing-log.md` |
| centred body prose | left-align it; centre only titles and figures |
