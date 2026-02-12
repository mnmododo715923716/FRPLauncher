"""
调试日志组件
"""

import sys
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor


class DebugLogger(QTextEdit):
    """调试日志输出组件"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

        # 重定向标准输出
        self.stdout = sys.stdout
        sys.stdout = self

    def setup_ui(self):
        """设置UI"""
        self.setReadOnly(True)
        self.setFont(QFont("Courier New", 9))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
        """)

    def write(self, text):
        """写入日志"""
        if text.strip():  # 只处理非空文本
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_text = f"[{timestamp}] {text}"

            # 在主线程中更新UI
            from PyQt5.QtCore import QMetaObject, Qt, pyqtSlot
            QMetaObject.invokeMethod(
                self,
                "appendText",
                Qt.QueuedConnection,
                str(log_text)
            )

        # 同时输出到原始stdout（控制台）
        self.stdout.write(text)

    def flush(self):
        """刷新缓冲区"""
        self.stdout.flush()

    @pyqtSlot(str)
    def appendText(self, text):
        """线程安全地追加文本"""
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def closeEvent(self, event):
        """关闭事件"""
        # 恢复标准输出
        sys.stdout = self.stdout
        super().closeEvent(event)


class DebugWindow(QWidget):
    """调试窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("调试信息")
        self.setGeometry(1000, 100, 600, 400)

        layout = QVBoxLayout()

        # 日志输出
        self.logger = DebugLogger()
        layout.addWidget(self.logger)

        # 控制按钮
        button_layout = QVBoxLayout()

        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.logger.clear)

        test_btn = QPushButton("测试端口扫描")
        test_btn.clicked.connect(self.test_port_scan)

        button_layout.addWidget(clear_btn)
        button_layout.addWidget(test_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 输出初始信息
        print("=== 调试窗口已打开 ===")
        print("使用此窗口查看程序运行日志")

    def test_port_scan(self):
        """测试端口扫描"""
        try:
            import psutil
            connections = psutil.net_connections(kind='inet')

            listening_ports = []
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    listening_ports.append(conn.laddr.port)

            print(f"找到 {len(listening_ports)} 个监听端口: {sorted(listening_ports)}")

        except Exception as e:
            print(f"测试端口扫描失败: {e}")
            traceback.print_exc()