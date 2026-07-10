# CONTEXT — COMFYUI-STORY-ILLUSTRATOR

> Память проекта. Выделен из COMFYUI-API-CHAT 2026-07-09.

## Суть

Batch-конвейер генерации серий иллюстраций к рассказам.
**Основной пайплайн:** OpenRouter Image API (google/gemini-3-pro-image) —
облачная модель, принимает референсы персонажей прямо в запросе.
**Резервный:** ComfyUI API (локально) — для NSFW и экспериментов.
Ключевая задача — **consistency персонажей** между сценами. Без сервера/чата.

## Роли (DEV-NOTES §1)

| Роль | Кто | Задача |
|------|-----|--------|
| Архитектор | Yuri + чат | Проектирует, пишет `tasks/TASK.md`, проверяет, ведёт журнал |
| Кодер | терминал (Windows) | Пишет код, тестирует, заполняет `tasks/REPORT.md` |

## Текущий фокус

TASK-003 Шаг 1 — этюд облачной генерации: проверить, может ли
google/gemini-3-pro-image сгенерировать сцену с ДВУМЯ узнаваемыми
персонажами по референсам. TASK-002 (ComfyUI-пайплайн) остановлен:
M5 дал брак (портреты вместо сцен), M6–M7 отменены.

## Стек

- **Python:** 3.11 системный (`C:\Python311\python.exe` — НЕ venv Hermes)
- **Основная генерация:** OpenRouter Image API (`google/gemini-3-pro-image`)
- **Резервная:** ComfyUI API (`http://127.0.0.1:8188`), workflow `class_type`
- **Скрипты:** `scripts/cloud_etude.py` (этюд), `scripts/cloud_batch.py` (раннер),
  `scripts/batch_scenes.py` (CLI, ComfyUI), `scripts/make_contact_sheet.py` (HTML)
- **Ключ:** `G:\AI\_MY_PROGRAMMING\HERMES-AGENT\.openrouter_key` → `.env`

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
├── sessions/                  ← выходы: рассказ → сцена
│   ├── ancient_greece_cloud/  ← облачная генерация (NEW)
│   ├── ancient_greece/        ← старый ComfyUI-формат
│   ├── _archive/              ← старые галереи
│   └── *.html                 ← страницы сравнения
├── experiments/               ← калибровки + CONCLUSION.md
├── ideas/story-illustrator/   ← проектные документы
├── tasks/                     ← TASK.md / REPORT.md / done/
├── KNOWLEDGE_BASE.md          ← главный справочник
└── README.md
```

## Ключевые пути (компьютер 2)

- OpenRouter ключ: `G:\AI\_MY_PROGRAMMING\HERMES-AGENT\.openrouter_key`
- ComfyUI: `G:\AI\_MY_PROGRAMMING_2\ComfyUI`
- Модели: `../ComfyUI/models/checkpoints`, `../ComfyUI/models/loras`
- Референсы: `characters/ancient_greece/{ares,aristocles,ploutos}.png`

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
- **09.07.2026 (вечер)** — ПИВОТ на облачную генерацию. M5 дал брак (IP-Adapter
  портреты вместо сцен). TASK-003: OpenRouter Image API (google/gemini-3-pro-image).
