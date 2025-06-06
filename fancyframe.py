from PyQt6 import QtWidgets, QtGui


class FancyFrame(QtWidgets.QWidget):
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        bgcolor = getattr(self, "bgcolor", None)
        if bgcolor == "green":
            painter.setBrush(QtGui.QColor(50, 128, 50, 30))
            painter.setPen(QtGui.QColor(0, 255, 0, 150))
        else:
            painter.setBrush(QtGui.QColor(128, 128, 128, 30))
            painter.setPen(QtGui.QColor(128, 128, 128, 90))
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        super().paintEvent(e)
