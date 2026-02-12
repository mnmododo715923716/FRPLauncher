"""
配置管理器 - 负责服务器配置的检测、保存和验证
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import tomlkit

class AuthType(Enum):
    """认证类型"""
    TOKEN = "token"
    OIDC = "oidc"
    NONE = "none"

@dataclass
class ServerConfig:
    """服务器配置数据类"""
    server_addr: str = ""
    server_port: int = 7000
    auth_type: AuthType = AuthType.NONE
    token: str = ""

    # OIDC 配置
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_issuer_url: str = ""
    oidc_token_endpoint: str = ""

    # 加密存储的敏感信息
    _encrypted_data: Optional[bytes] = None

    def is_complete(self) -> bool:
        """检查配置是否完整"""
        if not self.server_addr or self.server_port == 0:
            return False

        if self.auth_type == AuthType.TOKEN:
            return bool(self.token)
        elif self.auth_type == AuthType.OIDC:
            return (bool(self.oidc_client_id) and
                    bool(self.oidc_client_secret) and
                    bool(self.oidc_issuer_url))
        elif self.auth_type == AuthType.NONE:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含敏感信息）"""
        data = {
            "server_addr": self.server_addr,
            "server_port": self.server_port,
            "auth_type": self.auth_type.value,
        }

        # 根据认证类型添加相应字段
        if self.auth_type == AuthType.TOKEN and self.token:
            data["token"] = "[ENCRYPTED]"
        elif self.auth_type == AuthType.OIDC:
            data.update({
                "oidc_client_id": self.oidc_client_id,
                "oidc_issuer_url": self.oidc_issuer_url,
            })

        return data

@dataclass
class AppConfig:
    """应用程序配置"""
    scan_interval: int = 30  # 端口扫描间隔，单位：秒（默认30秒）
    ui_refresh_interval: int = 10  # UI刷新间隔，单位：秒（默认10秒）
    show_system_ports: bool = False  # 是否显示系统端口（<1024）
    auto_start_proxy: bool = True  # 添加代理后自动启动
    minimize_to_tray: bool = True  # 关闭窗口时最小化到托盘

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "scan_interval": self.scan_interval,
            "ui_refresh_interval": self.ui_refresh_interval,
            "show_system_ports": self.show_system_ports,
            "auto_start_proxy": self.auto_start_proxy,
            "minimize_to_tray": self.minimize_to_tray,
        }

