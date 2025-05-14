import os
import sys
import yaml

def load_config():
    """
    Load and validate the main YAML configuration file.
    Path can be overridden via MINIGOTCHI_CONFIG env var.
    """
    default_path = '~/.minigotchi/config.yml'
    path = os.path.expanduser(os.getenv('MINIGOTCHI_CONFIG', default_path))

    try:
        with open(path, 'r') as stream:
            config = yaml.safe_load(stream) or {}
    except FileNotFoundError:
        print(f"[!] Configuration file not found at {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[!] Error parsing YAML config: {e}")
        sys.exit(1)

    # Ensure required keys exist
    required = ['interface', 'wordlist_path', 'output_dir']
    missing = [key for key in required if key not in config]
    if missing:
        print(f"[!] Missing required config keys: {', '.join(missing)}")
        sys.exit(1)

    return config