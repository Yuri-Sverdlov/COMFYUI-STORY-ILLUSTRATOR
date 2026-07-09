"""
Batch runner: story x style profile -> illustration series via ComfyUI API.

Usage:
    python scripts/batch_scenes.py --story stories/ancient_greece.json \\
        --profile profiles/realism.json [--scenes 01,03] [--variants 2] \\
        [--out sessions] [--dry-run] [--seed 42]
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMFY_URL = "http://127.0.0.1:8188"
COMFY_MODELS = REPO_ROOT.parent / "ComfyUI" / "models"
VERSION = "2.0.0"


def load_json(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: File not found: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: Invalid JSON in {path}: {e}")


def resolve_path(relative: str, base: Path) -> Path:
    p = Path(relative)
    if p.is_absolute():
        return p
    return base / p


def validate_profile(profile: dict, profile_path: Path) -> None:
    required = ["name", "checkpoint", "params", "prompt_template", "ipadapter"]
    for key in required:
        if key not in profile:
            raise SystemExit(f"ERROR: profile missing '{key}': {profile_path}")

    params = profile["params"]
    for key in ["steps", "cfg", "sampler", "scheduler", "width", "height"]:
        if key not in params:
            raise SystemExit(f"ERROR: profile.params missing '{key}': {profile_path}")

    pt = profile["prompt_template"]
    for key in ["prefix", "suffix", "negative"]:
        if key not in pt:
            raise SystemExit(f"ERROR: profile.prompt_template missing '{key}': {profile_path}")

    ckpt_path = COMFY_MODELS / "checkpoints" / profile["checkpoint"]
    if not ckpt_path.exists():
        raise SystemExit(
            f"ERROR: checkpoint not found: {ckpt_path}\n"
            f"  Check: {COMFY_MODELS / 'checkpoints'}"
        )

    for lora in profile.get("loras", []):
        lora_path = COMFY_MODELS / "loras" / lora["file"]
        if not lora_path.exists():
            raise SystemExit(f"ERROR: LoRA not found: {lora_path}")

    ip = profile["ipadapter"]
    if ip.get("enabled"):
        ip_path = COMFY_MODELS / "ipadapter" / ip["model"]
        if not ip_path.exists():
            raise SystemExit(f"ERROR: IP-Adapter model not found: {ip_path}")

    if ip.get("enabled") and "weight" not in ip:
        raise SystemExit(f"ERROR: ipadapter.enabled but no 'weight': {profile_path}")


def validate_story(story: dict, story_path: Path) -> None:
    required = ["story", "title", "characters", "scenes"]
    for key in required:
        if key not in story:
            raise SystemExit(f"ERROR: story missing '{key}': {story_path}")

    if not story["scenes"]:
        raise SystemExit(f"ERROR: story has no scenes: {story_path}")

    for i, scene in enumerate(story["scenes"]):
        for key in ["id", "main_character", "prompt", "variants"]:
            if key not in scene:
                raise SystemExit(
                    f"ERROR: scene[{i}] missing '{key}': {story_path}"
                )
        mc = scene["main_character"]
        if mc not in story["characters"]:
            raise SystemExit(
                f"ERROR: scene '{scene['id']}' main_character='{mc}' "
                f"not in story.characters: {list(story['characters'])}"
            )


def check_comfyui() -> None:
    try:
        resp = urllib.request.urlopen(
            f"{COMFY_URL}/system_stats", timeout=5
        )
        data = json.loads(resp.read())
        if "system" not in data:
            raise SystemExit("ERROR: ComfyUI returned unexpected response")
    except urllib.error.URLError:
        raise SystemExit(
            "ERROR: ComfyUI not reachable at http://127.0.0.1:8188\n"
            "  Start: /c/Python311/python.exe ../ComfyUI/main.py --listen 127.0.0.1 --port 8188"
        )


def build_prompt(profile: dict, scene: dict, story: dict) -> str:
    pt = profile["prompt_template"]
    mc_name = scene["main_character"]
    mc_desc = story["characters"][mc_name]
    parts = [
        pt["prefix"],
        mc_desc,
        scene["prompt"],
        pt["suffix"],
    ]
    return ", ".join(p for p in parts if p)


def build_negative(profile: dict, scene: dict) -> str:
    pt = profile["prompt_template"]
    extra = scene.get("negative_extra", "")
    if extra:
        return f"{pt['negative']}, {extra}"
    return pt["negative"]


def build_workflow(profile: dict, scene: dict, story: dict,
                   seed: int, ref_image: Path | None) -> dict:
    params = profile["params"]
    prompt = build_prompt(profile, scene, story)
    negative = build_negative(profile, scene)
    ip = profile["ipadapter"]
    use_ip = ip.get("enabled") and ref_image is not None

    if not use_ip:
        return _build_workflow_no_ip(profile, prompt, negative, seed, params)

    return _build_workflow_ip(
        profile, prompt, negative, seed, params,
        ref_image, ip["weight"]
    )


def _build_workflow_no_ip(profile: dict, prompt: str, negative: str,
                          seed: int, params: dict) -> dict:
    ckpt = profile["checkpoint"]
    loras = profile.get("loras", [])

    wf = {}
    node_id = 1

    wf[str(node_id)] = {
        "inputs": {"ckpt_name": ckpt},
        "class_type": "CheckpointLoaderSimple"
    }
    node_id += 1

    model_ref = [str(node_id - 1), 0]
    clip_ref = [str(node_id - 1), 1]

    for lora in loras:
        wf[str(node_id)] = {
            "inputs": {
                "lora_name": lora["file"],
                "strength_model": lora["strength"],
                "strength_clip": lora["strength"],
                "model": model_ref,
                "clip": clip_ref,
            },
            "class_type": "LoraLoader"
        }
        model_ref = [str(node_id), 0]
        clip_ref = [str(node_id), 1]
        node_id += 1

    pos_node = str(node_id)
    wf[pos_node] = {
        "inputs": {"text": prompt, "clip": clip_ref},
        "class_type": "CLIPTextEncode"
    }
    node_id += 1

    neg_node = str(node_id)
    wf[neg_node] = {
        "inputs": {"text": negative, "clip": clip_ref},
        "class_type": "CLIPTextEncode"
    }
    node_id += 1

    latent_node = str(node_id)
    wf[latent_node] = {
        "inputs": {
            "width": params["width"],
            "height": params["height"],
            "batch_size": 1,
        },
        "class_type": "EmptyLatentImage"
    }
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {
            "seed": seed,
            "steps": params["steps"],
            "cfg": params["cfg"],
            "sampler_name": params["sampler"],
            "scheduler": params["scheduler"],
            "denoise": 1.0,
            "model": model_ref,
            "positive": [pos_node, 0],
            "negative": [neg_node, 0],
            "latent_image": [latent_node, 0],
        },
        "class_type": "KSampler"
    }
    sampler_node = str(node_id)
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {"samples": [sampler_node, 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    }
    decode_node = str(node_id)
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {
            "filename_prefix": f"batch/{seed}",
            "images": [decode_node, 0]
        },
        "class_type": "SaveImage"
    }

    return wf


def _build_workflow_ip(profile: dict, prompt: str, negative: str,
                       seed: int, params: dict,
                       ref_image: Path, weight: float) -> dict:
    ckpt = profile["checkpoint"]
    loras = profile.get("loras", [])

    wf = {}
    node_id = 1

    wf[str(node_id)] = {
        "inputs": {"ckpt_name": ckpt},
        "class_type": "CheckpointLoaderSimple"
    }
    node_id += 1

    model_ref = [str(node_id - 1), 0]
    clip_ref = [str(node_id - 1), 1]

    for lora in loras:
        wf[str(node_id)] = {
            "inputs": {
                "lora_name": lora["file"],
                "strength_model": lora["strength"],
                "strength_clip": lora["strength"],
                "model": model_ref,
                "clip": clip_ref,
            },
            "class_type": "LoraLoader"
        }
        model_ref = [str(node_id), 0]
        clip_ref = [str(node_id), 1]
        node_id += 1

    pos_node = str(node_id)
    wf[pos_node] = {
        "inputs": {"text": prompt, "clip": clip_ref},
        "class_type": "CLIPTextEncode"
    }
    node_id += 1

    neg_node = str(node_id)
    wf[neg_node] = {
        "inputs": {"text": negative, "clip": clip_ref},
        "class_type": "CLIPTextEncode"
    }
    node_id += 1

    load_image_node = str(node_id)
    wf[load_image_node] = {
        "inputs": {"image": str(ref_image.resolve())},
        "class_type": "LoadImage"
    }
    node_id += 1

    ip_loader_node = str(node_id)
    wf[ip_loader_node] = {
        "inputs": {
            "model": model_ref,
            "preset": "PLUS (high strength)"
        },
        "class_type": "IPAdapterUnifiedLoader"
    }
    node_id += 1

    ip_node = str(node_id)
    wf[ip_node] = {
        "inputs": {
            "model": [ip_loader_node, 0],
            "ipadapter": [ip_loader_node, 1],
            "image": [load_image_node, 0],
            "weight": weight,
            "weight_type": "standard",
            "start_at": 0.0,
            "end_at": 1.0,
        },
        "class_type": "IPAdapter"
    }
    node_id += 1

    latent_node = str(node_id)
    wf[latent_node] = {
        "inputs": {
            "width": params["width"],
            "height": params["height"],
            "batch_size": 1,
        },
        "class_type": "EmptyLatentImage"
    }
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {
            "seed": seed,
            "steps": params["steps"],
            "cfg": params["cfg"],
            "sampler_name": params["sampler"],
            "scheduler": params["scheduler"],
            "denoise": 1.0,
            "model": [ip_node, 0],
            "positive": [pos_node, 0],
            "negative": [neg_node, 0],
            "latent_image": [latent_node, 0],
        },
        "class_type": "KSampler"
    }
    sampler_node = str(node_id)
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {"samples": [sampler_node, 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    }
    decode_node = str(node_id)
    node_id += 1

    wf[str(node_id)] = {
        "inputs": {
            "filename_prefix": f"batch/{seed}",
            "images": [decode_node, 0]
        },
        "class_type": "SaveImage"
    }

    return wf


def poll_result(pid: str, timeout: int = 300) -> dict | None:
    for _ in range(timeout):
        time.sleep(1)
        try:
            resp = urllib.request.urlopen(
                f"{COMFY_URL}/history/{pid}", timeout=5
            )
            hist = json.loads(resp.read())
            if pid in hist:
                return hist[pid]
        except (urllib.error.URLError, json.JSONDecodeError):
            pass
    return None


def save_image(pid: str, result: dict, dest: Path) -> int:
    for node_out in result.get("outputs", {}).values():
        for img in node_out.get("images", []):
            subfolder = img.get("subfolder", "")
            ftype = img.get("type", "output")
            url = (
                f"{COMFY_URL}/view?filename={img['filename']}"
                f"&subfolder={subfolder}&type={ftype}"
            )
            raw = urllib.request.urlopen(url).read()
            dest.write_bytes(raw)
            return len(raw)
    return 0


def write_log(scene_dir: Path, scene: dict, profile: dict,
              story: dict, seed: int, variant: int,
              ref_image: str | None, timestamp: str) -> None:
    log = {
        "story": story["story"],
        "title": story["title"],
        "profile": profile["name"],
        "scene_id": scene["id"],
        "main_character": scene["main_character"],
        "variant": variant,
        "seed": seed,
        "checkpoint": profile["checkpoint"],
        "loras": profile.get("loras", []),
        "params": profile["params"],
        "ipadapter_weight": profile["ipadapter"].get("weight"),
        "ipadapter_model": profile["ipadapter"].get("model"),
        "reference_image": ref_image,
        "prompt": build_prompt(profile, scene, story),
        "negative": build_negative(profile, scene),
        "timestamp": timestamp,
        "runner_version": VERSION,
    }
    log_path = scene_dir / "log.json"
    existing = []
    if log_path.exists():
        existing = json.loads(log_path.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = [existing]
    existing.append(log)
    log_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                        encoding="utf-8")


def get_ref_image(story_name: str, main_character: str) -> Path | None:
    ref = REPO_ROOT / "characters" / story_name / f"{main_character}.png"
    if ref.exists():
        return ref
    return None


def plan_dry_run(story: dict, profile: dict, scene_ids: list[str] | None,
                 override_variants: int | None, out_base: Path) -> None:
    name = profile["name"]
    ckpt = profile["checkpoint"]
    ip = profile["ipadapter"]
    use_ip = ip.get("enabled")

    print(f"=== DRY RUN ===\n")
    print(f"Story: {story['title']} ({story['story']})")
    print(f"Profile: {name} (checkpoint: {ckpt})")
    print(f"Params: {profile['params']['steps']} steps, "
          f"CFG {profile['params']['cfg']}, "
          f"{profile['params']['sampler']}/{profile['params']['scheduler']}, "
          f"{profile['params']['width']}x{profile['params']['height']}")
    if profile.get("loras"):
        for lora in profile["loras"]:
            print(f"LoRA: {lora['file']} ({lora['strength']})")
    if use_ip:
        print(f"IP-Adapter: {ip['model']} (weight={ip['weight']})")
    else:
        print(f"IP-Adapter: disabled")
    print()

    for i, scene in enumerate(story["scenes"]):
        if scene_ids and scene["id"] not in scene_ids:
            continue
        variants = override_variants if override_variants else scene["variants"]
        prompt = build_prompt(profile, scene, story)
        negative = build_negative(profile, scene)
        ref = get_ref_image(story["story"], scene["main_character"])
        out_dir = out_base / story["story"] / name / scene["id"]

        print(f"Scene {i}: {scene['id']} ({variants} variants)")
        print(f"  Main character: {scene['main_character']}")
        if ref:
            print(f"  Reference: {ref}")
        else:
            print(f"  Reference: MISSING (characters/{story['story']}/{scene['main_character']}.png)")
        print(f"  Prompt: {prompt[:120]}...")
        print(f"  Negative: {negative[:100]}...")
        print(f"  Output: {out_dir}")
        print()

    total_scenes = len([s for s in story["scenes"]
                        if not scene_ids or s["id"] in scene_ids])
    total_variants = sum(
        (override_variants if override_variants else s["variants"])
        for s in story["scenes"]
        if not scene_ids or s["id"] in scene_ids
    )
    print(f"Total: {total_scenes} scenes, {total_variants} images")


def main():
    parser = argparse.ArgumentParser(
        description="Batch story illustration generator via ComfyUI API"
    )
    parser.add_argument("--story", required=True, help="Path to story JSON")
    parser.add_argument("--profile", required=True, help="Path to style profile JSON")
    parser.add_argument("--scenes", help="Comma-separated scene IDs (default: all)")
    parser.add_argument("--variants", type=int, help="Override variants per scene")
    parser.add_argument("--out", default="sessions", help="Output base directory")
    parser.add_argument("--seed", type=int, help="Base seed (overrides random)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan, no generation")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args()

    story_path = resolve_path(args.story, REPO_ROOT)
    profile_path = resolve_path(args.profile, REPO_ROOT)

    story = load_json(story_path)
    profile = load_json(profile_path)

    validate_story(story, story_path)
    validate_profile(profile, profile_path)

    scene_ids = set(args.scenes.split(",")) if args.scenes else None
    out_base = resolve_path(args.out, REPO_ROOT)

    if args.dry_run:
        plan_dry_run(story, profile, scene_ids, args.variants, out_base)
        return

    check_comfyui()

    name = profile["name"]
    story_name = story["story"]
    use_ip = profile["ipadapter"].get("enabled")

    total_scenes = len([s for s in story["scenes"]
                        if not scene_ids or s["id"] in scene_ids])
    total_variants = sum(
        (args.variants if args.variants else s["variants"])
        for s in story["scenes"]
        if not scene_ids or s["id"] in scene_ids
    )
    done = 0
    t0 = time.time()

    for scene in story["scenes"]:
        if scene_ids and scene["id"] not in scene_ids:
            continue

        scene_dir = out_base / story_name / name / scene["id"]
        scene_dir.mkdir(parents=True, exist_ok=True)

        variants = args.variants if args.variants else scene["variants"]
        mc = scene["main_character"]
        ref = get_ref_image(story_name, mc) if use_ip else None

        if use_ip and not ref:
            print(f"WARNING: No reference for '{mc}', "
                  f"IP-Adapter disabled for scene '{scene['id']}'")

        for v in range(variants):
            if args.seed is not None:
                seed = args.seed + v
            else:
                seed = hash(f"{scene['id']}_{v}_{time.time()}") % 1000000

            wf = build_workflow(profile, scene, story, seed, ref)

            payload = {
                "prompt": wf,
                "client_id": f"batch-{story_name}-{scene['id']}-{v}"
            }
            req = urllib.request.Request(
                f"{COMFY_URL}/prompt",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            resp = json.loads(urllib.request.urlopen(req).read())
            pid = resp.get("prompt_id")
            if not pid:
                print(f"ERROR: No prompt_id in response: {resp}")
                continue

            result = poll_result(pid)
            if not result:
                print(f"ERROR: Timeout for scene '{scene['id']}' v{v}")
                continue

            fname = f"v{v:02d}_seed{seed}.png"
            dest = scene_dir / fname
            size = save_image(pid, result, dest)
            if size == 0:
                print(f"ERROR: No output images for scene '{scene['id']}' v{v}")
                continue

            done += 1
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            ref_str = str(ref) if ref else None
            write_log(scene_dir, scene, profile, story, seed, v,
                      ref_str, timestamp)

            elapsed = int(time.time() - t0)
            print(f"[{done}/{total_variants}] {scene['id']} v{v:02d} "
                  f"-> {fname} ({size // 1024}KB) [{elapsed}s]")

    elapsed = int(time.time() - t0)
    print(f"\nDone! {done}/{total_variants} images in "
          f"{out_base / story_name / name} [{elapsed}s]")


if __name__ == "__main__":
    main()