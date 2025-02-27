import sys
import platform
import psutil
import cpuinfo
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QTabWidget, QScrollArea,
                           QHBoxLayout, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg
from platformdirs import user_cache_dir, user_config_dir, user_data_dir
from environment_monitor import EnvironmentMonitor

class PerformanceMonitor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # CPU Usage Graph
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout()
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setBackground('w')
        self.cpu_plot.setTitle("CPU Usage Over Time")
        self.cpu_plot.setLabel('left', 'Usage (%)')
        self.cpu_plot.setLabel('bottom', 'Time (s)')
        self.cpu_plot.showGrid(x=True, y=True)
        self.cpu_curve = self.cpu_plot.plot(pen='b')
        self.cpu_data = np.zeros(100)
        cpu_layout.addWidget(self.cpu_plot)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Memory Usage Graph
        mem_group = QGroupBox("Memory Usage")
        mem_layout = QVBoxLayout()
        self.mem_plot = pg.PlotWidget()
        self.mem_plot.setBackground('w')
        self.mem_plot.setTitle("Memory Usage Over Time")
        self.mem_plot.setLabel('left', 'Usage (%)')
        self.mem_plot.setLabel('bottom', 'Time (s)')
        self.mem_plot.showGrid(x=True, y=True)
        self.mem_curve = self.mem_plot.plot(pen='r')
        self.mem_data = np.zeros(100)
        mem_layout.addWidget(self.mem_plot)
        mem_group.setLayout(mem_layout)
        layout.addWidget(mem_group)
        
        # Network Usage
        net_group = QGroupBox("Network Usage")
        net_layout = QVBoxLayout()
        self.net_label = QLabel()
        self.net_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        net_layout.addWidget(self.net_label)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
        
        # Initialize network counters
        self.last_net_io = psutil.net_io_counters()
        self.last_time = self.timer.remainingTime()
    
    def update_data(self):
        # Update CPU data
        cpu_percent = psutil.cpu_percent()
        self.cpu_data = np.roll(self.cpu_data, -1)
        self.cpu_data[-1] = cpu_percent
        self.cpu_curve.setData(self.cpu_data)
        
        # Update Memory data
        mem_percent = psutil.virtual_memory().percent
        self.mem_data = np.roll(self.mem_data, -1)
        self.mem_data[-1] = mem_percent
        self.mem_curve.setData(self.mem_data)
        
        # Update Network data
        current_net_io = psutil.net_io_counters()
        current_time = self.timer.remainingTime()
        time_diff = (current_time - self.last_time) / 1000  # Convert to seconds
        
        bytes_sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
        bytes_recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
        
        self.net_label.setText(
            f"Upload Speed: {bytes_sent/1024:.2f} KB/s\n"
            f"Download Speed: {bytes_recv/1024:.2f} KB/s\n"
            f"Total Sent: {current_net_io.bytes_sent/1024/1024:.2f} MB\n"
            f"Total Received: {current_net_io.bytes_recv/1024/1024:.2f} MB"
        )
        
        self.last_net_io = current_net_io
        self.last_time = current_time

class ProcessList(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Process list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.process_widget = QWidget()
        self.process_layout = QVBoxLayout(self.process_widget)
        scroll.setWidget(self.process_widget)
        layout.addWidget(scroll)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Process List")
        refresh_btn.clicked.connect(self.update_processes)
        layout.addWidget(refresh_btn)
        
        # Initial update
        self.update_processes()
        
    def update_processes(self):
        # Clear existing widgets
        for i in reversed(range(self.process_layout.count())): 
            self.process_layout.itemAt(i).widget().setParent(None)
        
        # Get process list
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                         key=lambda p: p.info['cpu_percent'], 
                         reverse=True)[:20]:  # Show top 20 CPU-consuming processes
            try:
                info = proc.info
                label = QLabel(
                    f"PID: {info['pid']} | "
                    f"Name: {info['name']} | "
                    f"CPU: {info['cpu_percent']:.1f}% | "
                    f"Memory: {info['memory_percent']:.1f}%"
                )
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                self.process_layout.addWidget(label)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cross-Platform System Information")
        self.setMinimumSize(1024, 768)  # Increased size for better visibility
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Environment Monitor Tab (New)
        env_tab = EnvironmentMonitor()
        tabs.addTab(env_tab, "Environment")
        
        # System Info Tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # System Information
        system_info = [
            f"OS: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}",
            f"Python Version: {sys.version.split()[0]}",
            f"Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB",
            f"Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB",
            f"User Cache Dir: {user_cache_dir()}",
            f"User Config Dir: {user_config_dir()}",
            f"User Data Dir: {user_data_dir()}"
        ]
        
        for info in system_info:
            label = QLabel(info)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            scroll_layout.addWidget(label)
        
        scroll.setWidget(scroll_content)
        system_layout.addWidget(scroll)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Information")
        refresh_btn.clicked.connect(self.refresh_info)
        system_layout.addWidget(refresh_btn)
        
        tabs.addTab(system_tab, "System Info")
        
        # Performance Monitor Tab
        perf_tab = PerformanceMonitor()
        tabs.addTab(perf_tab, "Performance")
        
        # Process List Tab
        process_tab = ProcessList()
        tabs.addTab(process_tab, "Processes")
        
        # Disk Info Tab
        disk_tab = QWidget()
        disk_layout = QVBoxLayout(disk_tab)
        disk_scroll = QScrollArea()
        disk_scroll.setWidgetResizable(True)
        disk_content = QWidget()
        disk_layout_scroll = QVBoxLayout(disk_content)
        
        # Disk Information
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info = (
                    f"Device: {partition.device}\n"
                    f"Mount Point: {partition.mountpoint}\n"
                    f"File System Type: {partition.fstype}\n"
                    f"Total Size: {usage.total / (1024**3):.2f} GB\n"
                    f"Used: {usage.used / (1024**3):.2f} GB\n"
                    f"Free: {usage.free / (1024**3):.2f} GB\n"
                    f"Usage: {usage.percent}%\n"
                )
                label = QLabel(info)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                disk_layout_scroll.addWidget(label)
                disk_layout_scroll.addWidget(QLabel("---"))
            except PermissionError:
                continue
        
        disk_scroll.setWidget(disk_content)
        disk_layout.addWidget(disk_scroll)
        tabs.addTab(disk_tab, "Disk Info")

    def refresh_info(self):
        self.__init__()

def main():
    app = QApplication(sys.argv)
    
    # Set the style to fusion for better cross-platform appearance
    app.setStyle('Fusion')
    
    # Configure pyqtgraph
    pg.setConfigOptions(antialias=True)
    
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
