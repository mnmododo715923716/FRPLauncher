#!/usr/bin/env python3
"""
PortMapper 打包脚本
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path


def clean_build():
    """清理构建文件"""
    for item in ['build', 'dist', '__pycache__']:
        if os.path.exists(item):
            shutil.rmtree(item)


def build_portmapper():
    """构建 PortMapper"""
    args = [
        'main.py',
        '--name=FRPLauncher',
        '--onefile',
        '--windowed',
        '--icon=resources/icons/app.ico',
        '--add-data=styles;styles',
        '--hidden-import=PyQt5',
        '--hidden-import=tomlkit',
        '--hidden-import=psutil',
        '--hidden-import=cryptography',
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--clean',
        '--noconfirm',
    ]

    PyInstaller.__main__.run(args)


def main():
    """主打包函数"""
    print("开始打包 PortMapper...")
    clean_build()
    build_portmapper()
    print("打包完成！可执行文件位于 dist/FRPLauncher.exe")


if __name__ == "__main__":
    main()