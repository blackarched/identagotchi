FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3 python3-pip python3-venv \
      aircrack-ng reaver bully hashcat john tcpdump \
      iw iproute2 macchanger \
      rtl8812au-dkms \
      && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash minigotchi
USER minigotchi
WORKDIR /home/minigotchi

# Copy code and install Python deps
COPY --chown=minigotchi:minigotchi . .
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose web UI port
EXPOSE 8080

ENTRYPOINT ["./venv/bin/python3", "-m", "minigotchi.pwnagotchi1"]
CMD ["all"]