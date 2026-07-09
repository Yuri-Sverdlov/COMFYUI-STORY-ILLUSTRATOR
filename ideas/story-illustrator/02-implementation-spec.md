# COMFYUI-STORY-ILLUSTRATOR — Implementation Spec

**Created:** 2026-07-12
**Based on:** `01-design-doc.md` (все вопросы закрыты)
**Status:** Draft → на утверждение Yuri

## 1. Целевая структура репозитория

```
COMFYUI-STORY-ILLUSTRATOR/
├── scripts/
│   ├── batch_scenes.py        ← единый раннер (переработка текущего)
│   └── make_contact_sheet.py  ← HTML-контактлист: сцены × стили
├── profiles/
│   ├── realism.json
│   └── illustration.json
├── stories/
│   └── ancient_greece.json
├── characters/
│   └── ancient_greece/
│       ├── ares.png           ← 1 нейтральный референс на персонажа
│       ├── aristocles.png
│       └── ploutos.png
├── sessions/                  ← рассказ → стиль → сцена (см. §5)
├── experiments/               ← пробы моделей/весов + выводы (см. §7)
├── ideas/story-illustrator/   ← пакет документов (этот)
├── tasks/                     ← TASK.md / REPORT.md (процесс сохраняем)
└── KNOWLEDGE_BASE.md          ← разделы по стилям
```

## 2. Форматы конфигов (JSON, UTF-8)

### 2.1 Профиль стиля — `profiles/<style>.json`

```json
{
  "name": "realism",
  "checkpoint": "realismIllustriousBy_v50FP16.safetensors",
  "loras": [
    {"file": "cinematic_photography_detailed_illu_xl_v5.safetensors",
     "strength": 0.8}
  ],
  "params": {"steps": 25, "cfg": 7.0, "sampler": "euler",
             "width": 1216, "height": 832},
  "prompt_template": {
    "prefix": "cinematic photo, photorealistic, ...",
    "suffix": "detailed skin, natural light",
    "negative": "text, watermark, cartoon, ..."
  },
  "ipadapter": {"enabled": true,
                "model": "ip-adapter-plus_sdxl_vit-h.safetensors",
                "weight": 0.6}
}
```

`illustration.json` — то же, checkpoint = dreamshaper_xl_lightning,
свой prompt_template (живописный), свои params (lightning: мало steps,
низкий cfg — взять из KNOWLEDGE_BASE).

**Правило:** итоговый промпт = profile.prefix + scene.prompt +
profile.suffix. Сценовый промпт НЕ содержит стилевых слов.

### 2.2 Рассказ — `stories/<story>.json`

```json
{
  "story": "ancient_greece",
  "title": "В Древней Греции полдень горяч",
  "characters": {
    "ares": "muscular Spartan warrior, short beard, bronze helmet, red cloak",
    "aristocles": "thin bald Athenian man, pale himation",
    "ploutos": "plump wealthy Greek man, white cloak"
  },
  "scenes": [
    {
      "id": "01_hot_midday",
      "main_character": "ares",
      "prompt": "two friends at an outdoor table in an olive grove, ...",
      "negative_extra": "",
      "variants": 4
    }
  ]
}
```

- `main_character` → раннер подставляет `characters/<story>/<имя>.png`
  в IP-Adapter (если в профиле enabled) и его текст-описание в промпт.
- Описания остальных персонажей сцены — прямо в `prompt`.

## 3. Раннер `batch_scenes.py`

CLI (stdlib argparse):

```
python scripts/batch_scenes.py --story stories/ancient_greece.json \
    --profile profiles/realism.json [--scenes 01,03] [--variants 2] \
    [--out sessions] [--dry-run]
```

Поведение:
1. Загрузить оба JSON, провалидировать (обязательные поля; файлы
   checkpoint/lora/референсов существуют — иначе понятная ошибка).
2. Проверить ComfyUI (`/system_stats`), иначе выход с подсказкой запуска.
3. Для каждой сцены × вариант: собрать API-workflow (class_type),
   отправить в `/prompt`, дождаться, забрать png.
4. Разложить: `sessions/<story>/<profile>/<scene_id>/v<NN>_seed<S>.png`.
5. Рядом писать `log.json`: полный итоговый промпт, негатив, seed,
   checkpoint, loras, params, вес ipadapter, референс, время, версия
   раннера.
