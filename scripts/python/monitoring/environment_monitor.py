import sys
import psutil
import platform
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QProgressBar, QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
import qtawesome as qta

class CircularGauge(QWidget):
    def __init__(self, title="", min_value=0, max_value=100, parent=None):
        super().__init__(parent)
        self.title = title
        self.min_value = min_value
        self.max_value = max_value
        self.value = 0
        self.color = QColor(52, 152, 219)  # Default blue color
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(150, 150)

    def set_value(self, value):
        self.value = max(self.min_value, min(value, self.max_value))
        self.update()

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate sizes
        width = self.width()
        height = self.height()
        size = min(width, height)
        padding = size * 0.1
        center = self.rect().center()

        # Draw circle background
        painter.setPen(QPen(Qt.GlobalColor.gray, 3))
        painter.drawEllipse(center, size/2 - padding, size/2 - padding)

        # Draw value arc
        painter.setPen(QPen(self.color, 5))
        span = int(360 * (self.value - self.min_value) / (self.max_value - self.min_value))
        painter.drawArc(int(padding), int(padding),
                       int(size - 2*padding), int(size - 2*padding),
                       90 * 16, -span * 16)

        # Draw text
        painter.setPen(Qt.GlobalColor.black)
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        
        # Draw title
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        
        # Draw value
        font.setPointSize(20)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")

class ResourceIndicator(QWidget):
    def __init__(self, icon_name, title, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        # Icon
        icon_label = QLabel()
        icon = qta.icon(icon_name, color='black')
        icon_label.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.value_label = QLabel("0%")
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.value_label)
        layout.addLayout(info_layout)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        layout.setStretch(2, 1)  # Make progress bar take up remaining space

    def update_value(self, value, text=None):
        self.progress.setValue(int(value))
        self.value_label.setText(text if text else f"{int(value)}%")

class EnvironmentMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top row with circular gauges
        gauges_layout = QHBoxLayout()
        
        # CPU Usage Gauge
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout()
        self.cpu_gauge = CircularGauge("CPU")
        self.cpu_gauge.set_color(QColor(52, 152, 219))  # Blue
        cpu_layout.addWidget(self.cpu_gauge)
        cpu_group.setLayout(cpu_layout)
        gauges_layout.addWidget(cpu_group)
        
        # Memory Usage Gauge
        mem_group = QGroupBox("Memory Usage")
        mem_layout = QVBoxLayout()
        self.mem_gauge = CircularGauge("Memory")
        self.mem_gauge.set_color(QColor(46, 204, 113))  # Green
        mem_layout.addWidget(self.mem_gauge)
        mem_group.setLayout(mem_layout)
        gauges_layout.addWidget(mem_group)
        
        # Disk Usage Gauge
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout()
        self.disk_gauge = CircularGauge("Disk")
        self.disk_gauge.set_color(QColor(155, 89, 182))  # Purple
        disk_layout.addWidget(self.disk_gauge)
        disk_group.setLayout(disk_layout)
        gauges_layout.addWidget(disk_group)
        
        layout.addLayout(gauges_layout)

        # Resource indicators
        indicators_group = QGroupBox("System Resources")
        indicators_layout = QVBoxLayout()
        
        # CPU Temperature (if available)
        self.cpu_temp = ResourceIndicator("fa5s.thermometer-half", "CPU Temperature")
        indicators_layout.addWidget(self.cpu_temp)
        
        # Memory Usage Details
        self.mem_usage = ResourceIndicator("fa5s.memory", "Memory Usage")
        indicators_layout.addWidget(self.mem_usage)
        
        # Swap Usage
        self.swap_usage = ResourceIndicator("fa5s.exchange-alt", "Swap Usage")
        indicators_layout.addWidget(self.swap_usage)
        
        # Disk I/O
        self.disk_io = ResourceIndicator("fa5s.hdd", "Disk I/O")
        indicators_layout.addWidget(self.disk_io)
        
        # Network Usage
        self.net_usage = ResourceIndicator("fa5s.network-wired", "Network")
        indicators_layout.addWidget(self.net_usage)
        
        indicators_group.setLayout(indicators_layout)
        layout.addWidget(indicators_group)

        # System Info
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        
        system_info = [
            f"OS: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"Python: {platform.python_version()}",
            f"Processor: {platform.processor()}"
        ]
        
        for info in system_info:
            label = QLabel(info)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_layout.addWidget(label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Initialize network counters
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_time = self.timer.remainingTime()

    def update_stats(self):
        # Update gauges
        cpu_percent = psutil.cpu_percent()
        self.cpu_gauge.set_value(cpu_percent)
        
        mem = psutil.virtual_memory()
        self.mem_gauge.set_value(mem.percent)
        
        disk = psutil.disk_usage('/')
        self.disk_gauge.set_value(disk.percent)
        
        # Update indicators
        # CPU Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                temp = max(temp.current for temp in temps['coretemp'])
                self.cpu_temp.update_value(temp, f"{temp}°C")
            else:
                self.cpu_temp.update_value(0, "N/A")
        except:
            self.cpu_temp.update_value(0, "N/A")
        
        # Memory Usage
        self.mem_usage.update_value(
            mem.percent,
            f"Used: {mem.used/1024/1024/1024:.1f}GB / Total: {mem.total/1024/1024/1024:.1f}GB"
        )
        
        # Swap Usage
        swap = psutil.swap_memory()
        self.swap_usage.update_value(
            swap.percent,
            f"Used: {swap.used/1024/1024/1024:.1f}GB / Total: {swap.total/1024/1024/1024:.1f}GB"
        )
        
        # Disk I/O
        current_disk_io = psutil.disk_io_counters()
        current_time = self.timer.remainingTime()
        time_diff = (current_time - self.last_time) / 1000
        
        if time_diff > 0:
            read_speed = (current_disk_io.read_bytes - self.last_disk_io.read_bytes) / time_diff / 1024/1024
            write_speed = (current_disk_io.write_bytes - self.last_disk_io.write_bytes) / time_diff / 1024/1024
            self.disk_io.update_value(
                (read_speed + write_speed) * 5,  # Scale for progress bar
                f"Read: {read_speed:.1f} MB/s | Write: {write_speed:.1f} MB/s"
            )
        
        # Network Usage
        current_net_io = psutil.net_io_counters()
        if time_diff > 0:
            upload_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff / 1024/1024
            download_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff / 1024/1024
            self.net_usage.update_value(
                (upload_speed + download_speed) * 5,  # Scale for progress bar
                f"↑ {upload_speed:.1f} MB/s | ↓ {download_speed:.1f} MB/s"
            )
        
        # Update counters
        self.last_net_io = current_net_io
        self.last_disk_io = current_disk_io
        self.last_time = current_time
