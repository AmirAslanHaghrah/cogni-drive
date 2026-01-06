from pathlib import Path
import yaml

def load_settings() -> dict:
    """
    Load config/settings.yaml (project-local).
    In production you might change this to /etc/spara/sysmon/settings.yaml.
    """
    cfg_path = Path(__file__).resolve().parents[2] / "config" / "settings.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
