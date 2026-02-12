"""
应用程序设置对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget, QWidget, QMessageBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AppSettingsDialog(QDialog):
    """应用程序设置对话框"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("应用程序设置")
        self.setFixedSize(450, 450)

        layout = QVBoxLayout()

        # 创建选项卡
        tabs = QTabWidget()

        # 扫描设置选项卡
        scan_tab = QWidget()
        self.setup_scan_tab(scan_tab)
        tabs.addTab(scan_tab, "📡 扫描设置")

        # 行为设置选项卡
        behavior_tab = QWidget()
        self.setup_behavior_tab(behavior_tab)
        tabs.addTab(behavior_tab, "⚙️ 行为设置")

        # 高级设置选项卡
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        tabs.addTab(advanced_tab, "🔧 高级设置")

        layout.addWidget(tabs)

        # 按钮
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setMinimumHeight(40)

        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(40)

        reset_btn = QPushButton("🔄 恢复默认")
        reset_btn.clicked.connect(self.reset_to_default)
        reset_btn.setMinimumHeight(40)

        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setup_scan_tab(self, tab):
        """设置扫描选项卡"""
        layout = QVBoxLayout()

        # 扫描间隔设置
        scan_group = QGroupBox("端口扫描设置")
        scan_group.setFont(QFont("微软雅黑", 10))
        scan_layout = QFormLayout()

        # 端口扫描间隔
        self.scan_interval_spin = QSpinBox()
        self.scan_interval_spin.setRange(5, 300)
        self.scan_interval_spin.setValue(self.config_manager.get_scan_interval())
        self.scan_interval_spin.setSuffix(" 秒")
        self.scan_interval_spin.setToolTip("端口扫描的时间间隔\n较小的值会更快检测到端口变化\n但会增加系统资源占用")
        scan_layout.addRow("扫描间隔:", self.scan_interval_spin)

        # UI刷新间隔
        self.ui_refresh_spin = QSpinBox()
        self.ui_refresh_spin.setRange(2, 60)
        self.ui_refresh_spin.setValue(self.config_manager.get_ui_refresh_interval())
        self.ui_refresh_spin.setSuffix(" 秒")
        self.ui_refresh_spin.setToolTip("界面刷新的时间间隔\n不会影响端口扫描频率")
        scan_layout.addRow("UI刷新间隔:", self.ui_refresh_spin)

        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # 端口过滤设置
        filter_group = QGroupBox("端口过滤设置")
        filter_group.setFont(QFont("微软雅黑", 10))
        filter_layout = QVBoxLayout()

        self.show_system_check = QCheckBox("显示系统端口 (1-1023)")
        self.show_system_check.setChecked(self.config_manager.app_config.show_system_ports)
        self.show_system_check.setToolTip("是否显示系统保留端口")
        filter_layout.addWidget(self.show_system_check)

        self.show_ephemeral_check = QCheckBox("显示临时端口 (1024-65535)")
        self.show_ephemeral_check.setChecked(True)
        self.show_ephemeral_check.setEnabled(False)
        self.show_ephemeral_check.setToolTip("显示用户应用程序使用的端口")
        filter_layout.addWidget(self.show_ephemeral_check)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        layout.addStretch()
        tab.setLayout(layout)

    def setup_behavior_tab(self, tab):
        """设置行为选项卡"""
        layout = QVBoxLayout()

        # 代理行为设置
        proxy_group = QGroupBox("代理行为设置")
        proxy_group.setFont(QFont("微软雅黑", 10))
        proxy_layout = QVBoxLayout()

        self.auto_start_check = QCheckBox("添加代理后自动启动")
        self.auto_start_check.setChecked(self.config_manager.app_config.auto_start_proxy)
        self.auto_start_check.setToolTip("添加新的端口映射后是否自动启动代理")
        proxy_layout.addWidget(self.auto_start_check)

        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # 窗口行为设置
        window_group = QGroupBox("窗口行为设置")
        window_group.setFont(QFont("微软雅黑", 10))
        window_layout = QVBoxLayout()

        self.minimize_check = QCheckBox("关闭窗口时最小化到托盘")
        self.minimize_check.setChecked(self.config_manager.app_config.minimize_to_tray)
        self.minimize_check.setToolTip("点击关闭按钮时最小化到系统托盘而不是退出程序")
        window_layout.addWidget(self.minimize_check)

        self.start_minimized_check = QCheckBox("启动时最小化到托盘")
        self.start_minimized_check.setChecked(False)
        self.start_minimized_check.setToolTip("程序启动时直接最小化到系统托盘")
        window_layout.addWidget(self.start_minimized_check)

        window_group.setLayout(window_layout)
        layout.addWidget(window_group)

        layout.addStretch()
        tab.setLayout(layout)

    def setup_advanced_tab(self, tab):
        """设置高级选项卡"""
        layout = QVBoxLayout()

        # 日志设置
        log_group = QGroupBox("日志设置")
        log_group.setFont(QFont("微软雅黑", 10))
        log_layout = QFormLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentIndex(1)  # INFO
        self.log_level_combo.setToolTip("设置日志输出级别")
        log_layout.addRow("日志级别:", self.log_level_combo)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # frpc路径设置
        frpc_group = QGroupBox("frpc 设置")
        frpc_group.setFont(QFont("微软雅黑", 10))
        frpc_layout = QFormLayout()

        self.frpc_path_edit = QLineEdit()
        self.frpc_path_edit.setPlaceholderText("留空使用系统 PATH 中的 frpc")
        self.frpc_path_edit.setToolTip("指定 frpc 可执行文件的完整路径\n如果留空，程序会自动在 PATH 中查找")
        frpc_layout.addRow("frpc 路径:", self.frpc_path_edit)

        frpc_group.setLayout(frpc_layout)
        layout.addWidget(frpc_group)

        # 配置管理
        config_group = QGroupBox("配置管理")
        config_group.setFont(QFont("微软雅黑", 10))
        config_layout = QVBoxLayout()

        backup_btn = QPushButton("备份当前配置")
        backup_btn.clicked.connect(self.backup_config)
        config_layout.addWidget(backup_btn)

        restore_btn = QPushButton("恢复配置")
        restore_btn.clicked.connect(self.restore_config)
        config_layout.addWidget(restore_btn)

        clear_btn = QPushButton("清除所有配置")
        clear_btn.clicked.connect(self.clear_config)
        clear_btn.setStyleSheet("background-color: #5a2727;")
        config_layout.addWidget(clear_btn)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        layout.addStretch()
        tab.setLayout(layout)

    def save_settings(self):
        """保存设置"""
        try:
            # 保存扫描设置
            self.config_manager.set_scan_interval(self.scan_interval_spin.value())
            self.config_manager.set_ui_refresh_interval(self.ui_refresh_spin.value())
            self.config_manager.app_config.show_system_ports = self.show_system_check.isChecked()

            # 保存行为设置
            self.config_manager.app_config.auto_start_proxy = self.auto_start_check.isChecked()
            self.config_manager.app_config.minimize_to_tray = self.minimize_check.isChecked()

            # 保存配置
            if self.config_manager.save():
                QMessageBox.information(self, "成功", "应用程序设置已保存")
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "保存设置失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}")

    def reset_to_default(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认恢复",
            "确定要恢复所有设置为默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 重置所有设置
            self.scan_interval_spin.setValue(30)
            self.ui_refresh_spin.setValue(10)
            self.show_system_check.setChecked(False)
            self.auto_start_check.setChecked(True)
            self.minimize_check.setChecked(True)
            self.start_minimized_check.setChecked(False)

            QMessageBox.information(self, "已重置", "所有设置已恢复为默认值")

    def backup_config(self):
        """备份配置"""
        QMessageBox.information(self, "备份", "配置备份功能将在后续版本中实现")

    def restore_config(self):
        """恢复配置"""
        QMessageBox.information(self, "恢复", "配置恢复功能将在后续版本中实现")

    def clear_config(self):
        """清除所有配置"""
        reply = QMessageBox.warning(
            self, "警告",
            "确定要清除所有配置吗？\n"
            "这将删除所有服务器设置、应用程序设置和代理配置。\n"
            "此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.config_manager.clear()
                QMessageBox.information(self, "已清除", "所有配置已清除")
                self.reject()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清除配置时出错: {str(e)}")