# 语法：7z a <压缩包名> <包含的文件/目录列表> <排除规则>

7z a sspec.zip src pyproject.toml -xr!__pycache__
