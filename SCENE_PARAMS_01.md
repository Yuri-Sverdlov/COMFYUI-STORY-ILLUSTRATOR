# Матрица параметров сцены

> Универсальный шаблон. Заполняется для каждой сцены перед генерацией.
> Меняя один параметр за раз, отлаживаем композицию системно.

---

## Сцена: `01_hot_midday` — Жаркий полдень, Аристокл и Арес за столом

### 1. Пространство (где кто находится)

| Параметр | Текущее значение | Что можно менять |
|----------|-----------------|------------------|
| **Формат кадра** | Wide landscape (1344×768) | Квадрат (1024×1024), вертикаль |
| **Масштаб** | General plan, figures small in frame | Medium shot, American shot |
| **Позиция Ареса** | LEFT side of frame | RIGHT, center, foreground |
| **Позиция Аристокла** | RIGHT side of frame | LEFT, center, background |
| **Дистанция между ними** | Across the table (~1.5 м) | Close (рядом), far (разные концы стола) |
| **Кто ближе к камере** | Оба на одной линии | Арес ближе, Аристокл дальше |
| **Пространство вокруг** | Olive grove, tree canopies above, dusty ground | Добавить: храм на холме, дорога |

### 2. Действия (что делают)

| Параметр | Текущее значение | Варианты |
|----------|-----------------|----------|
| **Арес** | Gesturing impatiently with one hand | Пьёт вино, смотрит вдаль, снимает шлем, вытирает пот |
| **Аристокл** | Crumbling goat cheese, sweating | Крошит сыр, вытирает лысину, прищурился на солнце, отпивает вино |
| **Взаимодействие** | Facing each other across the table | Один говорит — другой слушает, оба смотрят на дорогу |

### 3. Настроение и эмоции

| Параметр | Арес | Аристокл |
|----------|------|----------|
| **Эмоция** | Impatient, irritated (недовольный) | Ironic, amused (ироничный, ему смешно) |
| **Выражение лица** | Frowning, gesturing | Sly smile, squinting |
| **Поза** | Напряжённая, прямая | Расслабленная, развалился |

### 4. Атмосфера и погода

| Параметр | Текущее значение | Варианты |
|----------|-----------------|----------|
| **Время суток** | Midday (полдень) | Afternoon, sunset |
| **Свет** | Golden dusty sunlight, harsh shadows | Мягкий рассеянный, контровой |
| **Жара** | Heat haze, sweating, cicada-hum | Прохлада, ветерок |
| **Небо** | Clear, bright | Лёгкая дымка, облака |

### 5. Предметы и детали (props)

| Параметр | Есть? | Детали |
|----------|:-----:|--------|
| Стол | ✅ | Wooden, rough |
| Кувшин с вином | ✅ | Clay wine jug |
| Кувшин с маслом | ✅ | Oil amphora |
| Хлеб | ✅ | Round bread loaf on wooden plate |
| Оливки | ✅ | Scattered olives |
| Козий сыр | ✅ | Crumbled goat cheese |
| Шлем Ареса | ✅ | Corinthian bronze helmet pushed back |
| Меч Ареса | ⚠️ | Short sword (не всегда видно) |
| Плащ Ареса | ✅ | Red wool cloak |
| Плащ Аристокла | ✅ | Worn faded beige cloak |

### 6. Стилистические директивы

| Параметр | Значение |
|----------|----------|
| Стиль | Photorealistic, cinematic, 8K |
| Оптика | Sharp focus, shallow depth of field |
| Цвета | Warm Mediterranean palette, gold, terracotta, olive green |
| Что исключить | Portrait, close-up, face-focused, cartoon, illustration, nude, NSFW |

---

## АНГЛИЙСКИЙ ПРОМПТ (текущий, Промпт #1)

```
LANDSCAPE orientation wide shot, environmental scene:
hot Mediterranean midday, two men seated at a wooden table under ancient olive trees in a dusty grove.
Figures occupy only one third of frame, tree canopies visible above, dusty ground visible below.
LEFT side: ARES — muscular rugged Spartan warrior, 48, thick short grey-streaked black hair,
Corinthian bronze helmet pushed back, weathered leathery skin, strong square stubbled jaw,
broken nose, battle scar, intense dark eyes, thick neck, red wool cloak.
He gestures impatiently with one hand, frowning, irritated by the heat.
RIGHT side: ARISTOCLES — skinny bald Athenian philosopher, 55, gaunt thin face,
prominent cheekbones, sun-spotted shiny bald head, deep wrinkles, shrewd squinting eyes,
faint sly ironic smile, worn faded beige cloak.
He crumbles goat cheese, sweating, amused by his companion's impatience.
They face each other across the table.
Between them on the table: clay wine jug, oil amphora, wooden plate with round bread and olives, crumbled goat cheese.
Golden dusty sunlight filtering through olive leaves, heat haze, cicada-hum atmosphere.
Mediterranean landscape visible behind — olive grove, distant hills, not desert.
Both figures visible from head to waist.
NOT a portrait, NOT close-up, NOT face-focused.
Photorealistic cinematic, 8K, warm Mediterranean palette, sharp focus.
```

---

*Заполнять для каждой сцены. Менять один параметр за раз.*
