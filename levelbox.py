import fancyframe
from PyQt6 import QtWidgets, uic, QtGui, QtCore
import threading
import os
import urllib.request
import utils
import flowlayout
import loading_spinner


class LevelBoxMetadata(QtWidgets.QPushButton):
    def __init__(self, icon, text, onclick=None, tooltip=None):
        super().__init__(" " + text)  # " " is a lazy way to fix icon spacing
        self.setFlat(True)

        self.setIcon(QtGui.QIcon(utils.get_icon_path(icon)))

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        if tooltip is not None:
            self.setToolTip(tooltip)
        if onclick is not None:
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.clicked.connect(onclick)


class LevelBoxTag(QtWidgets.QLabel):
    def __init__(self, text, onclick):
        super().__init__(text)
        self.setStyleSheet(
            "QLabel{background: rgba(128,128,128,0.2); padding: 2px 4px; border-radius: 8px;} QLabel:hover {background: rgba(128,128,128,0.4)}"
        )
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setWordWrap(True)
        self.onclick = onclick

    def mousePressEvent(self, eve):
        self.onclick()


class LevelBoxSeizureWarning(QtWidgets.QLabel):
    def __init__(self):
        super().__init__("⚠️ Seizure warning")
        self.setStyleSheet(
            "QLabel{background: rgb(252, 211, 77); color: rgba(27, 19, 6,0.8); padding: 2px 4px; border-radius: 8px;}"
        )
        self.setWordWrap(True)


