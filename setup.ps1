# Windows setup — mirrors setup.sh (macOS/Linux). Run from the repo root in PowerShell:
#   .\setup.ps1

$ErrorActionPreference = "Stop"

function Install-Tools {
    Write-Host "INFO: Installing Tools (uv, user-local install — no admin required)"
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "INFO: uv already installed"
    } else {
        irm https://astral.sh/uv/install.ps1 | iex
    }
}

function Install-ShopifyCli {
    Write-Host "`nINFO: Installing Shopify CLI (npm)"
    npm install -g @shopify/cli @shopify/theme
}

function Setup-PythonEnv {
    Write-Host "`nINFO: Creating Python Virtual Environment"
    uv venv .venv --python 3.14 --clear

    Write-Host "`nINFO: Activating Python Virtual Environment"
    & .\.venv\Scripts\Activate.ps1

    Write-Host "`nINFO: Installing Libraries"
    uv sync
    Write-Host "INFO: Python Version: $(python --version)"
    Write-Host "INFO: uv Version: $(uv --version)"
}

function Configure-ShopifyEnv {
    Write-Host "`nINFO: Shopify CLI Environment Setup"
    Write-Host "These values are used by 'shopify theme pull/push' and invoke shopify tasks."
    Write-Host "Values are exported for this session only — not written to any file."
    Write-Host ""

    $shopifyStore = Read-Host "Enter your Shopify store domain (e.g. mystore.myshopify.com)"
    $shopifyTokenSecure = Read-Host "Enter your Shopify Theme Access token (from Shopify Admin > Apps > Theme Access)" -AsSecureString
    $shopifyToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($shopifyTokenSecure))

    if ($shopifyStore -and $shopifyToken) {
        $env:SHOPIFY_FLAG_STORE = $shopifyStore
        $env:SHOPIFY_CLI_THEME_TOKEN = $shopifyToken
        Write-Host "INFO: Shopify env vars exported for this session."
    } else {
        Write-Host "WARN: Skipping Shopify env setup — one or both values were blank."
    }
}

Install-Tools
Install-ShopifyCli
Setup-PythonEnv
Configure-ShopifyEnv
