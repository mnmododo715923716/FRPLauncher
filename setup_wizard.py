"""
配置向导 - 引导用户完成服务器配置
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QComboBox,
    QRadioButton, QButtonGroup, QGroupBox,
    QFormLayout, QCheckBox, QPushButton,
    QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from config_manager import AuthType, ServerConfig

class ServerInfoPage(QWizardPage):
    """服务器信息页面"""

    def __init__(self):
        super().__init__()
        self.setTitle("服务器配置")
        self.setSubTitle("请输入 FRP 服务器的地址和端口")

        layout = QFormLayout()

        # 服务器地址
        self.server_addr_edit = QLineEdit()
        self.server_addr_edit.setPlaceholderText("例如: frp.example.com 或 123.123.123.123")
        layout.addRow("服务器地址:", self.server_addr_edit)

        # 服务器端口
        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(1, 65535)
        self.server_port_spin.setValue(7000)
        layout.addRow("服务器端口:", self.server_port_spin)

        # 验证规则
        self.registerField("server_addr*", self.server_addr_edit)
        self.registerField("server_port", self.server_port_spin)

        self.setLayout(layout)

    def validatePage(self):
        """页面验证"""
        addr = self.server_addr_edit.text().strip()
        if not addr:
            QMessageBox.warning(self, "输入错误", "请输入服务器地址")
            return False
        return True

class AuthTypePage(QWizardPage):
    """认证类型选择页面"""

    def __init__(self):
        super().__init__()
        self.setTitle("认证方式")
        self.setSubTitle("请选择服务器的认证方式")

        layout = QVBoxLayout()

        # 认证方式选择
        self.token_radio = QRadioButton("Token 认证")
        self.oidc_radio = QRadioButton("OIDC 认证")
        self.none_radio = QRadioButton("无需认证")

        self.token_radio.setChecked(True)

        layout.addWidget(self.token_radio)
        layout.addWidget(self.oidc_radio)
        layout.addWidget(self.none_radio)

        # 按钮组
        self.auth_group = QButtonGroup()
        self.auth_group.addButton(self.token_radio)
        self.auth_group.addButton(self.oidc_radio)
        self.auth_group.addButton(self.none_radio)

        self.setLayout(layout)

    def get_auth_type(self) -> AuthType:
        """获取选择的认证类型"""
        if self.token_radio.isChecked():
            return AuthType.TOKEN
        elif self.oidc_radio.isChecked():
            return AuthType.OIDC
        else:
            return AuthType.NONE

    def nextId(self):
        """根据选择的认证类型跳转到不同页面"""
        if self.token_radio.isChecked():
            return SetupWizard.PAGE_TOKEN
        elif self.oidc_radio.isChecked():
            return SetupWizard.PAGE_OIDC
        else:
            return SetupWizard.PAGE_TEST

class TokenAuthPage(QWizardPage):
    """Token 认证页面"""

    def __init__(self):
        super().__init__()
        self.setTitle("Token 认证")
        self.setSubTitle("请输入 FRP 服务器的认证令牌")

        layout = QFormLayout()

        # Token 输入
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("请输入服务器配置的 token")
        layout.addRow("认证令牌:", self.token_edit)

        # 显示/隐藏按钮
        show_token_btn = QPushButton("👁")
        show_token_btn.setFixedWidth(30)
        show_token_btn.clicked.connect(self.toggle_token_visibility)

        token_layout = QHBoxLayout()
        token_layout.addWidget(self.token_edit)
        token_layout.addWidget(show_token_btn)
        layout.insertRow(1, "认证令牌:", token_layout)

        # 验证规则
        self.registerField("token*", self.token_edit)

        self.setLayout(layout)

    def toggle_token_visibility(self):
        """切换 Token 可见性"""
        if self.token_edit.echoMode() == QLineEdit.Password:
            self.token_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.token_edit.setEchoMode(QLineEdit.Password)

    def validatePage(self):
        """页面验证"""
        token = self.token_edit.text().strip()
        if not token:
            QMessageBox.warning(self, "输入错误", "请输入认证令牌")
            return False
        return True

    def nextId(self):
        """下一步到测试页面"""
        return SetupWizard.PAGE_TEST

class OIDCAuthPage(QWizardPage):
    """OIDC 认证页面"""

    def __init__(self):
        super().__init__()
        self.setTitle("OIDC 认证")
        self.setSubTitle("请输入 OIDC 配置信息")

        layout = QFormLayout()

        # Client ID
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("OIDC 客户端 ID")
        layout.addRow("客户端 ID:", self.client_id_edit)

        # Client Secret
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setEchoMode(QLineEdit.Password)
        self.client_secret_edit.setPlaceholderText("OIDC 客户端密钥")
        layout.addRow("客户端密钥:", self.client_secret_edit)

        # Issuer URL
        self.issuer_url_edit = QLineEdit()
        self.issuer_url_edit.setPlaceholderText("https://auth.example.com")
        layout.addRow("Issuer URL:", self.issuer_url_edit)

        # Token Endpoint (可选)
        self.token_endpoint_edit = QLineEdit()
        self.token_endpoint_edit.setPlaceholderText("可选: 自定义 Token 端点")
        layout.addRow("Token 端点:", self.token_endpoint_edit)

        # 验证规则
        self.registerField("oidc_client_id*", self.client_id_edit)
        self.registerField("oidc_client_secret*", self.client_secret_edit)
        self.registerField("oidc_issuer_url*", self.issuer_url_edit)
        self.registerField("oidc_token_endpoint", self.token_endpoint_edit)

        self.setLayout(layout)

    def validatePage(self):
        """页面验证"""
        if not all([
            self.client_id_edit.text().strip(),
            self.client_secret_edit.text().strip(),
            self.issuer_url_edit.text().strip(),
        ]):
            QMessageBox.warning(self, "输入错误", "请填写所有必填字段")
            return False
        return True

    def nextId(self):
        """下一步到测试页面"""
        return SetupWizard.PAGE_TEST

class TestConnectionPage(QWizardPage):
    """连接测试页面"""

    test_complete = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.setTitle("连接测试")
        self.setSubTitle("正在测试与服务器的连接...")

        layout = QVBoxLayout()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定模式
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("正在连接到服务器...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 详细信息
        self.detail_label = QLabel("")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #888;")
        layout.addWidget(self.detail_label)

        self.setLayout(layout)

    def initializePage(self):
        """页面初始化时开始测试"""
        super().initializePage()
        self.start_test()

    def start_test(self):
        """开始连接测试"""
        # 这里实现实际的连接测试逻辑
        # 暂时模拟测试过程
        import threading
        import time

        def test_thread():
            time.sleep(2)  # 模拟连接测试

            # 模拟测试结果
            success = True
            message = "连接测试成功！服务器配置正确。"

            self.test_complete.emit(success, message)

        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()

    def on_test_complete(self, success: bool, message: str):
        """测试完成回调"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        if success:
            self.status_label.setText("✅ 连接测试成功")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText("❌ 连接测试失败")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")

        self.detail_label.setText(message)

        # 启用下一步按钮
        self.complete = True
        self.wizard().button(QWizard.NextButton).setEnabled(True)

    def isComplete(self):
        """页面是否完成"""
        return hasattr(self, 'complete') and self.complete

    def nextId(self):
        """下一步到完成页面"""
        return SetupWizard.PAGE_COMPLETE

