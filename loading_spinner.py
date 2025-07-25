import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QMargins, QTimer


class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(32, 32)

        self.ticks = 0
        self.rotation = 0
        self.length = 0
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.ticked)
        self.timer.start()

    def ticked(self):
        self.ticks += 1
        self.rotation += (math.sin(self.ticks / 15) + 2) * 4
        self.length = (math.sin(self.ticks / 15) + 2) * 90
        if self.rotation > 360:
            self.rotation -= 360

        self.repaint()

    def paintEvent(self, event):
        rect = self.rect().marginsRemoved(self.contentsMargins())
        with QPainter(self) as painter:
            painter: QPainter

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QColor(0, 0, 0, 0))

            border_width = int(min(self.height(), self.width()) / 8)

            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            painter.setBrush(self.window().palette().light())
            painter.drawEllipse(rect)

            painter.setBrush(self.window().palette().accent())
            painter.drawPie(
                rect,
                int(-self.rotation * 16 - self.length * 8),
                int(self.length * 16),
            )

            painter.setBrush(painter.background())
            painter.drawEllipse(
                rect.marginsRemoved(
                    QMargins(border_width, border_width, border_width, border_width)
                )
            )

        return super().paintEvent(event)
