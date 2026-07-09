"""
Contact sheet HTML generator: scenes x styles comparison grid.

Usage:
    python scripts/make_contact_sheet.py --story ancient_greece
    python scripts/make_contact_sheet.py --story ancient_greece --out sessions
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = "1.0.1"


def collect_images(session_dir: Path, story: str) -> dict[str, dict[str, list[Path]]]:
    """
    Walk sessions/<story>/ and collect:
    {style: {scene_id: [list of absolute image paths]}}
    """
    styles: dict[str, dict[str, list[Path]]] = {}
    story_dir = session_dir / story
    if not story_dir.exists():
        return styles

    for style_dir in sorted(story_dir.iterdir()):
        if not style_dir.is_dir() or style_dir.name.startswith("_") or style_dir.name.endswith(".html"):
            continue
        style_name = style_dir.name
        styles[style_name] = {}

        for scene_dir in sorted(style_dir.iterdir()):
            if not scene_dir.is_dir() or scene_dir.name.startswith("_"):
                continue
            scene_id = scene_dir.name
            images = sorted(
                scene_dir.glob("*.png"),
                key=lambda p: p.name
            )
            styles[style_name][scene_id] = images

    return styles


def generate_html(styles: dict, story: str) -> str:
    if not styles:
        return f"<html><body><h1>No images found for story '{story}'</h1></body></html>"

    style_names = sorted(styles.keys())
    all_scenes = sorted(set(
        scene for s in styles.values() for scene in s
    ))
    if not all_scenes:
        return f"<html><body><h1>No scenes found for story '{story}'</h1></body></html>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Contact Sheet: {story}</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
  h1 {{ color: #e94560; text-align: center; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th {{ background: #16213e; padding: 10px; position: sticky; top: 0; z-index: 2; }}
  th.style {{ color: #0f3460; background: #e94560; }}
  th.scene {{ color: #e94560; min-width: 120px; }}
  td {{ padding: 8px; vertical-align: top; border: 1px solid #333; }}
  .scene-cell {{ display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }}
  .scene-cell a {{ display: block; }}
  .scene-cell img {{ width: 200px; height: auto; border-radius: 4px; transition: transform 0.2s; }}
  .scene-cell img:hover {{ transform: scale(1.5); z-index: 10; position: relative; }}
  .variant-label {{ font-size: 10px; color: #999; text-align: center; }}
  .empty {{ color: #555; font-style: italic; text-align: center; padding: 20px; }}
  .legend {{ text-align: center; margin: 10px 0; color: #888; font-size: 13px; }}
</style>
</head>
<body>
<h1>Contact Sheet: {story}</h1>
<p class="legend">Rows: scenes | Columns: styles | Cells: variants (click to enlarge)</p>
<table>
<tr>
  <th>Scene</th>
"""
    for sn in style_names:
        html += f'  <th class="style">{sn}</th>\n'

    html += "</tr>\n"

    for scene in all_scenes:
        html += f'<tr>\n  <th class="scene">{scene}</th>\n'
        for sn in style_names:
            images = styles.get(sn, {}).get(scene, [])
            html += '  <td>'
            if not images:
                html += '<div class="empty">--</div>'
            else:
                html += '<div class="scene-cell">'
                for img_path in images:
                    fname = img_path.name
                    file_url = img_path.resolve().as_uri()
                    html += (
                        f'<div><a href="{file_url}" target="_blank">'
                        f'<img src="{file_url}" loading="lazy" alt="{fname}">'
                        f'</a><div class="variant-label">{fname}</div></div>'
                    )
                html += '</div>'
            html += '</td>\n'
        html += '</tr>\n'

    html += """</table>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML contact sheet: scenes x styles comparison"
    )
    parser.add_argument("--story", required=True, help="Story name (subdirectory in sessions/)")
    parser.add_argument("--out", default="sessions", help="Output base directory (default: sessions)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args()

    out_base = REPO_ROOT / args.out
    if not out_base.exists():
        raise SystemExit(f"ERROR: Output directory not found: {out_base}")

    styles = collect_images(out_base, args.story)
    if not styles:
        print(f"WARNING: No images found for story '{args.story}' in {out_base}")

    html = generate_html(styles, args.story)
    dest = out_base / args.story / "contact_sheet.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")

    total_images = sum(
        len(imgs) for s in styles.values() for imgs in s.values()
    )
    print(f"Contact sheet: {dest}")
    print(f"  {len(styles)} styles, {sum(1 for s in styles.values() for _ in s)} scene-slots, "
          f"{total_images} images")


if __name__ == "__main__":
    main()