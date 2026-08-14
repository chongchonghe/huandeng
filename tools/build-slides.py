#!/usr/bin/env python3
"""Build a Touying deck to PDF, HTML and PPTX.

    uv run python tools/build-slides.py demo                     # all three
    uv run python tools/build-slides.py <deck> --pdf --html
    uv run python tools/build-slides.py <deck> --pptx --dpi 300
    uv run python tools/build-slides.py <deck> --html --link-video

`<deck>` is any directory holding a `main.typ`, and defaults to the working directory, so you can
also just `cd` into a deck and run `uv run python ../tools/build-slides.py`.

Nothing here is deck-specific: a new talk is a folder with `main.typ`, `globals.typ`,
`content.typ` and its assets, and it shares this script unchanged. For a PDF you do not need this
script at all — `typst compile main.typ talk.pdf` is the whole pipeline. It exists because Typst
has no working HTML target for Touying (it emits an empty document) and no PPTX target at all.

PDF comes straight from the Typst compiler. HTML wraps one inline SVG per slide in a
self-contained viewer. PPTX places one rendered slide image per slide, because PowerPoint has no
Typst-native import path.

Video needs a per-format detour, since PDF cannot hold one. Each export is compiled with a
different `sys.inputs.target`, so the deck can lay out a flip-book for PDF and a poster frame for
the others. Where a poster goes, `globals.typ` also emits a `<video-rect>` label recording the page
and rectangle it occupies; this script queries those and drops a real `<video>` (HTML) or movie
shape (PPTX) on top. The mp4s themselves are encoded here from the PNG sequences under
`movie-frames/`, so nothing but frames needs to live in the repository.

Typst cannot list a directory, so `movie-frames/manifest.json` — regenerated at the start of every
build, and committed — is how a deck learns which frames exist. `--add-movie` extracts a video or
GIF into a new sequence; `--sync-frames` refreshes the manifest after frames are added by hand.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pymupdf
import typst
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt

# Frame rate for a sequence whose source is unknown. A string rational ("25", "100/8") so it
# reaches ffmpeg verbatim; a float would reintroduce formatting drift into a reproducible build.
DEFAULT_FPS = "25"

# Any of these in the rendered PDF means the sans stack in `main.typ` resolved. If none appear,
# Typst fell back to its serif default and the deck looks nothing like it does here.
EXPECTED_FONTS = ("Fira", "Helvetica", "Arial", "Liberation")

# Fixed member timestamp so an unchanged deck produces a byte-identical .pptx.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class Deck:
    """Everything this script needs to know about one talk, derived from its directory."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.source = self.root / "main.typ"
        if not self.source.is_file():
            raise SystemExit(f"{self.root} has no main.typ — is it a deck directory?")
        self.out = self.root / "out"
        self.media = self.out / "media"
        # Optional directories: a deck without video or bundled fonts simply has neither.
        self.frames = self.root / "movie-frames"
        self.manifest = self.frames / "manifest.json"
        self.fonts = self.root / "fonts"
        self.stem = self.root.name if self.root.name != "." else "slides"

    def compile_args(self, target: str) -> dict:
        args: dict = {"sys_inputs": {"target": target}}
        if self.fonts.is_dir():
            args["font_paths"] = [str(self.fonts)]
        return args


def warn_on_font_fallback(deck: Deck, pdf: Path | bytes) -> None:
    doc = pymupdf.open(pdf) if isinstance(pdf, Path) else pymupdf.open(stream=pdf, filetype="pdf")
    used = {font[3] for page in doc for font in page.get_fonts()}
    if any(name in font for font in used for name in EXPECTED_FONTS):
        return
    print(
        "warning: none of the deck's sans fonts are installed, so Typst fell back to its serif\n"
        f"         default. Fonts found: {', '.join(sorted(used)) or 'none'}\n"
        f"         Install Fira Sans, or drop the .otf/.ttf files into {deck.fonts.name}/ "
        "(build-slides.py picks that up automatically).",
        file=sys.stderr,
    )


def normalize_zip(path: Path) -> None:
    """Rewrite an archive with fixed timestamps, so identical input gives identical bytes."""
    with zipfile.ZipFile(path) as src:
        members = [(info, src.read(info.filename)) for info in src.infolist()]
    with zipfile.ZipFile(path, "w") as out:
        for info, data in members:
            fixed = zipfile.ZipInfo(info.filename, date_time=ZIP_EPOCH)
            fixed.compress_type = info.compress_type
            fixed.external_attr = info.external_attr
            out.writestr(fixed, data)

# Typst emits SVG ids such as `id="gAB12"` that are unique per page but not across pages.
# Inlining several pages into one HTML document therefore needs the ids namespaced.
_ID_ATTR = re.compile(rb'\bid="([^"]+)"')
_HREF = re.compile(rb'\b(xlink:href|href)="#([^"]+)"')
_URL_REF = re.compile(rb"url\(#([^)]+)\)")


