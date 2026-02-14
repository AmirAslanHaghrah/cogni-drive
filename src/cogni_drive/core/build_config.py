from dataclasses import dataclass
from enum import Enum

class BuildMode(str, Enum):
    DEBUG = "DEBUG"
    RELEASE = "RELEASE"

@dataclass(frozen=True)
class BuildConfig:
    # Logging behavior
    mode: BuildMode
    min_log_level: str
    log_to_console: bool

    # Performance knobs (disable expensive work in RELEASE)
    enable_cpu_percent: bool
    enable_cpu_temp: bool
    enable_ram: bool

def make_build_config(mode: str, settings: dict) -> BuildConfig:
    """
    Central policy for DEBUG/RELEASE differences.
    - DEBUG: more logs, more metrics for development.
    - RELEASE: fewer logs, optional metrics disabled for performance.
    """
    m = BuildMode((mode or "RELEASE").strip().upper())
    metrics = settings.get("metrics", {}) if isinstance(settings.get("metrics"), dict) else {}

    if m == BuildMode.DEBUG:
        return BuildConfig(
            mode=m,
            min_log_level="DEBUG",
            log_to_console=bool(settings.get("log_to_console", True)),
            enable_cpu_percent=bool(metrics.get("cpu_percent", True)),
            enable_cpu_temp=bool(metrics.get("cpu_temp", True)),
            enable_ram=bool(metrics.get("ram", True)),
        )

    # RELEASE defaults
    return BuildConfig(
        mode=m,
        min_log_level="INFO",
        log_to_console=bool(settings.get("log_to_console", False)),
        enable_cpu_percent=bool(metrics.get("cpu_percent", False)),
        enable_cpu_temp=bool(metrics.get("cpu_temp", True)),
        enable_ram=bool(metrics.get("ram", True)),
    )
