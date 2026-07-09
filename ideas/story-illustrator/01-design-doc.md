# COMFYUI-STORY-ILLUSTRATOR — Design Doc

**Created:** 2026-07-12
**Based on:** `00-idea-capture.md` (интервью завершено)
**Status:** Draft → на утверждение Yuri

## One-line summary

Локальный batch-конвейер «рассказ → серия иллюстраций» на ComfyUI API:
один движок, стили как конфигурации, consistency персонажей через
IP-Adapter, результаты по осям «рассказ → стиль → сцена».

## Problem / purpose

Иллюстрирование рассказов вручную через UI генераторов не воспроизводимо:
стили и модели перемешиваются, эксперименты неотличимы от результатов,
персонажи «плывут» между сценами. Нужен конвейер, которым можно управлять
из любого агента (Hermes, Cursor chat/terminal) по одному ТЗ.

## Product philosophy

- **Один движок, стили — конфиги.** Никаких скриптов-близнецов на стиль.
- **Эксперимент ≠ продукт.** Калибровки живут в `experiments/`, в основные
  папки попадает только отобранное.
- **Человек утверждает, машина генерирует.** Агент предлагает сцены и
  промпты; Yuri правит и утверждает; раннер исполняет без творчества.
- **Всё воспроизводимо.** Seed, модель, LoRA, вес адаптера, промпт —
  в логе рядом с картинкой.

## Target user

Yuri (единственный пользователь) + агенты-исполнители (Hermes, Cursor).
Без веб-интерфейса, без сервера — файлы и CLI.

## Core concept

```
текст рассказа
   ↓  (агент + Yuri: гибрид)
файл сцен рассказа (utверждённый)     ← story config
   +
профиль стиля (реализм / иллюстрация)  ← style profile
   +
канонические референсы персонажей      ← character sheets
   ↓  (раннер)
sessions/<рассказ>/<стиль>/<сцена>/v<NN>_seed<S>.png + лог
   ↓  (Yuri: отбор)
sessions/<рассказ>/<стиль>/_selected/
```

## Key features (MVP)

1. **Story config** — один файл на рассказ (сцены: id, промпт, негатив,
   главный герой сцены, число вариантов). Формат: JSON или python-dict —
   решить в implementation spec.
2. **Style profiles** — два в MVP:
   - `realism` — realismIllustrious + cinematic LoRA, промпты в стиле
     фотографических тегов;
   - `illustration` — dreamshaper (или лучший из KNOWLEDGE_BASE),
     живописные промпты.
   Профиль = checkpoint + LoRA(и) + шаблон промпта + негативы + steps/cfg/
   sampler + флаг/вес IP-Adapter.
3. **Character consistency (базовая)** — канонический референс на персонажа
   (`characters/<имя>.png` — один файл, не папка вариантов); IP-Adapter
   держит главного героя сцены; вес адаптера — из калибровки, лежит
   в профиле стиля.
4. **Batch runner** — один скрипт: story config × style profile →
   генерация → раскладка + `log.json` на сцену.
5. **Сравнение** — HTML-контактлист по рассказу: сцены в строках,
   стили в колонках.

## Layout / information architecture

```
COMFYUI-STORY-ILLUSTRATOR/
├── scripts/
│   └── batch_scenes.py          ← единый раннер
├── profiles/                    ← стили как конфиги
│   ├── realism.(json|py)
│   └── illustration.(json|py)
├── stories/                     ← входы: утверждённые файлы сцен
│   └── ancient_greece.(json|py)
├── characters/                  ← канонические референсы
│   └── ancient_greece/
│       ├── ares.png
│       ├── aristocles.png
│       └── ploutos.png
├── sessions/                    ← выходы: рассказ → стиль → сцена
│   └── ancient_greece/
│       ├── realism/
│       │   ├── 01_hot_midday/...
│       │   └── _selected/
│       └── illustration/...
├── experiments/                 ← калибровки, пробы + краткие выводы
├── ideas/story-illustrator/     ← этот пакет документов
├── KNOWLEDGE_BASE.md            ← разделы по стилям
└── tasks/ (TASK.md / REPORT.md) ← процесс архитектор → кодер
```

Миграция текущих галерей (`sessions/ancient_greece`, `dreamshaper_*`,
`realismIllustrious*`, `character_sheets`) в новую структуру — отдельной
задачей, старое не удалять до переноса.

## Technical shape

- **Python 3.11 системный** (`C:\Python311\python.exe`), stdlib-only
  (urllib, json) — уже принято, сохраняем.
- **ComfyUI API** `http://127.0.0.1:8188`, workflow в API-формате
  (`class_type`).
- **IP-Adapter**: `ip-adapter-plus_sdxl_vit-h` + энкодер ViT-H (1280).
- **Windows-грабли**: ASCII в print (cp1252), пути через `pathlib`.
- **Git**: код и конфиги в репо; png — по `.gitignore` (кроме, возможно,
  `_selected/` — открытый вопрос).

## Non-goals (MVP)

- Веб-интерфейс, сервер, чат — нет (это COMFYUI-API-CHAT).
- Regional IP-Adapter / несколько узнаваемых лиц в кадре — фаза 2.
- Абстракция и NSFW-профили — после MVP, как новые конфиги.
- Обучение LoRA персонажей — только если IP-Adapter не хватит (фаза 2+).
- Автоматический отбор лучших вариантов — отбор ручной.

## Roadmap after MVP

1. **Фаза 2 — мультиперсонажность:** Regional IP-Adapter / маски.
2. **Фаза 3 — vision-фидбек:** мультимодальная модель (OpenRouter,
   кандидат Qwen3-VL-30B-A3B) смотрит результат, сравнивает с референсом,
   диагностирует (лицо/композиция/брак) и предлагает правки промпта.
   Отдельный `scripts/vision_review.py` → `review.json` рядом с log.json.
   Vision — советник и предфильтр; финальный отбор остаётся за Yuri.
3. **Фаза 4 — новые профили:** абстракция, NSFW (отдельные принципы
   промптов, свои модели/LoRA).
4. **Фаза 5 — качество:** FaceDetailer / upscale прошедших отбор.

## Acceptance criteria (MVP)

1. **Греция готова:** 5 сцен × 2 стиля, персонажи узнаваемы между сценами
   (главный герой сцены), финалы отобраны в `_selected/`.
2. **Тест на новизну:** новый рассказ проходит конвейер добавлением только
   `stories/<новый>.json` и референсов — без правки кода раннера.

## Resolved questions (Yuri, 2026-07-12)

1. **Формат конфигов — JSON** (читается всеми агентами и stdlib).
2. **`_selected/` — коммитить в git** (финальные отобранные картинки —
   часть результата; остальные png под `.gitignore`).
3. **Эксперименты с другими моделями:** профиль указывает на текущего
   победителя (старт `illustration` = dreamshaper). Кандидаты прогоняются
   в `experiments/` на фиксированной паре тестовых сцен + краткий вывод.
   Победа кандидата = смена checkpoint в `profiles/illustration.json`,
   без правки кода.
4. **Референсы персонажей — один нейтральный** на персонажа, общий для
   обоих стилей (`characters/<рассказ>/<имя>.png`).

## Next steps

1. Yuri утверждает этот документ (или правит).
2. → `02-implementation-spec.md`: раннер, форматы конфигов, план миграции,
   задачи, тесты.
3. → `03-agent-build-handoff.md`: ТЗ для исполнителя (Cursor/кодер).
