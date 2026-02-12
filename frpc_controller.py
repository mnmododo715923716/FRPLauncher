"""
FRP控制器 - 管理内网穿透连接
"""

import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import tomlkit
import shutil
import sys
import os

class ProxyStatus(Enum):
    """代理状态"""
    STOPPED = "已停止"
    STARTING = "启动中"
    RUNNING = "运行中"
    STOPPING = "停止中"
    ERROR = "错误"

@dataclass
class ProxyConfig:
    """代理配置"""
    name: str
    local_port: int
    remote_port: int
    protocol: str = "tcp"
    local_ip: str = "127.0.0.1"
    status: ProxyStatus = ProxyStatus.STOPPED
    process: Optional[subprocess.Popen] = None
    created_at: float = field(default_factory=time.time)

    @property
    def is_active(self) -> bool:
        """代理是否活跃（运行中）"""
        return self.status == ProxyStatus.RUNNING

class FrpcController:
    """FRP控制器类"""

    def __init__(self, config_path: Path):
        """
        初始化FRP控制器

        Args:
            config_path: frpc配置文件路径
        """
        self.config_path = config_path
        self.proxies: Dict[str, ProxyConfig] = {}
        self.frpc_process: Optional[subprocess.Popen] = None
        self._lock = threading.RLock()
        self._output_callback = None
        self._frpc_path = self._find_frpc()
        self._frpc_available = self._frpc_path is not None
        self._process_started = False  # 标记是否已成功启动进程

    def _find_frpc(self) -> Optional[str]:
        """
        查找 frpc 可执行文件

        Returns:
            frpc 路径，未找到则返回 None
        """
        # 1. 环境变量 PATH 中查找
        frpc_path = shutil.which('frpc')
        if frpc_path:
            print(f"在 PATH 中找到 frpc: {frpc_path}")
            return frpc_path

        # 2. 当前目录查找
        current_dir = Path(__file__).parent
        possible_paths = [
            current_dir / 'frpc',
            current_dir / 'frpc.exe',
            current_dir.parent / 'frpc',
            current_dir.parent / 'frpc.exe',
        ]
        for path in possible_paths:
            if path.exists():
                print(f"在当前目录找到 frpc: {path}")
                return str(path)

        # 3. 常见安装路径
        if sys.platform == "win32":
            common_paths = [
                Path('C:/frp/frpc.exe'),
                Path.home() / 'frp/frpc.exe',
                Path('C:/Program Files/frp/frpc.exe'),
                Path('C:/Program Files (x86)/frp/frpc.exe'),
            ]
        else:
            common_paths = [
                Path('/usr/local/bin/frpc'),
                Path('/usr/bin/frpc'),
                Path.home() / '.local/bin/frpc',
                Path('/opt/frp/frpc'),
            ]

        for path in common_paths:
            if path.exists():
                print(f"在系统路径找到 frpc: {path}")
                return str(path)

        # 未找到
        print("未找到 frpc 可执行文件")
        return None

    def is_frpc_available(self) -> bool:
        """检查 frpc 是否可用（仅检查文件是否存在，不验证版本）"""
        return self._frpc_available

    def get_frpc_path(self) -> Optional[str]:
        """获取 frpc 路径"""
        return self._frpc_path

    def test_frpc_version(self) -> Tuple[bool, str]:
        """
        测试 frpc 版本，验证可执行文件是否正常工作

        Returns:
            (是否成功, 版本信息或错误信息)
        """
        if not self._frpc_path:
            return False, "未找到 frpc 可执行文件"

        try:
            result = subprocess.run(
                [self._frpc_path, '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version
            else:
                error = result.stderr.strip()
                return False, f"frpc 版本检查失败: {error}"
        except FileNotFoundError:
            return False, f"frpc 文件不存在: {self._frpc_path}"
        except PermissionError:
            return False, f"frpc 没有执行权限: {self._frpc_path}"
        except subprocess.TimeoutExpired:
            return False, "frpc 版本检查超时"
        except Exception as e:
            return False, f"frpc 版本检查异常: {str(e)}"

    def add_proxy(self, local_port: int, remote_port: int = None,
                  protocol: str = "tcp") -> Tuple[bool, str]:
        """
        添加代理

        Args:
            local_port: 本地端口
            remote_port: 远程端口（默认与本地端口相同）
            protocol: 协议类型

        Returns:
            (成功, 消息)
        """
        # 检查 frpc 是否可用
        if not self._frpc_available:
            return False, "frpc 不可用，未找到 frpc 可执行文件。请将 frpc 放入程序目录或添加到 PATH"

        if remote_port is None:
            remote_port = local_port

        # 生成代理名称
        proxy_name = f"{protocol}_{local_port}_to_{remote_port}"

        with self._lock:
            if proxy_name in self.proxies:
                return False, f"代理 {proxy_name} 已存在"

            # 创建代理配置
            proxy = ProxyConfig(
                name=proxy_name,
                local_port=local_port,
                remote_port=remote_port,
                protocol=protocol
            )

            self.proxies[proxy_name] = proxy

            # 更新配置文件
            if self._update_config():
                return True, f"已添加代理: {proxy_name}"
            else:
                del self.proxies[proxy_name]
                return False, "更新配置文件失败"

    def remove_proxy(self, proxy_name: str) -> bool:
        """
        移除代理

        Args:
            proxy_name: 代理名称

        Returns:
            是否成功
        """
        with self._lock:
            if proxy_name not in self.proxies:
                return False

            # 停止代理
            proxy = self.proxies[proxy_name]
            if proxy.status == ProxyStatus.RUNNING:
                self._stop_proxy(proxy)

            # 移除代理
            del self.proxies[proxy_name]

            # 更新配置文件
            return self._update_config()

    def start_proxy(self, proxy_name: str) -> Tuple[bool, str]:
        """
        启动代理

        Args:
            proxy_name: 代理名称

        Returns:
            (成功, 消息)
        """
        with self._lock:
            if proxy_name not in self.proxies:
                return False, f"代理 {proxy_name} 不存在"

            proxy = self.proxies[proxy_name]

            if proxy.status == ProxyStatus.RUNNING:
                return True, "代理已在运行中"

            try:
                # 检查 frpc 可用性
                if not self._frpc_available:
                    return False, "frpc 不可用，未找到 frpc 可执行文件"

                # 测试 frpc 版本，确保可执行文件正常
                version_ok, version_msg = self.test_frpc_version()
                if not version_ok:
                    return False, f"frpc 可执行文件异常: {version_msg}"

                print(f"使用 frpc 版本: {version_msg}")

                # 启动 frpc 进程（如果未启动）
                if self.frpc_process is None or self.frpc_process.poll() is not None:
                    start_ok, start_msg = self._start_frpc()
                    if not start_ok:
                        return False, f"启动 frpc 失败: {start_msg}"

                proxy.status = ProxyStatus.RUNNING
                return True, f"已启动代理: {proxy_name}"

            except Exception as e:
                proxy.status = ProxyStatus.ERROR
                return False, f"启动代理失败: {str(e)}"

    def stop_proxy(self, proxy_name: str) -> bool:
        """
        停止代理

        Args:
            proxy_name: 代理名称

        Returns:
            是否成功
        """
        with self._lock:
            if proxy_name not in self.proxies:
                return False

            proxy = self.proxies[proxy_name]

            if proxy.status == ProxyStatus.STOPPED:
                return True

            return self._stop_proxy(proxy)

    def toggle_proxy(self, proxy_name: str) -> Tuple[bool, str]:
        """
        切换代理状态

        Args:
            proxy_name: 代理名称

        Returns:
            (成功, 消息)
        """
        with self._lock:
            if proxy_name not in self.proxies:
                return False, f"代理 {proxy_name} 不存在"

            proxy = self.proxies[proxy_name]

            if proxy.status == ProxyStatus.RUNNING:
                success = self._stop_proxy(proxy)
                if success:
                    return True, f"已停止代理: {proxy_name}"
                else:
                    return False, "停止代理失败"
            else:
                return self.start_proxy(proxy_name)

    def get_proxy_status(self, proxy_name: str) -> Optional[ProxyStatus]:
        """
        获取代理状态

        Args:
            proxy_name: 代理名称

        Returns:
            代理状态
        """
        with self._lock:
            proxy = self.proxies.get(proxy_name)
            return proxy.status if proxy else None

    def get_all_proxies(self) -> List[ProxyConfig]:
        """
        获取所有代理

        Returns:
            代理列表
        """
        with self._lock:
            return list(self.proxies.values())

    def get_active_proxies(self) -> List[ProxyConfig]:
        """
        获取活跃（运行中）的代理

        Returns:
            活跃代理列表
        """
        with self._lock:
            return [p for p in self.proxies.values() if p.is_active]

    def get_proxy_by_local_port(self, local_port: int) -> Optional[ProxyConfig]:
        """
        根据本地端口查找代理

        Args:
            local_port: 本地端口号

        Returns:
            代理配置
        """
        with self._lock:
            for proxy in self.proxies.values():
                if proxy.local_port == local_port:
                    return proxy
            return None

    def _update_config(self) -> bool:
        """
        更新 frpc 配置文件 - 保留 common 部分，只更新代理配置

        Returns:
            是否成功
        """
        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 读取现有完整配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = tomlkit.load(f)
            else:
                # 配置文件不存在，创建一个包含 common 部分的基础配置
                config_data = tomlkit.document()
                # common 部分会在后续从 config_manager 获取？这里先创建空文档，后续会添加代理
                # 但为了 frpc 能启动，需要 common 部分。所以如果配置文件完全不存在，我们创建一个空的，然后在 start_frpc 前必须确保 common 存在
                # 更好的方式：在 start_frpc 时检查 common 部分，如果没有则报错
                pass

            # 移除旧的代理配置（保留非代理部分，如 common）
            keys_to_remove = []
            for key in config_data.keys():
                if key.startswith(('tcp_', 'udp_', 'http_', 'https_')):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del config_data[key]

            # 添加新的代理配置
            for proxy in self.proxies.values():
                proxy_config = {
                    'type': proxy.protocol,
                    'local_ip': proxy.local_ip,
                    'local_port': proxy.local_port,
                    'remote_port': proxy.remote_port,
                }
                config_data[proxy.name] = proxy_config

            # 写入配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                tomlkit.dump(config_data, f)

            return True
        except Exception as e:
            print(f"更新配置文件失败: {e}")
            return False

    def _start_frpc(self) -> Tuple[bool, str]:
        """
        启动 frpc 进程 - 增强版错误检测

        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 查找 frpc 可执行文件
            if not self._frpc_path:
                return False, "未找到 frpc 可执行文件"

            # 检查配置文件是否存在
            if not self.config_path.exists():
                return False, f"配置文件不存在: {self.config_path}"

            # 验证配置文件是否包含必要的 common 部分
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = tomlkit.load(f)
                if 'common' not in config_data:
                    return False, "配置文件中缺少 [common] 部分，请先在服务器设置中配置服务器信息"
            except Exception as e:
                return False, f"读取配置文件失败: {str(e)}"

            # 验证配置文件语法
            verify_cmd = [self._frpc_path, 'verify', '-c', str(self.config_path)]
            verify_result = subprocess.run(
                verify_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if verify_result.returncode != 0:
                error_msg = verify_result.stderr.strip()
                return False, f"配置文件验证失败: {error_msg}"

            # 启动 frpc
            try:
                self.frpc_process = subprocess.Popen(
                    [self._frpc_path, '-c', str(self.config_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    bufsize=1
                )
            except Exception as e:
                return False, f"启动进程失败: {str(e)}"

            # 等待一小段时间，收集初始输出
            time.sleep(0.5)

            # 检查进程是否仍在运行
            retcode = self.frpc_process.poll()
            if retcode is not None:
                # 进程已退出，读取所有输出
                try:
                    output, _ = self.frpc_process.communicate(timeout=2)
                    error_info = output[:500] if output else "无输出"
                except subprocess.TimeoutExpired:
                    self.frpc_process.kill()
                    output, _ = self.frpc_process.communicate()
                    error_info = output[:500] if output else "进程超时被强制终止"
                except Exception as e:
                    error_info = f"无法读取进程输出: {str(e)}"
                return False, f"frpc 启动后立即退出 (返回码: {retcode}): {error_info}"

            # 进程仍在运行，启动成功
            # 启动输出读取线程
            thread = threading.Thread(
                target=self._read_frpc_output,
                daemon=True
            )
            thread.start()

            print(f"frpc 进程已启动，PID: {self.frpc_process.pid}")
            return True, "frpc 启动成功"

        except subprocess.TimeoutExpired:
            return False, "配置文件验证超时"
        except FileNotFoundError:
            return False, f"frpc 文件不存在: {self._frpc_path}"
        except PermissionError:
            return False, f"frpc 没有执行权限: {self._frpc_path}"
        except Exception as e:
            return False, f"启动 frpc 异常: {str(e)}"

    def _stop_proxy(self, proxy: ProxyConfig) -> bool:
        """
        停止代理

        Args:
            proxy: 代理配置

        Returns:
            是否成功
        """
        try:
            # 实际上，frpc 不支持动态停止单个代理
            # 我们需要重新加载配置
            proxy.status = ProxyStatus.STOPPED

            # 更新配置文件（移除该代理）
            if self._update_config():
                # 发送 SIGHUP 信号让 frpc 重新加载配置
                if self.frpc_process:
                    import signal
                    try:
                        # Windows 不支持 SIGHUP，使用发送空字符串或其他方式
                        if sys.platform == "win32":
                            # Windows 下通过重新启动 frpc 来重新加载配置
                            self.frpc_process.terminate()
                            self.frpc_process = None
                            return self._start_frpc()[0]
                        else:
                            self.frpc_process.send_signal(signal.SIGHUP)
                            return True
                    except Exception as e:
                        print(f"发送信号失败: {e}, 尝试重启 frpc")
                        if self.frpc_process:
                            self.frpc_process.terminate()
                            self.frpc_process = None
                        return self._start_frpc()[0]
                return True
            return False

        except Exception as e:
            print(f"停止代理失败: {e}")
            return False

    def _read_frpc_output(self):
        """读取 frpc 输出"""
        if self.frpc_process is None:
            return

        while True:
            if self.frpc_process.stdout:
                try:
                    line = self.frpc_process.stdout.readline()
                    if not line:
                        break
                    if self._output_callback:
                        self._output_callback(line.strip())
                except Exception as e:
                    print(f"读取 frpc 输出失败: {e}")
                    break

    def set_output_callback(self, callback):
        """设置输出回调"""
        self._output_callback = callback

    def stop_all(self):
        """停止所有代理和 frpc 进程"""
        with self._lock:
            # 停止所有代理
            for proxy in self.proxies.values():
                proxy.status = ProxyStatus.STOPPED

            # 停止 frpc 进程
            if self.frpc_process:
                try:
                    self.frpc_process.terminate()
                    self.frpc_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.frpc_process.kill()
                except Exception as e:
                    print(f"停止 frpc 进程失败: {e}")
                finally:
                    self.frpc_process = None