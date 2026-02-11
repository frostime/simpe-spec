# patch_handler.py
"""
SEARCH/REPLACE Patch Handler (LRR Optimized)

解析并应用 SEARCH/REPLACE 格式的代码补丁。

Patch 块格式：
    # path/to/file.py[:L10-L25]
    <<<<<<< SEARCH
    old code here
    =======
    new code here
    >>>>>>> REPLACE

"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ============ 数据结构 ============

@dataclass
class PatchBlock:
    """单个 patch 块"""
    file_path: Path
    display_path: str
    line_range: Optional[tuple[int, int]]  # (start, end) 1-based, inclusive
    search_content: str
    replace_content: str
    source_line_start: int  # patch 在源文本中的起始行号（用于错误报告）


@dataclass
class PatchParseResult:
    """解析结果"""
    patches: list[PatchBlock]
    errors: list[str]


@dataclass
class PatchApplyResult:
    """单个 patch 应用结果"""
    patch: Optional[PatchBlock]
    success: bool
    error: Optional[str] = None


@dataclass
class BatchApplyResult:
    """批量应用结果"""
    results: list[PatchApplyResult]

    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.results)

    @property
    def failed_patches(self) -> list[PatchApplyResult]:
        return [r for r in self.results if not r.success]


# ============ 工具函数 ============

def strip_line_ending(line: str) -> str:
    """只移除行尾换行符：兼容 \\n / \\r\\n / \\r"""
    if line.endswith("\r\n"):
        return line[:-2]
    if line.endswith("\n") or line.endswith("\r"):
        return line[:-1]
    return line


def detect_newline_style(text: str) -> str:
    """检测文件主要换行风格：优先 \\r\\n，其次 \\r，否则 \\n"""
    if "\r\n" in text:
        return "\r\n"
    if "\r" in text:
        return "\r"
    return "\n"


def convert_newlines(text: str, newline: str) -> str:
    """把 text 中的所有换行统一成目标 newline（不额外添加/删除末尾换行）"""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    return t.replace("\n", newline)


def safe_resolve_under_root(root: Path, user_path: str) -> Path:
    """
    将 patch 里的相对路径解析到 root 下：
    - 禁止绝对路径
    - 禁止 .. 越界
    """
    p = Path(user_path)
    if p.is_absolute():
        raise ValueError(f"不允许绝对路径: {user_path}")

    root_abs = root.resolve()
    resolved = (root_abs / p).resolve()

    try:
        resolved.relative_to(root_abs)
    except ValueError:
        raise ValueError(f"路径越界（疑似使用 ..）: {user_path}")

    return resolved


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """原子写入：同目录临时文件 + os.replace，尽量保留原权限"""
    original_mode = None
    try:
        original_mode = path.stat().st_mode
    except Exception:
        original_mode = None

    dirpath = path.parent
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(dirpath))
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
            f.write(text)

        if original_mode is not None:
            try:
                os.chmod(tmp, original_mode)
            except Exception:
                pass

        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


# ============ LRR Phase 1: 行分类 ============

FILE_PATH_PATTERN = re.compile(r"^#\s+(\S+?)(?::L?(\d+)-L?(\d+))?\s*$")

SEARCH_MARK = "<<<<<<< SEARCH"
DELIM_MARK = "======="
REPLACE_MARK = ">>>>>>> REPLACE"


def classify_line(line: str) -> str:
    """
    分类规则：
    F - File path (# path/to/file[:L10-L25])
    S - Search marker (<<<<<<< SEARCH)
    D - Delimiter (=======)
    R - Replace marker (>>>>>>> REPLACE)
    B - Blank line (仅空白)
    C - Content (其他所有内容)
    """
    stripped = strip_line_ending(line)

    # 文件路径行（允许行尾空格）
    if FILE_PATH_PATTERN.match(stripped):
        return "F"

    # 标记行必须精确匹配（不允许额外空格）
    if stripped == SEARCH_MARK:
        return "S"
    if stripped == DELIM_MARK:
        return "D"
    if stripped == REPLACE_MARK:
        return "R"

    # 空行 / 纯空白行
    if stripped.strip() == "":
        return "B"

    return "C"


@dataclass
class LRRResult:
    lines: list[str]
    roles: list[str]
    schema: str

    def find(self, pattern: str | re.Pattern) -> list[re.Match]:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return list(pattern.finditer(self.schema))

    def extract_lines(self, match: re.Match, group: int | str = 0) -> list[str]:
        start, end = match.span(group)  # 这里 start/end 是 schema 字符索引 == 行索引
        return self.lines[start:end]

    def extract_line_range(self, match: re.Match, group: int | str = 0) -> tuple[int, int]:
        return match.span(group)


def lrr_scan(text: str) -> LRRResult:
    lines = text.splitlines(keepends=True)
    roles = [classify_line(line) for line in lines]
    schema = "".join(roles)  # 1 char per line -> match.span 可直接映射回行数组
    return LRRResult(lines=lines, roles=roles, schema=schema)


# ============ LRR Phase 2: 匹配 Patch 块 ============

# 允许：文件路径行 F 与 SEARCH 标记 S 之间有若干空行 B*
# 内容只允许 B/C（避免吞掉别的结构行）
PATCH_PATTERN = re.compile(r"F(?P<gap>B*)S(?P<search>[BC]*?)D(?P<replace>[BC]*?)R")


def parse_patches(patch_text: str, *, project_root: Optional[Path] = None) -> PatchParseResult:
    """解析 patch 文本，提取所有 patch 块（保持 LRR 风格）"""
    root = (project_root or Path.cwd()).resolve()

    lrr = lrr_scan(patch_text)
    patches: list[PatchBlock] = []
    errors: list[str] = []

    for match in lrr.find(PATCH_PATTERN):
        try:
            # match.start() == 文件路径行在 schema 中的位置 == 行索引
            file_line_idx = match.start()
            file_line = strip_line_ending(lrr.lines[file_line_idx])

            # 解析文件路径和行范围
            m = FILE_PATH_PATTERN.match(file_line)
            if not m:
                errors.append(f"Line {file_line_idx + 1}: 无法解析文件路径: {file_line}")
                continue

            file_path_str, start_str, end_str = m.groups()
            display_path = file_path_str

            # 安全解析路径
            try:
                file_path = safe_resolve_under_root(root, file_path_str)
            except Exception as e:
                errors.append(f"Line {file_line_idx + 1}: 路径不合法: {display_path} ({e})")
                continue

            # 检查文件是否存在
            if not file_path.exists():
                errors.append(f"Line {file_line_idx + 1}: 文件不存在: {display_path}")
                continue
            if not file_path.is_file():
                errors.append(f"Line {file_line_idx + 1}: 不是文件: {display_path}")
                continue

            line_range = None
            if start_str and end_str:
                start_i, end_i = int(start_str), int(end_str)
                if start_i <= 0 or end_i <= 0 or end_i < start_i:
                    errors.append(f"Line {file_line_idx + 1}: 非法行范围: {start_str}-{end_str}")
                    continue
                line_range = (start_i, end_i)

            # 提取 SEARCH / REPLACE 内容（不包括标记行）
            search_lines = lrr.extract_lines(match, "search")
            replace_lines = lrr.extract_lines(match, "replace")

            patches.append(PatchBlock(
                file_path=file_path,
                display_path=display_path,
                line_range=line_range,
                search_content="".join(search_lines),
                replace_content="".join(replace_lines),
                source_line_start=file_line_idx + 1,
            ))

        except Exception as e:
            errors.append(f"解析 patch 块失败: {e}")

    return PatchParseResult(patches=patches, errors=errors)


# ============ Patch 应用逻辑（行块匹配，避免子串误计数） ============

def norm_line_exact(line: str) -> str:
    """精确匹配：仅忽略行尾换行差异，不忽略行尾空格"""
    return strip_line_ending(line)


def norm_line_loose(line: str) -> str:
    """
    容忍匹配：
    - 忽略行尾空格/Tab
    - 纯空白行归一为 ""
    - 行首缩进保留（因为我们只 rstrip 行尾）
    """
    s = strip_line_ending(line).rstrip(" \t")
    if s.strip() == "":
        return ""
    return s


def split_lines_keepends(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def find_block_matches(region_lines: list[str], search_lines: list[str], *, loose: bool) -> list[int]:
    """按“行块”查找所有匹配起点索引"""
    if not search_lines:
        return []

    norm = norm_line_loose if loose else norm_line_exact
    target = [norm(x) for x in search_lines]

    matches: list[int] = []
    max_start = len(region_lines) - len(search_lines)
    for i in range(max_start + 1):
        ok = True
        for j in range(len(search_lines)):
            if norm(region_lines[i + j]) != target[j]:
                ok = False
                break
        if ok:
            matches.append(i)
    return matches


def apply_patch(patch: PatchBlock) -> PatchApplyResult:
    """应用单个 patch"""
    try:
        # 保留原文件换行
        with patch.file_path.open("r", encoding="utf-8", newline="") as f:
            content = f.read()

        file_newline = detect_newline_style(content)
        file_lines = split_lines_keepends(content)

        # 确定搜索范围
        if patch.line_range:
            start_idx = patch.line_range[0] - 1
            end_idx_excl = patch.line_range[1]  # inclusive -> exclusive

            if start_idx < 0 or end_idx_excl > len(file_lines):
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    error=f"行范围 {patch.line_range} 超出文件范围 (1-{len(file_lines)})",
                )

            prefix = file_lines[:start_idx]
            region = file_lines[start_idx:end_idx_excl]
            suffix = file_lines[end_idx_excl:]
        else:
            prefix = []
            region = file_lines
            suffix = []

        # patch 内容换行统一为文件风格（避免混合换行）
        search_text = convert_newlines(patch.search_content, file_newline)
        replace_text = convert_newlines(patch.replace_content, file_newline)

        search_lines = split_lines_keepends(search_text)
        replace_lines = split_lines_keepends(replace_text)

        if not search_lines:
            return PatchApplyResult(
                patch=patch,
                success=False,
                error="SEARCH 内容为空：为避免误改，拒绝应用该 patch",
            )

        # 1) 精确匹配
        exact = find_block_matches(region, search_lines, loose=False)
        if len(exact) == 1:
            match_start = exact[0]
        elif len(exact) > 1:
            return PatchApplyResult(
                patch=patch,
                success=False,
                error=f"找到 {len(exact)} 处精确匹配，存在歧义（建议加行范围限定）",
            )
        else:
            # 2) 容忍匹配（行尾空白/纯空白行）
            loose = find_block_matches(region, search_lines, loose=True)
            if len(loose) == 1:
                match_start = loose[0]
            elif len(loose) > 1:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    error=f"找到 {len(loose)} 处匹配（忽略行尾空白后），存在歧义（建议加行范围限定）",
                )
            else:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    error="未找到匹配的 SEARCH 内容",
                )

        match_end = match_start + len(search_lines)

        new_region = region[:match_start] + replace_lines + region[match_end:]
        new_content = "".join(prefix + new_region + suffix)

        atomic_write_text(patch.file_path, new_content, encoding="utf-8")
        return PatchApplyResult(patch=patch, success=True)

    except Exception as e:
        return PatchApplyResult(patch=patch, success=False, error=f"应用 patch 失败: {e}")


def apply_patches(patch_text: str, *, project_root: Optional[Path] = None) -> BatchApplyResult:
    """解析并批量应用 patches（保持原语义：解析阶段出现错误则不应用）"""
    parse_result = parse_patches(patch_text, project_root=project_root)

    if parse_result.errors:
        return BatchApplyResult(results=[
            PatchApplyResult(patch=None, success=False, error=err)
            for err in parse_result.errors
        ])

    results = [apply_patch(p) for p in parse_result.patches]
    return BatchApplyResult(results=results)


# ============ Prompt 模板 ============

PATCH_PROMPT = """请返回代码更改的 patch，遵循如下的 SEARCH/REPLACE 规范：

## 格式规范

每个 patch 块由两部分组成：

1) 文件路径行（SEARCH 必须紧跟其后；允许中间有空行，但不要插入其它文字）