def namespace_svg_ids(svg: bytes, page: int) -> bytes:
    prefix = f"p{page}-".encode()
    svg = _ID_ATTR.sub(lambda m: b'id="' + prefix + m.group(1) + b'"', svg)
    svg = _HREF.sub(lambda m: m.group(1) + b'="#' + prefix + m.group(2) + b'"', svg)
    svg = _URL_REF.sub(lambda m: b"url(#" + prefix + m.group(1) + b")", svg)
    return svg


# ----------------------------------------------------------------- checking --
#
# Expected pages, counted from the source: 1 per section divider and per `==` slide, plus one more
# for every reveal step on it. Compared against the built PDF, any excess is a slide that overflowed
# — Typst breaks an over-tall slide across two pages instead of erroring.
#
# This is a heuristic over Typst source, not a parser. It is exact on this repo's decks; treat a
# small mismatch on an unusual deck as a prompt to look, not as proof.

SLIDE_FNS = ("focus-slide", "empty-slide", "title-slide")

def strip_noise(src: str) -> str:
    """Drop line comments and raw blocks — code samples mention #pause without meaning it."""
    src = re.sub(r"```.*?```", "", src, flags=re.S)      # fenced code samples
    src = re.sub(r"`[^`\n]*`", "", src)                   # inline code: `#pause` is prose, not a reveal
    src = re.sub(r"^\s*//.*$", "", src, flags=re.M)
    return src


def let_strings(src: str) -> dict:
    """`#let zoom = "seq-name"` — movies are often passed by variable, not literal."""
    return dict(re.findall(r'^#let\s+([\w-]+)\s*=\s*"([^"]+)"\s*$', src, re.M))

