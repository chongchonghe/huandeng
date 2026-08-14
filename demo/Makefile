# Build this deck. Run from the deck's own directory.
#
#   make          the PDF, with Typst alone — the fast loop while writing
#   make watch    the same, recompiled on every save
#   make check    build and verify; catches a slide that silently spilled
#   make all      PDF, HTML and PPTX
#   make clean    delete out/
#
# `make` and `make watch` need nothing but Typst, so they still work in a deck
# copied anywhere, years from now. The other three need the shared build tool,
# which by design lives outside the deck; they look for it up the directory tree
# and say so plainly if it is not there.

DECK  := $(notdir $(CURDIR))
FONTS := $(if $(wildcard fonts),--font-path fonts,)

# Set EXPECT only if this deck deliberately produces a page count the source does
# not imply — a slide split on purpose, a multi-page bibliography. Pinning the
# real number keeps `make check` meaningful: it still fails the day a slide
# starts overflowing, because the count moves off the pinned one.
EXPECT ?=
CHECK  := --check $(if $(EXPECT),--expect $(EXPECT),)
ROOT  := $(shell d="$(CURDIR)"; while [ "$$d" != "/" ]; do \
             if [ -f "$$d/tools/build-slides.py" ]; then echo "$$d"; break; fi; \
             d=$$(dirname "$$d"); \
         done)

# Every tool target runs from the repo root, so `uv` finds the project, and is
# given this deck by absolute path.
define run-tool
@if [ -z "$(ROOT)" ]; then \
    echo "No tools/build-slides.py above $(CURDIR)."; \
    echo "This deck is on its own — 'make' and 'make watch' still work."; \
    exit 1; \
fi; \
cd "$(ROOT)" && uv run python tools/build-slides.py "$(CURDIR)" $(1)
endef

.DEFAULT_GOAL := pdf
.PHONY: pdf watch check all clean

pdf:
	@mkdir -p out
	typst compile $(FONTS) main.typ out/$(DECK).pdf

watch:
	@mkdir -p out
	typst watch $(FONTS) main.typ out/$(DECK).pdf

check:
	$(call run-tool,$(CHECK))

all:
	$(call run-tool,)

clean:
	rm -rf out
