"""
系统托盘 - 管理托盘图标和菜单
"""

from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QApplication,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, pyqtSignal
# 之前可能缺少的导入
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


class SystemTrayIcon(QSystemTrayIcon):
    """系统托盘图标类"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 设置图标
        self.setIcon(self.create_tray_icon())

        # 创建菜单
        self.create_menu()

        # 连接信号
        self.activated.connect(self.on_tray_activated)

    def create_tray_icon(self):
        """创建托盘图标"""
        from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
        from PyQt5.QtCore import Qt

        # 创建一个简单的圆形图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制外圆
        painter.setBrush(QBrush(QColor("#2196F3")))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(2, 2, 60, 60)

        # 绘制内圆
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(16, 16, 32, 32)

        # 绘制箭头
        painter.setPen(QPen(QColor("#2196F3"), 4))
        painter.drawLine(24, 32, 40, 32)  # 横线
        painter.drawLine(40, 32, 32, 24)  # 上箭头
        painter.drawLine(40, 32, 32, 40)  # 下箭头

        painter.end()

        return QIcon(pixmap)

    def create_menu(self):
        """创建托盘菜单"""
        menu = QMenu()

        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_main_window)
        menu.addAction(show_action)

        # 刷新端口
        refresh_action = QAction("刷新端口", self)
        refresh_action.triggered.connect(self.main_window.refresh_ports)
        menu.addAction(refresh_action)

        menu.addSeparator()

        # 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.main_window.show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_application)
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()
        elif reason == QSystemTrayIcon.Trigger:
            # 显示通知
            self.show_message(
                "端口映射控制器",
                "点击图标显示菜单，双击打开主窗口",
                QSystemTrayIcon.Information,
                2000
            )

    def show_main_window(self):
        """显示主窗口"""
        if self.main_window.isMinimized() or not self.main_window.isVisible():
            self.main_window.showNormal()
            self.main_window.activateWindow()
            self.main_window.raise_()

            # 窗口显示后立即刷新端口
            QTimer.singleShot(100, self.main_window.refresh_ports)
        else:
            self.main_window.activateWindow()

    def exit_application(self):
        """退出应用程序"""
        reply = QMessageBox.question(
            self.main_window, "确认退出",
            "确定要退出端口映射控制器吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 调用主窗口的真正关闭方法
            self.main_window.real_close()