"""
sspec - Lightweight AI collaboration spec
"""

from importlib.metadata import version as _get_version

try:
    __version__ = _get_version('sspec')
except Exception:
    __version__ = '0.0.0+dev'

__all__ = ['__version__']
