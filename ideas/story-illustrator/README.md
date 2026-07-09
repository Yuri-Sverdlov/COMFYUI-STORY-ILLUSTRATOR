# COMFYUI-STORY-ILLUSTRATOR — Idea Package

**Idea slug:** `story-illustrator`
**Mode:** Full (UI-стадия пропущена — CLI-конвейер)
**Created:** 2026-07-12
**Status:** Handoff ready ✅ → `03-agent-build-handoff.md`

## Artifact map

| # | File | Status |
|---|------|--------|
| 00 | `00-idea-capture.md` | ✅ Интервью завершено, 5 решений |
| 01 | `01-design-doc.md` | ✅ Утверждён Yuri (вопросы закрыты) |
| 02 | `02-implementation-spec.md` | ✅ Утверждён Yuri |
| 03 | `03-agent-build-handoff.md` | ✅ **ТЗ для исполнителя (Cursor/кодер)** |
| 04 | `04-spec-review.md` | ⏳ Pending (по желанию) |

## Quick summary

Batch-конвейер «рассказ → серия иллюстраций» на ComfyUI API. Один раннер,
стили — JSON-профили (MVP: realism + illustration), рассказы — JSON-файлы
сцен, персонажи — канонические референсы + IP-Adapter. Выходы по осям
«рассказ → стиль → сцена». Python 3.11 stdlib-only, Windows, локально.

## Key decisions

- Конвейер — цель; «В Древней Греции полдень горяч» — полигон.
- Один движок, стили — конфиги; эксперимент ≠ продукт (experiments/).
- Вход — гибрид: агент предлагает сцены, Yuri утверждает.
- Consistency MVP — базовая (главный герой сцены); Regional — фаза 2.
- Приёмка: Греция готова И новый рассказ проходит без правки кода.
- JSON-конфиги; _selected/ коммитятся; референс — один нейтральный.
- Смена модели = смена checkpoint в профиле после прогона в experiments/.

## Roadmap after MVP (из design doc)

Фаза 2 — Regional IP-Adapter (мультиперсонажность). **Фаза 3 —
vision-фидбек:** Qwen3-VL-30B-A3B через OpenRouter смотрит результаты,
сравнивает с референсом, предлагает правки промптов (советник, не судья).
Фаза 4 — профили abstract/NSFW. Фаза 5 — FaceDetailer/upscale.

## How to use (для Cursor)

Открыть `03-agent-build-handoff.md`, скопировать «Prompt for Build Agent»
в чат Cursor. Фазы M3 и M5 требуют ручного отбора Yuri.
