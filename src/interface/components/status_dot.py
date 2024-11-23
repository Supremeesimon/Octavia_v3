"""
Pulsating dot component with glowing effect for status indication
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QParallelAnimationGroup, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient

class PulsingDot(QWidget):
    """A pulsating dot widget with glowing effect for status indication"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self._opacity = 0.0
        self._radius = 2.5
        self._glow_radius = 1.5
        self._color = QColor("#e74c3c")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the animations"""
        # Create parallel animation group
        self.animation_group = QParallelAnimationGroup(self)
        
        # Opacity animation
        self.opacity_animation = QPropertyAnimation(self, b"opacity", self)
        self.opacity_animation.setDuration(2000)  # Slower breathing
        self.opacity_animation.setStartValue(0.3)  # Start more transparent
        self.opacity_animation.setEndValue(0.6)    # End less opaque
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.opacity_animation.setLoopCount(-1)  # Infinite loop
        
        # Glow radius animation
        self.glow_radius_animation = QPropertyAnimation(self, b"glow_radius", self)
        self.glow_radius_animation.setDuration(2000)  # Match opacity duration
        self.glow_radius_animation.setStartValue(1.2)  # Smaller start
        self.glow_radius_animation.setEndValue(1.8)    # Smaller end
        self.glow_radius_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.glow_radius_animation.setLoopCount(-1)  # Infinite loop
        
        # Add animations to group
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.addAnimation(self.glow_radius_animation)
        
        # Start animations immediately
        self.animation_group.start()
    
    def start_animation(self):
        """Start the breathing animation"""
        self.animation_group.start()
        
    def stop_animation(self):
        """Stop the breathing animation"""
        self.animation_group.stop()
        self._opacity = 1.0
        self._radius = 2.5
        self._glow_radius = 1.5
        self.update()
    
    def set_success(self):
        """Set dot color to green for success state"""
        self._color = QColor("#2ecc71")
        self.stop_animation()  # Stop animation for stable appearance
        self._opacity = 0.8  # Higher fixed opacity for better visibility
        self._glow_radius = 1.5  # Fixed glow radius
        self.update()
        
    def set_error(self):
        """Set dot color to red for error state"""
        self._color = QColor("#e74c3c")
        self.start_animation()
        self.update()
        
    def paintEvent(self, event):
        """Paint the dot with enhanced glow effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center in the larger widget
        center_x = self.width() / 2
        center_y = self.height() / 2
        center = QPointF(center_x, center_y)
        base_radius = 2.5  # Core dot radius stays the same
        
        # Create dark ring gradient
        dark_gradient = QRadialGradient(center_x, center_y, base_radius * 1.5)
        dark_gradient.setColorAt(0, QColor(0, 0, 0, 100))  # Semi-transparent black
        dark_gradient.setColorAt(1, QColor(0, 0, 0, 0))  # Fully transparent
        
        # Paint dark ring
        painter.setBrush(dark_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, base_radius * 2, base_radius * 2)
        
        # Create main glow gradient
        glow_gradient = QRadialGradient(center_x, center_y, base_radius * self._glow_radius * 2)
        
        # Create glowing effect with multiple color stops
        glow_gradient.setColorAt(0, QColor(self._color.red(), self._color.green(), self._color.blue(), int(255 * self._opacity)))
        glow_gradient.setColorAt(0.4, QColor(self._color.red(), self._color.green(), self._color.blue(), int(120 * self._opacity)))
        glow_gradient.setColorAt(0.7, QColor(self._color.red(), self._color.green(), self._color.blue(), int(50 * self._opacity)))
        glow_gradient.setColorAt(1, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))
        
        # Paint glow
        painter.setBrush(glow_gradient)
        painter.drawEllipse(center, base_radius * self._glow_radius * 2, base_radius * self._glow_radius * 2)
        
        # Paint core dot
        core_gradient = QRadialGradient(center_x, center_y, base_radius)
        core_gradient.setColorAt(0, self._color)
        core_gradient.setColorAt(0.7, self._color)
        core_gradient.setColorAt(1, QColor(self._color.red(), self._color.green(), self._color.blue(), int(200 * self._opacity)))
        
        painter.setBrush(core_gradient)
        painter.drawEllipse(center, base_radius, base_radius)
    
    # Properties for animation
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()
        
    def get_glow_radius(self):
        return self._glow_radius
        
    def set_glow_radius(self, radius):
        self._glow_radius = radius
        self.update()
        
    opacity = Property(float, get_opacity, set_opacity)
    glow_radius = Property(float, get_glow_radius, set_glow_radius)
