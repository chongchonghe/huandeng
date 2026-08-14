# Repo-wide builds. For one deck, cd into it and use its own Makefile.
#
#   make check     verify every deck, both flavours — run this before committing
#   make demo      build both demo decks
#   make clean     delete every out/
#
# DECKS is every directory holding a main.typ, so a Typst talk you copy into
# talks/ is picked up with no edit here. The Quarto decks are the ones with a
# _quarto.yml; quarto/Makefile finds those the same way.

DECKS  := $(patsubst %/main.typ,%,$(wildcard template/main.typ demo/main.typ talks/*/main.typ))
QDECKS := $(patsubst %/_quarto.yml,%,$(wildcard \
              quarto/template/_quarto.yml quarto/demo/_quarto.yml talks/*/_quarto.yml))

.DEFAULT_GOAL := help
.PHONY: help check check-typst check-quarto demo clean

help:
	@echo "typst decks:  $(DECKS)"
	@echo "quarto decks: $(QDECKS)"
	@echo
	@echo "  make check   verify every deck (page count, overflow, stretched figures)"
	@echo "  make demo    build demo/ and quarto/demo/"
	@echo "  make clean   delete every out/"
	@echo
	@echo "For one deck: cd into it, then make / make watch / make check / make all"

check: check-typst check-quarto

# Delegate to each deck's own Makefile, so a deck that pins a deliberate page
# count with EXPECT is checked against it. Keep going after a failure so one bad
# deck does not hide the others, then fail.
check-typst:
	@fail=0; for deck in $(DECKS); do \
	    echo "=== $$deck"; \
	    if [ -f "$$deck/Makefile" ]; then \
	        $(MAKE) --no-print-directory -C "$$deck" check || fail=1; \
	    else \
	        uv run python tools/build-slides.py "$$deck" --check || fail=1; \
	    fi; \
	done; exit $$fail

check-quarto:
	@$(MAKE) --no-print-directory -C quarto check

demo:
	uv run python tools/build-slides.py demo
	@$(MAKE) --no-print-directory -C quarto demo

clean:
	rm -rf $(addsuffix /out,$(DECKS))
	@$(MAKE) --no-print-directory -C quarto clean
