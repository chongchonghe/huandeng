# Every deck at once. For one deck, cd into it and use its own Makefile.
#
#   make check     verify every deck — run this before committing a slide edit
#   make demo      build demo/ to HTML, PDF and PPTX
#   make clean     delete every out/
#
# DECKS is every directory holding a _quarto.yml, so a talk you copy into
# talks/ is picked up with no edit here.

DECKS := $(patsubst %/_quarto.yml,%,$(wildcard \
             template/_quarto.yml demo/_quarto.yml talks/*/_quarto.yml))

.DEFAULT_GOAL := help
.PHONY: help check demo clean

help:
	@echo "decks: $(DECKS)"
	@echo
	@echo "  make check   verify every deck (overflow, stretched figures)"
	@echo "  make demo    build demo/ to HTML, PDF and PPTX"
	@echo "  make clean   delete every out/"
	@echo
	@echo "For one deck: cd into it, then make / make preview / make check / make all"

# Delegate to each deck's own Makefile, so a deck that pins a slide count with
# EXPECT is checked against it. Keep going after a failure so one bad deck does
# not hide the others, then fail.
check:
	@fail=0; for deck in $(DECKS); do \
	    echo "=== $$deck"; \
	    if [ -f "$$deck/Makefile" ]; then \
	        $(MAKE) --no-print-directory -C "$$deck" check || fail=1; \
	    else \
	        uv run python tools/build-slides.py "$$deck" --check || fail=1; \
	    fi; \
	done; exit $$fail

demo:
	uv run python tools/build-slides.py demo

clean:
	rm -rf $(addsuffix /out,$(DECKS)) $(addsuffix /.quarto,$(DECKS))
