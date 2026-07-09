"""
Batch-раннер: генерация иллюстраций к сценам через ComfyUI API.

Использование:
    python scripts/batch_scenes.py

Настройки внутри скрипта (SCENES, CKPT, LORA).
"""

import json, urllib.request, time, os

# ====== НАСТРОЙКИ ======
COMFY_URL = "http://127.0.0.1:8188"
OUT_BASE = os.path.join(os.path.dirname(__file__), "..", "sessions")
OUT_DIR = os.path.join(OUT_BASE, CKPT.replace(".safetensors", "").replace(".ckpt", ""))

CKPT = "realismIllustriousBy_v50FP16.safetensors"
LORA = "cinematic_photography_detailed_illu_xl_v5.safetensors"
LORA_STRENGTH = 0.8
STEPS = 25
CFG = 7.0
WIDTH = 1024
HEIGHT = 1024
VARIANTS = 4
NEGATIVE = "illustration, cartoon, anime, painting, drawing, 3D render, plastic skin, blurry, low quality, watermark, text, ugly, deformed, bad anatomy, extra limbs, fused fingers, disfigured, b&w"

# ====== ОПИСАНИЯ ПЕРСОНАЖЕЙ (для consistency) ======
ARES_DESC = "muscular ancient Greek Spartan warrior, 35 years old, short black curly hair, bronze helmet pushed back, weathered determined face, battle scar on left cheek, intense fierce eyes, red wool cloak"
ARISTOCLES_DESC = "skinny bald ancient Greek Athenian philosopher, 50 years old, thin face, prominent cheekbones, sun-spotted shiny bald head, shrewd ironic squinting eyes, faint sly smile, worn faded beige cloak"
PLOUTOS_DESC = "plump wealthy ancient Greek man, 45 years old, round cheerful face, rosy cheeks, double chin, balding with laurel wreath, amused twinkling eyes, pristine white wool cloak, gold fibula brooch"

SCENES = [
    {
        "id": "01_hot_midday",
        "prompt": f"Photorealistic cinematic scene: hot Mediterranean midday in ancient Greek olive grove. {ARES_DESC} sits at wooden table, gesturing impatiently. {ARISTOCLES_DESC} sits across, crumbling goat cheese, sweating under sun. Clay wine jugs, olives, bread on table. Golden dusty sunlight filtering through olive leaves, cicada-hum atmosphere. Hyperrealistic, dramatic natural lighting, 8K",
        "ru": "Жаркий полдень: Аристокл и Арес за столом в оливковой роще"
    },
    {
        "id": "02_ploutos_arrives",
        "prompt": f"Photorealistic cinematic scene: ancient Greek olive grove. {PLOUTOS_DESC} arrives at the table, followed by a slave carrying clay amphorae. {ARES_DESC} looks up with interest, {ARISTOCLES_DESC} already reaching for wine jug. Dusty path visible behind, warm afternoon light, hyperrealistic skin texture, cinematic photography, 8K",
        "ru": "Плутос приходит с вином и маслом"
    },
    {
        "id": "03_chimera_gossip",
        "prompt": f"Photorealistic cinematic scene: three ancient Greek men at wooden table under olive trees, deep in conversation. {PLOUTOS_DESC} gestures dramatically telling a story. {ARES_DESC} grips his sword, looking alarmed. {ARISTOCLES_DESC} skeptically sips wine from clay cup. Scattered olives, bread, amphorae on table. Dusty warm Mediterranean light, hyperrealistic, 8K cinematic photography, sharp focus",
        "ru": "Сплетни о Химере за столом"
    },
    {
        "id": "04_tornado_chimera",
        "prompt": f"Photorealistic dramatic cinematic scene: ancient Greek olive grove hit by massive blue tornado funnel descending from black storm clouds. {ARES_DESC} charges toward tornado with sword drawn, red cloak billowing. {PLOUTOS_DESC} clings to olive tree trunk in terror, white cloak torn. {ARISTOCLES_DESC} sits calmly at overturned table, clutching wine jug with blissful expression. Broken branches, flying dust, dramatic storm lighting, hyperrealistic, 8K",
        "ru": "Смерч принимают за Химеру"
    },
    {
        "id": "05_aftermath",
        "prompt": f"Photorealistic cinematic scene: aftermath of devastating storm in ancient Greek olive grove. {ARES_DESC} stands wounded, face bloodied, cloak torn, helmet missing, but still gripping short sword heroically. {ARISTOCLES_DESC} sits amid wreckage, torn beige cloak, hugging intact wine jug with blissful smile. {PLOUTOS_DESC} stands nearby bewildered, white cloak completely gone, both hands on his belt checking. Broken olive branches everywhere, scattered debris, warm post-storm light. Hyperrealistic, 8K cinematic photography",
        "ru": "После битвы: Арес ранен, Аристокл обнимает кувшин, Плутос без плаща"
    },
]


def make_workflow(ckpt, lora_name, lora_strength, prompt, negative, seed, w, h, steps, cfg):
    return {
        "1": {"inputs": {"ckpt_name": ckpt}, "class_type": "CheckpointLoaderSimple"},
        "2": {"inputs": {"lora_name": lora_name, "strength_model": lora_strength, "strength_clip": lora_strength, "model": ["1", 0], "clip": ["1", 1]}, "class_type": "LoraLoader"},
        "3": {"inputs": {"text": prompt, "clip": ["2", 1]}, "class_type": "CLIPTextEncode"},
        "4": {"inputs": {"text": negative, "clip": ["2", 1]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["6", 0]}, "class_type": "KSampler"},
        "6": {"inputs": {"width": w, "height": h, "batch_size": 1}, "class_type": "EmptyLatentImage"},
        "7": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
        "8": {"inputs": {"filename_prefix": f"batch/{seed}", "images": ["7", 0]}, "class_type": "SaveImage"},
    }


def run_batch():
    os.makedirs(OUT_DIR, exist_ok=True)
    total = len(SCENES) * VARIANTS
    done = 0

    for scene in SCENES:
        scene_dir = os.path.join(OUT_DIR, scene["id"])
        os.makedirs(scene_dir, exist_ok=True)

        for v in range(VARIANTS):
            seed = hash(scene["id"] + str(v)) % 1000000
            wf = make_workflow(CKPT, LORA, LORA_STRENGTH, scene["prompt"], NEGATIVE, seed, WIDTH, HEIGHT, STEPS, CFG)

            payload = {"prompt": wf, "client_id": f"batch-{scene['id']}-{v}"}
            req = urllib.request.Request(f"{COMFY_URL}/prompt", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]

            for t in range(180):
                time.sleep(1)
                hist = json.loads(urllib.request.urlopen(f"{COMFY_URL}/history/{pid}").read())
                if pid in hist:
                    for node_out in hist[pid].get("outputs", {}).values():
                        for img in node_out.get("images", []):
                            raw = urllib.request.urlopen(f"{COMFY_URL}/view?filename={img['filename']}&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}").read()
                            fname = f"{scene['id']}_v{v:02d}_seed{seed}.png"
                            with open(os.path.join(scene_dir, fname), "wb") as f:
                                f.write(raw)
                            done += 1
                            print(f"[{done}/{total}] {scene['ru']} v{v} -> {fname} ({len(raw)//1024}KB)")
                    break

    print(f"\nГотово! {done} картинок в {OUT_DIR}")


if __name__ == "__main__":
    run_batch()