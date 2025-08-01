import os
import sys
import zipfile
import yaml
import utils
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox


class InstallWindow(QWidget):
    def __init__(self, file):
        super().__init__()

        self.setWindowTitle("Level Installer")
        self.resize(500, 150)

        if not os.path.exists(file):
            QMessageBox.critical(None, "File not found", f"File {file} was not found")
            sys.exit(1)

        self.zipfile = zipfile.ZipFile(file)
        # Load JSON as YAML as it is more lenient
        levelContents = yaml.safe_load(
            self.zipfile.read("main.rdlevel").decode().replace("\t", "    ")
        )

        self.levelpath = utils.get_rd_level_folder(
            os.path.basename(self.zipfile.filename).split(".")[0]
        )

        self.vlay = QVBoxLayout(self)

        self.messageLabel = QLabel(
            f"Do you want to install {levelContents['settings']['song']} created by {levelContents['settings']['author']}?",
            self,
        )
        self.messageLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vlay.addWidget(self.messageLabel)

        self.installButton = QPushButton("Install", self)
        self.installButton.clicked.connect(self.install)
        self.vlay.addWidget(self.installButton, alignment=Qt.AlignmentFlag.AlignRight)

        if os.path.exists(self.levelpath):
            self.markInstalled()

    def markInstalled(self):
        self.installButton.setDisabled(True)
        self.installButton.setText("Installed")

    def install(self):
        self.zipfile.extractall(self.levelpath)
        self.markInstalled()
