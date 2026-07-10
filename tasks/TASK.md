# TASK — активное задание архитектор → кодер

> Одно активное задание. После выполнения — заполнить `tasks/REPORT.md`.
> **Внимание:** выполняй ТОЛЬКО шаг 1. После него — СТОП, жди указаний.

## TASK-003: Шаг 1 — Этюд облачной генерации (~$0.1)

**Контекст:** локальный ComfyUI-пайплайн с IP-Adapter дал брак (портреты
вместо сцен). Проект переходит на облачную генерацию через OpenRouter
Image API (google/gemini-3-pro-image). Модель принимает референс-картинки
прямо в запросе и сама держит лица/одежду — без IP-Adapter и негативов.

**Цель:** проверить гипотезу одним запросом — может ли облачная модель
сгенерировать сцену с ДВУМЯ узнаваемыми персонажами по референсам.

### Что сделать

1. Написать `scripts/cloud_etude.py` — один POST на OpenRouter:
   - Модель: `google/gemini-3-pro-image`
   - Ключ: из `G:\AI\_MY_PROGRAMMING\HERMES-AGENT\.openrouter_key`
     (скопировать в `.env` в корне репо как `OPENROUTER_API_KEY=...`)
   - Референсы: `characters/ancient_greece/ares.png` и
     `characters/ancient_greece/aristocles.png` — в base64
   - Промпт: натуральный язык, переписать сцену `01_hot_midday` из
     `stories/ancient_greece.json`:
     ```
     Create a cinematic photorealistic image: two men sit at a wooden table
     in an olive grove at hot Mediterranean midday. First man (reference
     image 1) is a muscular Spartan warrior with bronze helmet, red cloak,
     battle scar on left cheek. Second man (reference image 2) is a skinny
     bald Athenian philosopher with sun-spotted shiny bald head, shrewd
     squinting eyes, faint sly smile, worn faded beige cloak. Clay wine
     jugs, olives, bread on the table. Golden dusty sunlight filtering
     through olive leaves. Wide establishing shot, full scene, both figures
     fully visible from head to waist.
     ```
   - Python 3.11 stdlib-only (urllib, json, base64, pathlib)

2. Сохранить результат:
   - `sessions/ancient_greece_cloud/etude/v00.png` — картинка
   - `sessions/ancient_greece_cloud/etude/log.json` — полный ответ API:
     ```json
     {
       "story": "ancient_greece",
       "scene_id": "01_hot_midday",
       "model": "google/gemini-3-pro-image",
       "prompt": "...",
       "references": ["characters/ancient_greece/ares.png", "characters/ancient_greece/aristocles.png"],
       "seed": ...,
       "timestamp": "...",
       "usage": {...},
       "cost_usd": ...,
       "full_response": {...}
     }
     ```

3. **СТОП.** После выполнения:
   - Заполнить `tasks/REPORT.md` (факт: что получилось, cost, проблемы)
   - **НЕ продолжать** без подтверждения Yuri

### Критерий приёмки

- На картинке ДВА человека за столом (не портрет)
- Лица узнаваемо соответствуют референсам ares и aristocles
- Видна оливковая роща, стол, кувшины
- cost_usd в log.json ≈ $0.03–0.06

### Замечания

- Python: `C:\Python311\python.exe`, stdlib-only
- Ключ OpenRouter НЕ коммитить (`.env` под `.gitignore`)
- `print()` — ASCII (консоль cp1252)
- Пути через pathlib, относительные от корня репо
- ComfyUI НЕ трогать — этот скрипт работает только с OpenRouter HTTP API