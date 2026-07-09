# Генерация серии иллюстраций с сохранением характера персонажей

> Сводный документ. Обобщает опыт двух сессий: 06.07.2026 (редакторская оценка + начало) и 07.07.2026 (IP-Adapter + batch + отладка).
> Проект: иллюстрации к рассказу «В Древней Греции полдень горяч».
> Платформа: ComfyUI (локально) + ComfyUI API + IP-Adapter.

---

## 1. Модели и LoRA

### 1.1. Базовые модели (7 шт, ~55 GB)

| Модель | Семейство | Стиль промпта | Реализм | Сцены | NSFW-риск |
|--------|-----------|:------------:|:------:|:-----:|:---------:|
| `sd_xl_base_1.0` | SDXL | Натуральный язык | ★★★ | ★★★★★ | Низкий |
| `dreamshaper_xl_lightning` | SDXL Lightning | Натуральный язык | ★★★ | ★★★★★ | Низкий |
| `realismIllustriousBy_v50FP16` | Illustrious | Естественный + теги | ★★★★★ | ★★ | Высокий |
| `ponyDiffusionV6XL` | Pony | Натуральный язык | ★★★★ | ★★★ | Высокий |
| `illustriousXL_v01` | Illustrious | Danbooru-теги | ★★★ | ★★ | Средний |
| `aMixIllustrious_aMix` | Illustrious | Теги + естественный | ★★★★ | ★★ | Средний |
| `v1-5-pruned-emaonly` | SD 1.5 | Короткие теги | ★★ | ★★★ | Низкий |

**Ключевой вывод:** для сцен с несколькими персонажами — `sd_xl_base` или `dreamshaper_xl`. Для фотореализма — `realismIllustriousBy`, но с осторожностью (склонность к NSFW).

### 1.2. LoRA

| LoRA | Для модели | Размер | Эффект |
|------|-----------|:------:|--------|
| `cinematic_photography_detailed_illu_xl_v5` | Illustrious | 436 MB | Фотореализм, детализация кожи |
| `add-detail-xl` | SDXL | 218 MB | Усиление деталей |
| `Silver_Wolf_detail_enhancement` | SDXL | 325 MB | Детализация |
| `Hands v2.1` | SDXL | 162 MB | Фикс рук |

**Источник:** Civitai. Требуется API-ключ (`CIVITAI_API_KEY`). Ключ лежит в `G:\AI\_MY_PROGRAMMING_2\CIVITAI-DOWNLOAD-IMAGES\.env`.

### 1.3. Ловушка с LoRA
`cinematic_photography_detailed_illu_xl_v5` работает **только с Illustrious-моделями**. Для SDXL нужна отдельная photorealism LoRA (пока не скачана).

---

## 2. Стили промптов

| Модель | Формат | Пример |
|--------|--------|--------|
| **SDXL / Dreamshaper** | Длинный натуральный язык, описательные предложения | `Wide establishing shot: hot Mediterranean midday, two men seated at wooden table under olive trees. Ares, 48, muscular Spartan warrior, red cloak...` |
| **Pony V6** | Натуральный язык (подтверждено автором: *«simple natural language»*) | Такой же, как SDXL |
| **Illustrious** | Danbooru-теги через запятую + бустеры качества | `masterpiece, best quality, photorealistic, 1man, spartan, helmet, red cloak, olive grove, table, wine jug` |
| **SD 1.5** | Короткие теги, запятые | `spartan warrior, red cloak, olive grove, table, wine, photorealistic` |

### 2.1. Системный подход к промптам (таблица итераций)

При отладке композиции — вести таблицу:

| # | Цель | Что изменилось | Русский | English |
|:-:|------|---------------|---------|---------|
| 0 | База | — | ... | ... |
| 1 | Wide shot | `LANDSCAPE orientation`, `NOT portrait` | ... | ... |
| 2 | Два персонажа | `LEFT side... RIGHT side... facing each other` | ... | ... |

Тестировать по одному изменению за раз.

### 2.2. Ключевые приёмы для сцен
- **`Wide establishing shot, general plan, full scene`** — в начале промпта
- **`NOT a portrait, NOT close-up, NOT face-focused`** — в негативе
- **`LEFT side of frame: ... RIGHT side of frame: ...`** — для двух персонажей
- **`Both figures fully visible from head to waist`** — явное указание композиции
- **Возраст:** `48 years old`, `55 years old` — зрелые мужчины, меньше риска феминизации
- **Широкий кадр:** `1344×768` (16:9) вместо `1024×1024` (квадрат)

---

## 3. IP-Adapter — установка, настройка, подводные камни

