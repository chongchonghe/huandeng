# Repo-wide builds. For one deck, cd into it and use its own Makefile.
#
#   make check     verify every deck — run this before committing a slide edit
#   make demo      build the demo deck to PDF, HTML and PPTX
#   make clean     delete every out/
#
# DECKS is every directory holding a main.typ, so a talk you copy into talks/
# is picked up with no edit here.

DECKS := $(patsubst %/main.typ,%,$(wildcard template/main.typ demo/main.typ talks/*/main.typ))

.DEFAULT_GOAL := help
.PHONY: help check demo clean

help:
	@echo "decks: $(DECKS)"
	@echo
	@echo "  make check   verify every deck (page count, overflow, stretched figures)"
	@echo "  make demo    build demo/ to PDF, HTML and PPTX"
	@echo "  make clean   delete every out/"
	@echo
	@echo "For one deck: cd into it, then make / make watch / make check / make all"

# Delegate to each deck's own Makefile, so a deck that pins a deliberate page
# count with EXPECT is checked against it. Keep going after a failure so one bad
# deck does not hide the others, then fail.
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
	rm -rf $(addsuffix /out,$(DECKS))
