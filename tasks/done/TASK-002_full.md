# TASK-002 (полный план) — Batch-конвейер «рассказ → серия иллюстраций» (M1–M7)

> Архивный документ. Активное задание — `tasks/TASK.md`.
> Этот файл — полный план фаз M2–M7 для следующей сессии.

**Контекст:** проект переходит от монолитного `batch_scenes.py` с хардкодом
к конфигурируемому конвейеру. Фаза M1 выполнена архитектором (bootstrap):
созданы `profiles/`, `stories/`, обновлён `.gitignore`, переписан `batch_scenes.py`,
написан `make_contact_sheet.py`. Задача кодера — фазы M2–M7.

**Цель:** единый раннер, два стиля как JSON-профили, рассказы как JSON-файлы
сцен, consistency главного героя через IP-Adapter, выходы по осям
«рассказ → стиль → сцена», контактлист для сравнения.

**Проектные документы:** `ideas/story-illustrator/01-design-doc.md`,
`02-implementation-spec.md`, `03-agent-build-handoff.md`.

---

### M1: Проверка готовности

```powershell
C:\Python311\python.exe -m py_compile scripts/batch_scenes.py scripts/make_contact_sheet.py
C:\Python311\python.exe -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('profiles/*.json')+glob.glob('stories/*.json')]; print('JSON OK')"
C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/realism.json --dry-run
C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/illustration.json --dry-run
git check-ignore -v .env
```

---

### M2: Тестовый прогон (1 сцена × 2 профиля)

1. Запусти ComfyUI:
   ```powershell
   C:\Python311\python.exe G:\AI\_MY_PROGRAMMING_2\ComfyUI\main.py --listen 127.0.0.1 --port 8188
   ```

2. Сгенерируй 1 сцену × 2 профиля × 1 вариант:
   ```powershell
   C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/realism.json --scenes 01_hot_midday --variants 1
   C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/illustration.json --scenes 01_hot_midday --variants 1
   ```

3. Проверь: `sessions/ancient_greece/<style>/01_hot_midday/v00_seed*.png` + `log.json`
4. log.json: все поля (prompt, negative, seed, checkpoint, loras, params, ipadapter_weight, reference_image, timestamp, runner_version)
5. Контактлист: `C:\Python311\python.exe scripts/make_contact_sheet.py --story ancient_greece`
6. `contact_sheet.html` открывается в браузере, картинки видны (file:// пути, v1.0.1)

**Примечание:** IP-Adapter выключен (нет референсов). Скрипт должен дать WARNING, не упасть.

---

### M3: Референсы персонажей (СТОП — нужен Yuri)

1. Собери контактлист кандидатов из `sessions/character_sheets/`:
   - ares: `ares_masculine_v*` + `ares_v*` (8 файлов)
   - aristocles: `aristocles_v*` (4 файла)
   - ploutos: `ploutos_v*` (4 файла)
2. Сгенерируй HTML с миниатюрами всех кандидатов.
3. **ОСТАНОВИСЬ.** Предъяви контактлист Yuri. Он выберет по 1 референсу.
4. Выбранные → `characters/ancient_greece/{ares,aristocles,ploutos}.png`
5. Проверь визуально: мужские лица? Возраст 35–50? Нет NSFW?

---

### M4: EXP-1 — калибровка веса IP-Adapter

1. `experiments/2026-07-09_ipadapter_weight/`
2. Сцена `03_chimera_gossip`, фиксированный seed, веса 0.4/0.55/0.7/0.85 × оба профиля
3. 8 png + `CONCLUSION.md` (2–5 строк)
4. Выбранный вес → `ipadapter.weight` в оба профиля

---

### M5: Полный прогон Греции (СТОП — нужен Yuri)

1. Прогоны по профилю целиком (не чередовать checkpoint'ы):
   ```powershell
   C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/realism.json
   C:\Python311\python.exe scripts/batch_scenes.py --story stories/ancient_greece.json --profile profiles/illustration.json
   ```
2. Контактлист: `C:\Python311\python.exe scripts/make_contact_sheet.py --story ancient_greece`
3. **ОСТАНОВИСЬ.** Yuri отберёт финалы.
4. Отобранные → `sessions/ancient_greece/<style>/_selected/`
5. Закоммитить `_selected/` и `log.json`

---

### M6: Тест на новизну

1. Новый мини-рассказ (2–3 сцены) → `stories/<new>.json` (без правки кода)
2. Референсы → `characters/<new>/`
3. Прогон обоими профилями + контактлист

---

### M7: Миграция и документация

1. Старые галереи → `sessions/_archive/` (не удалять)
2. Обновить `KNOWLEDGE_BASE.md` (разделы по стилям)
3. Обновить `CONTEXT.md`, `README.md`
4. `git status` чистый

---

### Критерии приёмки (всего проекта)

- [ ] Один раннер обслуживает оба профиля; смена стиля = смена `--profile`
- [ ] 5 сцен × 2 стиля Греции сгенерированы, log.json полные
- [ ] Главный герой сцены визуально узнаваем между сценами одного стиля
- [ ] `_selected/` заполнен Yuri и закоммичен
- [ ] Новый рассказ прошёл без правки кода (M6)
- [ ] Старые галереи в `_archive/`, документы обновлены

### Замечания

- Python — `C:\Python311\python.exe`, stdlib-only
- Workflow — API-формат `class_type`
- M3 и M5 — стоп-точки, спросить Yuri
- Фазы последовательно: не запускать M5 пока M4 не закрыт
- Всё в `tasks/REPORT.md`