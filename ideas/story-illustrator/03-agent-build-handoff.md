# COMFYUI-STORY-ILLUSTRATOR — Agent Build Handoff

**Created:** 2026-07-12
**For:** Cursor (chat + terminal agent) или другой кодер-агент
**Source of truth:** `01-design-doc.md`, `02-implementation-spec.md` (этот
документ — их исполняемая выжимка; при противоречии главнее spec)

## Mission

Построить в репозитории `G:\AI\_MY_PROGRAMMING_2\COMFYUI-STORY-ILLUSTRATOR`
batch-конвейер «рассказ → серия иллюстраций» на ComfyUI API: единый раннер
`scripts/batch_scenes.py`, стили как JSON-профили, рассказы как JSON-файлы
сцен, выходы по осям «рассказ → стиль → сцена», consistency главного героя
сцены через IP-Adapter. Довести до двух критериев приёмки: рассказ
«В Древней Греции полдень горяч» полностью проиллюстрирован в двух стилях,
и новый рассказ проходит конвейер без правки кода.

## Product Vision

Yuri иллюстрирует свои рассказы локально, воспроизводимо и без «каши»:
стиль меняется заменой одного JSON, сцены пишутся один раз без стилевых
слов, каждый результат восстановим из log.json. Агенты (Hermes, Cursor)
взаимозаменяемы — источник правды в файлах репозитория.

## Non-Negotiable Requirements

- Один раннер для всех стилей. Никаких скриптов-на-стиль.
- Python 3.11 системный (`C:\Python311\python.exe`), **только stdlib**
  (urllib, json, argparse, pathlib). Никаких pip-зависимостей.
- Workflow — API-формат ComfyUI (`class_type`), не editor-формат.
- Итоговый промпт = profile.prefix + описание main_character +
  scene.prompt + profile.suffix. Стилевые слова только в профиле.
- Выходы: `sessions/<story>/<profile>/<scene_id>/v<NN>_seed<S>.png`
  + `log.json` на сцену (промпт, негатив, seed, checkpoint, loras,
  params, вес ipadapter, референс, timestamp).
- `print()` — только ASCII (консоль cp1252).
- Пути через pathlib, относительные от корня репо (положение скрипта).
- Существующие галереи НЕ удалять — переносить в `sessions/_archive/`.

## Out of Scope

- Веб-интерфейс, сервер, чат (это соседний COMFYUI-API-CHAT).
- Regional IP-Adapter / несколько узнаваемых лиц в кадре (фаза 2).
- Профили abstract / nsfw (после MVP, добавятся как JSON).
- Обучение LoRA персонажей.
- Автоотбор лучших вариантов (отбор ручной, Yuri).
- Vision-фидбек (мультимодальная модель критикует картинки и предлагает
  правки промпта) — фаза 3 роадмапа, НЕ этот handoff. Но не мешать ему:
  log.json уже содержит всё для будущего review.json.
- FaceDetailer / upscale (фаза 5).

## Technical Architecture

```
stories/<story>.json ──┐
profiles/<style>.json ─┼─→ batch_scenes.py ─→ ComfyUI API (127.0.0.1:8188)
characters/<story>/*.png ┘        │                  /prompt, /history, /view
                                  ↓
                sessions/<story>/<style>/<scene>/v*.png + log.json
                                  ↓
                make_contact_sheet.py → contact_sheet.html (сцены × стили)
```

ComfyUI: `G:\AI\_MY_PROGRAMMING_2\ComfyUI` (запуск:
`/c/Python311/python.exe main.py --listen 127.0.0.1 --port 8188`).
IP-Adapter ноды установлены (cubiq IPAdapter_plus, 35 нод), модель
`ip-adapter-plus_sdxl_vit-h.safetensors` + CLIP Vision ViT-H скачаны.

## Data Model

