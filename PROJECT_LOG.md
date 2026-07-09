# PROJECT_LOG — журнал сессий (append-only)

> «Правда о том, что было». Дописывать снизу, старое не править.

---

## 2026-07-09 — Выделение проекта из COMFYUI-API-CHAT

**Архитектор:** чат (Cowork).

- Проект `COMFYUI-API-CHAT` содержал два не связанных направления:
  старое интерактивное веб-приложение с ИИ-агентом (март–апрель 2026) и новый
  batch-конвейер иллюстраций к рассказам (6–7 июля 2026). Решение — разбить на два.
- Создан отдельный проект **COMFYUI-STORY-ILLUSTRATOR** (конвейер иллюстраций).
  Старое веб-приложение остаётся в `COMFYUI-API-CHAT` и развивается отдельно.
- Перенесены: `scripts/` (batch_scenes.py, lora_workflow.py), `KNOWLEDGE_BASE.md`,
  `SCENE_PARAMS_01.md`, сравнения `sessions/*.html`, `.env`.
- Созданы канонические файлы (DEV-NOTES §1): `AGENTS.md`, `CONTEXT.md`, `CLAUDE.md`,
  `tasks/TASK.md`, `tasks/REPORT.md`, `PROJECT_LOG.md`, `tasks/done/`, `.gitignore`.
- Тяжёлые галереи (~250 МБ) и `git init` — вынесены в `MIGRATION.ps1` (запуск кодером
  на Windows: mount из чата не умеет удалять/двигать и писать git-локи).

**Следующий шаг:** TASK-001 — приёмка выделенного проекта (см. `tasks/TASK.md`).
