# External Dependencies

Minigotchi relies on the following system tools and drivers:

| Tool / Library    | Minimum Version     | Purpose                                | Install (Debian/Kali)                           |
|-------------------|---------------------|----------------------------------------|-------------------------------------------------|
| aircrack-ng       | 1.6+                | Monitor-mode management, handshake     | `apt install aircrack-ng`                       |
| reaver            | 1.6.5               | WPS PIN attacks                        | `apt install reaver`                            |
| bully             | 1.4                 | Alternative WPS attacks                | `apt install bully`                             |
| hashcat           | 6.2+                | GPU-accelerated WPA cracking           | `apt install hashcat`                           |
| john              | 1.9+                | CPU-based cracking                     | `apt install john`                              |
| tcpdump           | any                 | Optional packet capture                | `apt install tcpdump`                           |
| iw                | any                 | Wireless interface management          | `apt install iw`                                |
| iproute2          | any                 | Interface management                   | `apt install iproute2`                          |
| macchanger        | any                 | MAC address randomization              | `apt install macchanger`                        |
| rtl8812au-dkms    | any                 | Driver for USB Wi-Fi adapters          | `apt install rtl8812au-dkms`                    |
| python3           | 3.8+                | Runtime                                | `apt install python3 python3-pip`               |
| pip               | any                 | Python package installer               | `apt install python3-pip`                       |