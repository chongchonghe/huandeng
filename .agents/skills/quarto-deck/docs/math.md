# Maths

## Which renderer, and why it matters

Quarto's revealjs format renders maths with **MathJax 2.7.9**, the `TeX-AMS_HTML-full` configuration,
loaded from a CDN. Three consequences, all of which have bitten:

1. **`\color{red}{..}`, never `\textcolor`.** That configuration does not load the `color.js`
   extension, so `\textcolor` is undefined and MathJax's `noUndefined` handler renders it as literal
   red error text on the slide. `\color` *is* built into the base TeX jax, but as a **two-argument
   macro** — `\color{<colour>}{<maths>}`, not a LaTeX-style switch — and it wraps the maths in
   `<mstyle mathcolor="..">`, so a named colour applies to exactly the braced part.

   ```markdown
   $$ \frac{\partial E}{\partial t} + \nabla\cdot\boldsymbol{F}
      = \color{red}{4\pi\rho j} - \rho\kappa cE $$
   ```

2. **Maths comes from a CDN.** A normal render needs the network to typeset. `make standalone`
   inlines MathJax with everything else — that is the build to hand to someone who may be offline,
   or to present from a conference wifi you do not trust.

3. `html-math-method: katex` does **not** fix (2) — Quarto fetches KaTeX from a CDN too.

## Inline and display

```markdown
Inline: the equation $E = mc^2$ sets in the surrounding text.

$$
\frac{\partial E}{\partial t} + \nabla \cdot \boldsymbol{F} = 4\pi\rho j - \rho\kappa cE
$$
```

Rendered equations are visually wider than their source, so an inline one can collide with the word
beside it. `theme.scss` adds `padding: 0 0.15em` to inline MathJax containers for that.

## Multiple lines

Use `\begin{aligned}` **inside** `$$..$$`:

```markdown
$$
\begin{aligned}
\frac{\partial E_\nu}{\partial t} + \nabla\cdot\boldsymbol{F}_\nu
  &= 4\pi\rho j_\nu - \rho\kappa_{\nu,a} cE_\nu \\
\frac{1}{c}\frac{\partial \boldsymbol{F}_\nu}{\partial t} + c\nabla\cdot\mathbb{P}_\nu
  &= -\rho\kappa_{\nu,a}\boldsymbol{F}_\nu
\end{aligned}
$$
```

Do **not** nest `equation` or `align` inside `$$..$$` — `$$` already opens display mode and the
environments fight it.

## An equation that builds up

`\class{fragment}{..}` makes a term arrive on its own keypress. Reveal's maths plugin recognises the
class MathJax emits and treats it as an ordinary fragment.

```markdown
$$
\underbrace{\frac{1}{c}\frac{\partial \boldsymbol{F}}{\partial t}}_{\text{time dependence}}
\class{fragment}{+ \underbrace{c\nabla\cdot\mathbb{P}}_{\text{transport}}}
\class{fragment}{= \underbrace{-\rho\kappa_a\boldsymbol{F}}_{\text{absorption}}}
$$
```

It costs a keypress and nothing else — the whole equation stays one slide.

**This construct does not survive any non-browser export.** Pandoc cannot convert `\class` to Typst
or LaTeX, so the whole `$$..$$` block falls through and prints as raw source. That is fine here,
because the only exports are the browser ones — but it is why `--to typst` and the Touying bridge
were abandoned (`exports.md`).

## Fitting

At most **one** display `$$..$$` per dense column; a second usually runs off the bottom. When an
equation does overflow, unwrap the continuation onto one line or move the slide to two columns
before shrinking anything — see `geometry.md`.
