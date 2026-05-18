# FoxDuplicateFinder

Прототип и архитектурный каркас сервиса поиска дубликатов фото/видео для Windows.

## Что уже есть в репозитории

- Python-пакет `foxduplicatefinder`.
- CLI-команда `foxdup scan` с базовыми флагами (`--deep`, `--nsfw`, `--similarity`).
- Базовый `pyproject.toml` для дальнейшей сборки в EXE (через PyInstaller/Nuitka на следующих этапах).

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
foxdup scan /path/to/folder --deep --nsfw --similarity 90
```

## Предложенная архитектура (по ТЗ)

### 1) Слой сканирования

- Обход ФС (HDD/SSD/USB/сетевые папки).
- Очереди задач и многопоточность.
- Кеш в SQLite:
  - метаданные файла;
  - контрольные суммы;
  - perceptual hash;
  - embeddings.

### 2) Ядро поиска дубликатов

**Точные дубликаты**
- размер + SHA256/BLAKE3.

**Похожие изображения**
- pHash/dHash;
- SSIM/OpenCV;
- CLIP embeddings (косинусная близость).

**Похожие видео**
- извлечение keyframes (ffmpeg);
- perceptual hash ключевых кадров;
- сравнение аудио-отпечатков.

### 3) NSFW/контент-анализ

- ONNX Runtime для локального инференса.
- NudeNet/OpenNSFW для взрослых сцен.
- Доп. категории:
  - кровь/жестокость,
  - anime NSFW,
  - suspicious content.
- Safe mode: скрытые превью и карантин.

### 4) Представление результатов

- Группы дубликатов (exact/similar/near-duplicate).
- Фильтры по типу, уверенности, размеру экономии.
- Экспорт JSON/CSV.

### 5) Интерфейсы

- **CLI**: пакетные сканы и автоматизация.
- **GUI (PySide6/PyQt6)**:
  - выбор папок/дисков/USB;
  - drag-and-drop;
  - предпросмотр;
  - перемещение в карантин / удаление.

## План следующего шага

1. Реализовать файловый индексатор и SQLite-кеш.
2. Добавить fast-pass точных дубликатов (size + hash).
3. Подключить imagehash/OpenCV и расчет pHash/dHash.
4. Вынести правила кластеризации дублей.
5. Добавить экспорт отчета.
6. Затем подключить видео и NSFW пайплайн.