写法 A（推荐，通常情况）：
# path/to/file.py

写法 B（可选，仅在 SEARCH 片段太短、可能多处匹配时使用）：
# path/to/file.py:10-25
或
# path/to/file.py:L10-L25

说明：
- 行号范围是可选的，只用于缩小搜索范围以避免多重匹配
- 行号是 1-based，且为闭区间（包含起止行）


2) SEARCH/REPLACE 块（标记行必须独占一行，不能有额外空格）

#### 案例 A：不带行号范围（最常用）

```text
# src/utils.py
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

#### 案例 B：带行号范围（不带 L）

```text
# src/utils.py:10-25
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

#### 案例 C：带行号范围（带 L）

```text
# src/utils.py:L10-L25
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

## 重要规则

1. 精确匹配优先：SEARCH 内容应与文件中的代码完全一致（包括缩进）
2. 空白容忍兜底：匹配时允许忽略行尾空格/Tab 与纯空白行差异，但行首缩进必须一致
3. 唯一匹配：若匹配到多处会失败（建议使用行范围限定）
4. 路径安全：必须是相对项目根目录路径，禁止绝对路径和 .. 越界
5. 文件存在性：patch 应用前会检查文件是否存在
"""


# ============ CLI 入口（可选）============

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python patch_handler.py <patch_file>")
        sys.exit(1)

    patch_file = Path(sys.argv[1])
    if not patch_file.exists():
        print(f"Error: File not found: {patch_file}")
        sys.exit(1)

    patch_text = patch_file.read_text(encoding="utf-8")
    result = apply_patches(patch_text, project_root=Path.cwd())

    if result.all_success:
        print(f"✓ Successfully applied {len(result.results)} patch(es)")
    else:
        print(f"✗ Failed to apply {len(result.failed_patches)} patch(es):")
        for failed in result.failed_patches:
            print(f"  - {failed.error}")
        sys.exit(1)
