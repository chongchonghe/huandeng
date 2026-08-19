# Build this deck. Run from the deck's own directory.
#
#   make            render the HTML — the fast loop while writing
#   make preview    a browser that reloads every time you save
#   make check      render, then look at every slide: overflow, stretched figures
#   make png        one PNG per slide, so you can read them
#   make all        HTML, PDF and PPTX
#   make standalone one self-contained .html you can email
#   make gallery    every theme side by side, as out/gallery.html
#
# To change the look, edit one line of _quarto.yml: `theme:`. themes/ holds
# ten of them and they all travel with this deck.
#   make clean      delete out/
#
# `make` and `make preview` need nothing but Quarto, so they still work in a
# deck copied anywhere, years from now. The other targets need the shared build
# tool, which by design lives outside the deck; they look for it up the
# directory tree and say so plainly if it is not there.

DECK := $(notdir $(CURDIR))

# Quarto and uv both install into ~/.local/bin, and a shell that is not a login
# shell — an editor's terminal, a hook, an agent — does not always inherit it.
# Then `make` dies with "quarto: No such file or directory" on a machine where
# quarto is plainly installed.
#
# Two fixes, because they cover different recipes. `export PATH` reaches the
# targets below that make runs through a shell, which is how `uv` gets found.
# It does *not* reach `quarto render`: a recipe that is one bare command with no
# shell metacharacters is exec'd by make directly, and that lookup ignores a
# PATH set in the makefile. So resolve quarto here instead and call $(QUARTO).
#
# Both append rather than prepend, so a quarto already on PATH still wins, and
# both go through $(HOME), so no one's home directory is written into a file
# that other people copy. Override either from the command line if your install
# is somewhere else: `make QUARTO=/opt/quarto/bin/quarto`.
export PATH := $(PATH):$(HOME)/.local/bin
QUARTO ?= $(shell command -v quarto 2>/dev/null || echo $(HOME)/.local/bin/quarto)

# Set EXPECT only if you want the slide count pinned. `make check` then fails
# the day a slide appears or disappears without you meaning it to.
EXPECT ?=
CHECK  := --check $(if $(EXPECT),--expect $(EXPECT),)

ROOT := $(shell d="$(CURDIR)"; while [ "$$d" != "/" ]; do \
            if [ -f "$$d/tools/build-slides.py" ]; then echo "$$d"; break; fi; \
            d=$$(dirname "$$d"); \
        done)

# Every tool target runs from the repo root, so `uv` finds the project, and is
# given this deck by absolute path.
define run-tool
@if [ -z "$(ROOT)" ]; then \
    echo "No tools/build-slides.py above $(CURDIR)."; \
    echo "This deck is on its own — 'make' and 'make preview' still work."; \
    exit 1; \
fi; \
cd "$(ROOT)" && uv run python tools/build-slides.py "$(CURDIR)" $(1)
endef

.DEFAULT_GOAL := html
.PHONY: html preview check png pdf pptx standalone all gallery clean

html:
	$(QUARTO) render

preview:
	$(QUARTO) preview

check:
	$(call run-tool,$(CHECK))

png:
	$(call run-tool,--png)

pdf:
	$(call run-tool,--pdf)

pptx:
	$(call run-tool,--pptx)

standalone:
	$(call run-tool,--standalone)

all:
	$(call run-tool,)

# Renders this deck once per stylesheet in themes/ and writes a contact sheet
# here. The dressing happens to a copy under /tmp — nothing in this deck
# changes; the gallery only shows you what there is to pick.
gallery:
	$(call run-tool,--gallery)

clean:
	rm -rf out .quarto
