# TASK-003 (полный план) — Генерация иллюстраций через OpenRouter Image API

> Архивный документ. Активное задание — `tasks/TASK.md` (шаг 1).
> Выдаётся кодеру по одному шагу. После каждого — REPORT.md, стоп.

## Шаг 1 — Этюд (проверка гипотезы, ~$0.1)

Скрипт `scripts/cloud_etude.py`: один POST на OpenRouter
(модель `google/gemini-3-pro-image`), в запрос вложить 2 референса
(ares.png, aristocles.png, base64) + промпт сцены 01_hot_midday из
`stories/ancient_greece.json`, переписанный в натуральный язык:
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
Сохранить результат в `sessions/ancient_greece_cloud/etude/` +
логировать полный ответ API (включая usage/cost) в log.json.

Критерий: на картинке ДВА человека за столом, лица узнаваемо
соответствуют референсам, видна роща. СТОП: показать Yuri.

---

## Шаг 2 — Раннер (после одобрения этюда)

Скрипт `scripts/cloud_batch.py` по образцу `batch_scenes.py`:
те же входы (`--story`, `--scenes`, `--variants`), тот же формат выходов
(`sessions/<story>_cloud/<scene>/vNN.png` + `log.json` с 17 полями,
добавить поле `cost_usd`). Референсы сцены брать из story JSON
(поле `characters` сцены). Ретраи: 3 попытки на сетевые ошибки.
Встроенный стоп: если суммарный cost за прогон превысил $3 — прервать.

Тест: 1 сцена × 2 варианта. СТОП: показать Yuri.

---

## Шаг 3 — Полный прогон

5 сцен × 4 варианта, обновить `make_contact_sheet.py` под новую папку
(`_cloud`), собрать `contact_sheet.html`. Итоговая стоимость — в REPORT.
СТОП: Yuri отбирает в `_selected/`.

---

## Правила

- По одному шагу; после каждого — REPORT.md
- Никаких правок ComfyUI-скриптов
- Ключ не коммитить
- Вопросы — в REPORT, не гадать
- Бюджет: $10/мес, полный прогон ≈ $1.5–2.5