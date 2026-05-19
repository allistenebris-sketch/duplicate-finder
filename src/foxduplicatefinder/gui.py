from __future__ import annotations

from pathlib import Path

from .cache import ScanCache
from .scanner import find_exact_duplicates, iter_files

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )
except Exception:
    QApplication = None


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FoxDuplicateFinder")
        self.resize(1200, 760)
        self.safe_mode = True
        self.paths: list[Path] = []

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        toggle_safe = QAction("Safe mode: ON", self)
        toggle_safe.triggered.connect(lambda: self.set_safe_mode(not self.safe_mode))
        toolbar.addAction(toggle_safe)
        self.toggle_safe_action = toggle_safe

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Choose folder to scan")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse)
        scan_btn = QPushButton("Scan")
        scan_btn.clicked.connect(self.scan)
        top.addWidget(self.path_edit)
        top.addWidget(browse_btn)
        top.addWidget(scan_btn)
        layout.addLayout(top)

        split = QSplitter(Qt.Orientation.Horizontal)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Group", "Size", "Path"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.preview_current)
        split.addWidget(self.table)

        right = QWidget()
        rlayout = QVBoxLayout(right)
        self.preview = QLabel("Preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(420, 420)
        self.preview.setStyleSheet("border: 1px solid #555;")
        self.meta = QLabel()
        self.meta.setWordWrap(True)
        rlayout.addWidget(self.preview)
        rlayout.addWidget(self.meta)
        split.addWidget(right)
        layout.addWidget(split)

    def set_safe_mode(self, enabled: bool) -> None:
        self.safe_mode = enabled
        self.toggle_safe_action.setText(f"Safe mode: {'ON' if enabled else 'OFF'}")

    def browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            self.path_edit.setText(folder)

    def scan(self) -> None:
        target = Path(self.path_edit.text().strip())
        if not target.exists():
            QMessageBox.warning(self, "Invalid folder", f"Path does not exist: {target}")
            return

        files = iter_files(target, deep=True)
        cache = ScanCache(Path(".foxdup/cache.sqlite3"))
        try:
            groups = find_exact_duplicates(files, cache)
        finally:
            cache.close()

        self.paths.clear()
        self.table.setRowCount(0)
        for group in groups:
            for p in group.files:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(group.key))
                self.table.setItem(row, 1, QTableWidgetItem(str(group.total_size)))
                self.table.setItem(row, 2, QTableWidgetItem(str(p)))
                self.paths.append(p)

    def preview_current(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.paths):
            return
        path = self.paths[row]
        pix = QPixmap(str(path))
        if pix.isNull():
            self.preview.setText("No image preview available")
        elif self.safe_mode:
            self.preview.setText("Preview hidden in safe mode")
        else:
            self.preview.setPixmap(pix.scaled(420, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.meta.setText(str(path))


def run_gui() -> None:
    if QApplication is None:
        raise RuntimeError("PySide6 is required for GUI mode. Install dependency and try again.")
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
