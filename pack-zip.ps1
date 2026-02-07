# 语法：7z a <压缩包名> <包含的文件/目录列表> <排除规则>

7z a sspec.zip src pyproject.toml -xr!__pycache__

# 最终交付
# - CHANGE.md 里面记录了所有变更，文件级别到内部说明
# - sspec-update.zip：将所有**更新过** 的文件打包到 zip 中，保留文件结构
# - update.ps1: 将 sspec-update.zip 放在项目根目录，运行 update.ps1 可以自动将文件更新到本地，避免一个个手动替换