### 3.1. Установка

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
pip install insightface
# Перезапустить ComfyUI
```

### 3.2. Модели

| Файл | Размер | Где |
|------|:------:|-----|
| `ip-adapter-plus_sdxl_vit-h.safetensors` | 809 MB | `models/ipadapter/` |
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | 2.4 GB | `models/clip_vision/` |

### 3.3. КЛЮЧЕВАЯ ЛОВУШКА

В репозитории `h94/IP-Adapter` две папки:
- **`models/image_encoder/`** → ViT-**H** (1280-dim) ← ПРАВИЛЬНО для `ip-adapter-plus_sdxl_vit-h`
- **`sdxl_models/image_encoder/`** → ViT-**bigG** (1664-dim) ← НЕ БРАТЬ

Суффикс **`vit-h`** в имени адаптера определяет энкодер, а не папка `sdxl_models`.

Ошибка при несовместимости:
```
size mismatch for proj_in.weight: copying [1280, 1280], current [1280, 1664]
```

### 3.4. Скачивание CLIP Vision (правильное)

```python
from huggingface_hub import hf_hub_download
hf_hub_download('h94/IP-Adapter', 'models/image_encoder/model.safetensors',
    local_dir='ComfyUI/models/clip_vision')
# Переименовать в: CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

### 3.5. Рабочий workflow

```
CheckpointLoaderSimple → LoraLoader (опционально) → IPAdapterUnifiedLoader("PLUS")
    → IPAdapter → KSampler → VAEDecode → SaveImage
```

CLIP для текста — от LoraLoader (или CheckpointLoaderSimple, если без LoRA).

### 3.6. Вес IP-Adapter

| Вес | Эффект | Когда использовать |
|:---:|--------|-------------------|
| 0.85-1.0 | IP-Adapter доминирует → выходят портреты | Тест силы адаптера |
| 0.5-0.7 | Баланс: лицо держится, композиция от промпта | **Сцены с персонажами** |
| 0.3-0.4 | Слабое влияние, почти без эффекта | Не нужно |

**Вывод:** для сцен с несколькими персонажами — `weight=0.4-0.5`.

### 3.7. Референсы (character sheets)

Перед batch-прогоном **проверить референс визуально:**
- Мужское лицо? (не женственное)
- Возраст соответствует? (40-55 лет = грубая кожа, морщины)
- Нет NSFW-артефактов?

Женственный референс × 20 картинок = 6 минут впустую.

---

## 4. Character consistency — стратегии

### 4.1. Способ А: промпт-инженерия
Одинаковые описания персонажей во всех промптах. Работает слабо — лица плывут.

### 4.2. Способ Б: IP-Adapter (один референс)
Работает для **одного** персонажа. Для нескольких — только главный герой держит лицо, остальные через промпт.

### 4.3. Способ В: Regional IP-Adapter
Нода `IPAdapterRegionalConditioning` — маски для разных зон, каждой свой референс. Не тестировали.

### 4.4. Способ Г: три прохода + композитинг
Генерируем каждого персонажа отдельно → собираем через inpainting/фотомонтаж. Не тестировали.

### 4.5. Текущий best practice
1. Сгенерировать качественные референсы (по 4 варианта, выбрать лучший)
2. Для каждой сцены: `weight=0.4-0.5` + детальный промпт с позиционированием персонажей
3. 4 варианта на сцену → выбрать лучший

---

## 5. Структура проекта и папок

```
COMFYUI-API-CHAT/                    ← основной проект
├── scripts/
│   ├── batch_scenes.py              ← batch-раннер (5 сцен × 4 варианта)
│   └── lora_workflow.py            ← шаблон workflow с LoRA
├── workflows/                       ← 16 JSON-workflow
├── sessions/                        ← ВСЕ результаты генерации
│   ├── {имя_модели}/                ← папка = базовая модель
│   │   ├── {сцена}/                 ← подпапка = сцена
│   │   │   ├── v00_seed{seed}.png   ← вариант
│   │   │   ├── v01_seed{seed}.png
│   │   │   └── ...
│   │   └── ...
│   └── character_sheets/            ← референсы персонажей
├── server.py                        ← FastAPI + чат
├── comfyui/                         ← API-клиент
├── providers/                       ← LLM-провайдеры
├── README.md                        ← инструкция
├── CONTEXT.md                       ← документация проекта
├── extra_model_paths.yaml           ← общие модели
└── .env                             ← API-ключи
```

**Правило именования:** `sessions/{модель}/{сцена}/v{вариант}_seed{seed}.png`

### Связанные папки

| Папка | Назначение |
|-------|-----------|
| `../ComfyUI/` | Установка ComfyUI, модели, LoRA, custom nodes |
| `../SOURCES-COMFYUI/` | Сырые diffusion-компоненты (архив) |
| `../COMFYUI-WAN2-2/` | Видео-модели Wan 2.2 |
| `../CIVITAI-DOWNLOAD-IMAGES/` | Загрузчик с Civitai |

