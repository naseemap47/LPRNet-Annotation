import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
                             QAction, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog)
from PyQt5.QtGui import QPixmap

class ImageLabeler(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Labeler")
        self.setGeometry(100, 100, 800, 600)

        self.image_paths = []
        self.labels = {}
        self.current_index = 0
        self.ok_count = 0
        self.not_ok_count = 0

        self.init_ui()

    def init_ui(self):
        # Menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Files")

        open_images_action = QAction("Open Image Directory", self)
        open_images_action.triggered.connect(self.open_image_directory)
        file_menu.addAction(open_images_action)

        open_labels_action = QAction("Open Labels Path", self)
        open_labels_action.triggered.connect(self.open_labels_path)
        file_menu.addAction(open_labels_action)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Image display
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Label display
        self.label_display = QLabel(self)
        self.layout.addWidget(self.label_display)

        # Navigation buttons
        self.prev_button = QPushButton("Previous Image", self)
        self.prev_button.clicked.connect(self.prev_image)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Image", self)
        self.next_button.clicked.connect(self.next_image)
        self.layout.addWidget(self.next_button)

        # OK and Not OK buttons
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.increment_ok)
        self.layout.addWidget(self.ok_button)

        self.not_ok_button = QPushButton("Not OK", self)
        self.not_ok_button.clicked.connect(self.increment_not_ok)
        self.layout.addWidget(self.not_ok_button)

        # Count display
        self.count_display = QLabel(f"OK: {self.ok_count} | Not OK: {self.not_ok_count}", self)
        self.layout.addWidget(self.count_display)

    def open_image_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.image_paths = [os.path.join(directory, f) for f in os.listdir(directory)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_index = 0
            self.load_image()

    def open_labels_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Labels Directory")
        if path:
            self.labels = {}
            for filename in os.listdir(path):
                if filename.lower().endswith('.txt'):
                    with open(os.path.join(path, filename), 'r') as file:
                        self.labels[filename[:-4]] = file.read().strip()
            self.load_label()

    def load_image(self):
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_index])
            self.image_label.setPixmap(pixmap.scaled(600, 400, aspectRatioMode=True))
            self.load_label()

    def load_label(self):
        image_name = os.path.basename(self.image_paths[self.current_index])
        label_name = image_name[:-4]  # Remove extension
        self.label_display.setText(self.labels.get(label_name, "No label found"))

    def next_image(self):
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_image()

    def prev_image(self):
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def increment_ok(self):
        self.ok_count += 1
        self.update_count_display()

    def increment_not_ok(self):
        self.not_ok_count += 1
        self.update_count_display()

    def update_count_display(self):
        self.count_display.setText(f"OK: {self.ok_count} | Not OK: {self.not_ok_count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())