class LevelBox(fancyframe.FancyFrame):
    def get_float_string(self, num):
        if int(num) == num:
            return str(int(num))
        else:
            return str(num)

    def __init__(self, data, mw):
        super().__init__()
        uic.loadUi("ui/levelbox.ui", self)

        self.labelArtist: QtWidgets.QLabel
        self.labelDifficulty: QtWidgets.QLabel
        self.labelId: QtWidgets.QLabel
        self.horizontalLayout: QtWidgets.QHBoxLayout

        self.data = data
        self.mw = mw
        self.isDestroyed = []
        if len(self.data["description"]) == 0:
            self.descriptionText: QtWidgets.QTextEdit = None
        else:
            self.descriptionText = QtWidgets.QTextEdit(self)
            self.descriptionText.setReadOnly(True)
            self.descriptionText.setMarkdown(self.data["description"])
            self.descriptionText.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.descriptionText.setStyleSheet(
                "QTextEdit {background: rgba(0,0,0,0.8); border-top-left-radius: 8px; border-top-right-radius: 8px; color: white;font-size: 14px;}"
            )
            self.descriptionText.setFixedSize(self.thumbnail.minimumSize())
            self.descriptionText.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
                | QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.descriptionOpacityEffect = QtWidgets.QGraphicsOpacityEffect(
                self.descriptionText
            )
            self.descriptionOpacityEffect.setOpacity(0)
            self.descriptionOpacityAnimation = QtCore.QPropertyAnimation(
                self.descriptionOpacityEffect,
                "opacity".encode(),  # Don't ask me why I need to encode a property name...
                self.descriptionOpacityEffect,
            )
            self.descriptionOpacityAnimation.setStartValue(0)
            self.descriptionOpacityAnimation.setEndValue(1)
            self.descriptionOpacityAnimation.setDuration(100)
            self.descriptionText.setGraphicsEffect(self.descriptionOpacityEffect)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)
        self.destroyed.connect(
            lambda: self.isDestroyed.append(True)
        )  # extremely hacky way
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layoutMetadata = flowlayout.FlowLayout(self.widgetMetadata, 0, 0, 0)
        self.layoutMetadata.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layoutMetadata.setContentsMargins(8, 0, 8, 0)
        self.layoutTags = flowlayout.FlowLayout(self.widgetTags, 0, 4, 4)
        self.layoutTags.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layoutTags.setContentsMargins(8, 0, 8, 0)
        self.bottompart.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.labelId.setText(self.data["id"])
        self.labelId.setStyleSheet("color: rgba(128,128,128,0.4)")
        self.labelSong.setText(self.data["song"])
        self.labelArtist.setText(self.data["artist"])
        opacityEffect = QtWidgets.QGraphicsOpacityEffect(self.labelArtist)
        opacityEffect.setOpacity(0.7)
        self.labelArtist.setGraphicsEffect(opacityEffect)
        self.labelDifficulty.setText(
            ["Easy", "Medium", "Tough", "Very Tough"][self.data["difficulty"]]
        )
        self.labelDifficulty.setStyleSheet(
            "padding: 2px 4px 2px 10px; font-weight: 500;"
        )
        self.labelDifficulty.installEventFilter(self)

        self.horizontalLayout.setAlignment(
            self.labelDifficulty, QtCore.Qt.AlignmentFlag.AlignTop
        )

        QtCore.QTimer.singleShot(10, self.start_load_extra)

        for i in self.data["authors"]:
            self.add_author(i)
        bpmtext = (
            self.get_float_string(self.data["min_bpm"])
            + "-"
            + self.get_float_string(self.data["max_bpm"])
        )
        if self.data["min_bpm"] == self.data["max_bpm"]:
            bpmtext = self.get_float_string(self.data["min_bpm"])
        self.add_metadata("heart", bpmtext + " BPM")
        if self.data["approval"] == -1:
            self.add_metadata(
                "x",
                "Non-Referred",
                tooltip="Non-Referred: a trusted member of the community has checked for correct\nBPM/offset, metadata, and cues to ensure playability, and has found that this level\ndoes not meet standards.",
            )
        elif self.data["approval"] >= 10:
            self.add_metadata(
                "checkmark",
                "Reviewed",
                onclick=lambda: self.change_facet_approval(True),
                tooltip="Peer-Reviewed: a trusted member of the community has checked for correct\nBPM/offset, metadata, and cues to ensure playability.",
            )
        if self.data["seizure_warning"]:
            self.layoutTags.addWidget(LevelBoxSeizureWarning())
        for i in self.data["tags"]:
            self.add_tag(i)
        self.btnDownload: (
            QtWidgets.QPushButton
        )  # just for allowing auto complete in vs code
        self.btnDownload.setFixedSize(38, 38)
        self.btnDownload.clicked.connect(self.download_click)
        self.update_download_button()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent):
        if watched == self.labelDifficulty:
            if isinstance(event, QtGui.QPaintEvent):
                difficultycolor = [
                    QtGui.QColor(13, 148, 136, 130),
                    QtGui.QColor(217, 119, 6, 130),
                    QtGui.QColor(244, 63, 94, 130),
                    QtGui.QColor(139, 92, 246, 130),
                ][self.data["difficulty"]]
                p = QtGui.QPainter(self.labelDifficulty)

                poly = QtGui.QPolygonF()
                poly.append(QtCore.QPointF(0, 0))
                poly.append(
                    QtCore.QPointF(
                        self.labelDifficulty.height() / 2, self.labelDifficulty.height()
                    )
                )
                poly.append(
                    QtCore.QPointF(
                        self.labelDifficulty.width(), self.labelDifficulty.height()
                    )
                )
                poly.append(QtCore.QPointF(self.labelDifficulty.width(), 0))

                path = QtGui.QPainterPath()
                path.addPolygon(poly)

                p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                p.fillPath(path, difficultycolor)
        return super().eventFilter(watched, event)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        if self.descriptionText is not None:
            self.descriptionOpacityAnimation.setDirection(
                QtCore.QPropertyAnimation.Direction.Forward
            )
            self.descriptionOpacityAnimation.start()
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if self.descriptionText is not None:
            self.descriptionOpacityAnimation.setDirection(
                QtCore.QPropertyAnimation.Direction.Backward
            )
            self.descriptionOpacityAnimation.start()
        return super().leaveEvent(a0)

    def change_facet_approval(self, onlyreviewed):
        self.mw.shareddata["onlyreviewed"] = onlyreviewed
        self.mw.reloadLevels()

    def change_facet_author(self, author):
        if author not in self.mw.shareddata["facet"]["authors"]:
            self.mw.shareddata["facet"]["authors"].append(author)
            self.mw.reloadLevels()

    def change_facet_tag(self, tag):
        if tag not in self.mw.shareddata["facet"]["tags"]:
            self.mw.shareddata["facet"]["tags"].append(tag)
            self.mw.reloadLevels()

    def add_metadata(self, icon, text, onclick=None, tooltip=None):
        self.layoutMetadata.addWidget(
            LevelBoxMetadata(icon, text, tooltip=tooltip, onclick=onclick)
        )

    def add_tag(self, text):
        self.layoutTags.addWidget(
            LevelBoxTag(text, lambda: self.change_facet_tag(text))
        )

    def add_author(self, author):
        self.add_metadata(
            "user",
            author,
            onclick=lambda: self.change_facet_author(author),
        )

    def start_load_extra(self):
        threading.Thread(target=self.load_extra).start()

    def load_extra(self):
        filepath = utils.get_temp_folder() + "/" + self.data["id"] + ".png"
        if not os.path.exists(filepath):
            urllib.request.urlretrieve(self.data["image"], filepath)

        if len(self.isDestroyed) > 0:
            return

        thumbnailtext: QtWidgets.QLabel = self.thumbnail
        pixmap = QtGui.QPixmap(filepath).scaled(
            thumbnailtext.width(),
            thumbnailtext.height(),
            transformMode=QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        final_pixmap = QtGui.QPixmap(pixmap.width(), pixmap.height())
        final_pixmap.fill(QtGui.QColor(255, 255, 255, 0))
        with QtGui.QPainter(final_pixmap) as painter:
            path = QtGui.QPainterPath()
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            path.addRoundedRect(0, 0, final_pixmap.width(), final_pixmap.height(), 8, 8)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.setClipping(False)
            painter.drawPixmap(
                0, 32, pixmap.copy(0, 32, pixmap.width(), pixmap.height() - 32)
            )

        thumbnailtext.setText("")
        thumbnailtext.setPixmap(final_pixmap)

    def update_download_button(self):
        QtCore.QTimer.singleShot(0, self.update_download_button_)

    def update_download_button_(self):
        if self.is_installed():
            self.lblInstalled.setVisible(True)
            self.btnDownload.setToolTip("Uninstall")
            if QtGui.QIcon.hasThemeIcon("user-trash-full-symbolic"):
                self.btnDownload.setIcon(
                    QtGui.QIcon.fromTheme("user-trash-full-symbolic")
                )
            else:
                self.btnDownload.setIcon(QtGui.QIcon(utils.get_icon_path("trash")))
            self.bgcolor = "green"
        else:
            self.lblInstalled.setVisible(False)
            self.btnDownload.setToolTip("Install")
            if QtGui.QIcon.hasThemeIcon("download"):
                self.btnDownload.setIcon(QtGui.QIcon.fromTheme("download"))
            elif QtGui.QIcon.hasThemeIcon("folder-download-symbolic"):
                self.btnDownload.setIcon(
                    QtGui.QIcon.fromTheme("folder-download-symbolic")
                )
            else:
                self.btnDownload.setIcon(QtGui.QIcon(utils.get_icon_path("download")))
            self.bgcolor = None
        self.repaint()

    def is_installed(self):
        return utils.get_available_rd_level_name(self.data) is not None

    def download_click(self):
        self.loading_spinner = loading_spinner.LoadingSpinner(self.btnDownload)
        self.loading_spinner.setContentsMargins(6, 6, 0, 0)
        self.loading_spinner.show()
        self.labelId.setFocus()
        self.btnDownload.setDisabled(True)
        if self.is_installed():
            threading.Thread(target=self._remove).start()
        else:
            threading.Thread(target=self._download).start()

    def _remove(self):
        utils.remove_rd_level(self.data)

        self.loading_spinner.deleteLater()
        self.update_download_button()
        self.btnDownload.setDisabled(False)

    def _download(self):
        utils.download_rd_level(self.data)
        if len(self.isDestroyed) > 0:
            print("download finished and levelbox is destroyed")
            return
        self.loading_spinner.deleteLater()
        self.update_download_button()
        self.btnDownload.setDisabled(False)