class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置目录路径
        """
        if config_dir is None:
            # 使用用户目录下的 .portmapper 文件夹
            home_dir = Path.home()
            self.config_dir = home_dir / ".portmapper"
        else:
            self.config_dir = Path(config_dir)

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.config_file = self.config_dir / "config.json"
        self.app_config_file = self.config_dir / "app_config.json"
        self.frpc_config_file = self.config_dir / "frpc.toml"

        # 当前配置
        self.server_config = ServerConfig()
        self.app_config = AppConfig()

        # 加载现有配置
        self.load()

    def get_encryption_key(self) -> bytes:
        """生成加密密钥（基于机器特征）"""
        # 使用机器名和用户名生成密钥
        import getpass
        import socket

        machine_info = f"{socket.gethostname()}_{getpass.getuser()}"
        key = hashlib.sha256(machine_info.encode()).digest()
        return key[:32]  # 使用前32字节作为AES密钥

    def encrypt_data(self, data: str) -> bytes:
        """加密敏感数据"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

            # 生成密钥
            key = self.get_encryption_key()

            # 使用Fernet加密
            f = Fernet(base64.urlsafe_b64encode(key))
            encrypted = f.encrypt(data.encode())
            return encrypted
        except ImportError:
            # 如果cryptography不可用，使用简单的base64编码
            return base64.b64encode(data.encode())
        except Exception as e:
            print(f"加密失败: {e}")
            return data.encode()

    def decrypt_data(self, encrypted: bytes) -> str:
        """解密数据"""
        try:
            from cryptography.fernet import Fernet

            key = self.get_encryption_key()
            f = Fernet(base64.urlsafe_b64encode(key))
            decrypted = f.decrypt(encrypted)
            return decrypted.decode()
        except:
            # 回退到base64解码
            try:
                return base64.b64decode(encrypted).decode()
            except:
                return encrypted.decode()

    def load(self) -> bool:
        """加载配置文件"""
        try:
            # 加载服务器配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 加载基本配置
                self.server_config = ServerConfig(
                    server_addr=data.get('server_addr', ''),
                    server_port=data.get('server_port', 7000),
                    auth_type=AuthType(data.get('auth_type', 'none')),
                )

                # 加载加密的敏感数据
                encrypted_token = data.get('encrypted_token')
                if encrypted_token:
                    self.server_config.token = self.decrypt_data(
                        base64.b64decode(encrypted_token)
                    )

                # 加载OIDC配置
                self.server_config.oidc_client_id = data.get('oidc_client_id', '')
                oidc_secret = data.get('encrypted_oidc_secret')
                if oidc_secret:
                    self.server_config.oidc_client_secret = self.decrypt_data(
                        base64.b64decode(oidc_secret)
                    )
                self.server_config.oidc_issuer_url = data.get('oidc_issuer_url', '')
                self.server_config.oidc_token_endpoint = data.get('oidc_token_endpoint', '')

            # 加载应用程序配置
            if self.app_config_file.exists():
                with open(self.app_config_file, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)

                self.app_config = AppConfig(
                    scan_interval=app_data.get('scan_interval', 30),
                    ui_refresh_interval=app_data.get('ui_refresh_interval', 10),
                    show_system_ports=app_data.get('show_system_ports', False),
                    auto_start_proxy=app_data.get('auto_start_proxy', True),
                    minimize_to_tray=app_data.get('minimize_to_tray', True),
                )

            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def save(self) -> bool:
        """保存配置文件"""
        try:
            # 准备服务器配置数据
            data = {
                'server_addr': self.server_config.server_addr,
                'server_port': self.server_config.server_port,
                'auth_type': self.server_config.auth_type.value,
            }

            # 加密并保存敏感数据
            if self.server_config.auth_type == AuthType.TOKEN and self.server_config.token:
                encrypted = self.encrypt_data(self.server_config.token)
                data['encrypted_token'] = base64.b64encode(encrypted).decode()

            elif self.server_config.auth_type == AuthType.OIDC:
                data['oidc_client_id'] = self.server_config.oidc_client_id
                if self.server_config.oidc_client_secret:
                    encrypted = self.encrypt_data(self.server_config.oidc_client_secret)
                    data['encrypted_oidc_secret'] = base64.b64encode(encrypted).decode()
                data['oidc_issuer_url'] = self.server_config.oidc_issuer_url
                data['oidc_token_endpoint'] = self.server_config.oidc_token_endpoint

            # 写入服务器配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # 准备应用程序配置数据
            app_data = self.app_config.to_dict()

            # 写入应用程序配置文件
            with open(self.app_config_file, 'w', encoding='utf-8') as f:
                json.dump(app_data, f, indent=2, ensure_ascii=False)

            # 同时更新 frpc.toml 文件
            self.update_frpc_config()

            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def update_frpc_config(self):
        """更新 frpc.toml 配置文件"""
        try:
            config_data = {}

            # 添加 common 部分
            config_data['common'] = {
                'server_addr': self.server_config.server_addr,
                'server_port': self.server_config.server_port,
            }

            # 添加认证信息
            if self.server_config.auth_type == AuthType.TOKEN:
                config_data['common']['token'] = self.server_config.token
            elif self.server_config.auth_type == AuthType.OIDC:
                # OIDC 配置需要特殊处理
                config_data['common']['oidc'] = {
                    'client_id': self.server_config.oidc_client_id,
                    'client_secret': self.server_config.oidc_client_secret,
                    'issuer_url': self.server_config.oidc_issuer_url,
                }
                if self.server_config.oidc_token_endpoint:
                    config_data['common']['oidc']['token_endpoint'] = \
                        self.server_config.oidc_token_endpoint

            # 写入 TOML 文件
            with open(self.frpc_config_file, 'w', encoding='utf-8') as f:
                tomlkit.dump(config_data, f)

        except Exception as e:
            print(f"更新 frpc 配置失败: {e}")

    def is_complete(self) -> bool:
        """检查配置是否完整"""
        return self.server_config.is_complete()

    def get_frpc_config_path(self) -> Path:
        """获取 frpc 配置文件路径"""
        return self.frpc_config_file

    def clear(self):
        """清除所有配置"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            if self.app_config_file.exists():
                self.app_config_file.unlink()
            if self.frpc_config_file.exists():
                self.frpc_config_file.unlink()
            self.server_config = ServerConfig()
            self.app_config = AppConfig()
        except Exception as e:
            print(f"清除配置失败: {e}")

    def set_scan_interval(self, interval: int):
        """设置扫描间隔"""
        if interval < 5:
            interval = 5  # 最小5秒
        elif interval > 300:
            interval = 300  # 最大5分钟
        self.app_config.scan_interval = interval

    def set_ui_refresh_interval(self, interval: int):
        """设置UI刷新间隔"""
        if interval < 2:
            interval = 2  # 最小2秒
        elif interval > 60:
            interval = 60  # 最大1分钟
        self.app_config.ui_refresh_interval = interval

    def get_scan_interval(self) -> int:
        """获取扫描间隔"""
        return self.app_config.scan_interval

    def get_ui_refresh_interval(self) -> int:
        """获取UI刷新间隔"""
        return self.app_config.ui_refresh_interval