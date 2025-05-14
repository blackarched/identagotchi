# Minigotchi

A miniature Pwnagotchi-inspired Wi-Fi pentesting companion. Scans networks, performs deauthentication attacks, and brute-forces captured handshakes, all accessible via CLI or a Flask-based web dashboard.

## Features
- Wi-Fi scanning (iwlist)
- Deauthentication attacks (aireplay-ng)
- Password brute-forcing (John the Ripper)
- Threaded orchestration for continuous operation
- Flask web UI with real-time controls and log viewing

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/minigotchi.git
   cd minigotchi