---

## 6. Batch-генерация

### 6.1. Подготовка

```bash
# 1. Запустить ComfyUI (системный Python!)
/c/Python311/python.exe ../ComfyUI/main.py --listen 127.0.0.1 --port 8188

# 2. Проверить
curl -s http://127.0.0.1:8188/system_stats
```

### 6.2. Запуск

```bash
cd G:\AI\_MY_PROGRAMMING_2\COMFYUI-API-CHAT
/c/Python311/python.exe scripts/batch_scenes.py
```

### 6.3. Параметры по умолчанию

| Параметр | Значение |
|----------|----------|
| Модель | `realismIllustriousBy_v50FP16` |
| LoRA | `cinematic_photography_detailed_illu_xl_v5` (0.8) |
| Steps | 25 |
| CFG | 7.0 |
| Sampler | euler |
| Вариантов | 4 |
| Размер | 1024×1024 |

### 6.4. Производительность

| Модель | Время на картинку | 20 картинок |
|--------|:----------------:|:----------:|
| `dreamshaper_xl_lightning` (8 steps) | ~8 сек | ~3 мин |
| `realismIllustriousBy` (25 steps) | ~20 сек | ~7 мин |
| `sd_xl_base` (25 steps) | ~20 сек | ~7 мин |

RTX 4060, 8 GB VRAM.

---

## 7. Уроки и грабли (debug-log)

### 7.1. Python — системный, не venv Hermes
`python` в терминале → `~/.hermes/hermes-agent/venv/Scripts/python` (нет пакетов).
Правильно: `/c/Python311/python.exe`.

### 7.2. extra_model_paths.yaml — без вложенных словарей
```yaml
# ПРАВИЛЬНО:
comfyui:
  base_path: G:\путь
  checkpoints: models/checkpoints/

# НЕПРАВИЛЬНО (dict внутри):
comfyui:
  checkpoints:
    base_path: G:\путь   # → AttributeError: 'dict' object has no attribute 'split'
```

### 7.3. Civitai API требует токен
Без токена скачивается `{"error":"Unauthorized"}` (106 байт).

### 7.4. Имя CLIP Vision файла критично
Должно соответствовать regex `ViT.H.14.*s32B.b79K`. Иначе `IPAdapterUnifiedLoader` не найдёт.

### 7.5. Порт 8188 занят → `OSError: [Errno 10048]`
Предыдущий процесс ComfyUI не убит. Использовать `kill_port_8188.py`.

### 7.6. Женственный референс = женские лица на всех картинках
Проверять референс визуально перед batch-прогоном.

### 7.7. IP-Adapter weight > 0.7 → портреты вместо сцен
Промпт проигрывает референсу. Держать 0.4-0.5 для сцен.

---

## 8. Сравнение моделей (по результатам тестов)

| Критерий | dreamshaper_xl | realismIllustriousBy | sd_xl_base |
|----------|:---:|:---:|:---:|
| Фотореализм | ★★★ | ★★★★★ | ★★★ |
| Сцены (композиция) | ★★★★★ | ★★ | ★★★★ |
| Мужские лица | ★★★★ | ★★ | ★★★★ |
| NSFW-артефакты | Нет | Есть | Нет |
| Скорость | ★★★★★ (8 steps) | ★★★ (25 steps) | ★★★ (25 steps) |
| IP-Adapter | ★★★★ | ★★★★★ | ★★★★ |
| **Лучше всего для** | Сюжетные сцены | Портреты, лица | Чистые сцены без NSFW |

**Вывод:** `dreamshaper_xl` + IP-Adapter (w=0.5) — лучший компромисс для серийных иллюстраций. `sd_xl_base` — если нужна чистота без NSFW-рисков.

---

## 9. Этапы развития проекта

| Этап | Дата | Что сделано | Результат |
|------|------|-------------|-----------|
| 1 | 06.07 | Редакторская оценка рассказа | 9 пунктов улучшений |
| 2 | 06.07 | Midjourney-промпты для 5 сцен | 5 промптов EN+RU |
| 3 | 06.07 | Переход на ComfyUI | Аудит папки, выбор COMFYUI-API-CHAT |
| 4 | 06.07 | Первый batch (dreamshaper) | 20 картинок — сцены работают, лица плывут |
| 5 | 07.07 | Установка IP-Adapter | 35 нод, модели скачаны |
| 6 | 07.07 | Поиск CLIP Vision | 4 попытки, решено через вторую LLM |
| 7 | 07.07 | Batch с IP-Adapter (realismIllustrious) | 20 картинок — лица держатся, но женственные + портреты |
| 8 | 07.07 | Отладка: weight + wide shot + возраст | В процессе |

---

*Документ создан 07.07.2026. Обновлять по мере новых находок.*
