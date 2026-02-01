#!/bin/bash

# OmniGate Pro - One-line Installer
# Compatible with Linux, macOS, and Windows (WSL)
# Supports x86_64 and arm64

set -e

# --- 1. 彩色日志与图标 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

LOG_INFO="${BLUE}[INFO]${NC}"
LOG_SUCCESS="${GREEN}[SUCCESS]${NC}"
LOG_WARN="${YELLOW}[WARN]${NC}"
LOG_ERROR="${RED}[ERROR]${NC}"

echo -e "${CYAN}"
echo "  ____                 _  _____       _         ____                 "
echo " / __ \               (_)/ ____|     | |       |  _ \                "
echo "| |  | |_ __ ___  _ __  | |  __  __ _| |_ ___  | |_) |_ __ ___       "
echo "| |  | | '_ \` _ \| '_ \ | | |_ |/ _\` | __/ _ \ |  ___/| '__/ _ \      "
echo "| |__| | | | | | | | | || |__| | (_| | ||  __/ | |    | | | (_) |     "
echo " \____/|_| |_| |_|_| |_| \_____|\__,_|\__\___| |_|    |_|  \___/      "
echo -e "${NC}"
echo -e "OmniGate Pro - Clawdbot 核心增强插件安装程序"
echo "------------------------------------------------"

# --- 2. 环境验证 ---
OS="$(uname -s)"
ARCH="$(uname -m)"
INSTALL_DIR="$HOME/.omnigate"
REPO_URL="https://github.com/abwoo/OmniGatePro.git"

echo -e "$LOG_INFO 检测系统环境: $OS ($ARCH)"

# --- 3. 依赖检测与安装提示 ---
check_command() {
    command -v "$1" >/dev/null 2>&1
}

install_system_deps() {
    echo -e "$LOG_INFO 正在尝试自动安装系统依赖..."
    if [[ "$OS" == "Linux" ]]; then
        if check_command apt-get; then
            sudo apt-get update && sudo apt-get install -y git python3 python3-venv nodejs npm
        elif check_command yum; then
            sudo yum install -y git python3 nodejs npm
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        if check_command brew; then
            brew install git python node pnpm
        else
            echo -e "$LOG_WARN 未检测到 Homebrew，请先安装 Homebrew 或手动安装依赖。"
        fi
    fi
}

echo -e "$LOG_INFO 检查基础依赖..."
MISSING_DEPS=0
for cmd in git python3 node pnpm; do
    if ! check_command "$cmd"; then
        echo -e "$LOG_WARN 缺少命令: $cmd"
        MISSING_DEPS=1
    fi
done

if [[ $MISSING_DEPS -eq 1 ]]; then
    read -p "是否尝试自动安装缺失的系统依赖? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_deps
    else
        echo -e "$LOG_ERROR 请手动安装依赖后再运行此脚本。"
        exit 1
    fi
fi

# --- 4. 源码下载与构建 ---
if [ -d "$INSTALL_DIR" ]; then
    echo -e "$LOG_WARN 发现已存在的安装目录 $INSTALL_DIR，正在更新..."
    cd "$INSTALL_DIR" && git pull
else
    echo -e "$LOG_INFO 正在下载 OmniGate Pro 源码..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# --- 5. Python 环境与依赖 ---
echo -e "$LOG_INFO 配置 Python 虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# --- 6. OpenClaw 环境构建 ---
echo -e "$LOG_INFO 构建 OpenClaw 核心组件..."
if [ -d "openclaw/openclaw" ]; then
    cd openclaw/openclaw
    pnpm install
    pnpm ui:build
    pnpm build
    cd ../..
fi

# --- 7. PATH 配置与权限 ---
echo -e "$LOG_INFO 配置 PATH 环境变量..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat << EOF > "$BIN_DIR/omni"
#!/bin/bash
source "$INSTALL_DIR/.venv/bin/activate"
python3 "$INSTALL_DIR/cli.py" "\$@"
EOF
chmod +x "$BIN_DIR/omni"

# 检查 PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    [[ "$SHELL" == */zsh ]] && SHELL_RC="$HOME/.zshrc"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    echo -e "$LOG_INFO 已将 $BIN_DIR 添加到 $SHELL_RC"
    echo -e "$LOG_WARN 请运行 'source $SHELL_RC' 或重启终端以生效。"
fi

# --- 8. 卸载脚本生成 ---
echo -e "$LOG_INFO 生成卸载脚本..."
cat << EOF > "$INSTALL_DIR/uninstall.sh"
#!/bin/bash
echo "正在卸载 OmniGate Pro..."
rm -rf "$INSTALL_DIR"
rm "$BIN_DIR/omni"
echo "卸载完成。"
EOF
chmod +x "$INSTALL_DIR/uninstall.sh"

# --- 9. 完成输出 ---
VERSION=$(.venv/bin/python cli.py --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo -e "\n$LOG_SUCCESS 安装成功！"
echo -e "------------------------------------------------"
echo -e "当前版本: ${CYAN}v$VERSION${NC}"
echo -e "安装路径: $INSTALL_DIR"
echo -e "\n使用示例:"
echo -e "  ${YELLOW}omni${NC}              # 启动交互式控制中心"
echo -e "  ${YELLOW}omni --version${NC}    # 查看版本号"
echo -e "  ${YELLOW}omni --help${NC}       # 查看帮助信息"
echo -e "------------------------------------------------"
echo -e "提示: 如果 'omni' 命令未找到，请运行 'source $SHELL_RC'。"