6. `--dry-run`: напечатать план и итоговые промпты, не генерить.
7. print — только ASCII.

Технические требования: Python 3.11 системный, stdlib-only, пути через
pathlib, без хардкода абсолютных путей (корень = положение скрипта).

## 4. Контактлист `make_contact_sheet.py`

```
python scripts/make_contact_sheet.py --story ancient_greece
```

→ `sessions/ancient_greece/contact_sheet.html`: строки — сцены,
колонки — стили, в ячейке все варианты миниатюрами (относительные пути,
file:// работает локально).

## 5. Выходы и git

- `sessions/<story>/<style>/<scene>/` — рабочие варианты, в `.gitignore`.
- `sessions/<story>/<style>/_selected/` — отобранные Yuri финалы,
  **коммитятся** (исключение в .gitignore: `!**/_selected/**`).
- `log.json` — коммитятся (лёгкие, дают воспроизводимость).

## 6. Миграция существующего

1. Старые галереи (`sessions/dreamshaper_xl_lightning`,
   `sessions/realismIllustriousBy_v50FP16`, `sessions/ancient_greece`)
   → `sessions/_archive/` (не удалять).
2. `character_sheets` → выбрать по 1 нейтральному референсу на персонажа
   → `characters/ancient_greece/` (выбор — за Yuri, задача агенту:
   подготовить контактлист кандидатов).
3. Промпты сцен из текущего `batch_scenes.py` → `stories/ancient_greece.json`
   (очистить от стилевых слов — они уходят в профили).

## 7. Эксперименты

`experiments/<дата>_<тема>/` — png + `CONCLUSION.md` (2–5 строк: что
проверяли, что вышло, решение). Обязательные эксперименты MVP:

- **EXP-1. Вес IP-Adapter:** сцена `03_chimera_gossip`, фиксированный seed,
  weight = 0.4 / 0.55 / 0.7 / 0.85, оба профиля. Выбранный вес → в профили.
- **EXP-2. Кандидат модели для illustration** (по желанию, после MVP):
  фиксированная пара сцен, кандидат vs dreamshaper.

## 8. План работ (фазы MVP)

| # | Задача | Критерий готовности |
|---|--------|---------------------|
| M1 | Структура + конфиги: profiles/, stories/ancient_greece.json, .gitignore | JSON валидны, dry-run печатает план |
| M2 | Раннер: генерация по story×profile, раскладка, log.json | 1 сцена × 2 профиля дала файлы + логи |
| M3 | Референсы: контактлист кандидатов → Yuri выбирает → characters/ | 3 нейтральных png на месте |
| M4 | EXP-1 калибровка веса IP-Adapter | вывод в experiments/, вес в профилях |
| M5 | Полный прогон Греции: 5 сцен × 2 стиля × 4 варианта | контактлист готов, Yuri отобрал _selected |
| M6 | Тест на новизну: новый мини-рассказ (2–3 сцены) только конфигом | генерация без правки кода |
| M7 | Миграция архива + обновление README/CONTEXT/KNOWLEDGE_BASE | документы соответствуют реальности |

M1–M2 можно делать в Cursor по handoff-документу; M3–M5 требуют
участия Yuri (отбор).

## 9. Тесты и верификация

- `py_compile` обоих скриптов.
- `--dry-run` на ancient_greece × оба профиля: план без ошибок.
- Негативный тест: битый JSON / отсутствующий checkpoint → понятная
  ошибка, не traceback.
- M2-приёмка: файл png существует, log.json содержит все поля §3.5.
- Финальная приёмка MVP = критерии из design doc (Греция + новизна).

## 10. Риски

| Риск | Смягчение |
|------|-----------|
| IP-Adapter снова задавит композицию | EXP-1 до полного прогона; weight в конфиге |
| Lightning-модель требует других params | params в профиле, не в коде |
| Пути/кодировка на Windows | pathlib + ASCII print + отн. пути |
| VRAM при смене checkpoint между профилями | прогоны по профилю, не чередуя |
| Каша вернётся | правило _selected/experiments + контактлисты |

## Next steps

1. Yuri утверждает spec (или правит).
2. → `03-agent-build-handoff.md` — ТЗ-хэндофф для исполнителя
   (Cursor chat/terminal или кодер-агент): миссия, задачи M1–M7,
   тесты, acceptance, prompt для агента.
3. → `04-spec-review.md` — рецензия готовности.
