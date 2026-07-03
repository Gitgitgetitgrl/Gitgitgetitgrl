#!/usr/bin/env bash
# Turn the appliance into a self-contained OFFLINE Wi-Fi access point.
# Clients that join get an IP from dnsmasq and reach Rom at http://10.42.0.1:8080.
# There is NO internet routing here on purpose — it's an island network.
#
# Run with sudo:  sudo ./scripts/01-setup-wifi-hotspot.sh
# Requires a Wi-Fi interface that supports AP mode (check: iw list | grep -A5 "Supported interface modes").
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "Run with sudo."; exit 1; fi

SSID="${ROM_SSID:-ROM-LIBRARY}"
PASS="${ROM_WIFI_PASS:-emergency-library}"   # change this; min 8 chars
WIFI_IF="${WIFI_IF:-wlan0}"
AP_IP="10.42.0.1"

echo "==> Configuring access point '$SSID' on $WIFI_IF ($AP_IP)"
if ! iw dev "$WIFI_IF" info >/dev/null 2>&1; then
    echo "!! Interface $WIFI_IF not found. Set WIFI_IF=... and retry."; exit 1
fi

systemctl stop hostapd dnsmasq 2>/dev/null || true

# Static IP on the AP interface
ip addr flush dev "$WIFI_IF" || true
ip addr add "$AP_IP/24" dev "$WIFI_IF"
ip link set "$WIFI_IF" up

# hostapd (the AP itself)
cat >/etc/hostapd/hostapd.conf <<EOF
interface=$WIFI_IF
driver=nl80211
ssid=$SSID
hw_mode=g
channel=6
wmm_enabled=1
auth_algs=1
wpa=2
wpa_passphrase=$PASS
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF
sed -i 's|^#\?DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd 2>/dev/null || true

# dnsmasq (hands out DHCP leases; resolves a friendly captive name)
cat >/etc/dnsmasq.d/rom.conf <<EOF
interface=$WIFI_IF
bind-interfaces
dhcp-range=10.42.0.10,10.42.0.200,255.255.255.0,24h
dhcp-option=3,$AP_IP
dhcp-option=6,$AP_IP
# Point a friendly hostname at the box (http://library.local also works via mDNS)
address=/rom.library/$AP_IP
address=/library.local/$AP_IP
EOF

systemctl unmask hostapd 2>/dev/null || true
systemctl enable hostapd dnsmasq
systemctl restart dnsmasq
systemctl restart hostapd

echo
echo "==> Access point is up."
echo "    SSID:     $SSID"
echo "    Password: $PASS   (change ROM_WIFI_PASS and re-run to set your own)"
echo "    Rom:      http://$AP_IP:8080     Library: http://$AP_IP:8090"
echo "    (also try http://rom.library:8080 once joined)"
