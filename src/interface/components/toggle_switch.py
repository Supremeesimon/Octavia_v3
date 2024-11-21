"""
Toggle switch component for Octavia
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QColor, QBrush


class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 20)  
        self._is_checked = False
        self.animation_value = 0
        self.setToolTip("Switch between Action and Chat modes")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw track 
        track_color = QColor("#4a4a4a") if self._is_checked else QColor("#666666")
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 4, 36, 12, 6, 6)  

        # Draw handle 
        handle_x = 18 if self._is_checked else 2
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(handle_x, 1, 18, 18)  

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self.update()
            self.toggled.emit(self._is_checked)

    def isChecked(self):
        return self._is_checked

    def setChecked(self, checked):
        if self._is_checked != checked:
            self._is_checked = checked
            self.update()
            self.toggled.emit(self._is_checked)
