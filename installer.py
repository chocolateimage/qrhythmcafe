import os
import sys
import zipfile
import yaml
import utils
import traceback
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QPixmap


class ImageWidget(QLabel):
    def __init__(self, parent, pixmap: QPixmap):
        super().__init__(parent)

        self.originalPixmap = pixmap
        self.setMinimumSize(1, 1)
        self.generatePixmap()

    def resizeEvent(self, a0):
        self.generatePixmap()
        return super().resizeEvent(a0)

    def generatePixmap(self):
        self.setPixmap(
            self.originalPixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class InstallWindow(QWidget):
    def __init__(self, file):
        super().__init__()

        self.setWindowTitle("Level Installer")
        self.resize(500, 200)

        if not os.path.exists(file):
            QMessageBox.critical(None, "File not found", f"File {file} was not found")
            sys.exit(1)

        try:
            self.zipfile = zipfile.ZipFile(file)
            # Load JSON as YAML as it is more lenient
            levelContents = yaml.safe_load(
                self.zipfile.read("main.rdlevel").decode().replace("\t", "    ")
            )
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(
                None, "Load error", "An error occured while loading the level data"
            )
            sys.exit(1)

        self.levelpath = utils.get_rd_level_folder(
            os.path.basename(self.zipfile.filename).split(".")[0]
        )

        self.vlay = QVBoxLayout(self)
        self.vlay.setContentsMargins(0, 0, 0, 0)
        self.vlay.setSpacing(0)

        try:
            previewImage = self.zipfile.read(levelContents["settings"]["previewImage"])
            previewPixmap = QPixmap()
            previewPixmap.loadFromData(previewImage)
        except Exception:
            previewPixmap = None

        if previewPixmap is not None and not previewPixmap.isNull():
            self.imageWidget = ImageWidget(self, previewPixmap)
            self.imageWidget.setFixedHeight(80)
            self.vlay.addWidget(self.imageWidget)

        self.innerLay = QVBoxLayout()
        self.innerLay.setContentsMargins(9, 9, 9, 9)
        self.innerLay.setSpacing(9)
        self.vlay.addLayout(self.innerLay, 1)

        self.messageLabel = QLabel(
            f"Do you want to install <b>{levelContents['settings']['song']}</b> created by <b>{levelContents['settings']['author']}</b>?",
            self,
        )
        self.messageLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.innerLay.addWidget(self.messageLabel)

        self.installButton = QPushButton("Install", self)
        self.installButton.clicked.connect(self.install)
        self.innerLay.addWidget(
            self.installButton, alignment=Qt.AlignmentFlag.AlignRight
        )

        if os.path.exists(self.levelpath):
            self.markInstalled()

    def markInstalled(self):
        self.installButton.setDisabled(True)
        self.installButton.setText("Installed")

    def install(self):
        self.zipfile.extractall(self.levelpath)
        self.markInstalled()
