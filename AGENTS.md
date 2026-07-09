# AGENTS.md — устав кодера (COMFYUI-STORY-ILLUSTRATOR)

> Общие грабли среды — в каноне `G:\AI\DEV-NOTES.md` (не дублировать сюда).
> Здесь — только специфика этого проекта.

## Обзор проекта

**COMFYUI-STORY-ILLUSTRATOR** — batch-конвейер генерации серий иллюстраций к
рассказам через ComfyUI API. Задача — consistency персонажей между сценами.
Без веб-сервера и чата. Python 3.11, только стандартная библиотека.

## Двухагентная схема (см. DEV-NOTES §1)

- **Архитектор** (чат) — проектирует, пишет `tasks/TASK.md`, проверяет, ведёт `PROJECT_LOG.md`.
- **Кодер** (терминал, Windows) — пишет код, тестирует, заполняет `tasks/REPORT.md`.

**Старт сессии кодера:** `Прочитай CONTEXT.md, затем AGENTS.md, затем tasks/TASK.md и выполни задание.`

## Запуск

### 1. ComfyUI (отдельно, на этой машине — компьютер 2)
```bash
/c/Python311/python.exe /g/AI/_MY_PROGRAMMING_2/ComfyUI/main.py --listen 127.0.0.1 --port 8188
```
Проверка (не блокирует): `curl -s http://127.0.0.1:8188/system_stats`

### 2. Batch-генерация
```bash
/c/Python311/python.exe scripts/batch_scenes.py
```
Настройки — в шапке скрипта (`SCENES`, `CKPT`, `LORA`, `STEPS`, `CFG`).

## Проверка кода (тестов пока нет)
```bash
/c/Python311/python.exe -m py_compile scripts/batch_scenes.py scripts/lora_workflow.py
/c/Python311/python.exe -c "import json, urllib.request"   # зависимостей нет
```

## Грабли проекта

1. **Python** — системный `C:\Python311\python.exe`, НЕ venv Hermes.
2. **Формат workflow** — API-формат с `class_type` (не editor-формат с `nodes`/`links`).
3. **IP-Adapter** — суффикс `vit-h` требует энкодер ViT-H (1280-dim),
   НЕ bigG (1664). Брать из `models/image_encoder/`, не `sdxl_models/`.
4. **LoRA** `cinematic_photography_detailed_illu_xl_v5` — только для Illustrious-моделей.
5. **Civitai** — скачивание моделей требует `CIVITAI_API_KEY`
   (`../CIVITAI-DOWNLOAD-IMAGES/.env`).
6. **Модели** `realismIllustriousBy` склонны к NSFW — для многофигурных сцен
   надёжнее `sd_xl_base` / `dreamshaper_xl`. Детали — в `KNOWLEDGE_BASE.md`.

## Код-стайл (Python)

- Python 3.11 — union `X | Y`, `pathlib.Path`, f-strings.
- Импорты: stdlib → third-party → local. Без wildcard.
- Type hints на сигнатурах; специфичные except, не голый `except:`.
- Константы — `UPPER_SNAKE_CASE` на уровне модуля.

### ⚠️ Кодировка консоли (DEV-NOTES §4)
Консоль этого ПК — **cp1252**. В `print()` — только **ASCII** (`->`, `<=`, `'`),
иначе `UnicodeEncodeError`. Сами файлы — всегда UTF-8 (JSON, тексты промптов — ок).

## Git (DEV-NOTES §2, §3)

- **commit/push — только кодер на Windows** (mount из чата блокирует git-локи).
- Архитектор из чата — read-only: `git status`, `git log`, `git fetch`.
- `.env` с ключами — **никогда не коммитить** (уже в `.gitignore`).
