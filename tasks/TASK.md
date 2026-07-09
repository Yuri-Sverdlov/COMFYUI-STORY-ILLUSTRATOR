# TASK — активное задание архитектор → кодер

> Одно активное задание. После выполнения — заполнить `tasks/REPORT.md`.

## TASK-002: Commit + push bootstrap M1 на GitHub

**Контекст:** Архитектор выполнил bootstrap M1 — создал каркас batch-конвейера
(profiles/, stories/, .gitignore, batch_scenes.py, make_contact_sheet.py).
Файлы лежат в репо, но не закоммичены и не запушены. Рабочее время кончилось,
нужно сохранить всё на GitHub.

**Цель:** закоммитить и запушить текущее состояние репо.

**Шаги:**

1. Проверить состояние:
   ```powershell
   git status
   ```

2. Закоммитить всё:
   ```powershell
   git add -A
   git commit -m "TASK-002 M1: batch-conveyor bootstrap (profiles, stories, CLI runner, contact sheet)"
   ```

3. Запушить:
   ```powershell
   git push origin main
   ```

4. Заполнить `tasks/REPORT.md` (факт: закоммичено, запушено, хеш коммита).

**Критерий приёмки:** `git status` чистый; `git log --oneline -1` показывает
коммит; `git ls-remote origin refs/heads/main` совпадает с локальным HEAD.

**Следующая сессия:** TASK-002 продолжится фазами M2–M7
(см. `tasks/done/TASK-002_full.md` — полный план на следующую сессию).

---

### Замечания

- Python — системный `C:\Python311\python.exe`, не venv.
- git commit/push — только Кодер на Windows (DEV-NOTES §3).
- Remote: `https://github.com/Yuri-Sverdlov/COMFYUI-STORY-ILLUSTRATOR.git` (уточнить `git remote -v`).