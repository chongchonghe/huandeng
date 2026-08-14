# Build this deck. Run from the deck's own directory.
#
#   make            render the HTML — the fast loop while writing
#   make preview    a browser that reloads every time you save
#   make check      render, then look at every slide: overflow, stretched figures
#   make png        one PNG per slide, so you can read them
#   make all        HTML, PDF and PPTX
#   make standalone one self-contained .html you can email
#   make clean      delete out/
#
# `make` and `make preview` need nothing but Quarto, so they still work in a
# deck copied anywhere, years from now. The other targets need the shared build
# tool, which by design lives outside the deck; they look for it up the
# directory tree and say so plainly if it is not there.

DECK := $(notdir $(CURDIR))

# Set EXPECT only if you want the slide count pinned. `make check` then fails
# the day a slide appears or disappears without you meaning it to.
EXPECT ?=
CHECK  := --check $(if $(EXPECT),--expect $(EXPECT),)

ROOT := $(shell d="$(CURDIR)"; while [ "$$d" != "/" ]; do \
            if [ -f "$$d/quarto/tools/build-slides.py" ]; then echo "$$d"; break; fi; \
            d=$$(dirname "$$d"); \
        done)

# Every tool target runs from the repo root, so `uv` finds the project, and is
# given this deck by absolute path.
define run-tool
@if [ -z "$(ROOT)" ]; then \
    echo "No quarto/tools/build-slides.py above $(CURDIR)."; \
    echo "This deck is on its own — 'make' and 'make preview' still work."; \
    exit 1; \
fi; \
cd "$(ROOT)" && uv run --extra quarto python quarto/tools/build-slides.py "$(CURDIR)" $(1)
endef

.DEFAULT_GOAL := html
.PHONY: html preview check png pdf pptx standalone all clean

html:
	quarto render

preview:
	quarto preview

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

clean:
	rm -rf out .quarto
