# FoxDuplicateFinder

FoxDuplicateFinder — сервис поиска дубликатов фото и видео (Windows-first, Python).

## Реализовано в текущем MVP

- Файловый индексатор медиа-файлов (изображения/видео) по расширениям.
- SQLite-кеш метаданных и SHA256 (path, size, mtime_ns, sha256).
- Fast-pass точных дубликатов: группировка `size -> sha256`.
- CLI-экспорт результатов в JSON/CSV.

## CLI

```bash
foxdup scan D:\Photos --deep --export report.json
foxdup scan D:\Photos --deep --export report.csv
foxdup scan D:\Photos --deep --nsfw
```

Опции:

- `--deep` — рекурсивный обход.
- `--nsfw` — флаг зарезервирован под будущий AI-анализ.
- `--similarity` — зарезервирован под будущий поиск похожих файлов.
- `--cache-db` — путь к SQLite-кешу.
- `--export` — экспорт отчета (`.json` или `.csv`).

## Следующие этапы

1. Подключить BLAKE3 и/или комбинированный hash-пайплайн.
2. Добавить pHash/dHash + OpenCV/SSIM для похожих изображений.
3. Вынести правила кластеризации near-duplicates.
4. Добавить видео-пайплайн (keyframes/audio fingerprint).
5. Интегрировать NSFW/violence/anime классификацию через ONNX Runtime.
6. Реализовать GUI (PySide6/PyQt6) + quarantine workflow.
