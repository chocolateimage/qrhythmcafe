#!/usr/bin/python3
import os
import sys

if __name__ == "__main__":  # make imports work when opening from another directory
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
import requests
import flowlayout
import levelbox
import utils
import facet
import webbrowser
import math

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.5",
    "Referer": "https://rhythm.cafe/",
    "x-typesense-api-key": "nicolebestgirl",
    "Origin": "https://rhythm.cafe",
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui/mainwindow.ui", self)
        self.setWindowIcon(QtGui.QIcon("ui/icon.png"))
        self.scrollarea: QtWidgets.QScrollArea = self.scrollArea
        self.scrollarea.verticalScrollBar().valueChanged.connect(self.onMainScroll)
        self.vlay: QtWidgets.QWidget = self.verticalLayoutWidget
        self.thething: QtWidgets.QWidget = self.thething
        self.thething.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vlaylayout = flowlayout.FlowLayout(self.vlay, 12, 8, 8)
        self.actionOpen_rhythm_cafe.triggered.connect(
            lambda: webbrowser.open("https://rhythm.cafe/")
        )
        self.actionExit.triggered.connect(lambda: self.close())
        self.actionAbout.triggered.connect(lambda: self.showabout())
        self.actionAbout_QT.triggered.connect(lambda: self.showaboutqt())

        self.loadingmovie = QtGui.QMovie("ui/loading.gif", parent=self)
        self.loadingmovie.start()
        self.loadingmovie.setScaledSize(QtCore.QSize(32, 32))
        self.loading_spinner = QtWidgets.QLabel(self.vlay)
        self.loading_spinner.setMovie(self.loadingmovie)
        self.loading_spinner.hide()
        self.shareddata = {
            "facet": {},
            "onlyreviewed": False,
            "page": 1,
            "maxpage": 1,
            "ispageloading": False,
            "latestpageloadid": 0,
        }
        self.reloadLevels()
        self.txtSearch: QtWidgets.QLineEdit = self.txtSearch
        self.txtSearch.textChanged.connect(lambda x: self.onsearchchanged())
        self.txtSearch.returnPressed.connect(self.onsearchpress)
        self.searchTimer = None

    def onMainScroll(self, value):
        diff = self.scrollarea.verticalScrollBar().maximum() - value
        if diff < 1000:
            if not self.shareddata["ispageloading"]:
                if self.shareddata["page"] != self.shareddata["maxpage"]:
                    self.navChange(1)

    def showabout(self):
        QtWidgets.QMessageBox.about(
            self,
            "About QRhythmCafe",
            "A desktop version of rhythm.cafe to download levels directly into the Rhythm Doctor levels folder\n\nVersion "
            + utils.VERSION_NUMBER,
        )

    def showaboutqt(self):
        QtWidgets.QMessageBox.aboutQt(self)

    def navChange(self, by):
        self.shareddata["page"] += by
        self.reloadLevels(resetpage=False)

    def makeSearchRequest(self, facet_query=None):
        filterby = []
        for facetname, facetvalues in self.shareddata["facet"].items():
            for j in facetvalues:
                if facetname == "difficulty":
                    filterby.append(facetname + ":=[" + j + "]")
                else:
                    filterby.append(facetname + ":=`" + j + "`")
        if self.shareddata["onlyreviewed"]:
            filterby.append("approval:=[10..20]")
        else:
            filterby.append("approval:=[-1..20]")
        params = {
            "q": self.txtSearch.text().strip(),
            "query_by": "song, authors, artist, tags, description",
            "query_by_weights": "12, 8, 6, 5, 4",
            "facet_by": "authors,tags,source,difficulty,artist",
            "per_page": "25",
            "max_facet_values": "10",
            "filter_by": " && ".join(filterby),
            "page": self.shareddata["page"],
            "sort_by": "_text_match:desc,last_updated:desc",
            "num_typos": "2, 1, 1, 1, 0",
        }
        if facet_query is not None:
            params["facet_query"] = facet_query
        print(params)
        response = requests.get(
            "https://orchardb.fly.dev/typesense/collections/levels/documents/search",
            params=params,
            headers=headers,
        )
        return response.json()

    def onsearchpress(self):
        self.onsearchchanged(0)

    def onsearchchanged(self, delay=700):
        if self.searchTimer != None:
            self.searchTimer.stop()
        self.shareddata["facet"] = {}
        self.searchTimer = QtCore.QTimer()
        self.searchTimer.setSingleShot(True)
        self.searchTimer.setInterval(delay)
        self.searchTimer.timeout.connect(self.reloadLevels)
        self.searchTimer.start()

    def reloadLevels(self, resetpage=True):
        if resetpage:
            self.shareddata["page"] = 1
        self.shareddata["ispageloading"] = True
        currentpageloadid = self.shareddata["latestpageloadid"] + 1
        self.shareddata["latestpageloadid"] = currentpageloadid
        if resetpage:
            self.loading_spinner.move(
                int(self.rightsidething.width() / 2) - 16,
                int(self.rightsidething.height() / 2) - 16,
            )
            self.loading_spinner.raise_()
        else:
            self.vlaylayout.addWidget(self.loading_spinner)
        self.loading_spinner.show()

        class ReloadLevelsThread(QtCore.QThread):
            finished = QtCore.pyqtSignal(object)

            def run(this):
                print("searching")
                this.finished.emit(self.makeSearchRequest())

        self.t = ReloadLevelsThread()
        self.t.finished.connect(
            lambda a: self._reloadLevels(a, resetpage, currentpageloadid)
        )
        self.t.start()

    def _reloadLevels(self, js, resetpage, currentpageloadid):
        if self.shareddata["latestpageloadid"] != currentpageloadid:
            return

        self.shareddata["ispageloading"] = False
        self.loading_spinner.hide()
        if not resetpage:
            self.vlaylayout.removeWidget(self.loading_spinner)

        if "hits" not in js:
            self.navFound.setText(
                "An error has occured. If this keeps happening, file an issue here:\nhttps://github.com/chocolateimage/qrhythmcafe/issues/new/choose"
            )
            print()
            print("-- An error occured --")
            print(js)
            print("-- An error occured (END) --")
            print()
            return

        if len(js["hits"]) == 0:
            maxpage = 1
        else:
            maxpage = math.ceil(js["found"] / len(js["hits"]))

        if resetpage:
            self.shareddata["maxpage"] = maxpage

        if js["request_params"]["q"] == "":
            self.navFound.setText("")
        else:
            self.navFound.setText(
                str(js["found"]) + " levels found for " + js["request_params"]["q"]
            )

        if resetpage:
            for i in self.thething.children():
                if isinstance(i, facet.Facet) or isinstance(
                    i, facet.PeerReviewedWidget
                ):
                    i.deleteLater()
            for i in js["facet_counts"]:
                if i["field_name"] == "source":
                    continue
                if i["field_name"] not in self.shareddata["facet"]:
                    self.shareddata["facet"][i["field_name"]] = []

                f = facet.Facet(i, self)
                self.thething.layout().addWidget(f)
            self.thething.layout().addWidget(facet.PeerReviewedWidget(self))

            for i in self.vlay.children():
                if isinstance(i, levelbox.LevelBox):
                    i.deleteLater()

        for i in js["hits"]:
            lb = levelbox.LevelBox(i["document"], self)
            self.vlaylayout.addWidget(lb)
        if resetpage:
            self.scrollarea.verticalScrollBar().setValue(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if os.name == "nt":
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
