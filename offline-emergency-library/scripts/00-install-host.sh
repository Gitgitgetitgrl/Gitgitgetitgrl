#!/usr/bin/env bash
# Install host dependencies for the ROM offline library appliance.
# Target: Ubuntu Server 24.04 LTS / Debian 12 (also works on Raspberry Pi OS).
# Run with sudo:  sudo ./scripts/00-install-host.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then echo "Run with sudo."; exit 1; fi

echo "==> Updating package lists"
apt-get update -y

echo "==> Installing base tools"
apt-get install -y --no-install-recommends \
    ca-certificates curl wget aria2 git jq \
    hostapd dnsmasq iproute2 iw \
    python3 python3-pip

echo "==> Installing Docker Engine + compose plugin"
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
# Ensure the compose plugin is present
docker compose version >/dev/null 2>&1 || apt-get install -y docker-compose-plugin

# Let the invoking (non-root) user run docker without sudo.
if [[ -n "${SUDO_USER:-}" ]]; then
    usermod -aG docker "$SUDO_USER" || true
    echo "==> Added $SUDO_USER to the 'docker' group (log out/in to take effect)."
fi

# ---- Optional: NVIDIA GPU support (Tier 3) ----
if lspci 2>/dev/null | grep -qi nvidia; then
    echo "==> NVIDIA GPU detected."
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        echo "    Install the NVIDIA driver (e.g. 'ubuntu-drivers autoinstall'), then re-run."
    fi
    if ! dpkg -l | grep -q nvidia-container-toolkit; then
        echo "==> Installing NVIDIA Container Toolkit for GPU-accelerated Ollama"
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
            | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
            | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
            > /etc/apt/sources.list.d/nvidia-container-toolkit.list
        apt-get update -y && apt-get install -y nvidia-container-toolkit
        nvidia-ctk runtime configure --runtime=docker && systemctl restart docker
    fi
    echo "    GPU ready. Uncomment the 'deploy:' block under 'ollama' in docker-compose.yml."
fi

echo
echo "==> Host setup complete."
echo "    Next: (with internet) ./scripts/02-download-content.sh, then ./scripts/03-start.sh"
