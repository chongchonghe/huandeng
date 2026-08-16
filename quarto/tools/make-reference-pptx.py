#!/usr/bin/env python3
"""Build a deck's `reference.pptx` — the template Pandoc styles PPTX from.

    make-reference-pptx.py <deck>            write <deck>/reference.pptx
    make-reference-pptx.py <deck> --show     print what is in the current one

Pandoc does not invent a look for PowerPoint: it copies one out of a reference
document — slide masters, layouts, theme fonts and theme colours — and pours the
Markdown into it. Quarto ships Pandoc's default, which is Calibri on Office blue.
This rewrites the theme of that default to match `theme.scss`, so the PPTX at
least arrives in the deck's own colours.

The file it writes is a binary, and a binary nobody can regenerate is exactly
what this repository is against — hence this script rather than a checked-in
mystery. It takes nothing from the network: the base document comes from
`quarto pandoc --print-default-data-file reference.pptx`.

What this can and cannot buy is worth knowing before you spend time on it:

  colours          travel inside the file, so they always arrive
  layouts          real — title, section header, two-content, comparison
  fonts            only if the machine opening it has them. PowerPoint can
                   embed fonts on Windows only, and Pandoc does not, so the
                   default here is Aptos: not this deck's Fira Sans, but a face
                   that current Office actually ships, which is the point of
                   the format.
  everything else  no. `.fig` credits, `.media-row`, fragments, video and
                   `.absolute` are CSS, and PowerPoint has never heard of CSS.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Aptos is the Microsoft 365 default since 2024. Set FONT to "Fira Sans" to
# match the deck exactly, and accept that any machine without it substitutes
# something else — silently, and differently every time.
FONT = "Aptos"

# The theme slots Pandoc's layouts actually reference, mapped to theme.scss.
COLOURS = {
    "dk2": "1A1A1A",  # body text        --deck-ink
    "lt2": "EEF5FA",  # subtle fills     --deck-soft
    "accent1": "0A6EBD",  # headings     --deck-primary
    "accent2": "2E97DB",  #               --deck-secondary
    "accent3": "6FC2E8",  #               --deck-tertiary
    "hlink": "0A6EBD",
    "folHlink": "6B7280",  #              --deck-muted
}


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def pandoc_default(tmp: Path) -> Path:
    exe = shutil.which("quarto")
    if exe is None:
        die("quarto is not on PATH — see https://quarto.org/docs/get-started/")
    out = tmp / "pandoc-default.pptx"
    with out.open("wb") as fh:
        result = subprocess.run(
            [exe, "pandoc", "--print-default-data-file", "reference.pptx"], stdout=fh
        )
    if result.returncode != 0 or out.stat().st_size == 0:
        die("could not get Pandoc's default reference.pptx out of quarto")
    return out


def restyle(src: Path, dst: Path) -> None:
    """Rewrite the theme and master, copying every other part byte for byte."""
    zin = zipfile.ZipFile(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            name = item.filename
            if name.startswith("ppt/theme/") and name.endswith(".xml"):
                data = patch_theme(data.decode("utf-8")).encode("utf-8")
            elif name.startswith("ppt/slideMasters/") and name.endswith(".xml"):
                data = patch_master(data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(dst)


def patch_master(xml: str) -> str:
    """Make slide titles look like the deck's: primary blue, left, semibold.

    Setting the theme's accent colour is not enough on its own — Pandoc's master
    colours titles from `tx1`, which is black whatever the accents say. The one
    place to change it is `<p:titleStyle>` on the master, which every layout
    inherits from.
    """
    start = xml.find("<p:titleStyle>")
    end = xml.find("</p:titleStyle>", start)
    if start < 0 or end < 0:
        return xml  # a master we do not recognise; leave it alone
    block = xml[start:end]
    block = block.replace('<a:schemeClr val="tx1"/>', '<a:schemeClr val="accent1"/>')
    block = block.replace('algn="ctr"', 'algn="l"')
    block = block.replace("<a:defRPr sz=", '<a:defRPr b="1" sz=')
    return xml[:start] + block + xml[end:]


def patch_theme(xml: str) -> str:
    # Major and minor latin faces are what every placeholder inherits.
    xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
    for slot, hexv in COLOURS.items():
        # Theme colours are either a literal sRGB or a system colour carrying
        # its resolved value in lastClr; both forms appear in Pandoc's default.
        xml = re.sub(
            rf'(<a:{slot}>\s*<a:srgbClr val=")[0-9A-Fa-f]{{6}}(")',
            rf"\g<1>{hexv}\g<2>",
            xml,
        )
        xml = re.sub(
            rf'(<a:{slot}>\s*<a:sysClr [^/>]*lastClr=")[0-9A-Fa-f]{{6}}(")',
            rf"\g<1>{hexv}\g<2>",
            xml,
        )
    return xml


def show(path: Path) -> int:
    if not path.exists():
        die(f"no {path} — run without --show to build one")
    z = zipfile.ZipFile(path)
    xml = z.read("ppt/theme/theme1.xml").decode("utf-8")
    fonts = sorted(set(re.findall(r'<a:latin typeface="([^"]*)"', xml)))
    print(f"{path}")
    print(f"  fonts   {', '.join(fonts) or '(none)'}")
    for slot in COLOURS:
        m = re.search(rf'<a:{slot}>.*?val="([0-9A-Fa-f]{{6}})"', xml, re.S)
        print(f"  {slot:9s} #{m.group(1) if m else '??????'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("deck", type=Path, help="the deck directory")
    ap.add_argument("--show", action="store_true", help="describe the existing file")
    args = ap.parse_args(argv)

    deck = args.deck.resolve()
    if not deck.is_dir():
        die(f"no such deck: {args.deck}")
    target = deck / "reference.pptx"

    if args.show:
        return show(target)

    tmp = deck / ".reference-build"
    tmp.mkdir(exist_ok=True)
    try:
        restyle(pandoc_default(tmp), target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {target}")
    return show(target)


if __name__ == "__main__":
    raise SystemExit(main())
