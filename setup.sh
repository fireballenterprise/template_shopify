# Setup Python Virtual Environment
echo -e
echo "INFO: Creating Python Virtual Environment"
uv venv .venv --python 3.14 --clear
echo -e
echo "INFO: Activating Python Virtual Environment"
source .venv/bin/activate

# Install Tools
echo -e
echo "INFO: Installing Tools (Homebrew)"
brew install uv

echo -e
echo "INFO: Installing Shopify CLI (npm)"
npm install -g @shopify/cli @shopify/theme

# Download Project Libraries
echo -e
echo "INFO: Installing Libraries"
uv sync
echo "INFO: Python Version: $(python --version)"
echo "INFO: uv Version: $(uv --version)"

# Shopify CLI environment variables
echo -e
echo "INFO: Shopify CLI Environment Setup"
echo "These values are used by 'shopify theme pull/push' and invoke shop tasks."
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
