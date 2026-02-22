#!/usr/bin/env python3

"""
Present Directory of Markdown on Corkboard Demostration
"""

import sys
from pathlib import Path
import textwrap

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QLabel,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsItem,
    QMenuBar,
    QStatusBar,
)


class CardItem(QGraphicsRectItem):
    def __init__(self, title: str, description: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRect(0, 0, 260, 160)
        self.setBrush(Qt.white)
        self.setPen(QColor("black"))  # or QPen(Qt.black)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setDefaultTextColor(Qt.black)
        self.title_item.setPos(8, 6)

        if description:
            wrapped = textwrap.fill(description, width=32)
            self.desc_item = QGraphicsTextItem(wrapped, self)
            self.desc_item.setDefaultTextColor(Qt.darkGray)
            self.desc_item.setPos(8, 40)


class CorkboardView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def add_card(self, title: str, description: str | None, pos):
        card = CardItem(title, description)
        card.setPos(pos)
        self.scene().addItem(card)


def parse_front_matter(path: Path):
    """Return (title, description) from YAML front matter if present, else (stem, None)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return path.stem, None

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return path.stem, None

    yaml_lines = []
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        yaml_lines.append(lines[i])
        i += 1

    title = None
    description = None

    for line in yaml_lines:
        stripped = line.strip()
        if stripped.startswith("title:") and title is None:
            title = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("description:") and description is None:
            description = stripped.split(":", 1)[1].strip().strip('"')

    if not title:
        title = path.stem

    return title, description


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Corkboard — Current Directory")
        self.resize(1200, 800)

        self.corkboard = CorkboardView()

        layout = QHBoxLayout()
        layout.addWidget(self.corkboard)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("File")

        reload_action = QAction("Reload Current Directory", self)
        reload_action.triggered.connect(self.load_current_directory)
        file_menu.addAction(reload_action)

        self.setMenuBar(menu_bar)
        self.setStatusBar(QStatusBar())

        self.load_current_directory()

    def load_current_directory(self):
        self.corkboard.scene().clear()
        cwd = Path.cwd()
        md_files = sorted(cwd.glob("*.md"))
        self.statusBar().showMessage(f"Loaded {len(md_files)} markdown files from {cwd}")

        col_width = 280
        row_height = 190
        cols = 4

        for idx, path in enumerate(md_files):
            title, desc = parse_front_matter(path)
            col = idx % cols
            row = idx // cols
            x = 20 + col * col_width
            y = 20 + row * row_height
            self.corkboard.add_card(title, desc, self.corkboard.mapToScene(x, y))


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
