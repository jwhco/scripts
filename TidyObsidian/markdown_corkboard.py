import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
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
    def __init__(self, note_path: Path, title: str, metadata: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRect(0, 0, 220, 140)
        self.setBrush(Qt.white)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.note_path = note_path

        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setDefaultTextColor(Qt.black)
        self.title_item.setPos(6, 4)

        self.meta_item = QGraphicsTextItem(metadata, self)
        self.meta_item.setDefaultTextColor(Qt.darkGray)
        self.meta_item.setPos(6, 32)


class CorkboardView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def add_card(self, note_path: Path, title: str, metadata: str, pos=None):
        card = CardItem(note_path, title, metadata)
        if pos is None:
            pos = self.scene().sceneRect().bottomRight()
            if pos.isNull():
                pos = self.mapToScene(self.viewport().rect().center())
        card.setPos(pos)
        self.scene().addItem(card)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Corkboard Prototype")
        self.resize(1200, 800)

        self.current_folder: Path | None = None

        # Left panel: list + metadata preview
        self.folder_list = QListWidget()
        self.folder_list.setMinimumWidth(260)
        self.folder_list.itemSelectionChanged.connect(self.on_note_selected)

        self.meta_label = QLabel("Select a note to see metadata here.")
        self.meta_label.setWordWrap(True)

        self.corkboard = CorkboardView()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Notes"))
        left_layout.addWidget(self.folder_list)
        left_layout.addWidget(QLabel("Metadata preview"))
        left_layout.addWidget(self.meta_label)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        central_layout = QHBoxLayout()
        central_layout.addWidget(left_widget)
        central_layout.addWidget(self.corkboard, 1)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Menu
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Markdown Folder", self)
        open_action.triggered.connect(self.choose_folder)
        file_menu.addAction(open_action)

        self.setMenuBar(menu_bar)
        self.setStatusBar(QStatusBar())

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Markdown Folder")
        if not folder:
            return
        self.current_folder = Path(folder)
        self.statusBar().showMessage(f"Folder: {self.current_folder}")
        self.load_notes()

    def load_notes(self):
        self.folder_list.clear()
        self.corkboard.scene().clear()

        if not self.current_folder:
            return

        # Very simple grid layout for cards
        index = 0
        for path in sorted(self.current_folder.glob("*.md")):
            title = path.stem
            metadata = self.extract_metadata(path)

            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, path)
            self.folder_list.addItem(item)

            col = index % 3
            row = index // 3
            x = 40 + col * 240
            y = 40 + row * 160
            self.corkboard.add_card(path, title, metadata, self.corkboard.mapToScene(x, y))
            index += 1

    def extract_metadata(self, path: Path) -> str:
        # Simple metadata: first non-empty line after optional YAML front matter
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return ""

        lines = text.splitlines()
        i = 0

        # Skip YAML front matter if present
        if lines and lines[0].strip() == "---":
            i += 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            i += 1

        for j in range(i, len(lines)):
            if lines[j].strip():
                preview = lines[j].strip()
                if len(preview) > 120:
                    preview = preview[:117] + "..."
                return preview
        return ""

    def on_note_selected(self):
        items = self.folder_list.selectedItems()
        if not items:
            return
        item = items[0]
        path = item.data(Qt.UserRole)
        metadata = self.extract_metadata(path)
        self.meta_label.setText(f"File: {path.name}\nPreview: {metadata}")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
