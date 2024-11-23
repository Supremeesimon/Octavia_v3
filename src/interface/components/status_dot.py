"""
Pulsating dot component with glowing effect for status indication
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QColor, QRadialGradient

class PulsingDot(QWidget):
    """A pulsating dot widget with glowing effect for status indication"""
    
    def __init__(self, parent=None, size=8):
        super().__init__(parent)
        self.size = size
        self._opacity = 1.0
        self._glow_radius = 1.0
        self._color = QColor("#e74c3c")  # Default to red
        
        # Make widget background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set fixed size (larger to accommodate glow)
        glow_size = size * 6  # Increased space for glow
        self.setFixedSize(glow_size, glow_size)
        
        # Setup the pulsing animation
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup the breathing animation group"""
        # Create animation group for parallel animations
        self.animation_group = QParallelAnimationGroup()
        
        # Opacity animation
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(3000)  # Slower breathing
        self.opacity_animation.setLoopCount(-1)
        self.opacity_animation.setStartValue(0.8)  # Start more visible
        self.opacity_animation.setEndValue(0.3)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Glow radius animation
        self.glow_animation = QPropertyAnimation(self, b"glow_radius")
        self.glow_animation.setDuration(3000)  # Match opacity duration
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.setStartValue(1.2)  # Start slightly expanded
        self.glow_animation.setEndValue(1.8)  # Don't expand as much
        self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Add both animations to group
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.addAnimation(self.glow_animation)
        
    def start_animation(self):
        """Start the breathing animation"""
        self.animation_group.start()
        
    def stop_animation(self):
        """Stop the breathing animation"""
        self.animation_group.stop()
        self._opacity = 1.0
        self._glow_radius = 1.0
        self.update()
    
    def set_success(self):
        """Set dot color to green for success state"""
        self._color = QColor("#2ecc71")
        self.stop_animation()
        self.update()
        
    def set_error(self):
        """Set dot color to red for error state"""
        self._color = QColor("#e74c3c")
        self.start_animation()
        self.update()
        
    def paintEvent(self, event):
        """Paint the glowing dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate center and radius
        center_x = self.width() / 2
        center_y = self.height() / 2
        base_radius = self.size / 2
        
        # Create radial gradient for glow effect
        gradient = QRadialGradient(center_x, center_y, base_radius * 3 * self._glow_radius)
        gradient.setColorAt(0, QColor(self._color.red(), self._color.green(), self._color.blue(), 180))  # More solid center
        gradient.setColorAt(0.4, QColor(self._color.red(), self._color.green(), self._color.blue(), 120))
        gradient.setColorAt(0.7, QColor(self._color.red(), self._color.green(), self._color.blue(), 40))
        gradient.setColorAt(1.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))  # Fully transparent edge
        
        # Draw glow with softer opacity
        painter.setOpacity(self._opacity * 0.5)  # Reduced base opacity for glow
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        
        # Draw circular glow
        glow_size = base_radius * 6 * self._glow_radius
        painter.drawEllipse(
            center_x - glow_size/2,
            center_y - glow_size/2,
            glow_size,
            glow_size
        )
        
        # Draw solid dot with full opacity
        painter.setOpacity(self._opacity)
        painter.setBrush(self._color)
        painter.drawEllipse(
            center_x - base_radius,
            center_y - base_radius,
            base_radius * 2,
            base_radius * 2
        )
    
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
