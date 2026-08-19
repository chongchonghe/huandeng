# Every deck at once. For one deck, cd into it and use its own Makefile.
#
#   make check     verify every deck — run this before committing a slide edit
#   make demo      build demo/ to HTML, PDF and PPTX
#   make clean     delete every out/
#
# DECKS is every directory holding a _quarto.yml, so a talk you copy into
# talks/ is picked up with no edit here. template/ is the deck you copy to start
# one, and it is checked like any other.

DECKS := $(patsubst %/_quarto.yml,%,$(wildcard \
             template/_quarto.yml demo/_quarto.yml talks/*/_quarto.yml))

# Quarto and uv both install into ~/.local/bin, which a non-login shell does not
# always inherit. Appended, not prepended, so anything already on PATH wins.
export PATH := $(PATH):$(HOME)/.local/bin

.DEFAULT_GOAL := help
.PHONY: help check demo gallery clean

help:
	@echo "decks: $(DECKS)"
	@echo
	@echo "  make check   verify every deck (overflow, stretched figures)"
	@echo "  make demo    build demo/ to HTML, PDF and PPTX"
	@echo "  make gallery every theme side by side, to pick one"
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

# Every theme a deck could wear, rendered and laid side by side, because a name
# is not something anyone can choose between. Lands in template/out/gallery.html;
# from a deck of your own, `make gallery` there puts it in that deck's out/.
gallery:
	uv run python tools/build-slides.py template --gallery

clean:
	rm -rf $(addsuffix /out,$(DECKS)) $(addsuffix /.quarto,$(DECKS))
