from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import FileRecord


class ScanCache:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                size INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                sha256 TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(size)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)")
        self.conn.commit()

    def get(self, path: Path, size: int, mtime_ns: int) -> FileRecord | None:
        row = self.conn.execute(
            "SELECT path, size, mtime_ns, sha256 FROM files WHERE path = ?", (str(path),)
        ).fetchone()
        if not row:
            return None
        if row["size"] != size or row["mtime_ns"] != mtime_ns:
            return None
        return FileRecord(path=Path(row["path"]), size=row["size"], mtime_ns=row["mtime_ns"], sha256=row["sha256"])

    def upsert(self, rec: FileRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO files(path, size, mtime_ns, sha256)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
              size=excluded.size,
              mtime_ns=excluded.mtime_ns,
              sha256=excluded.sha256,
              updated_at=CURRENT_TIMESTAMP
            """,
            (str(rec.path), rec.size, rec.mtime_ns, rec.sha256),
        )

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