class CompletionPage(QWizardPage):
    """完成页面"""

    def __init__(self):
        super().__init__()
        self.setTitle("配置完成")
        self.setSubTitle("服务器配置已保存")

        layout = QVBoxLayout()

        # 成功图标和消息
        self.success_label = QLabel("🎉 配置完成！")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        layout.addWidget(self.success_label)

        # 配置摘要
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.summary_label)

        # 提示信息
        tip_label = QLabel("点击【完成】按钮开始使用端口映射功能")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("color: #888;")
        layout.addWidget(tip_label)

        self.setLayout(layout)

    def initializePage(self):
        """页面初始化时显示配置摘要"""
        wizard = self.wizard()
        if wizard:
            summary = wizard.get_config_summary()
            self.summary_label.setText(summary)

class SetupWizard(QWizard):
    """配置向导主类"""

    # 页面ID
    PAGE_SERVER = 0
    PAGE_AUTH_TYPE = 1
    PAGE_TOKEN = 2
    PAGE_OIDC = 3
    PAGE_TEST = 4
    PAGE_COMPLETE = 5

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()

    def setup_ui(self):
        """设置向导界面"""
        self.setWindowTitle("服务器配置向导")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.IndependentPages, False)
        self.setOption(QWizard.CancelButtonOnLeft, True)

        # 设置向导大小
        self.setFixedSize(500, 400)

        # 添加页面
        self.addPage(ServerInfoPage())
        self.addPage(AuthTypePage())
        self.addPage(TokenAuthPage())
        self.addPage(OIDCAuthPage())
        self.addPage(TestConnectionPage())
        self.addPage(CompletionPage())

        # 设置页面ID
        self.setPage(self.PAGE_SERVER, self.page(self.PAGE_SERVER))
        self.setPage(self.PAGE_AUTH_TYPE, self.page(self.PAGE_AUTH_TYPE))
        self.setPage(self.PAGE_TOKEN, self.page(self.PAGE_TOKEN))
        self.setPage(self.PAGE_OIDC, self.page(self.PAGE_OIDC))
        self.setPage(self.PAGE_TEST, self.page(self.PAGE_TEST))
        self.setPage(self.PAGE_COMPLETE, self.page(self.PAGE_COMPLETE))

        # 连接信号
        self.currentIdChanged.connect(self.on_page_changed)

    def on_page_changed(self, page_id):
        """页面变化事件"""
        if page_id == self.PAGE_TEST:
            # 开始连接测试
            test_page = self.page(self.PAGE_TEST)
            test_page.test_complete.connect(test_page.on_test_complete)

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        summary = []

        # 服务器信息
        server_addr = self.field("server_addr")
        server_port = self.field("server_port")
        summary.append(f"服务器: {server_addr}:{server_port}")

        # 认证信息
        auth_page = self.page(self.PAGE_AUTH_TYPE)
        auth_type = auth_page.get_auth_type()

        if auth_type == AuthType.TOKEN:
            summary.append("认证方式: Token")
        elif auth_type == AuthType.OIDC:
            client_id = self.field("oidc_client_id")
            issuer = self.field("oidc_issuer_url")
            summary.append(f"认证方式: OIDC")
            summary.append(f"客户端: {client_id[:10]}...")
            summary.append(f"Issuer: {issuer}")
        else:
            summary.append("认证方式: 无")

        return "\n".join(summary)

    def save_config(self) -> bool:
        """保存配置到管理器"""
        try:
            # 获取服务器配置
            self.config_manager.server_config.server_addr = self.field("server_addr")
            self.config_manager.server_config.server_port = self.field("server_port")

            # 获取认证配置
            auth_page = self.page(self.PAGE_AUTH_TYPE)
            auth_type = auth_page.get_auth_type()
            self.config_manager.server_config.auth_type = auth_type

            if auth_type == AuthType.TOKEN:
                self.config_manager.server_config.token = self.field("token")
            elif auth_type == AuthType.OIDC:
                self.config_manager.server_config.oidc_client_id = self.field("oidc_client_id")
                self.config_manager.server_config.oidc_client_secret = self.field("oidc_client_secret")
                self.config_manager.server_config.oidc_issuer_url = self.field("oidc_issuer_url")
                self.config_manager.server_config.oidc_token_endpoint = self.field("oidc_token_endpoint")

            # 保存配置
            return self.config_manager.save()
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def exec_and_setup(self) -> bool:
        """执行向导并返回是否成功配置"""
        result = self.exec()

        if result == QWizard.Accepted:
            # 保存配置
            if self.save_config():
                QMessageBox.information(self, "成功", "服务器配置已保存！")
                return True
            else:
                QMessageBox.critical(self, "错误", "保存配置失败！")
                return False
        else:
            # 用户取消
            return False