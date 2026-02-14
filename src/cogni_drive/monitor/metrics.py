from pathlib import Path
import psutil

_THERMAL_PATHS = [Path("/sys/class/thermal/thermal_zone0/temp")]

def read_cpu_temp_c() -> float | None:
    """
    Returns CPU temperature in Celsius (best-effort).
    """
    for p in _THERMAL_PATHS:
        try:
            raw = p.read_text().strip()
            val = float(raw)
            return val / 1000.0 if val > 1000 else val
        except Exception:
            continue
    return None

def read_cpu_percent(sample_window_sec: float = 0.1) -> float:
    """
    Returns CPU usage percentage.
    Note: interval>0 blocks briefly to measure usage.
    """
    return float(psutil.cpu_percent(interval=sample_window_sec))

def read_ram_usage() -> dict:
    """
    Returns RAM usage statistics.
    """
    vm = psutil.virtual_memory()
    return {
        "percent": float(vm.percent),
        "used_mb": float(vm.used) / (1024 * 1024),
        "total_mb": float(vm.total) / (1024 * 1024),
    }
