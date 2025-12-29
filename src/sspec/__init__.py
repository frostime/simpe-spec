"""
sspec - Lightweight AI collaboration spec
"""

from importlib.metadata import version as _get_version

try:
    __version__ = _get_version("sspec")
except Exception:
    # 开发模式下（未安装）的回退方案
    __version__ = "0.0.0+dev"

# 导出版本号
__all__ = ["__version__"]
