"""sspec - Lightweight AI collaboration spec for solo/small projects."""

# src/sspec/__init__.py
try:
    # build 时候自动生成
    from ._version import __version__  # type: ignore
except ImportError:
    # 如果没安装或在开发环境中未生成 _version.py
    from importlib.metadata import PackageNotFoundError, version
    try:
        __version__ = version("sspec")
    except PackageNotFoundError:
        __version__ = "unknown"
