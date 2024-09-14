import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QWidget, QAction, QMenuBar, QHBoxLayout, QListWidget, QListWidgetItem, QSplitter, QProgressBar
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageLabelingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_dir = None
        self.label_dir = None
        self.image_list = []
        self.current_image_index = 0
        self.completed_images = set()  # Set to keep track of completed images

        self.initUI()

    def initUI(self):
        # Set window title and size
        self.setWindowTitle("Image Labeling App")
        self.setGeometry(100, 100, 1000, 600)

        # Create Menu Bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Files')

        # Add Open Image Directory action
        open_image_dir_action = QAction('Open Image Directory', self)
        open_image_dir_action.triggered.connect(self.open_image_directory)
        fileMenu.addAction(open_image_dir_action)

        # Add Open Labels Directory action
        open_label_dir_action = QAction('Open Labels Path', self)
        open_label_dir_action.triggered.connect(self.open_label_directory)
        fileMenu.addAction(open_label_dir_action)

        # Main layout (using QVBoxLayout for the overall layout)
        main_layout = QVBoxLayout()

        # Create a top layout for the completion label and progress bar
        top_layout = QHBoxLayout()

        # Completion label (e.g., "3/10 images labeled")
        self.completion_label = QLabel("0/0 images labeled", self)
        top_layout.addWidget(self.completion_label)

        # Add Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        top_layout.addWidget(self.progress_bar)

        main_layout.addLayout(top_layout)

        # Create a QSplitter for separating the image display and the list of images
        splitter = QSplitter()

        # Right side layout (Image display, text field, and buttons)
        right_layout = QVBoxLayout()

        # Image label (to show the image)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.image_label)

        # Text field for image description
        self.text_field = QLineEdit(self)
        right_layout.addWidget(self.text_field)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton('Previous', self)
        self.prev_button.clicked.connect(self.show_previous_image)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.show_next_image)
        nav_layout.addWidget(self.next_button)

        right_layout.addLayout(nav_layout)

        # Submit button
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.save_label)
        right_layout.addWidget(self.submit_button)

        # Delete button
        self.delete_button = QPushButton('Delete Image', self)
        self.delete_button.clicked.connect(self.delete_current_image)
        right_layout.addWidget(self.delete_button)

        # Add right layout to a widget and then to the splitter
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Image list (moved to the right side)
        self.image_list_widget = QListWidget()
        self.image_list_widget.clicked.connect(self.on_image_list_click)
        splitter.addWidget(self.image_list_widget)

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_image_directory(self):
        # Open a file dialog to select the image directory
        self.image_dir = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if self.image_dir:
            self.image_list = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.current_image_index = 0
            self.load_image_list()
            self.show_image()
            self.update_progress()  # Update the progress bar and label after loading images

    def open_label_directory(self):
        # Open a file dialog to select the labels directory
        self.label_dir = QFileDialog.getExistingDirectory(self, "Select Labels Path")
        if self.label_dir:
            self.load_image_list()  # Load the image list with the updated labels path
            self.update_progress()  # Update progress based on loaded labels

    def load_image_list(self):
        """Load the images into the QListWidget and check their label status."""
        self.image_list_widget.clear()
        for image_name in self.image_list:
            item = QListWidgetItem(image_name)
            self.image_list_widget.addItem(item)
            self.update_image_item_status(item, image_name)

    def update_image_item_status(self, item, image_name):
        """Update the QListWidgetItem status with a tick if the label is completed."""
        if self.label_dir:
            label_path = os.path.join(self.label_dir, f"{os.path.splitext(image_name)[0]}.txt")
            if os.path.exists(label_path):
                item.setCheckState(Qt.Checked)
                self.completed_images.add(image_name)
            else:
                item.setCheckState(Qt.Unchecked)

    def show_image(self):
        # Display the current image
        if self.image_list:
            image_path = os.path.join(self.image_dir, self.image_list[self.current_image_index])
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

            # Clear the text field before loading any previous label
            self.text_field.setText('')

            # Load label if exists
            self.load_label_if_exists()

    def load_label_if_exists(self):
        """Load the label for the current image if it exists."""
        if self.label_dir and self.image_list:
            image_name = os.path.splitext(self.image_list[self.current_image_index])[0]
            label_path = os.path.join(self.label_dir, f"{image_name}.txt")
            if os.path.exists(label_path):
                with open(label_path, 'r') as label_file:
                    label_text = label_file.read()
                    self.text_field.setText(label_text)

    def show_next_image(self):
        # Show the next image in the directory
        if self.image_list and self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.image_list_widget.setCurrentRow(self.current_image_index)
            self.show_image()

    def show_previous_image(self):
        # Show the previous image in the directory
        if self.image_list and self.current_image_index > 0:
            self.current_image_index -= 1
            self.image_list_widget.setCurrentRow(self.current_image_index)
            self.show_image()

    def on_image_list_click(self):
        """Handle image selection from the list."""
        self.current_image_index = self.image_list_widget.currentRow()
        self.show_image()

    def save_label(self):
        # Save the label in the label path with the same name as the image
        if self.label_dir and self.image_list:
            image_name = os.path.splitext(self.image_list[self.current_image_index])[0]
            label_path = os.path.join(self.label_dir, f"{image_name}.txt")
            with open(label_path, 'w') as label_file:
                label_file.write(self.text_field.text())

            # Mark the image as completed in the list
            current_item = self.image_list_widget.item(self.current_image_index)
            self.update_image_item_status(current_item, self.image_list[self.current_image_index])

            # Update progress bar and completion label
            self.update_progress()

    def delete_current_image(self):
        """Delete the current image from the directory and remove it from the list."""
        if self.image_list and self.image_dir:
            image_name = self.image_list[self.current_image_index]
            image_path = os.path.join(self.image_dir, image_name)

            # Confirm the file exists and delete it
            if os.path.exists(image_path):
                os.remove(image_path)

                # Remove the corresponding label file if it exists
                if self.label_dir:
                    label_path = os.path.join(self.label_dir, f"{os.path.splitext(image_name)[0]}.txt")
                    if os.path.exists(label_path):
                        os.remove(label_path)

                # Remove the image from the list
                self.image_list.pop(self.current_image_index)
                self.image_list_widget.takeItem(self.current_image_index)

                # Reset the current image index if needed
                if self.current_image_index >= len(self.image_list):
                    self.current_image_index = len(self.image_list) - 1

                # Update the displayed image
                if self.image_list:
                    self.show_image()
                else:
                    self.image_label.clear()  # Clear the image display if no images are left

                # Update progress bar and completion label
                self.update_progress()

    def update_progress(self):
        """Update the progress bar and completion label based on the number of completed images."""
        total_images = len(self.image_list)
        completed_images = len(self.completed_images)

        if ((total_images > 0) and (completed_images > 0)):
            progress = int((completed_images / total_images) * 100)
            self.progress_bar.setValue(progress)
            self.completion_label.setText(f"{completed_images}/{total_images} images labeled")
        else:
            self.progress_bar.setValue(0)
            self.completion_label.setText("0/0 images labeled")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageLabelingApp()
    ex.show()
    sys.exit(app.exec_())
