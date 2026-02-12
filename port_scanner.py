"""
端口扫描器 - 检测本地监听的端口
"""

import psutil
import socket
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading
import time
import traceback

from PyQt5.QtCore import QObject, pyqtSignal

@dataclass
class PortInfo:
    """端口信息"""
    port: int
    protocol: str  # tcp/udp
    pid: int
    process_name: str
    local_addr: str
    status: str
    create_time: float

    @property
    def display_name(self) -> str:
        """显示名称"""
        if self.process_name:
            return f"{self.process_name} ({self.port})"
        return f"端口 {self.port}"

    @property
    def is_listening(self) -> bool:
        """是否在监听状态"""
        return self.status == 'LISTEN'

class PortScanner(QObject):
    """端口扫描器类"""

    # 定义信号
    ports_updated = pyqtSignal(list, list, list)  # added, removed, changed

    def __init__(self, update_interval: int = 5):
        """
        初始化端口扫描器

        Args:
            update_interval: 更新间隔（秒）
        """
        super().__init__()
        self.update_interval = update_interval
        self.ports: Dict[str, PortInfo] = {}
        self._running = False
        self._thread = None
        self._lock = threading.RLock()

    def start(self):
        """启动端口扫描"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()
        print(f"端口扫描器已启动，更新间隔: {self.update_interval}秒")

    def stop(self):
        """停止端口扫描"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("端口扫描器已停止")

    def _scan_loop(self):
        """扫描循环"""
        while self._running:
            try:
                self.scan_ports()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"端口扫描错误: {e}")
                time.sleep(self.update_interval)

    def scan_ports(self):
        """扫描所有监听端口"""
        new_ports = {}

        try:
            # 获取所有网络连接
            connections = psutil.net_connections(kind='inet')

            for conn in connections:
                # 检查是否在监听状态
                if conn.status == 'LISTEN' and conn.laddr:
                    port = conn.laddr.port
                    protocol = 'tcp' if conn.type == socket.SOCK_STREAM else 'udp'

                    # 获取进程信息
                    pid = conn.pid
                    process_name = ""

                    if pid:
                        try:
                            proc = psutil.Process(pid)
                            process_name = proc.name()

                            # 尝试获取命令行信息（更详细）
                            try:
                                cmdline = " ".join(proc.cmdline())
                                if cmdline:
                                    # 提取可执行文件名
                                    import os
                                    exe_name = os.path.basename(cmdline.split()[0])
                                    if exe_name:
                                        process_name = exe_name
                            except:
                                pass

                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "系统进程"

                    # 创建唯一的键值
                    key = f"{port}_{protocol}_{pid}"

                    # 创建端口信息
                    port_info = PortInfo(
                        port=port,
                        protocol=protocol,
                        pid=pid,
                        process_name=process_name,
                        local_addr=conn.laddr.ip,
                        status=conn.status,
                        create_time=datetime.now().timestamp()
                    )

                    new_ports[key] = port_info

            # 调试信息
            if len(new_ports) > 0:
                print(f"扫描完成: 找到 {len(new_ports)} 个监听端口")
            else:
                print("扫描完成: 未找到监听端口")

        except Exception as e:
            print(f"扫描端口失败: {e}")
            traceback.print_exc()

        # 更新端口列表
        with self._lock:
            old_ports = self.ports.copy()
            self.ports = new_ports

        # 找出变化的端口
        added = []
        removed = []
        changed = []

        # 找出新增的端口
        for key in new_ports:
            if key not in old_ports:
                added.append(new_ports[key])

        # 找出移除的端口
        for key in old_ports:
            if key not in new_ports:
                removed.append(old_ports[key])

        # 找出状态变化的端口
        for key in new_ports:
            if key in old_ports:
                old_status = old_ports[key].status
                new_status = new_ports[key].status
                if old_status != new_status:
                    changed.append(new_ports[key])

        # 如果检测到变化，发射信号
        if added or removed or changed:
            self.ports_updated.emit(added, removed, changed)

    def get_listening_ports(self) -> List[PortInfo]:
        """获取所有监听端口"""
        with self._lock:
            return [p for p in self.ports.values() if p.is_listening]

    def get_port_by_number(self, port: int) -> List[PortInfo]:
        """根据端口号获取端口信息"""
        with self._lock:
            return [p for p in self.ports.values()
                   if p.port == port and p.is_listening]

    def is_port_listening(self, port: int) -> bool:
        """检查端口是否在监听"""
        ports = self.get_port_by_number(port)
        return len(ports) > 0