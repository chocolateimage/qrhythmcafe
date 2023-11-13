import fancyframe
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import threading
import os
import urllib.request
import utils
import flowlayout

class LevelBoxMetadata(QtWidgets.QPushButton):
    def __init__(self,icon,text,onclick=None,tooltip=None):
        super().__init__(" " + text) # " " is a lazy way to fix icon spacing
        self.setFlat(True)
        self.setIcon(QtGui.QIcon(icon))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        if tooltip != None:
            self.setToolTip(tooltip)
        if onclick != None:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.clicked.connect(onclick)

class LevelBoxTag(QtWidgets.QLabel):
    def __init__(self,text,onclick):
        super().__init__(text)
        self.setStyleSheet("QLabel{background: rgba(128,128,128,0.2); padding: 2px 4px; border-radius: 8px;} QLabel:hover {background: rgba(128,128,128,0.4)}")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setWordWrap(True)
        self.onclick = onclick
    def mousePressEvent(self,eve):
        self.onclick()

class LevelBoxSeizureWarning(QtWidgets.QLabel):
    def __init__(self):
        super().__init__("⚠️ Seizure warning")
        self.setStyleSheet("QLabel{background: rgb(252, 211, 77); color: rgba(27, 19, 6,0.8); padding: 2px 4px; border-radius: 8px;}")
        self.setWordWrap(True)


class LevelBox(fancyframe.FancyFrame):
    def get_float_string(self,num):
        if int(num) == num:
            return str(int(num))
        else:
            return str(num)
    def __init__(self,data,mw):
        super().__init__()
        uic.loadUi("ui/levelbox.ui",self)
        self.data = data
        self.mw = mw
        self.isDestroyed = []
        self.destroyed.connect(lambda: self.isDestroyed.append(True)) # extremely hacky way
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.layoutMetadata = flowlayout.FlowLayout(self.widgetMetadata,0,0,0)
        self.layoutMetadata.setAlignment(QtCore.Qt.AlignTop)
        self.layoutTags = flowlayout.FlowLayout(self.widgetTags,0,4,4)
        self.layoutTags.setAlignment(QtCore.Qt.AlignTop)
        self.bottompart.layout().setAlignment(QtCore.Qt.AlignTop)
        self.labelId.setText(self.data["id"])
        self.labelId.setStyleSheet("color: rgba(128,128,128,0.4)")
        self.labelSong.setText(self.data["song"])
        self.labelArtist.setText(self.data["artist"])
        self.labelDifficulty.setText(["Easy","Medium","Tough","Very Tough"][self.data["difficulty"]])
        difficultycolor = [
            "13, 148, 136, 0.3",
            "217, 119, 6, 0.3",
            "244, 63, 94, 0.3",
            "139, 92, 246, 0.3",
        ][self.data["difficulty"]]
        self.labelDifficulty.setStyleSheet("background-color: rgba("+difficultycolor+");padding: 2px 4px;")
        threading.Thread(target=self.load_extra).start()
        for i in self.data["authors"]:
            self.add_author(i)
        bpmtext = self.get_float_string(self.data["min_bpm"]) + "-" + self.get_float_string(self.data["max_bpm"])
        if self.data["min_bpm"] == self.data["max_bpm"]:
            bpmtext = self.get_float_string(self.data["min_bpm"])
        self.add_metadata("ui/heart-solid.svg",bpmtext + " BPM")
        if self.data["approval"] == -1:
            self.add_metadata("ui/x.svg","Non-Referred",tooltip="Non-Referred: a trusted member of the community has checked for correct\nBPM/offset, metadata, and cues to ensure playability, and has found that this level\ndoes not meet standards.")
        elif self.data["approval"] >= 10:
            self.add_metadata("ui/checkmark.svg","Reviewed",onclick=lambda: self.change_facet_approval(True),tooltip="Peer-Reviewed: a trusted member of the community has checked for correct\nBPM/offset, metadata, and cues to ensure playability.")
        if self.data["seizure_warning"]:
            self.layoutTags.addWidget(LevelBoxSeizureWarning())
        for i in self.data["tags"]:
            self.add_tag(i)
        self.btnDownload: QtWidgets.QPushButton = self.btnDownload # just for allowing auto complete in vs code
        self.btnDownload.clicked.connect(self.download_click)
        self.update_download_button()
    def change_facet_approval(self,onlyreviewed):
        self.mw.shareddata["onlyreviewed"] = onlyreviewed
        self.mw.reloadLevels()
    def change_facet_author(self,author):
        if author not in self.mw.shareddata["facet"]["authors"]:
            self.mw.shareddata["facet"]["authors"].append(author)
            self.mw.reloadLevels()
    def change_facet_tag(self,tag):
        if tag not in self.mw.shareddata["facet"]["tags"]:
            self.mw.shareddata["facet"]["tags"].append(tag)
            self.mw.reloadLevels()
    def add_metadata(self,icon,text,onclick=None,tooltip=None):
        self.layoutMetadata.addWidget(LevelBoxMetadata(icon,text,tooltip=tooltip,onclick=onclick))
    def add_tag(self,text):
        self.layoutTags.addWidget(LevelBoxTag(text,lambda: self.change_facet_tag(text)))
    def add_author(self,author):
        self.add_metadata("ui/user-solid.svg",author,onclick=lambda: self.change_facet_author(author))
    def load_extra(self):
        filepath = utils.get_temp_folder() + "/" + self.data["id"] + ".png"
        if not os.path.exists(filepath):
            urllib.request.urlretrieve(self.data["image"],filepath)
        thumbnailtext: QtWidgets.QLabel = self.thumbnail
        thumbnailtext.setText("")
        thumbnailtext.setPixmap(QtGui.QPixmap(filepath))
    def update_download_button(self):
        QtCore.QTimer.singleShot(0,self.update_download_button_)
    def update_download_button_(self):
        if self.is_installed():
            self.lblInstalled.setVisible(True)
            self.btnDownload.setToolTip("Uninstall")
            if os.name == "nt":
                self.btnDownload.setIcon(QtGui.QIcon("ui/trash-solid.svg"))
            else:
                self.btnDownload.setIcon(QtGui.QIcon.fromTheme("user-trash-full-symbolic"))
            self.bgcolor = "green"
        else:
            self.lblInstalled.setVisible(False)
            self.btnDownload.setToolTip("Install")
            if os.name == "nt":
                self.btnDownload.setIcon(QtGui.QIcon("ui/download-solid.svg"))
            else:
                self.btnDownload.setIcon(QtGui.QIcon.fromTheme("download"))
            self.bgcolor = None
        self.repaint()
    def is_installed(self):
        return utils.get_available_rd_level_name(self.data) != None
    def download_click(self):
        self.loadingmovie = QtGui.QMovie("ui/loading.gif",parent=self)
        self.loadingmovie.frameChanged.connect(lambda x: self.btnDownload.setIcon(QtGui.QIcon(self.loadingmovie.currentPixmap())))
        self.btnDownload.setDisabled(True)
        self.loadingmovie.start()
        if self.is_installed():
            threading.Thread(target=self._remove).start()
        else:
            threading.Thread(target=self._download).start()
    def _remove(self):
        utils.remove_rd_level(self.data)

        self.loadingmovie.stop()
        self.update_download_button()
        self.btnDownload.setDisabled(False)
    def _download(self):
        utils.download_rd_level(self.data)
        if len(self.isDestroyed) > 0:
            print("download finished and levelbox is destroyed")
            return
        self.loadingmovie.stop()
        self.update_download_button()
        self.btnDownload.setDisabled(False)