Форматы JSON — точно по `02-implementation-spec.md` §2:
- **profiles/<style>.json**: name, checkpoint, loras[{file,strength}],
  params{steps,cfg,sampler,scheduler,width,height},
  prompt_template{prefix,suffix,negative},
  ipadapter{enabled,model,weight}.
- **stories/<story>.json**: story, title, characters{имя: описание},
  scenes[{id, main_character, prompt, negative_extra, variants}].

Стартовые значения профилей:
- `realism`: realismIllustriousBy_v50FP16 + LoRA
  cinematic_photography_detailed_illu_xl_v5 (0.8); steps=25, cfg=7.0,
  euler; ipadapter weight 0.6 (до EXP-1).
- `illustration`: dreamshaper_xl_lightning; lightning-параметры взять из
  `KNOWLEDGE_BASE.md` (мало steps, низкий cfg); ipadapter weight 0.6.

## Database / Storage

БД нет — файловая структура + git. Осознанное решение, не менять.

## Hosting / Deployment

Локально, компьютер 2 (Windows). Ничего не покидает машину, кроме git push
(push.ps1). Секреты: `.env` под .gitignore (проверять `git check-ignore`).

## Platform Targets

CLI-скрипты на Windows (Git Bash / PowerShell). Никаких GUI/мобильных.

## Integrations

- ComfyUI REST API + WebSocket (опционально для прогресса; можно
  поллинг /history — проще на stdlib).
- Git (push.ps1 уже есть).

## Implementation Phases (M1–M7 из spec §8)

### Phase M1: Структура и конфиги
Goal: каркас репо + валидные JSON.
Tasks: создать profiles/realism.json, profiles/illustration.json,
stories/ancient_greece.json (сцены/промпты перенести из текущего
batch_scenes.py, ОЧИСТИВ от стилевых слов — они уходят в prefix/suffix
профилей); обновить .gitignore (png игнорить, `!**/_selected/**` и
log.json — коммитить).
Verification: `python -c "import json; json.load(open(...))"` на все три
файла; `batch_scenes.py --dry-run` печатает план.

### Phase M2: Раннер
Goal: рабочая генерация story × profile.
Tasks: переписать scripts/batch_scenes.py по spec §3 (CLI, валидация,
сборка workflow, IP-Adapter ветка при enabled, раскладка, log.json,
--dry-run, --scenes, --variants); написать scripts/make_contact_sheet.py
(spec §4).
Verification: py_compile; прогон 1 сцены × оба профиля → png + log.json
в правильных путях.

### Phase M3: Референсы персонажей (с участием Yuri)
Goal: characters/ancient_greece/{ares,aristocles,ploutos}.png.
Tasks: собрать контактлист кандидатов из sessions/character_sheets
(включая ares_masculine_*); Yuri выбирает; выбранные скопировать под
каноническими именами. Отсутствующие/неудачные — перегенерить нейтральный
портрет (муж. лица! проверять глазами до использования).
Verification: 3 файла на месте, Yuri подтвердил.

### Phase M4: EXP-1 калибровка веса IP-Adapter
Goal: рабочий вес адаптера, при котором лицо держится, а композиция
сцены не схлопывается в портрет.
Tasks: experiments/<дата>_ipadapter_weight/: сцена 03_chimera_gossip,
фикс. seed, weight 0.4/0.55/0.7/0.85 × оба профиля; CONCLUSION.md;
выбранный вес прописать в оба профиля.
Verification: 8 png + вывод; профили обновлены.

