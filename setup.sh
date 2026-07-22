#!/usr/bin/env bash
set -e

# ---------------------------------------------------------------------------
# OS-specific tool installation
# ---------------------------------------------------------------------------

install_uv_curl() {
  echo "INFO: Installing Tools (uv, user-local install — no sudo, no system package manager)"
  if command -v uv &> /dev/null; then
    echo "INFO: uv already installed"
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    source "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
  fi
}

install_tools_macos() {
  if command -v brew &> /dev/null; then
    echo "INFO: Installing Tools (Homebrew)"
    brew install uv
  else
    echo "INFO: Homebrew not found — falling back to user-local install"
    install_uv_curl
  fi
}

install_tools_linux() {
  install_uv_curl
  echo "NOTE: For Windows, use setup.ps1 in PowerShell instead of this script."
}

# ---------------------------------------------------------------------------
# Shared steps (macOS + Linux)
# ---------------------------------------------------------------------------

install_shopify_cli() {
  echo -e
  echo "INFO: Installing Shopify CLI (npm)"
  npm install -g @shopify/cli @shopify/theme
}

setup_python_env() {
  echo -e
  echo "INFO: Creating Python Virtual Environment"
  uv venv .venv --python 3.14 --clear
  echo -e
  echo "INFO: Activating Python Virtual Environment"
  source .venv/bin/activate

  echo -e
  echo "INFO: Installing Libraries"
  uv sync
  echo "INFO: Python Version: $(python --version)"
  echo "INFO: uv Version: $(uv --version)"
}

configure_shopify_env() {
  echo -e
  echo "INFO: Shopify CLI Environment Setup"
  echo "These values are used by 'shopify theme pull/push' and invoke shopify tasks."
  echo "Values are exported for this session only — not written to any file."
  echo -e

  read -rp "Enter your Shopify store domain (e.g. mystore.myshopify.com): " shopify_store
  read -rsp "Enter your Shopify Theme Access token (from Shopify Admin > Apps > Theme Access): " shopify_token
  echo -e

  if [[ -n "$shopify_store" && -n "$shopify_token" ]]; then
    export SHOPIFY_FLAG_STORE="$shopify_store"
    export SHOPIFY_CLI_THEME_TOKEN="$shopify_token"
    echo "INFO: Shopify env vars exported for this session."
  else
    echo "WARN: Skipping Shopify env setup — one or both values were blank."
  fi
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
  case "$(uname)" in
    Darwin)
      install_tools_macos
      ;;
    Linux)
      install_tools_linux
      ;;
    *)
      echo "ERROR: Unsupported OS: $(uname)"
      echo "For Windows, run setup.ps1 in PowerShell instead of this script."
      exit 1
      ;;
  esac

  install_shopify_cli
  setup_python_env
  configure_shopify_env
}

main "$@"
