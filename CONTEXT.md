# CONTEXT — COMFYUI-STORY-ILLUSTRATOR

> Память проекта. Выделен из COMFYUI-API-CHAT 2026-07-09.

## Суть

Batch-конвейер генерации серий иллюстраций к рассказам через ComfyUI API.
Ключевая задача — **consistency персонажей** между сценами. Без сервера/чата.

## Роли (DEV-NOTES §1)

| Роль | Кто | Задача |
|------|-----|--------|
| Архитектор | Yuri + чат | Проектирует, пишет `tasks/TASK.md`, проверяет, ведёт журнал |
| Кодер | терминал (Windows) | Пишет код, тестирует, заполняет `tasks/REPORT.md` |

## Текущий фокус

TASK-001 — приёмка выделенного проекта: запустить `MIGRATION.ps1`, прогнать
`batch_scenes.py` на одной сцене, убедиться в работоспособности. Далее —
доводка consistency персонажей (IP-Adapter) на рассказе про Древнюю Грецию.

## Стек

- **Python:** 3.11 системный (`C:\Python311\python.exe` — НЕ venv Hermes)
- **Генерация:** ComfyUI API (`http://127.0.0.1:8188`), workflow формата `class_type`
- **Скрипты:** `scripts/batch_scenes.py` (standalone, только stdlib), `scripts/lora_workflow.py`
- **Модели:** Illustrious + LoRA для реализма, IP-Adapter для лиц

## Структура

```
COMFYUI-STORY-ILLUSTRATOR/
├── scripts/
│   ├── batch_scenes.py     ← batch-раннер (SCENES, CKPT, LORA в шапке)
│   └── lora_workflow.py     ← шаблон workflow с LoRA
├── sessions/                ← результаты генераций (по имени модели)
│   ├── ancient_greece/      ← рассказ «В Древней Греции полдень горяч»
│   ├── character_sheets/    ← портреты персонажей для consistency
│   └── *.html               ← страницы сравнения вариантов
├── KNOWLEDGE_BASE.md        ← главный справочник (модели, промпты, LoRA, IP-Adapter)
├── SCENE_PARAMS_01.md       ← параметры сцен
└── README.md
```

## Ключевые пути (компьютер 2)

- ComfyUI: `G:\AI\_MY_PROGRAMMING_2\ComfyUI`
- Модели: `../ComfyUI/models/checkpoints`, `../ComfyUI/models/loras`
- Civitai-ключ: `../CIVITAI-DOWNLOAD-IMAGES/.env`

## Грабли

1. **Python** — системный `C:\Python311\python.exe`, не venv.
2. **API workflow** — формат с `class_type` (не editor-формат с `nodes`/`links`).
3. **IP-Adapter** — суффикс `vit-h` требует энкодер ViT-H (1280), НЕ bigG (1664).
4. **LoRA** `cinematic_photography...illu` — только для Illustrious-моделей.
5. **Civitai** — скачивание моделей требует API-токен.

## История

- **30.03–14.04.2026** — жил как часть COMFYUI-API-CHAT (веб-приложение).
- **06–07.07.2026** — смена направления: batch-конвейер, KNOWLEDGE_BASE, IP-Adapter.
- **09.07.2026** — выделен в отдельный проект.
