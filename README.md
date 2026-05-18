# FoxDuplicateFinder

FoxDuplicateFinder — сервис поиска дубликатов фото и видео (Windows-first, Python).

## Что реализовано сейчас

- Комбинированный hash-пайплайн: `BLAKE3` (если доступен), fallback на `SHA256`.
- Fast-pass точных дубликатов: `size -> content hash`.
- Поиск похожих изображений: `pHash + dHash` + OpenCV SSIM post-filter для near-duplicates.
- SQLite-кеш метаданных/хешей.
- Экспорт точных дублей в JSON/CSV.
- Видео-пайплайн: keyframe count + audio fingerprint (PCM hash через ffmpeg).
- NSFW-пайплайн на ONNX Runtime: реальный inference (при переданном `--nsfw-model`) с категориями `nsfw`, `violence`, `anime`.
- PySide6 GUI: выбор папки, скан, список дублей, предпросмотр, safe mode (скрытие превью).

## CLI

```bash
foxdup scan D:\Photos --deep --similarity 90 --nsfw --nsfw-model models/safety.onnx --export report.json
foxdup gui
```