def units(src: str):
    """Split a deck body into slide units, each (kind, heading_or_none, body)."""
    marks = []
    # Any deck-level function that starts its own slide. A deck that defines another must be
    # added here, or --check will under-count by one per call.
    for m in re.finditer(
        r"^(==?) +(.*)$|^#(focus-slide|empty-slide)\b|^#(title-slide)\(", src, re.M
    ):
        if m.group(1) is not None:
            marks.append((m.start(), "section" if m.group(1) == "=" else "slide", m.group(2)))
        else:
            marks.append((m.start(), "fn", m.group(3) or m.group(4)))
    for i, (pos, kind, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(src)
        yield kind, label, src[pos:end]

LETS: dict = {}


def reveals(body: str, movie_pages) -> int:
    n = 1 + len(re.findall(r"#(?:pause|meanwhile)\b", body))
    # Inside $...$ the hash is dropped, so `pause` appears bare. Only look there — in prose
    # "pause" is an ordinary English word.
    for math in re.findall(r"\$.*?\$", body, re.S):
        n += len(re.findall(r"(?<![\w#])(?:pause|meanwhile)\b", math))
    for m in re.finditer(r"#(?:only|uncover)\(\s*(\d+)", body):
        n = max(n, int(m.group(1)))
    for m in re.finditer(r"(?<![\w-])alternatives\b", body):
        tail = body[m.end():]
        spread = re.match(r"\(\s*\.\.\(([^)]*)\)", tail)
        if spread:                       # alternatives(..(a, b, c).map(f))
            n = max(n, len([x for x in spread.group(1).split(",") if x.strip()]))
        else:                            # alternatives[..][..][..]
            n = max(n, tail.count("][") + 1)
    for m in re.finditer(r'(?<![\w-])movie\(\s*"?([\w-]+)"?', body):
        name = m.group(1)
        n = max(n, movie_pages.get(name, movie_pages.get(LETS.get(name, ""), 1)))
    return n

def expected(deck: Path, movie_pages) -> int:
    main = strip_noise((deck / "main.typ").read_text())
    body = strip_noise((deck / "content.typ").read_text()) if (deck / "content.typ").is_file() else ""
    # main.typ contributes only from #title-slide onward; config above it is not slides
    i = main.find("#title-slide(")
    src = (main[i:] if i != -1 else "") + "\n" + body
    LETS.clear(); LETS.update(let_strings(body))
    total = 0
    for kind, label, unit in units(src):
        rest = unit.split("\n", 1)[1] if "\n" in unit else ""
        has_body = bool(re.sub(r"\s|^#(pagebreak\(\)|---)$", "", rest, flags=re.M).strip())
        if kind == "section":
            hidden = "<touying:hidden>" in (label or "")
            total += (0 if hidden else 1) + (reveals(rest, movie_pages) if has_body else 0)
        else:
            total += reveals(unit, movie_pages)
    return total


def check_aspect(pdf: Path, tolerance: float = 0.02) -> list[str]:
    """Report every image the PDF draws at an aspect ratio other than its own.

    Distortion is silent — a squashed plot still looks like a plot — and on a scientific figure it
    is a wrong figure, not a cosmetic flaw: equal axes stop being square, a circle becomes an
    ellipse. So this compares each drawn box against the embedded image's pixel dimensions and
    reports any disagreement beyond a rounding tolerance.

    It catches the two ways it happens: passing both `width:` and `height:` to `image`, and frames
    extracted from a video with non-square pixels (see display_size).
    """
    problems = []
    for page_number, page in enumerate(pymupdf.open(pdf), start=1):
        for info in page.get_image_info():
            w, h = info["width"], info["height"]
            x0, y0, x1, y1 = info["bbox"]
            bw, bh = x1 - x0, y1 - y0
            if not (w and h and bw > 1 and bh > 1):
                continue
            drawn, native = bw / bh, w / h
            if abs(drawn / native - 1) > tolerance:
                problems.append(
                    f"  aspect: page {page_number} draws a {w}x{h} image at {bw:.0f}x{bh:.0f} "
                    f"— stretched by {drawn / native:.2f}x"
                )
    return problems


def check_deck(deck: Deck, pdf: Path, expect: int | None = None) -> int:
    """Compare the built PDF against what the source says it should be. Returns an exit code."""
    try:
        raw = typst.query(deck.source, "<movie-cost>", field="value", **deck.compile_args("pdf"))
        movie_pages = {c["name"]: c["used"] for c in json.loads(raw)}
    except Exception:
        movie_pages = {}

    want = expect if expect is not None else expected(deck.root, movie_pages)
    source = "declared" if expect is not None else "expected from source"
    doc = pymupdf.open(pdf)
    got = doc.page_count
    print(f"pages: {got} built, {want} {source}")

    # Locate the damage: consecutive pages under one running title whose slide counter moves.
    # A reveal step keeps the counter; an overflowed page gets a new one.
    pages = []
    for page in doc:
        text = page.get_text()
        counter = re.findall(r"\b(\d+)\s*/\s*(\d+)\b", text)
        title = next((l.strip() for l in text.split("\n") if l.strip()), "")
        pages.append((title, counter[-1][0] if counter else None))

    suspects = []
    for i in range(1, len(pages)):
        (t0, c0), (t1, c1) = pages[i - 1], pages[i]
        if t0 == t1 and c0 is not None and c1 is not None and c0 != c1:
            suspects.append((i, i + 1, t1[:56]))

    for a, b, title in suspects:
        print(f"  overflow: pages {a}-{b} share a title but not a counter — {title}")
    if got != want and not suspects:
        print("  no counter anomaly; the extra page is on a slide that has reveal steps,")
        print("  or is a deliberate break such as a multi-page bibliography")

    # Distinct failures, so both are always reported: a deck can paginate perfectly and still be
    # drawing a squashed figure.
    stretched = check_aspect(pdf)
    for line in stretched[:12]:
        print(line)
    if len(stretched) > 12:
        print(f"  ... and {len(stretched) - 12} more")

    if got == want and not stretched:
        print("ok: no slide overflows, no stretched images")
        return 0
    if got == want:
        print("pages are right, but some images are drawn at the wrong aspect ratio")
    return 1


def read_manifest(deck: Deck) -> dict:
    if not deck.manifest.is_file():
        return {}
    try:
        return json.loads(deck.manifest.read_text())
    except json.JSONDecodeError:
        return {}


def frame_names(directory: Path) -> list[str]:
    """The frame file names in one sequence directory, in play order.

    PNG is the default, but a sequence of dense simulation renders is photographic: the same
    frames cost roughly ten times more as PNG than as JPEG, which is the difference between a
    deck you can commit and one you cannot. A sequence is all one format — mixing them would make
    the ffmpeg glob below ambiguous.
    """
    for suffix in (".png", ".jpg"):
        frames = sorted(f.name for f in directory.glob(f"*{suffix}"))
        if frames:
            return frames
    return []


def scan_sequences(deck: Deck) -> dict:
    """Describe every image sequence under `movie-frames/`.

    Typst cannot list a directory (typst#2123), so this is how a deck learns which frames exist:
    the manifest is written here and read back with `#json()` in `globals.typ`.
    """
    sequences: dict = {}
    if not deck.frames.is_dir():
        return sequences
    # `fps` is probed from the source video at ingest and cannot be recovered from the frames,
    # so carry forward whatever a previous scan recorded.
    previous = read_manifest(deck).get("sequences", {})
    for directory in sorted(p for p in deck.frames.iterdir() if p.is_dir()):
        frames = frame_names(directory)
        if not frames:
            continue
        width, height = Image.open(directory / frames[0]).size
        sequences[directory.name] = {
            "fps": previous.get(directory.name, {}).get("fps", DEFAULT_FPS),
            "width": width,
            "height": height,
            "frames": frames,
        }
    return sequences


def write_manifest(deck: Deck, check: bool = False) -> bool:
    """Regenerate the manifest. Returns True if it changed, or would have under `check`."""
    if not deck.frames.is_dir():
        return False
    text = json.dumps({"version": 1, "sequences": scan_sequences(deck)}, indent=2, sort_keys=True)
    text += "\n"
    if deck.manifest.is_file() and deck.manifest.read_text() == text:
        return False
    if not check:
        deck.manifest.write_text(text)
    return True


def encode_movies(deck: Deck) -> None:
    """Encode every sequence in the manifest into `out/media/<name>.mp4`."""
    sequences = read_manifest(deck).get("sequences", {})
    if not sequences:
        return
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required to encode the video sequences (brew install ffmpeg)")

    deck.media.mkdir(parents=True, exist_ok=True)
    manifest_mtime = deck.manifest.stat().st_mtime
    for name, sequence in sorted(sequences.items()):
        directory = deck.frames / name
        movie = deck.media / f"{name}.mp4"
        # The manifest counts as an input: editing `fps` must invalidate the encode.
        newest = max(
            [manifest_mtime] + [(directory / f).stat().st_mtime for f in sequence["frames"]]
        )
        if movie.exists() and movie.stat().st_mtime >= newest:
            continue
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-framerate", str(sequence["fps"]),
                # Frame names are arbitrary, so glob rather than `%06d` — the numeric form stops
                # at the first gap in the numbering. The suffix comes from the manifest so a JPEG
                # sequence encodes the same way a PNG one does.
                "-pattern_type", "glob",
                "-i", str(directory / f"*{Path(sequence['frames'][0]).suffix}"),
                # H.264 needs even dimensions and yuv420p to play in browsers and PowerPoint.
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24",
                "-movflags", "+faststart",
                str(movie),
            ],
            check=True,
        )


