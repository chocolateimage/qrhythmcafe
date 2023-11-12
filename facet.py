from PyQt5 import QtWidgets, uic, QtCore
import fancyframe

class Facet(fancyframe.FancyFrame):
    def __init__(self,data,mw):
        super().__init__()
        uic.loadUi("ui/facet.ui",self)
        self.mw = mw
        self.itemsLayout: QtWidgets.QVBoxLayout = self.itemsLayout
        self.txtFilter: QtWidgets.QLineEdit = self.txtFilter
        self.topLayout.setAlignment(QtCore.Qt.AlignTop)
        self.load_data(data)
        self.txtFilter.returnPressed.connect(self.onSearch)
    def load_data(self,data):
        self.data = data
        self.fieldname = self.data["field_name"]
        if self.fieldname == "difficulty":
            self.txtFilter.setVisible(False)
        self.lblName.setText(self.fieldname.capitalize())
        self.lblTotal.setText("("+str(self.data["stats"]["total_values"])+")")
        thelist = self.data["counts"]
        if self.fieldname == "difficulty":
            thelist = sorted(self.data["counts"],key=lambda a: a["value"])
        for i in range(self.itemsLayout.count()):
            self.itemsLayout.itemAt(i).widget().deleteLater()
        for i in thelist:
            self.add_cb(i)
    def onSearch(self):
        js = self.mw.makeSearchRequest(facet_query=self.fieldname + ":" + self.txtFilter.text())
        for i in js["facet_counts"]:
            if i["field_name"] == self.fieldname:
                self.load_data(i)
    def add_cb(self,i):
        nam = i["value"]
        displayname = nam
        if self.fieldname == "difficulty":
            displayname = {"0":"Easy","1":"Medium","2":"Tough","3":"Very Tough"}[displayname]
        cb = QtWidgets.QCheckBox(displayname + " ("+str(i["count"])+")")
        cb.setChecked(nam in self.mw.shareddata["facet"][self.fieldname])
        cb.toggled.connect(lambda x: self.cb_toggle(nam,x))
        self.itemsLayout.addWidget(cb)
    def cb_toggle(self,nam,val):
        self.mw.reloadLevels()
        if nam in self.mw.shareddata["facet"][self.fieldname]:
            self.mw.shareddata["facet"][self.fieldname].remove(nam)
        else:
            self.mw.shareddata["facet"][self.fieldname].append(nam)

class PeerReviewedWidget(fancyframe.FancyFrame):
    def __init__(self,mw):
        super().__init__()
        uic.loadUi("ui/facet.ui",self)
        self.mw = mw
        self.itemsLayout: QtWidgets.QVBoxLayout = self.itemsLayout
        self.topLayout.setAlignment(QtCore.Qt.AlignTop)
        self.txtFilter.setVisible(False)
        self.lblName.setText("Peer Review")
        self.lblTotal.setVisible(False)
        self.add_radiobutton("Only peer-reviewed levels",True)
        self.add_radiobutton("All levels",False)
    def add_radiobutton(self,text,value):
        rb = QtWidgets.QRadioButton(text)
        rb.setChecked(value == self.mw.shareddata["onlyreviewed"])
        if value:
            rb.toggled.connect(self.change_toggle)
        self.itemsLayout.addWidget(rb)
    def change_toggle(self,val):
        self.mw.shareddata["onlyreviewed"] = val
        self.mw.reloadLevels()