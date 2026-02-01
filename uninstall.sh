#!/bin/bash

# OmniGate Pro - Uninstaller
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}正在卸载 OmniGate Pro...${NC}"

INSTALL_DIR="$HOME/.omnigate"
BIN_PATH="$HOME/.local/bin/omni"

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}已移除安装目录: $INSTALL_DIR${NC}"
fi

if [ -f "$BIN_PATH" ]; then
    rm "$BIN_PATH"
    echo -e "${GREEN}已移除可执行文件: $BIN_PATH${NC}"
fi

echo -e "\n${GREEN}卸载完成！${NC}"
echo "注意：您可以手动从 .bashrc 或 .zshrc 中移除 PATH 配置。"
