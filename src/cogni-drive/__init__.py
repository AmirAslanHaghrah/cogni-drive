"""
Cogni-Drive: autonomous car core services (system monitoring + status signaling).
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cogni-drive")
except PackageNotFoundError:
    # Running from source without installation
    __version__ = "0.0.0"

__all__ = ["__version__"]
