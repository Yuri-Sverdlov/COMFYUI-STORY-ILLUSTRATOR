# COMFYUI-STORY-ILLUSTRATOR — конвейер иллюстраций к рассказам

Batch-генерация серий иллюстраций через ComfyUI API с сохранением характера
персонажей (consistency). Без веб-сервера и чата — чистый пайплайн.

> Выделен из `COMFYUI-API-CHAT` (2026-07-09). Старый проект — интерактивное
> веб-приложение с ИИ-агентом — остаётся отдельно и развивается своим путём.

## Что делает

Берёт список сцен (описания + промпты), прогоняет их через ComfyUI и выдаёт
по несколько вариантов на сцену. Персонажи описаны один раз и переиспользуются
во всех сценах, чтобы лица не «плавали» от кадра к кадру.

Текущий рассказ-пример: «В Древней Греции полдень горяч» (5 сцен × 4 варианта).

## Быстрый старт

### 1. Запустить ComfyUI (на этой машине, компьютер 2)
```bash
/c/Python311/python.exe /g/AI/_MY_PROGRAMMING_2/ComfyUI/main.py --listen 127.0.0.1 --port 8188
```
Проверка: http://127.0.0.1:8188/system_stats

### 2. Batch-генерация
```bash
python scripts/batch_scenes.py
```
Сцены, модель и LoRA настраиваются прямо в шапке `scripts/batch_scenes.py`
(словарь `SCENES`, переменные `CKPT`, `LORA`, `STEPS`, `CFG`).

Результаты складываются в `sessions/<имя_модели>/`.

## Реализм-пайплайн

| Тип | Файл | Размер |
|-----|------|:------:|
| Checkpoint | `realismIllustriousBy_v50FP16.safetensors` | 6.6 GB |
| LoRA | `cinematic_photography_detailed_illu_xl_v5.safetensors` | 436 MB |

Параметры: `steps=25, cfg=7.0, sampler=euler, lora_strength=0.8`.

Для consistency персонажей — IP-Adapter (`ip-adapter-plus_sdxl_vit-h`, энкодер
ViT-H 1280). Подробности и ловушки — в `KNOWLEDGE_BASE.md`.

## Документы

- `KNOWLEDGE_BASE.md` — сравнение 7 моделей, стили промптов по семействам,
  ловушки LoRA, настройка IP-Adapter. **Главный справочник проекта.**
- `SCENE_PARAMS_01.md` — параметры сцен.
- `CONTEXT.md` — память проекта (стек, пути, грабли).
- `scripts/lora_workflow.py` — шаблон workflow с LoRA.

## Зависимости

Только стандартная библиотека Python 3.11 (`urllib`, `json`) — `batch_scenes.py`
обращается к ComfyUI API напрямую, без внешних пакетов.

## Связанные проекты

| Проект | Путь |
|--------|------|
| ComfyUI (установка) | `../ComfyUI` |
| Старое веб-приложение | `../COMFYUI-API-CHAT` |
| Civitai Downloader | `../CIVITAI-DOWNLOAD-IMAGES` |
