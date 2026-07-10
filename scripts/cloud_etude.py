"""
Etude: single OpenRouter image generation request with 2 character references.

Usage:
    C:\Python311\python.exe scripts\cloud_etude.py
"""

import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3-pro-image"


def load_key() -> str:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        raise SystemExit("ERROR: .env not found")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OPENROUTER_API_KEY="):
            val = line.split("=", 1)[1].strip().strip("\"'")
            if val:
                return val
    raise SystemExit("ERROR: OPENROUTER_API_KEY not found in .env")


def image_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    return base64.b64encode(raw).decode("ascii")


def build_payload(prompt: str, refs: list[Path]) -> dict:
    content: list[dict] = [{"type": "text", "text": prompt}]
    for ref in refs:
        b64 = image_to_base64(ref)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"}
        })
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}]
    }


def call_openrouter(payload: dict, key: str) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Yuri-Sverdlov/COMFYUI-STORY-ILLUSTRATOR",
        }
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())


def save_image_from_response(resp: dict, dest: Path) -> tuple[int, str]:
    choices = resp.get("choices", [])
    if not choices:
        raise SystemExit(f"ERROR: No choices in response: {json.dumps(resp, indent=2)[:500]}")

    msg = choices[0].get("message", {})

    # Gemini returns images in message.images field
    images = msg.get("images", [])
    if images:
        img = images[0]
        url = img.get("image_url", {}).get("url", "")
        if url.startswith("data:image"):
            b64 = url.split(",", 1)[1]
            raw = base64.b64decode(b64)
            dest.write_bytes(raw)
            return len(raw), "gemini_images"
        elif url.startswith("http"):
            img_resp = urllib.request.urlopen(url, timeout=30)
            raw = img_resp.read()
            dest.write_bytes(raw)
            return len(raw), "url"

    content = msg.get("content", "")
    if not content:
        raise SystemExit(
            f"ERROR: No images or content in response.\n"
            f"  Message keys: {list(msg.keys())}\n"
            f"  Response preview: {json.dumps(resp, indent=2)[:500]}"
        )

    if isinstance(content, list):
        for part in content:
            if part.get("type") == "image_url":
                url = part["image_url"]["url"]
                if url.startswith("data:image"):
                    b64 = url.split(",", 1)[1]
                    raw = base64.b64decode(b64)
                    dest.write_bytes(raw)
                    return len(raw), "inline_base64"
                elif url.startswith("http"):
                    img_resp = urllib.request.urlopen(url, timeout=30)
                    raw = img_resp.read()
                    dest.write_bytes(raw)
                    return len(raw), "url"
    elif isinstance(content, str):
        import re
        m = re.search(r'!\[.*?\]\(data:image/png;base64,([^)]+)\)', content)
        if m:
            b64 = m.group(1)
            raw = base64.b64decode(b64)
            dest.write_bytes(raw)
            return len(raw), "markdown_base64"
        m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', content)
        if m:
            b64 = m.group(1)
            raw = base64.b64decode(b64)
            dest.write_bytes(raw)
            return len(raw), "raw_base64"

    raise SystemExit(
        f"ERROR: Could not extract image. Content type: {type(content).__name__}\n"
        f"  Content preview: {str(content)[:300]}"
    )


def main():
    t0 = time.time()

    key = load_key()
    print(f"-> Key loaded ({key[:8]}...{key[-4:]})")

    ref_dir = REPO_ROOT / "characters" / "ancient_greece"
    refs = [ref_dir / "ares.png", ref_dir / "aristocles.png"]
    for r in refs:
        if not r.exists():
            raise SystemExit(f"ERROR: Reference not found: {r}")

    prompt = (
        "Create a cinematic photorealistic image: two men sit at a wooden table "
        "in an olive grove at hot Mediterranean midday. First man (reference "
        "image 1) is a muscular Spartan warrior with bronze helmet, red cloak, "
        "battle scar on left cheek. Second man (reference image 2) is a skinny "
        "bald Athenian philosopher with sun-spotted shiny bald head, shrewd "
        "squinting eyes, faint sly smile, worn faded beige cloak. Clay wine "
        "jugs, olives, bread on the table. Golden dusty sunlight filtering "
        "through olive leaves. Wide establishing shot, full scene, both figures "
        "fully visible from head to waist."
    )

    print(f"-> Building payload (model={MODEL}, refs={len(refs)})")
    payload = build_payload(prompt, refs)

    print("-> POST to OpenRouter...")
    resp = call_openrouter(payload, key)

    elapsed = int(time.time() - t0)
    print(f"-> Response received [{elapsed}s]")

    out_dir = REPO_ROOT / "sessions" / "ancient_greece_cloud" / "etude"
    out_dir.mkdir(parents=True, exist_ok=True)

    img_path = out_dir / "v00.png"
    size, method = save_image_from_response(resp, img_path)
    print(f"-> Image saved: {img_path} ({size // 1024}KB, method={method})")

    # Build log
    usage = resp.get("usage", {})
    cost_usd = usage.get("cost") or usage.get("total_cost") or None
    if cost_usd is not None:
        cost_usd = round(float(cost_usd), 6)

    log = {
        "story": "ancient_greece",
        "scene_id": "01_hot_midday",
        "model": MODEL,
        "prompt": prompt,
        "references": [str(r) for r in refs],
        "seed": None,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "usage": usage,
        "cost_usd": cost_usd,
        "full_response": resp,
    }

    log_path = out_dir / "log.json"
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"-> Log saved: {log_path}")

    total_elapsed = int(time.time() - t0)
    print(f"\nDone! [{total_elapsed}s]")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()