def video_rects(deck: Deck, target: str) -> dict[int, list[dict]]:
    """Where each poster frame landed, as {page number: [rect, ...]}, in points."""
    raw = typst.query(deck.source, "<video-rect>", field="value", **deck.compile_args(target))
    by_page: dict[int, list[dict]] = {}
    for rect in json.loads(raw):
        by_page.setdefault(rect["page"], []).append(rect)
    return by_page


def build_pdf(deck: Deck) -> Path:
    out = deck.out / f"{deck.stem}.pdf"
    typst.compile(deck.source, output=out, **deck.compile_args("pdf"))
    warn_on_font_fallback(deck, out)
    return out


def build_html(deck: Deck, embed_video: bool = True, frames: bool = False) -> Path:
    # A flip-book is built from the PNGs themselves, so in that mode there is no mp4 to encode
    # and ffmpeg is not needed at all.
    if not frames:
        encode_movies(deck)
    pages = typst.compile(deck.source, format="svg", **deck.compile_args("html"))
    if isinstance(pages, bytes):  # single-page deck
        pages = [pages]
    rects = video_rects(deck, "html")

    # Every page is the same size, so a rectangle in points becomes a percentage of the slide and
    # tracks the SVG however the browser scales it.
    page_w, page_h = svg_page_size(pages[0])

    uid = 0
    slides = []
    for i, svg in enumerate(pages):
        parts = []
        for rect in rects.get(i + 1, []):
            if frames:
                uid += 1
                parts.append(frames_tag(deck, rect, page_w, page_h, embed_video, uid))
            else:
                parts.append(video_tag(deck, rect, page_w, page_h, embed_video))
        overlays = "".join(parts)
        slides.append(
            f'<section class="slide" id="slide-{i + 1}"><div class="stage">'
            + namespace_svg_ids(svg, i + 1).decode("utf-8")
            + overlays
            + "</div></section>"
        )

    out = deck.out / f"{deck.stem}.html"
    out.write_text(
        HTML_TEMPLATE.format(
            title=html.escape(deck.stem),
            count=len(pages),
            aspect=f"{page_w / page_h:.6f}",
            slides="\n".join(slides),
        ),
        encoding="utf-8",
    )
    return out