### Phase M5: Полный прогон Греции (с участием Yuri)
Goal: 5 сцен × 2 стиля × 4 варианта + отбор.
Tasks: полный batch по обоим профилям (последовательно, не чередуя
checkpoint'ы — VRAM); contact_sheet.html; Yuri отбирает → _selected/.
Verification: контактлист открывается, _selected заполнен, закоммичен.

### Phase M6: Тест на новизну
Goal: доказать переносимость.
Tasks: новый мини-рассказ (2–3 сцены, текст даст Yuri или взять любой
короткий): только stories/<new>.json + референс(ы) → прогон.
Verification: генерация прошла БЕЗ единой правки scripts/.

### Phase M7: Миграция и документация
Goal: репо соответствует документам.
Tasks: старые галереи → sessions/_archive/; README.md, CONTEXT.md,
KNOWLEDGE_BASE.md обновить под новую структуру (KNOWLEDGE_BASE —
разделы по стилям); tasks/TASK.md закрыть/обновить.
Verification: структура == схеме spec §1; git status чистый.

## Testing Requirements

- Unit: не требуется (stdlib-скрипт), но валидация конфигов обязана
  давать понятные ошибки — проверить на битом JSON и несуществующем
  checkpoint (не traceback, а сообщение).
- Integration: M2-прогон 1 сцены × 2 профиля.
- E2E: M5 (Греция) + M6 (новизна).
- Manual: визуальная проверка референсов ДО batch-прогонов (урок
  прошлой итерации: женское лицо ушло в 20 картинок).

## Verification Commands

```bash
# синтаксис
/c/Python311/python.exe -m py_compile scripts/batch_scenes.py scripts/make_contact_sheet.py
# конфиги
/c/Python311/python.exe -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('profiles/*.json')+glob.glob('stories/*.json')]; print('OK')"
# ComfyUI жив
curl -s http://127.0.0.1:8188/system_stats
# план без генерации
/c/Python311/python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/realism.json --dry-run
# секреты
git check-ignore -v .env
```

## Acceptance Criteria

- [ ] Один раннер обслуживает оба профиля; смена стиля = смена --profile.
- [ ] 5 сцен × 2 стиля Греции сгенерированы, log.json полные.
- [ ] Главный герой сцены визуально узнаваем между сценами одного стиля.
- [ ] _selected/ заполнен Yuri и закоммичен.
- [ ] Новый рассказ прошёл без правки кода (M6).
- [ ] Старые галереи в _archive/, документы обновлены.

## Done Means

- [ ] Все Non-Negotiable Requirements соблюдены.
- [ ] Verification Commands проходят со свежим выводом.
- [ ] Фазы M1–M7 закрыты (M3/M5 — с подтверждением Yuri).
- [ ] Ограничения и нерешённое задокументированы в REPORT.md.

## Known Risks

- IP-Adapter давит композицию → EXP-1 обязателен ДО M5; вес в конфиге.
- Lightning-модель с чужими params даёт мусор → params только из профиля.
- cp1252 ломает print с кириллицей → ASCII-only в print.
- Референс не проверен глазами → правило M3: смотреть до batch.
- VRAM при чередовании checkpoint → прогоны по профилю целиком.

## Open Questions

- Точные lightning-параметры dreamshaper (steps/cfg/sampler) — взять из
  KNOWLEDGE_BASE.md; если там нет — 6 steps / cfg 2 / dpmpp_sde как
  стартовая гипотеза, уточнить экспериментом.
- Текст рассказа для M6 — предоставит Yuri.

## Prompt for Build Agent (Cursor)

```text
You are implementing COMFYUI-STORY-ILLUSTRATOR from this build handoff.

First, read this entire document, then 02-implementation-spec.md and
01-design-doc.md in ideas/story-illustrator/, then inspect the current
repository state (scripts/batch_scenes.py, sessions/, KNOWLEDGE_BASE.md).
Do not start coding immediately.

Work phase by phase (M1 → M7). Phases M3 and M5 require Yuri's manual
selection — stop and ask at those points. Preserve the scope and
non-goals. Python 3.11 system interpreter, stdlib only, ASCII-only
console output, pathlib paths. Verify each phase with the listed
commands before moving on. Do not claim completion until Acceptance
Criteria and Done Means pass with fresh evidence. Write results to
tasks/REPORT.md in Russian.
```
