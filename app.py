import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QLabel, QPushButton, 
                             QVBoxLayout, QWidget, QFileDialog, QListWidget, QProgressBar,
                             QHBoxLayout, QFrame, QScrollArea, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

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
        self.completed_images = []
        self.scale_factor = 1.0

        self.load_state()  # Load state from file if exists
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
        self.layout = QHBoxLayout(self.central_widget)

        # Left side layout for image display and controls
        left_layout = QVBoxLayout()

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        # Image display with scroll area for zoom functionality
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        left_layout.addWidget(self.scroll_area)

        # Label display widget
        self.label_display = QLineEdit(self)
        # self.label_display.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label_display)

        # Submit button to save the updated label
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_label)
        left_layout.addWidget(self.submit_button)

        # OK and Not OK counter display widget
        counter_frame = QFrame(self)
        counter_layout = QHBoxLayout()
        counter_frame.setLayout(counter_layout)
        counter_frame.setFrameShape(QFrame.StyledPanel)
        self.ok_count_label = QLabel(f"OK: {self.ok_count}", self)
        self.not_ok_count_label = QLabel(f"Not OK: {self.not_ok_count}", self)
        counter_layout.addWidget(self.ok_count_label)
        counter_layout.addWidget(self.not_ok_count_label)
        left_layout.addWidget(counter_frame)

        # Zoom buttons layout
        zoom_buttons_layout = QHBoxLayout()
        self.zoom_out_button = QPushButton("Zoom Out", self)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_buttons_layout.addWidget(self.zoom_out_button)
        
        self.zoom_in_button = QPushButton("Zoom In", self)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_buttons_layout.addWidget(self.zoom_in_button)
        left_layout.addLayout(zoom_buttons_layout)

        # Navigation buttons (Previous and Next side by side)
        nav_buttons_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Image", self)
        self.prev_button.clicked.connect(self.prev_image)
        nav_buttons_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Image", self)
        self.next_button.clicked.connect(self.next_image)
        nav_buttons_layout.addWidget(self.next_button)
        left_layout.addLayout(nav_buttons_layout)

        # OK and Not OK buttons (side by side)
        action_buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.increment_ok)
        action_buttons_layout.addWidget(self.ok_button)

        self.not_ok_button = QPushButton("Not OK", self)
        self.not_ok_button.clicked.connect(self.increment_not_ok)
        action_buttons_layout.addWidget(self.not_ok_button)
        left_layout.addLayout(action_buttons_layout)

        self.layout.addLayout(left_layout)

        # Right side layout for image list
        self.image_list = QListWidget(self)
        self.image_list.setFixedWidth(150)
        self.image_list.itemClicked.connect(self.select_image)
        self.layout.addWidget(self.image_list)

        self.update_image_list()  # Update the list with previously loaded images

    def load_state(self):
        try:
            with open('state.json', 'r') as file:
                state = json.load(file)
                self.ok_count = state.get('ok_count', 0)
                self.not_ok_count = state.get('not_ok_count', 0)
                self.completed_images = state.get('completed_images', [])
                self.image_paths = state.get('image_paths', [])
                self.current_index = state.get('current_index', 0)
        except FileNotFoundError:
            pass  # File not found, just start fresh
        except json.JSONDecodeError:
            pass  # Error reading JSON, just start fresh

    def save_state(self):
        state = {
            'ok_count': self.ok_count,
            'not_ok_count': self.not_ok_count,
            'completed_images': self.completed_images,
            'image_paths': self.image_paths,
            'current_index': self.current_index,
        }
        with open('state.json', 'w') as file:
            json.dump(state, file)

    def closeEvent(self, event):
        self.save_state()  # Save state when closing
        event.accept()  # Accept the event

    def open_image_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.image_paths = [os.path.join(directory, f) for f in os.listdir(directory)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.image_list.clear()
            self.image_list.addItems([os.path.basename(img) for img in self.image_paths])
            self.update_image_list()  # Mark previously completed images
            self.load_image()
            self.update_progress_bar()

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
            self.image_label.setPixmap(pixmap.scaled(int(600 * self.scale_factor), 
                                                    int(400 * self.scale_factor), 
                                                    aspectRatioMode=Qt.KeepAspectRatio))
            self.update_progress_bar()  # Update progress bar after loading the image

    def load_label(self):
        if self.image_paths:
            image_name = os.path.basename(self.image_paths[self.current_index])
            label_name = image_name[:-4]  # Remove the image extension to match the label filename
            label_text = self.labels.get(label_name, "")
            self.label_display.setText(label_text)  # Update the label display widget

    # def load_label(self):
    #     if self.image_paths:
    #         image_name = os.path.basename(self.image_paths[self.current_index])
    #         label_name = image_name[:-4]  # Remove the image extension to match the label filename
    #         label_text = self.labels.get(label_name, "")  # Get the label, default to empty if not found
    #         self.label_edit.setText(label_text)  # Set the text in the editable field


    def next_image(self):
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_image()
            self.load_label()  # Load corresponding label after loading image

    def prev_image(self):
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.load_image()
            self.load_label()  # Load corresponding label after loading image


    def select_image(self, item):
        self.current_index = self.image_list.currentRow()
        self.load_image()

    def increment_ok(self):
        self.ok_count += 1
        self.update_count_display()
        self.mark_image_completed()  # Mark the image as completed
        self.next_image()  # Go to the next image after pressing OK

    def increment_not_ok(self):
        self.not_ok_count += 1
        self.update_count_display()
        self.mark_image_completed()  # Mark the image as completed
        self.next_image()  # Go to the next image after pressing Not OK

    def update_count_display(self):
        self.ok_count_label.setText(f"OK: {self.ok_count}")
        self.not_ok_count_label.setText(f"Not OK: {self.not_ok_count}")

    def update_progress_bar(self):
        total_images = len(self.image_paths)
        completed = self.ok_count + self.not_ok_count
        self.progress_bar.setMaximum(total_images)
        self.progress_bar.setValue(completed)

    def mark_image_completed(self):
        item = self.image_list.item(self.current_index)
        if item:
            item.setCheckState(2)  # Check the item (mark as completed)
            self.completed_images.append(os.path.basename(self.image_paths[self.current_index]))
            self.update_image_list()  # Update the image list to reflect completed state

    def update_image_list(self):
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if os.path.basename(self.image_paths[i]) in self.completed_images:
                item.setCheckState(2)  # Check the item if completed
            else:
                item.setCheckState(0)  # Uncheck the item if not completed

    def zoom_in(self):
        self.scale_factor *= 1.1  # Increase scale factor for zoom in
        self.load_image()  # Reload image with the new scale

    def zoom_out(self):
        self.scale_factor /= 1.1  # Decrease scale factor for zoom out
        self.load_image()  # Reload image with the new scale

    # def submit_label(self):
    #     if self.image_paths and self.labels_path:
    #         image_name = os.path.basename(self.image_paths[self.current_index])
    #         label_name = image_name[:-4]  # Remove the image extension to get the label name

    #         # Get the new label from the QLineEdit
    #         new_label = self.label_edit.text()

    #         # Update the label dictionary
    #         self.labels[label_name] = new_label

    #         # Write the updated label back to the corresponding file in the labels path
    #         label_file_path = os.path.join(self.labels_path, label_name + '.txt')
    #         with open(label_file_path, 'w') as file:
    #             file.write(new_label)

    #         # Optionally, show a message that the label was saved
    #         QMessageBox.information(self, "Success", f"Label for {image_name} updated successfully!")

    def open_labels_path(self):
        # Open a file dialog to select the labels directory
        self.labels_path = QFileDialog.getExistingDirectory(self, "Select Labels Directory")
        
        # Optionally, load existing labels from the directory
        if self.labels_path:
            self.load_labels()

    def load_labels(self):
        self.labels = {}
        for filename in os.listdir(self.labels_path):
            if filename.endswith(".txt"):
                label_name = filename[:-4]  # Remove .txt extension
                with open(os.path.join(self.labels_path, filename), 'r') as file:
                    self.labels[label_name] = file.read().strip()
    
    def open_labels_path(self):
        # Open a file dialog to select the labels directory
        self.labels_path = QFileDialog.getExistingDirectory(self, "Select Labels Directory")
        
        # Load existing labels from the directory
        if self.labels_path:
            self.load_labels()

    def load_labels(self):
        self.labels = {}
        for filename in os.listdir(self.labels_path):
            if filename.endswith(".txt"):
                label_name = filename[:-4]  # Remove .txt extension
                with open(os.path.join(self.labels_path, filename), 'r') as file:
                    self.labels[label_name] = file.read().strip()
    
    def submit_label(self):
        if self.image_paths and self.labels_path:
            image_name = os.path.basename(self.image_paths[self.current_index])
            label_name = image_name[:-4]  # Remove the image extension to get the label name

            # Get the new label from the QLineEdit
            new_label = self.label_display.text()

            # Update the label dictionary
            self.labels[label_name] = new_label

            # Write the updated label back to the corresponding file in the labels path
            label_file_path = os.path.join(self.labels_path, label_name + '.txt')
            with open(label_file_path, 'w') as file:
                file.write(new_label)

            # Optionally, show a message that the label was saved
            # QMessageBox.information(self, "Success", f"Label for {image_name} updated successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageLabeler()
    window.show()
    sys.exit(app.exec_())