def svg_page_size(svg: bytes) -> tuple[float, float]:
    box = re.search(rb'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    return float(box.group(1)), float(box.group(2))


def video_tag(deck: Deck, rect: dict, page_w: float, page_h: float, embed: bool) -> str:
    src_path = deck.out / rect["src"]
    if embed:
        mime = mimetypes.guess_type(src_path.name)[0] or "video/mp4"
        src = f"data:{mime};base64," + base64.b64encode(src_path.read_bytes()).decode()
    else:
        src = html.escape(rect["src"])
    style = (
        f"left:{rect['x'] / page_w:.4%};top:{rect['y'] / page_h:.4%};"
        f"width:{rect['w'] / page_w:.4%};height:{rect['h'] / page_h:.4%}"
    )
    return f'<video class="overlay" style="{style}" src="{src}" controls loop muted playsinline></video>'


def parse_fps(value) -> float:
    """`fps` is stored the way ffprobe reports it, which may be a fraction like "25/4"."""
    if isinstance(value, (int, float)):
        return float(value) or 12.0
    num, _, den = str(value).partition("/")
    try:
        return (float(num) / float(den or 1)) or 12.0
    except (ValueError, ZeroDivisionError):
        return 12.0


def frames_tag(deck: Deck, rect: dict, page_w: float, page_h: float, embed: bool, uid: int) -> str:
    """The same sequence as a flip-book of `<img>`s instead of a `<video>`.

    Every frame is stacked in the overlay and exactly one is opaque at a time, stepped by a
    generated `@keyframes` rule — so the animation is pure CSS with no player, no codec and no
    ffmpeg. It starts paused and answers the slide's first `space`, the same as a <video>.
    The trade is weight: N PNGs embed larger than one mp4.
    """
    name = Path(rect["src"]).stem
    sequence = read_manifest(deck).get("sequences", {}).get(name)
    if not sequence:
        raise SystemExit(f"--html-frames: no sequence {name!r} in {deck.manifest}")
    files = sequence["frames"]
    count = len(files)
    duration = count / parse_fps(sequence.get("fps"))

    imgs = []
    for i, frame in enumerate(files):
        if embed:
            mime = mimetypes.guess_type(frame)[0] or "image/png"
            data = base64.b64encode((deck.frames / name / frame).read_bytes()).decode()
            src = f"data:{mime};base64,{data}"
        else:
            # The HTML sits in out/, so the sequence is one level up beside it.
            src = html.escape(f"../{deck.frames.name}/{name}/{frame}")
        # A negative delay starts each frame that far into the cycle, which is what staggers them.
        imgs.append(f'<img src="{src}" style="animation-delay:{-i * duration / count:.4f}s">')

    style = (
        f"left:{rect['x'] / page_w:.4%};top:{rect['y'] / page_h:.4%};"
        f"width:{rect['w'] / page_w:.4%};height:{rect['h'] / page_h:.4%}"
    )
    # One frame's slice of the cycle. The two stops sit a hair apart so the swap reads as a cut
    # rather than a cross-fade.
    hold = 100.0 / count
    # Longhands, deliberately: the `animation:` shorthand resets animation-play-state to
    # `running`, and this #id rule outranks the `.flipbook img` class rule that parks the
    # sequence -- so the shorthand would silently start every flip-book at load.
    css = (
        f"@keyframes flip-{uid}{{0%,{hold * 0.98:.4f}%{{opacity:1}}"
        f"{hold:.4f}%,100%{{opacity:0}}}}"
        f"#flip-{uid} img{{animation-name:flip-{uid};"
        f"animation-duration:{duration:.4f}s;"
        f"animation-timing-function:linear;"
        f"animation-iteration-count:infinite}}"
    )
    return (
        f"<style>{css}</style>"
        f'<div class="overlay flipbook" id="flip-{uid}" style="{style}">{"".join(imgs)}</div>'
    )


def build_pptx(deck: Deck, dpi: int) -> Path:
    encode_movies(deck)
    pdf = typst.compile(deck.source, **deck.compile_args("pptx"))
    rects = video_rects(deck, "pptx")

    doc = pymupdf.open(stream=pdf, filetype="pdf")
    pres = Presentation()
    pres.slide_width = Inches(doc[0].rect.width / 72)
    pres.slide_height = Inches(doc[0].rect.height / 72)
    blank = pres.slide_layouts[6]

    with tempfile.TemporaryDirectory() as scratch:
        for i, page in enumerate(doc):
            frame = Path(scratch) / f"{i + 1:03d}.png"
            page.get_pixmap(dpi=dpi).save(frame)
            slide = pres.slides.add_slide(blank)
            slide.shapes.add_picture(
                str(frame), 0, 0, width=pres.slide_width, height=pres.slide_height
            )
            # The rendered page already shows the poster; the movie shape covers it exactly.
            for rect in rects.get(i + 1, []):
                movie = deck.out / rect["src"]
                slide.shapes.add_movie(
                    str(movie),
                    Pt(rect["x"]), Pt(rect["y"]), Pt(rect["w"]), Pt(rect["h"]),
                    poster_frame_image=str(deck.root / rect["poster"])
                    if rect.get("poster")
                    else None,
                    mime_type=mimetypes.guess_type(movie.name)[0] or "video/mp4",
                )

    out = deck.out / f"{deck.stem}.pptx"
    pres.save(out)
    normalize_zip(out)
    return out


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; --aspect: {aspect}; }}
  html, body {{
    margin: 0; height: 100%; overflow: hidden; background: #1a1a1a;
    font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}
  #deck {{
    height: 100%; display: flex; align-items: center; justify-content: center;
  }}
  .slide {{ display: none; width: 100%; height: 100%; }}
  .slide.active {{ display: flex; align-items: center; justify-content: center; }}
  /* The largest box of the deck's aspect ratio that fits the viewport. The SVG fills it exactly,
     so the percentage-positioned video overlays stay glued to it at any size. */
  .stage {{
    position: relative;
    width: min(100vw, calc(100vh * var(--aspect)));
    height: min(100vh, calc(100vw / var(--aspect)));
  }}
  .slide svg {{ display: block; width: 100%; height: 100%; }}
  .overlay {{ position: absolute; object-fit: fill; }}
  /* --html-frames: the frames are stacked and the generated @keyframes reveals one at a time.
     The overlay rectangle already carries the sequence's own aspect ratio, so `fill` is exact
     here and never stretches a frame. */
  .flipbook {{ overflow: hidden; }}
  /* Paused until the slide's first `space`, the same beat a <video> waits for. Held at cycle
     time zero the only opaque frame is the first, so a parked flip-book shows its poster. */
  .flipbook img {{
    position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: fill; opacity: 0; animation-play-state: paused;
  }}
  .flipbook.playing img {{ animation-play-state: running; }}
  @media (prefers-reduced-motion: reduce) {{
    .flipbook img {{ animation: none; }}
    .flipbook img:first-child {{ opacity: 1; }}
  }}
  /* The slide is full-bleed, so the HUD sits on top of it: keep it out of the way until asked. */
  #hud {{
    position: fixed; right: 14px; bottom: 12px; color: #ddd;
    background: rgba(0, 0, 0, .55); padding: 4px 10px; border-radius: 999px;
    font-variant-numeric: tabular-nums; user-select: none; pointer-events: none;
    opacity: 0; transition: opacity .3s;
  }}
  #hud.show {{ opacity: 1; }}
  #hud kbd {{ color: #aaa; }}
  @media print {{
    html, body {{ height: auto; overflow: visible; background: #fff; }}
    .slide {{ display: flex !important; page-break-after: always; }}
    .stage {{ width: 100%; height: auto; aspect-ratio: var(--aspect); }}
    #hud {{ display: none; }}
  }}
</style>
</head>
<body>
<div id="deck">
{slides}
</div>
<div id="hud"><span id="pos">1</span> / {count} &nbsp; <kbd>&larr;</kbd> <kbd>&rarr;</kbd> <kbd>f</kbd><span id="playhint"> <kbd>space</kbd> play</span></div>
<script>
  const slides = Array.from(document.querySelectorAll('.slide'));
  const hud = document.getElementById('hud');
  const pos = document.getElementById('pos');
  const playhint = document.getElementById('playhint');
  let current = 0;
  let hudTimer;
  const played = new Set();

  const videosOn = (i) => Array.from(slides[i].querySelectorAll('video'));
  // --html-frames renders a movie as a CSS flip-book instead of a <video>. It answers to the
  // same space bar, so everything below treats the two as one kind of thing: "playable".
  const flipbooksOn = (i) => Array.from(slides[i].querySelectorAll('.flipbook'));
  const playableCount = (i) => videosOn(i).length + flipbooksOn(i).length;

  function rewindFlipbook(fb) {{
    fb.classList.remove('playing');
    // Clearing the animation name and forcing a reflow resets the animation's clock; without
    // this the sequence would resume mid-cycle instead of from frame one.
    const imgs = fb.querySelectorAll('img');
    imgs.forEach((img) => {{ img.style.animationName = 'none'; }});
    void fb.offsetWidth;
    imgs.forEach((img) => {{ img.style.animationName = ''; }});
  }}

  function flashHud() {{
    hud.classList.add('show');
    clearTimeout(hudTimer);
    hudTimer = setTimeout(() => hud.classList.remove('show'), 2000);
  }}

  // First space on a slide starts every video on it at once; the next space moves on, so the
  // rhythm is the same as any other slide. Returns false when there is nothing left to play.
  function playOnce() {{
    if (!playableCount(current) || played.has(current)) return false;
    played.add(current);
    videosOn(current).forEach((v) => {{
      v.currentTime = 0;
      v.play();
    }});
    flipbooksOn(current).forEach((fb) => fb.classList.add('playing'));
    return true;
  }}

  function show(i) {{
    const previous = current;
    current = Math.max(0, Math.min(slides.length - 1, i));
    // Leaving a slide rewinds whatever it was playing, so coming back re-arms the first space.
    if (previous !== current) {{
      played.delete(previous);
      videosOn(previous).forEach((v) => {{
        v.pause();
        v.currentTime = 0;
      }});
      flipbooksOn(previous).forEach(rewindFlipbook);
    }}
    slides.forEach((s, n) => s.classList.toggle('active', n === current));
    pos.textContent = current + 1;
    playhint.hidden = playableCount(current) === 0;
    if (location.hash !== '#' + (current + 1)) {{
      history.replaceState(null, '', '#' + (current + 1));
    }}
    flashHud();
  }}

  document.addEventListener('mousemove', flashHud);

  document.addEventListener('keydown', (e) => {{
    if (e.key === ' ') {{
      // Space plays the slide's video the first time, then advances like anywhere else.
      if (!playOnce()) show(current + 1);
      e.preventDefault();
    }} else if (['ArrowRight', 'ArrowDown', 'PageDown', 'Enter'].includes(e.key)) {{
      show(current + 1); e.preventDefault();
    }} else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) {{
      show(current - 1); e.preventDefault();
    }} else if (e.key === 'Home') {{
      show(0);
    }} else if (e.key === 'End') {{
      show(slides.length - 1);
    }} else if (e.key === 'f') {{
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    }}
  }});

  document.addEventListener('click', (e) => {{
    if (e.target.closest('a, video')) return;   // let links and video controls work
    show(current + (e.clientX < window.innerWidth / 3 ? -1 : 1));
  }});

  window.addEventListener('hashchange', () => show(parseInt(location.hash.slice(1), 10) - 1 || 0));
  show(parseInt(location.hash.slice(1), 10) - 1 || 0);
</script>
</body>
</html>
"""


VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".gif", ".m4v"}


def probe_fps(src: Path) -> str:
    """The source's average frame rate as a rational string, or DEFAULT_FPS if unreadable."""
    if shutil.which("ffprobe") is None:
        return DEFAULT_FPS
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", str(src)],
        capture_output=True, text=True,
    )
    rate = probe.stdout.strip()
    return rate if rate and rate not in {"0/0", "N/A"} else DEFAULT_FPS


