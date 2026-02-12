"""
应用程序主题样式 - 增强版
"""

class DarkTheme:
    """深色主题"""

    @staticmethod
    def get_stylesheet() -> str:
        """获取样式表"""
        return """
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                color: #ffffff;
                font-family: '微软雅黑', 'Microsoft YaHei', sans-serif;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            QLabel[title="true"] {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4d4d4d;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            
            QPushButton:disabled {
                background-color: #323232;
                color: #888888;
                border-color: #444444;
            }
            
            /* 输入框样式 - 确保文字清晰可见 */
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #4a6ea9;
                selection-color: #ffffff;
                font-size: 11pt;
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #6a9ae6;
                background-color: #454545;
            }
            
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
                border-color: #6a9ae6;
                background-color: #404040;
            }
            
            /* 下拉框样式 */
            QComboBox {
                padding: 6px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ffffff;
                margin-top: -2px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                selection-background-color: #4a6ea9;
                selection-color: #ffffff;
            }
            
            /* 微调按钮样式 */
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                height: 15px;
                border-left: 1px solid #555555;
                border-bottom: 1px solid #555555;
                border-top-right-radius: 4px;
                background-color: #3c3c3c;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                height: 15px;
                border-left: 1px solid #555555;
                border-bottom-right-radius: 4px;
                background-color: #3c3c3c;
            }
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #555555;
            }
            
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid #ffffff;
                margin-top: 2px;
            }
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-bottom: 2px;
            }
            
            /* 单选/复选框样式 */
            QRadioButton, QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            
            QRadioButton::indicator, QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            
            QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked {
                border: 2px solid #5a5a5a;
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            
            QRadioButton::indicator:checked, QCheckBox::indicator:checked {
                border: 2px solid #4a6ea9;
                background-color: #4a6ea9;
                border-radius: 10px;
            }
            
            QCheckBox::indicator:unchecked {
                border-radius: 4px;
            }
            
            QCheckBox::indicator:checked {
                border-radius: 4px;
            }
            
            /* 分组框 */
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #252525;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 12px 0 12px;
                background-color: #3c3c3c;
                border-radius: 4px;
            }
            
            /* 进度条 */
            QProgressBar {
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                background-color: #2d2d2d;
                text-align: center;
                color: #ffffff;
            }
            
            QProgressBar::chunk {
                background-color: #4a6ea9;
                border-radius: 4px;
            }
            
            /* 向导页面 */
            QWizard {
                background-color: #1e1e1e;
            }
            
            QWizardPage {
                background-color: #252525;
                border-radius: 8px;
                margin: 10px;
            }
            
            /* 消息框、输入对话框等 */
            QMessageBox, QInputDialog, QDialog {
                background-color: #2d2d2d;
            }
            
            QMessageBox QLabel, QInputDialog QLabel, QDialog QLabel {
                color: #ffffff;
            }
            
            QMessageBox QPushButton, QInputDialog QPushButton, QDialog QPushButton {
                min-width: 80px;
                min-height: 30px;
            }
            
            /* 滚动条样式 */
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 14px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 7px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #6a6a6a;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            /* 系统托盘菜单 */
            QMenu {
                background-color: #323232;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 6px 24px 6px 24px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #4a6ea9;
                color: white;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #4a4a4a;
                margin: 4px 8px 4px 8px;
            }
            
            /* 表格样式 */
            QTableWidget {
                background-color: #252525;
                color: #ffffff;
                gridline-color: #3c3c3c;
                selection-background-color: #4a6ea9;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3c3c3c;
                font-weight: bold;
            }
        """