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

TASK-002 — batch-конвейер «рассказ → серия иллюстраций» (M1–M7).
M1 выполнен Архитектором (bootstrap): profiles/, stories/, .gitignore,
batch_scenes.py (CLI), make_contact_sheet.py. M2–M7 — Кодеру по `tasks/TASK.md`.
M3 и M5 — стоп-точки, требуют ручного выбора Yuri.

## Стек

- **Python:** 3.11 системный (`C:\Python311\python.exe` — НЕ venv Hermes)
- **Генерация:** ComfyUI API (`http://127.0.0.1:8188`), workflow формата `class_type`
- **Скрипты:** `scripts/batch_scenes.py` (CLI-раннер, stdlib), `scripts/make_contact_sheet.py` (HTML-контактлист), `scripts/lora_workflow.py` (legacy-шаблон)
- **Модели:** Illustrious + LoRA для реализма, IP-Adapter для лиц

## Структура

```
COMFYUI-STORY-ILLUSTRATOR/
├── scripts/
│   ├── batch_scenes.py        ← единый CLI-раннер (--story, --profile, --dry-run)
│   ├── make_contact_sheet.py  ← HTML-контактлист сцены × стили
│   └── lora_workflow.py       ← legacy-шаблон workflow с LoRA
├── profiles/                  ← стили как JSON-конфиги
│   ├── realism.json           ← realismIllustriousBy + cinematic LoRA
│   └── illustration.json      ← dreamshaper_xl_lightning
├── stories/                   ← входы: рассказы как JSON
│   └── ancient_greece.json    ← 5 сцен, 3 персонажа
├── characters/                ← канонические референсы (1 png на персонажа)
│   └── ancient_greece/        ← ares.png, aristocles.png, ploutos.png (M3)
├── sessions/                  ← выходы: рассказ → стиль → сцена
│   ├── ancient_greece/        ← новый формат
│   ├── _archive/              ← старые галереи (M7)
│   └── *.html                 ← страницы сравнения
├── experiments/               ← калибровки + CONCLUSION.md
├── ideas/story-illustrator/   ← проектные документы
├── tasks/                     ← TASK.md / REPORT.md / done/
├── KNOWLEDGE_BASE.md          ← главный справочник
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
- **09.07.2026** — выделен в отдельный проект. TASK-002: проектирование конвейера
  (M1 bootstrap Архитектором, M2–M7 заданы Кодеру).
