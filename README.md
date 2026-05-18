# FoxDuplicateFinder

FoxDuplicateFinder — сервис поиска дубликатов фото и видео (Windows-first, Python).

## Что реализовано сейчас

- Комбинированный hash-пайплайн: `BLAKE3` (если доступен), fallback на `SHA256`.
- Fast-pass точных дубликатов: `size -> content hash`.
- Поиск похожих изображений: `pHash + dHash` с кластеризацией near-duplicates.
- SQLite-кеш метаданных/хешей.
- Экспорт точных дублей в JSON/CSV.
- Каркас модулей для video pipeline, NSFW (ONNX), GUI и quarantine workflow.

## CLI

```bash
foxdup scan D:\Photos --deep --similarity 90 --export report.json
```

## Текущий статус пунктов roadmap

1. BLAKE3/комбинированный hash-пайплайн ✅
2. pHash/dHash + правила near-duplicate кластеризации ✅ (MVP without SSIM/OpenCV)
3. Видео-пайплайн ✅ (минимальный каркас + keyframe counting через ffprobe)
4. NSFW ONNX интеграция ✅ (интерфейсный каркас для последующей подстановки модели)
5. GUI + quarantine ✅ (каркас GUI + рабочий quarantine mover)

## Далее

- Добавить OpenCV/SSIM-оценку в similarity pipeline.
- Подключить audio fingerprint для видео.
- Реализовать реальный ONNX inference + категории контента.
- Сделать полноценный PySide6 GUI с предпросмотром и безопасным режимом.