def display_size(src: Path) -> tuple[int, int] | None:
    """The size the source is meant to be *seen* at, in square pixels.

    A video's stored frame is not always its displayed frame: a non-square sample aspect ratio
    means the player stretches it back on the way out. Screen recordings and anything that has
    been through a Keynote or PowerPoint round trip routinely carry one. Extracting frames without
    applying it hands you a silently distorted image — one of these sources stores 1288x1080 and
    is meant to be seen at 161:338, a two-and-a-half-fold horizontal stretch — and for a
    scientific figure a wrong aspect ratio is a wrong figure.

    Returns None if ffprobe is unavailable or the stream cannot be read.
    """
    if shutil.which("ffprobe") is None:
        return None
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,sample_aspect_ratio", "-of", "csv=p=0", str(src)],
        capture_output=True, text=True,
    )
    parts = probe.stdout.strip().split(",")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    width, height = int(parts[0]), int(parts[1])
    sar = parts[2] if len(parts) > 2 else "1:1"
    if ":" in sar:
        num, _, den = sar.partition(":")
        if num.isdigit() and den.isdigit() and int(den) and int(num):
            width = round(width * int(num) / int(den))
    return width, height


def ingest(deck: Deck, src: Path, name: str | None, fps: str, max_width: int, force: bool,
           frame_format: str = "png") -> None:
    """Extract a video or GIF into `movie-frames/<name>/` so `#movie("<name>")` can play it.

    A GIF needs no special case: PDF cannot animate one and Typst renders it static, so the only
    way to show motion is these frames. `-vf fps=N` is also exactly what resamples a GIF's
    variable per-frame delays onto a constant rate.
    """
    if not src.is_file():
        raise SystemExit(f"no such file: {src}")
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required to extract frames (brew install ffmpeg)")
    if src.suffix.lower() not in VIDEO_SUFFIXES:
        print(f"warning: {src.suffix} is an unusual source; trying ffmpeg anyway", file=sys.stderr)

    slug = name or re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", src.stem.lower())).strip("-")
    directory = deck.frames / slug
    if directory.exists():
        if not force:
            raise SystemExit(f"{directory.relative_to(deck.root)} already exists — pass --force to replace it")
        shutil.rmtree(directory)
    directory.mkdir(parents=True)

    rate = probe_fps(src) if fps == "auto" else fps

    # Scale to explicit numbers rather than an ffmpeg expression, because the target is the
    # *displayed* size (see display_size) and `-2` would recompute height from the stored frame,
    # reintroducing the very distortion we are removing. `setsar=1` marks the output square so a
    # later tool cannot stretch it again. Both dimensions are even: H.264 requires it, and it
    # keeps the encode-side scale filter a no-op, so flip-book frames and video stay identical.
    shown = display_size(src)
    if shown:
        dw, dh = shown
        if dw > max_width:
            dh = round(dh * max_width / dw)
            dw = max_width
        scale = f"scale={max(2, dw - dw % 2)}:{max(2, dh - dh % 2)},setsar=1"
    else:
        print("warning: could not read the source's display size; assuming square pixels",
              file=sys.stderr)
        scale = f"scale=min(iw\\,{max_width}):-2,setsar=1"

    quality = ["-q:v", "3"] if frame_format == "jpg" else []
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-vf", f"fps={rate},{scale}", *quality,
         "-start_number", "0", str(directory / f"frame_%06d.{frame_format}")],
        check=True,
    )

    frames = [directory / f for f in frame_names(directory)]
    if not frames:
        shutil.rmtree(directory)
        raise SystemExit(f"ffmpeg produced no frames from {src}")

    # Record the probed rate before the generic scan can default it to DEFAULT_FPS.
    write_manifest(deck)
    manifest = read_manifest(deck)
    manifest["sequences"][slug]["fps"] = rate
    deck.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    size = sum(f.stat().st_size for f in frames) / 1e6
    width, height = Image.open(frames[0]).size
    print(f"{directory.relative_to(deck.root)}: {len(frames)} frames, {width}x{height}, "
          f"{rate} fps, {size:.1f} MB")
    if size > 50:
        print(f"warning: {size:.0f} MB of frames — consider --max-width or a lower --fps",
              file=sys.stderr)
    print(f'\nAdd to content.typ:\n\n    #movie("{slug}", width: 90%)\n')


