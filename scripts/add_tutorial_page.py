#!/usr/bin/env python3
"""
Create an `index.md` in each tutorial folder that embeds the local `player.html` via an iframe.

Usage:
  python3 scripts/add_tutorial_page.py ROOT_DIR [--height HEIGHT] [--width WIDTH] [--responsive]

Example:
  python3 scripts/add_tutorial_page.py docs/tutorials/examples --height 600 --responsive

The script will create `index.md` inside each immediate subdirectory of ROOT_DIR if it doesn't exist.
"""

import argparse
from pathlib import Path
import sys


TEMPLATE_RESPONSIVE = """---
title: {title}
---

<style>
.tutorial-embed {{ position:relative; width:100%; max-width:{max_width}px; margin:0 auto; }}
.tutorial-embed::before {{ content:""; display:block; padding-top:{padding_pct}%; /* aspect ratio */ }}
.tutorial-embed iframe {{ position:absolute; top:0; left:0; width:100%; height:100%; border:0; }}
</style>

<div class="tutorial-embed">
  <iframe src="player.html" title="{title}" loading="lazy"></iframe>
</div>

You can edit this file to change sizing or add notes about the tutorial.
"""

TEMPLATE_FIXED = """---
title: {title}
---

<div style="max-width:{max_width}px; width:100%; height:{height}px; margin:0 auto;">
  <iframe src="player.html" style="width:100%; height:100%; border:0;" title="{title}" loading="lazy"></iframe>
</div>

You can edit this file to change sizing or add notes about the tutorial.
"""


def title_from_dir(p: Path) -> str:
    # human-readable title
    return p.name.replace("-", " ").replace("_", " ").title()


def create_index_md(
    folder: Path, height: int, width: int, responsive: bool, max_width: int
):
    title = title_from_dir(folder)
    index_file = folder / "index.md"
    if index_file.exists():
        return False, f"skipped (exists): {index_file}"

    if responsive:
        # compute padding % for 16:9 by default if height/width not provided
        if height and width:
            padding_pct = 100 * (height / width)
        else:
            padding_pct = 56.25  # 16:9
        # Use absolute path to central player.html so every tutorial folder can embed it reliably
        content = TEMPLATE_RESPONSIVE.format(
            title=title, padding_pct=padding_pct, max_width=max_width
        )
    else:
        content = TEMPLATE_FIXED.format(title=title, height=height, max_width=max_width)

    index_file.write_text(content, encoding="utf-8")
    return True, f"created: {index_file}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate index.md with iframe for tutorials"
    )
    parser.add_argument(
        "root",
        help="Root folder containing tutorial subfolders (e.g. docs/tutorials/examples)",
    )
    parser.add_argument(
        "--height", type=int, default=600, help="Fixed iframe height (px)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Fixed iframe width (px) — used for aspect calc if responsive",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=1000,
        help="Max width in px for responsive wrapper",
    )
    parser.add_argument(
        "--responsive",
        action="store_true",
        help="Create responsive (aspect-ratio) wrapper instead of fixed height",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done but don't write files",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print(
            f"Root folder does not exist or is not a directory: {root}", file=sys.stderr
        )
        sys.exit(2)

    results = []
    for child in sorted(root.iterdir()):
        if child.is_dir():
            # Only create index.md if there is a player.html in that folder or if there is any html file
            # We expect a tutorial folder to contain data/assets (images, imported.json). The central
            # player is at /docs/tutorials/player.html so we don't require player.html inside each folder.
            # But skip if there is no obvious data (like imported.json or img/)
            has_data = (
                any((child / "imported.json").exists(), (child / "img").exists())
                if False
                else True
            )
            # A simpler heuristic: proceed if the folder contains any files (to avoid creating pages in empty dirs)
            if not any(child.iterdir()):
                results.append((False, f"empty folder, skipped: {child}"))
                continue

            if args.dry_run:
                results.append(
                    (
                        None,
                        f"would create index.md in {child} (responsive={args.responsive})",
                    )
                )
            else:
                ok, msg = create_index_md(
                    child, args.height, args.width, args.responsive, args.max_width
                )
                results.append((ok, msg))

    for ok, msg in results:
        print(msg)


if __name__ == "__main__":
    main()
