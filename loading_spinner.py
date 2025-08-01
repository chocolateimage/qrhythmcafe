import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import QTimer, Qt


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
        self.rotation += (math.sin(self.ticks / 20) + 1.5) * 6
        self.length = (math.sin(self.ticks / 20) + 1.1) * 90
        if self.rotation > 360:
            self.rotation -= 360

        self.repaint()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter: QPainter

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            border_width = int(min(self.height(), self.width()) / 8)
            palette = self.window().palette()

            rect = (
                self.rect()
                .marginsRemoved(self.contentsMargins())
                .adjusted(
                    int(border_width / 2),
                    int(border_width / 2),
                    int(border_width / -2),
                    int(border_width / -2),
                )
            )

            painter.setPen(QPen(palette.light(), border_width))
            painter.drawEllipse(rect)

            painter.setPen(
                QPen(
                    palette.accent()
                    if hasattr(palette, "accent")
                    else palette.highlight(),
                    border_width,
                    cap=Qt.PenCapStyle.FlatCap,
                )
            )
            painter.drawArc(
                rect,
                int(-self.rotation * 16 - self.length * 8),
                int(self.length * 16),
            )

        return super().paintEvent(event)
