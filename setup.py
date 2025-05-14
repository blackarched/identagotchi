# --- FILE STATUS: NEWLY CREATED ---
# --- NEW FILENAME: setup.py ---
# --- PURPOSE: Packaging and console script entry points for Minigotchi application ---

from setuptools import setup, find_packages

setup(
    name='minigotchi',
    version='0.1.0',
    description='A miniature Pwnagotchi-like pentesting companion for Wi-Fi analysis and attacks.',
    author='Minigotchi Contributors',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # No external Python packages required; all imports are from the standard library.
    ],
    entry_points={
        'console_scripts': [
            'minigotchi-gui=minigotchi_gui:main',
            'wifi-scanner=wifi_scanner:main',
            'deauth-attack=deauth_attack:main',
            'password-brute=password_brute:main',
            'pwnagotchi1=pwnagotchi1:main',
        ],
    },
    scripts=['cron_jobs.sh'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
)