import re
import sys
import shutil
import tempfile
import subprocess
import atexit
from scapy.all import rdpcap, EAPOL

# 1) Verify presence of external tools
REQUIRED_TOOLS = ['airmon-ng', 'iw', 'ip', 'airodump-ng']
for tool in REQUIRED_TOOLS:
    if shutil.which(tool) is None:
        print(f"[!] Required tool not found: {tool}. Please install it.")
        sys.exit(1)

def enable_monitor(iface):
    """Enable monitor mode on a validated interface name."""
    if not re.match(r'^[a-zA-Z0-9]+$', iface):
        print(f"[!] Invalid interface name: {iface}")
        sys.exit(1)
    try:
        subprocess.run(['airmon-ng', 'start', iface], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to enable monitor mode on {iface}: {e}")
        sys.exit(1)
    return iface + 'mon'

def disable_monitor(iface_mon):
    """Disable monitor mode; registered to run on exit."""
    subprocess.run(['airmon-ng', 'stop', iface_mon], check=False)

def capture_handshake(iface_mon, channel, bssid, timeout=60):
    """Run airodump-ng to capture a handshake, return path to pcap."""
    # Unique, secure temp file
    tmp = tempfile.NamedTemporaryFile(prefix='minigotchi_', suffix='.cap', delete=False)
    cap_file = tmp.name
    tmp.close()

    cmd = [
        'airodump-ng',
        '--bssid', bssid,
        '--channel', str(channel),
        '--write-interval', '1',
        '--output-format', 'pcap',
        '--write', cap_file.replace('.cap', '')
    ]
    try:
        proc = subprocess.Popen(cmd + [iface_mon], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.terminate()
    except Exception as e:
        print(f"[!] Error running airodump-ng: {e}")
        sys.exit(1)

    return cap_file

def valid_handshake(pcap_path):
    """Return True if capture contains ≥4 EAPOL frames."""
    try:
        packets = rdpcap(pcap_path)
    except Exception as e:
        print(f"[!] Unable to read pcap file {pcap_path}: {e}")
        return False

    eapol_count = sum(1 for p in packets if p.haslayer(EAPOL))
    return eapol_count >= 4

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Capture WPA handshake")
    parser.add_argument('iface', help="Wireless interface name")
    parser.add_argument('bssid', help="Target AP BSSID")
    parser.add_argument('channel', type=int, help="Target channel")
    args = parser.parse_args()

    mon_iface = enable_monitor(args.iface)
    atexit.register(disable_monitor, mon_iface)

    cap = capture_handshake(mon_iface, args.channel, args.bssid)
    if valid_handshake(cap):
        print(f"[+] Handshake captured: {cap}")
    else:
        print("[!] No valid handshake found.")
        sys.exit(1)