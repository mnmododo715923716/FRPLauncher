# FRPLauncher

FRPLauncher(原名PortMapper) 是一个基于 PyQt5 的图形化 FRP 客户端管理工具，旨在简化内网穿透的配置与操作。它能够自动扫描本地监听端口，通过点击即可快速创建/关闭 FRP 端口映射，并支持 Token / OIDC 认证、系统托盘、扫描频率自定义等特性。

---

## ✨ 特性

- 🔍 **自动端口扫描**：实时检测本机所有处于 `LISTEN` 状态的端口，并显示对应的进程名称。
- 🖱️ **一键映射**：点击任意端口，输入远程端口即可快速添加 FRP 代理；再次点击已映射端口即可关闭。
- 🔐 **认证支持**：支持 Token 认证和 OIDC 认证，配置向导引导完成服务器设置。
- ⚙️ **灵活配置**：可调整端口扫描间隔、UI刷新频率、是否自动启动代理等。
- 🧩 **系统托盘**：关闭窗口时自动最小化到托盘，双击托盘图标恢复主界面。
- 📦 **独立运行**：无需手动编写 FRP 配置文件，所有代理配置自动维护。

---

## 🚀 快速开始

### 1. 环境准备

#### 使用 Conda 创建虚拟环境（推荐）

```bash
# 创建 Python 3.9 环境
conda create -n frplauncher python=3.9
conda activate frplauncher

# 安装依赖
pip install PyQt5 tomlkit psutil cryptography
```

#### 下载 FRP 客户端

从 [FRP Releases](https://github.com/fatedier/frp/releases) 下载对应平台的 `frpc` 可执行文件：

- Windows: `frpc.exe`
- Linux/macOS: `frpc`

将 `frpc` 放入以下任一位置（程序会自动查找）：
- 当前工作目录
- 系统 PATH 环境变量包含的目录
- `C:/frp/` (Windows) 或 `/usr/local/bin/` (Linux)

### 2. 运行程序

```bash
python main.py
```

首次运行将自动弹出**服务器配置向导**，依次设置：
- FRP 服务器地址、端口
- 认证方式（Token / OIDC / 无）

配置完成后即可进入主界面。

---

## 📖 使用指南

### 主界面布局

- **端口列表**：展示所有本地监听端口，绿色表示已映射，蓝色表示可映射，红色表示 frpc 不可用。
- **状态栏**：显示 frpc 可用状态、端口总数、活跃映射数、当前扫描间隔。
- **控制按钮**：
  - 🔄 刷新端口：立即重新扫描。
  - ⚙️ 服务器设置：修改 FRP 服务器信息。
  - 📊 应用设置：调整扫描间隔、UI刷新间隔、自动启动代理等。
  - ❌ 退出：完全退出程序。

### 端口操作

- **开启映射**：点击未映射的端口 → 输入远程端口 → 自动添加并启动代理。
- **关闭映射**：点击已映射的端口 → 确认后移除代理。
- **frpc 不可用时**：端口显示为红色，点击会提示安装指引。

### 系统托盘

- 关闭主窗口默认最小化到托盘。
- 右键托盘图标可快速：显示主窗口、刷新端口、打开设置、退出程序。

---

## 🛠️ 配置说明

配置文件保存在用户目录的 `.portmapper/` 文件夹下：

| 文件 | 说明 |
|------|------|
| `config.json` | 服务器配置（加密存储 Token/Secret） |
| `app_config.json` | 应用程序设置（扫描间隔、行为选项） |
| `frpc.toml` | 自动生成的 FRP 客户端配置文件 |

可通过“应用设置”对话框修改扫描参数，修改后立即生效。

---

## 📦 打包为独立可执行文件

使用 PyInstaller 打包成单个 exe 文件（以 Windows 为例）：

```bash
# 激活虚拟环境
conda activate frplauncher

# 安装 PyInstaller
pip install pyinstaller

# 执行打包命令
pyinstaller --onefile --windowed --name FRPLauncher --icon=resources/icon.ico main.py
```

> **提示**：如果未准备图标文件，可省略 `--icon` 参数。打包后的 exe 位于 `dist/FRPLauncher.exe`。

**注意事项**：
- 打包后需将 `frpc.exe` 与生成的 `FRPLauncher.exe` 放置于**同一目录**，或确保 frpc 在系统 PATH 中。
- 若需添加版本信息，可使用 `--version-file` 参数。

---

## ❓ 常见问题

**Q: 为什么端口扫描不到？**  
A: 请以管理员身份运行程序（部分系统端口需要较高权限才能读取进程信息）。

**Q: 添加映射时提示“frpc 不可用”**  
A: 请确认 frpc 可执行文件已下载并放置在正确位置，且具有执行权限。

**Q: 如何修改服务器配置？**  
A: 主界面点击“⚙️ 服务器设置”即可重新运行配置向导。

**Q: 配置文件可以手动编辑吗？**  
A: 不建议手动编辑，程序会自动维护。如需重置，直接删除 `~/.portmapper` 文件夹即可。

---

## 📄 许可证

本项目基于 Apache-2.0 许可证开源。

---

**FRPLauncher** – 让内网穿透更简单。
