#!/usr/bin/env bash

# Artfish Shell Completion Installer
# Installs completion for Typer-based CLI

SHELL_NAME=$(basename "$SHELL")

echo "Installing completion for $SHELL_NAME..."

case "$SHELL_NAME" in
    bash)
        python3 cli.py --install-completion bash
        ;;
    zsh)
        python3 cli.py --install-completion zsh
        ;;
    fish)
        python3 cli.py --install-completion fish
        ;;
    *)
        echo "Unsupported shell: $SHELL_NAME"
        echo "Try manual installation: python3 cli.py --install-completion [bash|zsh|fish|powershell]"
        exit 1
        ;;
esac

echo "Done! Please restart your shell or source your rc file."
