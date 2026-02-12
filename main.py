#!/usr/bin/env python3
"""
智能端口映射控制器 - 主程序入口
采用向导式配置，自动检测并管理端口转发
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QFont, QIcon

from config_manager import ConfigManager
from setup_wizard import SetupWizard
from main_window import MainWindow
from tray_icon import SystemTrayIcon


class PortMapperApp:
    """主应用程序类"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = ConfigManager()
        self.tray_icon = None
        self.main_window = None

        # 初始化应用程序
        self.init_app()

    def init_app(self):
        """初始化应用程序设置"""
        # 设置应用程序信息
        self.app.setApplicationName("智能端口映射控制器")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("PortMapper")

        # 设置字体
        font = QFont("微软雅黑", 10)
        self.app.setFont(font)

        # 设置高DPI支持
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # 设置样式
        self.setup_styles()

    def setup_styles(self):
        """设置应用程序样式"""
        from styles.theme import DarkTheme
        self.app.setStyleSheet(DarkTheme.get_stylesheet())

    def run(self):
        """运行应用程序"""
        # 检查配置是否完整
        if not self.config.is_complete():
            # 显示配置向导
            wizard = SetupWizard(self.config)
            if not wizard.exec_and_setup():
                return  # 用户取消配置

        # 创建主窗口
        self.main_window = MainWindow(self.config)

        # 创建系统托盘
        self.tray_icon = SystemTrayIcon(self.main_window)
        self.tray_icon.show()

        # 显示主窗口（初始最小化到托盘）
        # self.main_window.show()
        self.main_window.showMinimized()

        # 启动事件循环
        sys.exit(self.app.exec_())


def main():
    """应用程序主函数"""
    app = PortMapperApp()
    app.run()


if __name__ == "__main__":
    main()

