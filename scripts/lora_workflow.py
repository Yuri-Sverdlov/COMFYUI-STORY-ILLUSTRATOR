"""
Шаблон workflow с LoRA для ComfyUI API.

Использование:
    from scripts.lora_workflow import make_workflow
    wf = make_workflow(
        ckpt="realismIllustriousBy_v50FP16.safetensors",
        lora_name="cinematic_photography_detailed_illu_xl_v5.safetensors",
        lora_strength=0.8,
        prompt="your prompt here",
        negative="ugly, deformed...",
        seed=42,
        width=1024, height=1024,
        steps=25, cfg=7.0
    )
    # Отправить wf в ComfyUI: POST /prompt {"prompt": wf, "client_id": "..."}
"""


def make_workflow(ckpt, lora_name, lora_strength, prompt, negative, seed, width, height, steps, cfg):
    """
    Создаёт API-формат workflow с LoRA.

    Структура:
        CheckpointLoaderSimple → LoraLoader → KSampler + CLIPTextEncode → VAEDecode → SaveImage
    """
    return {
        "1": {
            "inputs": {"ckpt_name": ckpt},
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
                "model": ["1", 0],
                "clip": ["1", 1]
            },
            "class_type": "LoraLoader"
        },
        "3": {
            "inputs": {
                "text": prompt,
                "clip": ["2", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "4": {
            "inputs": {
                "text": negative,
                "clip": ["2", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["6", 0]
            },
            "class_type": "KSampler"
        },
        "6": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "7": {
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            },
            "class_type": "VAEDecode"
        },
        "8": {
            "inputs": {
                "filename_prefix": "generated",
                "images": ["7", 0]
            },
            "class_type": "SaveImage"
        }
    }