def report_movie_cost(deck: Deck) -> None:
    """List what each movie costs in PDF pages, from the `<movie-cost>` labels the deck emits."""
    raw = typst.query(deck.source, "<movie-cost>", field="value", **deck.compile_args("pdf"))
    costs = {c["name"]: c for c in json.loads(raw)}
    if not costs:
        return
    print("movies:")
    width = max(len(n) for n in costs)
    for name, cost in sorted(costs.items()):
        flag = "  ⚠ over budget" if cost["used"] > 40 else ""
        print(f"  {name:<{width}}  {cost['total']} frames → {cost['used']} PDF pages{flag}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "deck",
        nargs="?",
        default=".",
        type=Path,
        help="directory holding the deck's main.typ (default: the working directory)",
    )
    parser.add_argument("--pdf", action="store_true", help="build out/<deck>.pdf")
    parser.add_argument("--html", action="store_true", help="build out/<deck>.html")
    parser.add_argument("--pptx", action="store_true", help="build out/<deck>.pptx")
    parser.add_argument("--dpi", type=int, default=200, help="PPTX slide image DPI")
    parser.add_argument(
        "--add-movie",
        metavar="SRC",
        type=Path,
        help="extract a video or GIF into movie-frames/<name>/ and exit",
    )
    parser.add_argument("--name", help="sequence name for --add-movie (default: the file stem)")
    parser.add_argument("--fps", default="auto", help="frame rate for --add-movie (default: probe)")
    parser.add_argument("--max-width", type=int, default=1280, help="downscale cap for --add-movie")
    parser.add_argument("--frame-format", choices=("png", "jpg"), default="png",
                        help="frame format for --add-movie; jpg for photographic renders")
    parser.add_argument("--force", action="store_true", help="replace an existing sequence")
    parser.add_argument(
        "--sync-frames",
        action="store_true",
        help="regenerate movie-frames/manifest.json after adding frames by hand, and exit",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="build the PDF, then verify no slide overflowed; exit 1 if any did",
    )
    parser.add_argument(
        "--expect",
        type=int,
        metavar="N",
        help="with --check: the true page count, when a deck breaks a slide on purpose "
        "(a multi-page bibliography, say). Overrides the estimate.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="with --sync-frames: exit 1 if it would change"
    )
    parser.add_argument(
        "--html-frames",
        action="store_true",
        help="in the HTML, play each movie as a CSS flip-book of its own PNG frames instead of "
        "a <video>. Needs no ffmpeg and no codec; waits for the slide's first space, like a "
        "video does. The frames embed larger than the equivalent mp4. Combines with "
        "--link-video.",
    )
    parser.add_argument(
        "--link-video",
        action="store_true",
        help="reference the mp4s from out/media/ instead of inlining them, "
        "for a much smaller but no longer self-contained HTML file",
    )
    args = parser.parse_args(argv)
    deck = Deck(args.deck)

    targets = [name for name in ("pdf", "html", "pptx") if getattr(args, name)]
    if args.check and not targets:
        targets = ["pdf"]

    # Ingest and sync are modes, not targets: they author the deck rather than build it, and a
    # three-format build of a half-finished slide is pure cost.
    if args.add_movie or args.sync_frames:
        if targets:
            parser.error("--add-movie/--sync-frames build nothing; drop --pdf/--html/--pptx")
        if args.add_movie:
            ingest(deck, args.add_movie, args.name, args.fps, args.max_width, args.force,
                   args.frame_format)
            return 0
        changed = write_manifest(deck, check=args.dry_run)
        rel = deck.manifest.relative_to(deck.root)
        if args.dry_run:
            print(f"{rel} is {'out of date' if changed else 'up to date'}")
            return 1 if changed else 0
        print(f"{rel} {'updated' if changed else 'already up to date'}")
        return 0

    if not targets:
        targets = ["pdf", "html", "pptx"]

    # Every target compiles the deck, and the deck reads the manifest — so it must exist first.
    write_manifest(deck)

    builders = {
        "pdf": lambda: build_pdf(deck),
        "html": lambda: build_html(
            deck, embed_video=not args.link_video, frames=args.html_frames
        ),
        "pptx": lambda: build_pptx(deck, args.dpi),
    }

    deck.out.mkdir(parents=True, exist_ok=True)
    for name in targets:
        out = builders[name]()
        print(f"{out.relative_to(deck.root)}  ({out.stat().st_size / 1e6:.1f} MB)")
    if "pdf" in targets:
        report_movie_cost(deck)
        if args.check:
            return check_deck(deck, deck.out / f"{deck.stem}.pdf", args.expect)
    return 0


if __name__ == "__main__":
    sys.exit(main())
