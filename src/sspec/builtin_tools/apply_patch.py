# ruff: noqa: E501
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
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from rich.console import Console

__all__ = [
    'apply_patches',
    'PATCH_PROMPT',
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

# ============ Tool Interface (Minimal 1.0) ============

TOOL_NAME = 'patch'
TOOL_DESCRIPTION = 'Apply SEARCH/REPLACE format patches to files'
# TOOL_PROMPT defined at end of file (same as PATCH_PROMPT)

# ============ 数据结构 ============


@dataclass
class PatchBlock:
    """单个 patch 块"""

    file_path: Path
    display_path: str
    line_range: tuple[int | None, int | None] | None  # (start, end) 1-based, inclusive
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

    patch: PatchBlock | None
    success: bool
    status: Literal[
        'applied',
        'already_applied',
        'search_not_found',
        'search_ambiguous',
        'replace_ambiguous',
        'search_replace_coexist',
        'invalid_path',
        'missing_file',
        'not_a_file',
        'invalid_line_range',
        'out_of_range',
        'parse_error',
        'write_error',
        'no_change_patch',
    ]
    error: str | None = None
    match_mode: str | None = None  # exact | loose
    match_line: int | None = None  # 1-based line number in file
    related_lines: list[int] | None = None
    source_line_start: int | None = None
    search_line_count: int = 0
    replace_line_count: int = 0


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
    if line.endswith('\r\n'):
        return line[:-2]
    if line.endswith('\n') or line.endswith('\r'):
        return line[:-1]
    return line


def detect_newline_style(text: str) -> str:
    """检测文件主要换行风格：优先 \\r\\n，其次 \\r，否则 \\n"""
    if '\r\n' in text:
        return '\r\n'
    if '\r' in text:
        return '\r'
    return '\n'


def convert_newlines(text: str, newline: str) -> str:
    """把 text 中的所有换行统一成目标 newline（不额外添加/删除末尾换行）"""
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    return t.replace('\n', newline)


def read_text_robust(file_path: Path) -> str:
    """
    健壮地读取文本文件，处理编码和换行符问题：
    - 保留原始换行符（\\r\\n, \\n, \\r）
    - 尝试多种编码（UTF-8, UTF-8-SIG, GBK, Latin1）
    - 自动去除 BOM（Byte Order Mark）
    """
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin1']

    for encoding in encodings:
        try:
            with file_path.open('r', encoding=encoding, newline='') as f:
                text = f.read()
                # 去除 BOM（如果 encoding='utf-8' 且文件包含 BOM）
                if text.startswith('\ufeff'):
                    text = text[1:]
                return text
        except (UnicodeDecodeError, LookupError):
            continue

    # 最后尝试 errors='replace' 作为兜底
    with file_path.open('r', encoding='utf-8', errors='replace', newline='') as f:
        text = f.read()
        if text.startswith('\ufeff'):
            text = text[1:]
        return text


def read_patch_text_interactive() -> str:
    """Read patch text via prompt_toolkit multiline input.

    Submit with Esc+Enter (or Ctrl+D). Cancel with Ctrl+C.
    """
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings

    bindings = KeyBindings()

    @bindings.add('escape', 'enter')
    def _submit_escape_enter(event):
        event.current_buffer.validate_and_handle()

    @bindings.add('c-d')
    def _submit_ctrl_d(event):
        event.current_buffer.validate_and_handle()

    session = PromptSession(multiline=True, key_bindings=bindings)

    try:
        text = session.prompt('> ')
    except (KeyboardInterrupt, EOFError):
        return ''

    if text and not text.endswith('\n'):
        text += '\n'
    return text


def resolve_patch_path(root: Path, user_path: str) -> Path:
    """
    将 patch 里的路径解析为目标文件：
    - 允许绝对路径
    - 相对路径仍禁止 .. 越界
    """
    p = Path(user_path)
    if p.is_absolute():
        return p.resolve(strict=False)

    root_abs = root.resolve()
    resolved = (root_abs / p).resolve()

    try:
        resolved.relative_to(root_abs)
    except ValueError:
        raise ValueError(f'Path escapes workspace root: {user_path}') from None

    return resolved


def parse_line_range(text: str) -> tuple[int | None, int | None]:
    """Parse `L10-L20`, `L10-`, `-L20`, or legacy `10-20` syntax."""
    patterns = [
        re.compile(r'^L(?P<start>\d+)-L(?P<end>\d+)$'),
        re.compile(r'^L(?P<start>\d+)-$'),
        re.compile(r'^-L(?P<end>\d+)$'),
        re.compile(r'^(?P<start>\d+)-(?P<end>\d+)$'),
    ]

    for pattern in patterns:
        match = pattern.fullmatch(text)
        if not match:
            continue

        start = match.groupdict().get('start')
        end = match.groupdict().get('end')
        start_i = int(start) if start else None
        end_i = int(end) if end else None

        if start_i is not None and start_i <= 0:
            raise ValueError(f'Invalid line range: {text}')
        if end_i is not None and end_i <= 0:
            raise ValueError(f'Invalid line range: {text}')
        if start_i is not None and end_i is not None and end_i < start_i:
            raise ValueError(f'Invalid line range: {text}')

        return start_i, end_i

    raise ValueError(f'Invalid line range: {text}')


def _parse_patch_header_text(text: str) -> tuple[str, tuple[int | None, int | None] | None]:
    """Parse patch header body (without leading `# `)."""
    if not text:
        raise ValueError(f'Invalid patch header: {text}')

    if ':' not in text:
        return text, None

    path_part, suffix = text.rsplit(':', 1)
    if not path_part:
        raise ValueError(f'Invalid patch header: {text}')

    try:
        return path_part, parse_line_range(suffix)
    except ValueError:
        return text, None


def parse_patch_header(
    header: str,
    *,
    project_root: Path,
) -> tuple[Path, str, tuple[int | None, int | None] | None]:
    """Parse '# <path>[:<range>]' with absolute/relative path support."""
    stripped = strip_line_ending(header)
    if not stripped.startswith('# '):
        raise ValueError(f'Invalid patch header: {header}')

    display_path, line_range = _parse_patch_header_text(stripped[2:].strip())
    return resolve_patch_path(project_root, display_path), display_path, line_range


def path_is_within_root(path: Path, root: Path) -> bool:
    """Return whether a resolved path is inside the current workspace root."""
    try:
        path.resolve(strict=False).relative_to(root.resolve())
        return True
    except ValueError:
        return False


def find_external_absolute_patches(
    patches: list[PatchBlock], workspace_root: Path
) -> list[PatchBlock]:
    """Collect absolute-path patches that target files outside the workspace."""
    external: list[PatchBlock] = []
    for patch in patches:
        if not Path(patch.display_path).is_absolute():
            continue
        if path_is_within_root(patch.file_path, workspace_root):
            continue
        external.append(patch)
    return external


def is_patch_header_line(line: str) -> bool:
    """Return whether a line looks like a patch file header."""
    stripped = strip_line_ending(line)
    if not stripped.startswith('# '):
        return False

    try:
        _parse_patch_header_text(stripped[2:].strip())
        return True
    except ValueError:
        return False


def atomic_write_text(path: Path, text: str, *, encoding: str = 'utf-8') -> None:
    """原子写入：同目录临时文件 + os.replace，尽量保留原权限"""
    original_mode = None
    try:
        original_mode = path.stat().st_mode
    except Exception:
        original_mode = None

    dirpath = path.parent
    fd, tmp = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=str(dirpath))
    try:
        with os.fdopen(fd, 'w', encoding=encoding, newline='') as f:
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

SEARCH_MARK = '<<<<<<< SEARCH'
DELIM_MARK = '======='
REPLACE_MARK = '>>>>>>> REPLACE'


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
    if is_patch_header_line(stripped):
        return 'F'

    # 标记行必须精确匹配（不允许额外空格）
    if stripped == SEARCH_MARK:
        return 'S'
    if stripped == DELIM_MARK:
        return 'D'
    if stripped == REPLACE_MARK:
        return 'R'

    # 空行 / 纯空白行
    if stripped.strip() == '':
        return 'B'

    return 'C'


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
    schema = ''.join(roles)  # 1 char per line -> match.span 可直接映射回行数组
    return LRRResult(lines=lines, roles=roles, schema=schema)


# ============ LRR Phase 2: 匹配 Patch 块 ============

# 允许：文件路径行 F 与 SEARCH 标记 S 之间有若干空行 B*
# 内容只允许 B/C（避免吞掉别的结构行）
PATCH_PATTERN = re.compile(r'F(?P<gap>B*)S(?P<search>[BC]*?)D(?P<replace>[BC]*?)R')


def parse_patches(patch_text: str, *, project_root: Path | None = None) -> PatchParseResult:
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
            try:
                file_path, display_path, line_range = parse_patch_header(
                    file_line, project_root=root
                )
            except ValueError:
                errors.append(
                    f'Line {file_line_idx + 1}: Failed to parse patch header: {file_line}'
                )
                continue
            except Exception as e:
                errors.append(f'Line {file_line_idx + 1}: Invalid path: {file_line} ({e})')
                continue

            # 检查文件是否存在
            if not file_path.exists():
                errors.append(f'Line {file_line_idx + 1}: File does not exist: {display_path}')
                continue
            if not file_path.is_file():
                errors.append(f'Line {file_line_idx + 1}: Not a file: {display_path}')
                continue

            # 提取 SEARCH / REPLACE 内容（不包括标记行）
            search_lines = lrr.extract_lines(match, 'search')
            replace_lines = lrr.extract_lines(match, 'replace')

            patches.append(
                PatchBlock(
                    file_path=file_path,
                    display_path=display_path,
                    line_range=line_range,
                    search_content=''.join(search_lines),
                    replace_content=''.join(replace_lines),
                    source_line_start=file_line_idx + 1,
                )
            )

        except Exception as e:
            errors.append(f'Failed to parse patch block: {e}')

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
    s = strip_line_ending(line).rstrip(' \t')
    if s.strip() == '':
        return ''
    return s


def split_lines_keepends(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def find_block_matches(
    region_lines: list[str], search_lines: list[str], *, loose: bool
) -> list[int]:
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


def find_preferred_matches(
    region_lines: list[str], needle_lines: list[str]
) -> tuple[list[int], str | None]:
    """Return exact matches first, else loose matches."""
    exact = find_block_matches(region_lines, needle_lines, loose=False)
    if exact:
        return exact, 'exact'

    loose = find_block_matches(region_lines, needle_lines, loose=True)
    if loose:
        return loose, 'loose'

    return [], None


def normalize_line_range(
    line_range: tuple[int | None, int | None] | None,
    total_lines: int,
) -> tuple[int, int] | None:
    """Resolve open-ended 1-based line ranges against file length."""
    if line_range is None:
        return None

    start_raw, end_raw = line_range
    start = 1 if start_raw is None else start_raw
    end = total_lines if end_raw is None else end_raw

    if start <= 0 or end <= 0 or end < start:
        raise ValueError(f'Invalid line range: {format_line_range(line_range)}')

    return start, end


def absolute_line_numbers(prefix_len: int, matches: list[int]) -> list[int]:
    """Convert region-relative match offsets to file line numbers."""
    return [prefix_len + match + 1 for match in matches]


def format_line_range(line_range: tuple[int | None, int | None] | None) -> str:
    """Format a line range using canonical display syntax."""
    if line_range is None:
        return 'Full file'

    start, end = line_range
    if start is not None and end is not None:
        return f'L{start}-L{end}'
    if start is not None:
        return f'L{start}-'
    if end is not None:
        return f'-L{end}'
    return 'Full file'


def apply_patch(patch: PatchBlock) -> PatchApplyResult:
    """应用单个 patch"""
    try:
        # 保留原文件换行
        with patch.file_path.open('r', encoding='utf-8', newline='') as f:
            content = f.read()

        file_newline = detect_newline_style(content)
        file_lines = split_lines_keepends(content)
        total_lines = len(file_lines)

        # 确定搜索范围
        if patch.line_range:
            try:
                normalized_range = normalize_line_range(patch.line_range, total_lines)
                if normalized_range is None:
                    raise ValueError('Resolved line range is empty')
                scope_start, scope_end = normalized_range
            except ValueError as e:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    status='invalid_line_range',
                    error=str(e),
                    source_line_start=patch.source_line_start,
                )

            start_idx = scope_start - 1
            end_idx_excl = scope_end

            if start_idx < 0 or end_idx_excl > total_lines:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    status='out_of_range',
                    error=f'Line range {format_line_range(patch.line_range)} is outside file bounds (1-{total_lines})',
                    source_line_start=patch.source_line_start,
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
                status='parse_error',
                error='SEARCH content is empty',
                source_line_start=patch.source_line_start,
            )

        if search_text == replace_text:
            return PatchApplyResult(
                patch=patch,
                success=True,
                status='no_change_patch',
                error='SEARCH and REPLACE are identical',
                source_line_start=patch.source_line_start,
                search_line_count=len(search_lines),
                replace_line_count=len(replace_lines),
            )

        search_matches, search_mode = find_preferred_matches(region, search_lines)
        replace_matches, replace_mode = find_preferred_matches(region, replace_lines)

        if len(search_matches) == 1:
            match_start = search_matches[0]
            match_mode = search_mode
        elif len(search_matches) > 1:
            related_lines = absolute_line_numbers(len(prefix), search_matches)
            status = 'search_replace_coexist' if replace_matches else 'search_ambiguous'
            reason = (
                'SEARCH and REPLACE both exist in scope; narrow the line range'
                if replace_matches
                else 'SEARCH matched multiple locations; narrow the line range'
            )
            return PatchApplyResult(
                patch=patch,
                success=False,
                status=status,
                error=reason,
                match_mode=search_mode,
                related_lines=related_lines,
                source_line_start=patch.source_line_start,
                search_line_count=len(search_lines),
                replace_line_count=len(replace_lines),
            )
        else:
            if len(replace_matches) == 1:
                return PatchApplyResult(
                    patch=patch,
                    success=True,
                    status='already_applied',
                    error='SEARCH not found, but REPLACE already exists',
                    match_mode=replace_mode,
                    match_line=absolute_line_numbers(len(prefix), replace_matches)[0],
                    source_line_start=patch.source_line_start,
                    search_line_count=len(search_lines),
                    replace_line_count=len(replace_lines),
                )
            if len(replace_matches) > 1:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    status='replace_ambiguous',
                    error='SEARCH not found, and REPLACE matched multiple locations',
                    match_mode=replace_mode,
                    related_lines=absolute_line_numbers(len(prefix), replace_matches),
                    source_line_start=patch.source_line_start,
                    search_line_count=len(search_lines),
                    replace_line_count=len(replace_lines),
                )

            return PatchApplyResult(
                patch=patch,
                success=False,
                status='search_not_found',
                error='SEARCH content not found in scope',
                source_line_start=patch.source_line_start,
                search_line_count=len(search_lines),
                replace_line_count=len(replace_lines),
            )

        match_end = match_start + len(search_lines)

        # 计算匹配的文件行号（1-based）
        match_line = len(prefix) + match_start + 1

        new_region = region[:match_start] + replace_lines + region[match_end:]
        new_content = ''.join(prefix + new_region + suffix)

        atomic_write_text(patch.file_path, new_content, encoding='utf-8')
        return PatchApplyResult(
            patch=patch,
            success=True,
            status='applied',
            match_mode=match_mode,
            match_line=match_line,
            source_line_start=patch.source_line_start,
            search_line_count=len(search_lines),
            replace_line_count=len(replace_lines),
        )

    except Exception as e:
        return PatchApplyResult(
            patch=patch,
            success=False,
            status='write_error',
            error=f'Failed to apply patch: {e}',
            source_line_start=patch.source_line_start,
        )


def format_patch_header(patch: PatchBlock) -> str:
    header = f'# {patch.display_path}'
    if patch.line_range:
        header += f':{format_line_range(patch.line_range)}'
    return header


def apply_patches(patch_text: str, *, project_root: Path | None = None) -> BatchApplyResult:
    """解析并批量应用 patches（保持原语义：解析阶段出现错误则不应用）"""
    parse_result = parse_patches(patch_text, project_root=project_root)

    if parse_result.errors:
        return BatchApplyResult(
            results=[
                PatchApplyResult(patch=None, success=False, status='parse_error', error=err)
                for err in parse_result.errors
            ]
        )

    results = [apply_patch(p) for p in parse_result.patches]
    return BatchApplyResult(results=results)


# ============ Prompt 模板 ============

PATCH_PROMPT = """# patch - SEARCH/REPLACE file editing helper

`sspec tool patch` is a helper for editing existing files with structured SEARCH/REPLACE patch blocks.

## Patch Format

### Single Patch Block

- Header: `# <path>` or `# <path>:<range>`
- Range syntax: `L10-L25`, `L10-`, `-L25`
- Paths: relative paths resolve from project root / cwd; absolute paths are also allowed
- Absolute paths outside the current workspace require confirmation, or `--unsafe` to bypass

```patch
# src/utils.py:L10-L25
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

Example with an absolute path that contains spaces:

```patch
# C:\\My Project\\docs\\my file.md:L3-
<<<<<<< SEARCH
old text
=======
new text
>>>>>>> REPLACE
```

### Multiple Patch Blocks

- Multiple patch blocks can be combined in one input
- You may insert arbitrary explanation text between patch blocks
- Each patch block only needs to keep its own format valid

## Apply Patch via CLI

### Basic command

```bash
sspec tool patch [OPTIONS]
```

### Input methods

1. `--stdin` - recommended for agents
2. `PATCH_FILE` or `--file PATCH_FILE`
3. `--input` - interactive input

### Safety flag

- `--unsafe` bypasses the outside-workspace absolute path confirmation

### `--stdin` example (bash)

```bash
cat <<'EOF' | sspec tool patch --stdin --yes
# src/utils.py
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
EOF
```

### `--stdin` example (powershell)

```powershell
@'
# src/utils.py
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
'@ | sspec tool patch --stdin --yes
```

## Important Rules

1. SEARCH must match exactly first; loose fallback ignores trailing whitespace and blank-line-only differences
2. If SEARCH matches multiple locations, add a narrower line range
3. Target files must already exist
4. Relative paths must stay under the detected project root / current working directory; absolute paths are allowed
5. If SEARCH is missing but REPLACE exists uniquely in scope, the patch is treated as already applied
6. Failed patch output may contain explanation text outside fenced `patch` blocks; those fenced blocks remain directly reusable as later patch input
7. Absolute paths outside the current workspace require explicit confirmation unless `--unsafe` is provided
"""

# Alias for Tool Interface
TOOL_PROMPT = PATCH_PROMPT


def register_command(group):
    """Register patch command to the tool group."""
    import click
    from rich.console import Console
    from rich.table import Table

    from sspec.core import find_sspec_root

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument(
        'patch_file',
        type=click.Path(exists=True, path_type=Path),
        required=False,
    )
    @click.option(
        '-f',
        '--file',
        'patch_file_opt',
        type=click.Path(exists=True, path_type=Path),
        help='Read patch text from a file (alternative to positional PATCH_FILE)',
    )
    @click.option(
        '--stdin',
        'stdin_mode',
        is_flag=True,
        help='Read patch text from stdin.',
    )
    @click.option(
        '-i',
        '--input',
        'input_mode',
        is_flag=True,
        help='Enter patch text interactively (default when no file is provided)',
    )
    @click.option(
        '--dry-run',
        is_flag=True,
        help='Preview patches without applying changes',
    )
    @click.option(
        '--unsafe',
        is_flag=True,
        help='Bypass confirmation for absolute paths outside the current workspace.',
    )
    @click.option(
        '--output-failed',
        type=click.Path(path_type=Path),
        help='Custom markdown file or directory for failed patch bundle output.',
    )
    @click.option(
        '--yes',
        is_flag=True,
        help='Skip confirmation prompt',
    )
    @click.option(
        '--prompt',
        is_flag=True,
        help='Show detailed patch format specification',
    )
    def patch_command(
        patch_file: Path | None,
        patch_file_opt: Path | None,
        stdin_mode: bool,
        input_mode: bool,
        dry_run: bool,
        unsafe: bool,
        output_failed: Path | None,
        yes: bool,
        prompt: bool,
    ):
        """Apply SEARCH/REPLACE format patches to files."""

        # Show prompt specification
        if prompt:
            console.print(TOOL_PROMPT)
            return

        # Determine input source (default to --input when no file is provided)
        file_sources = [p for p in [patch_file, patch_file_opt] if p is not None]
        explicit_sources = int(bool(file_sources)) + int(stdin_mode) + int(input_mode)
        if explicit_sources > 1:
            console.print(
                '[red]Error:[/red] Use exactly one input source: PATCH_FILE/--file, --stdin, or --input.'
            )
            raise click.Abort()
        if len(file_sources) > 1:
            console.print(
                '[red]Error:[/red] Provide only one patch file source (PATCH_FILE or --file).'
            )
            raise click.Abort()

        use_stdin = stdin_mode
        use_input = input_mode or (explicit_sources == 0)

        # Determine project root (used for path safety + prompt file completion)
        sspec_root = find_sspec_root()
        if sspec_root is None:
            project_root = Path.cwd()
            console.print(
                f'[yellow]Warning:[/yellow] Not in sspec project, using cwd: {project_root}'
            )
        else:
            # find_sspec_root() returns .sspec dir, we need its parent (project root)
            project_root = sspec_root.parent

        patch_text = ''
        if use_stdin:
            if sys.stdin.isatty():
                console.print('[red]Error:[/red] No stdin content detected.')
                raise click.Abort()
            try:
                patch_text = sys.stdin.buffer.read().decode('utf-8')
            except UnicodeDecodeError as e:
                console.print(f'[red]Error:[/red] Failed to decode stdin as utf-8: {e}')
                raise click.Abort() from None
            if not patch_text.strip():
                console.print('[yellow]No input. Skipped.[/yellow]')
                return
        elif use_input:
            console.print(
                '[cyan]Interactive input:[/cyan] paste/write patch text, then Esc+Enter (or Ctrl+D) to submit.'
            )
            patch_text = read_patch_text_interactive()

            if not patch_text.strip():
                console.print('[yellow]No input. Skipped.[/yellow]')
                return
        else:
            patch_path = file_sources[0]
            try:
                patch_text = read_text_robust(patch_path)
            except Exception as e:
                console.print(f'[red]Error reading patch file:[/red] {e}')
                raise click.Abort() from None

        # Parse patches
        parse_result = parse_patches(patch_text, project_root=project_root)

        if parse_result.errors:
            console.print('[red]Parsing errors:[/red]')
            for err in parse_result.errors:
                console.print(f'  - {err}')
            bundle_path = _save_failed_patches(
                console,
                failed_results=[],
                raw_patch_text=patch_text,
                parse_errors=parse_result.errors,
                output_path=output_failed,
                project_root=project_root,
                in_sspec_project=sspec_root is not None,
            )
            console.print(f'[yellow]Full failed patch bundle:[/yellow] {bundle_path}')
            raise click.exceptions.Exit(code=1)

        patches = parse_result.patches
        console.print(f'[green][OK][/green] Found {len(patches)} patch(es)\n')

        # Always show preview table (helps understand what will happen)
        table = Table(title='Patches', show_header=True)
        table.add_column('# header', style='cyan', no_wrap=True)
        table.add_column('Scope', style='dim')

        for patch in patches:
            scope = format_line_range(patch.line_range)
            table.add_row(format_patch_header(patch), scope)

        console.print(table)
        console.print()

        external_absolute_patches = find_external_absolute_patches(patches, project_root)
        if external_absolute_patches:
            console.print(
                '[yellow]Warning:[/yellow] Absolute path(s) outside the current workspace:'
            )
            for patch in external_absolute_patches:
                console.print(f'  - {patch.display_path}')
            console.print(f'Workspace: {project_root}')

            if dry_run:
                console.print(
                    '[yellow]Dry-run note:[/yellow] no confirmation required because no changes will be applied.'
                )
            elif unsafe:
                console.print(
                    '[yellow]Unsafe mode:[/yellow] outside-workspace confirmation bypassed.'
                )
            elif use_stdin:
                console.print(
                    '[red]Error:[/red] `--stdin` mode cannot request outside-workspace confirmation. '
                    'Re-run with `--unsafe` if you intend to patch these paths.'
                )
                raise click.exceptions.Exit(code=1)
            elif not click.confirm(
                'Allow patching files outside the current workspace?',
                default=False,
            ):
                console.print('[yellow]Aborted.[/yellow]')
                raise click.Abort()

        if dry_run:
            console.print('[yellow]Dry-run mode:[/yellow] no changes will be applied')
            return

        if not yes:
            if not click.confirm('Apply these patches?', default=False):
                console.print('[yellow]Aborted.[/yellow]')
                raise click.Abort()

        # Apply patches
        console.print('[cyan]Applying patches...[/cyan]')
        results = [apply_patch(p) for p in parse_result.patches]

        # Display results
        _display_results(console, results)

        # Save failed patches
        failed_results = [r for r in results if not r.success]
        if failed_results:
            bundle_path = _save_failed_patches(
                console,
                failed_results=failed_results,
                raw_patch_text=patch_text,
                parse_errors=[],
                output_path=output_failed,
                project_root=project_root,
                in_sspec_project=sspec_root is not None,
            )
            _display_failed_details(console, failed_results, bundle_path)
            console.print(f'[yellow]Full failed patch bundle:[/yellow] {bundle_path}')

        # Exit with appropriate code
        if failed_results:
            raise click.exceptions.Exit(code=1)


def _display_results(console: Console, results: list[PatchApplyResult]) -> None:
    """Display patch application results in a table."""
    from rich.table import Table

    table = Table(title='Results', show_header=True)
    table.add_column('# header', style='cyan', no_wrap=True)
    table.add_column('Status', justify='center')
    table.add_column('Match', style='dim', no_wrap=True)
    table.add_column('Δ lines', style='dim', justify='right', no_wrap=True)
    table.add_column('Note', style='dim')

    applied = 0
    already_applied = 0
    no_change = 0
    failed = 0

    for result in results:
        if result.patch is None:
            failed += 1
            table.add_row(
                'N/A',
                '[red][X][/red]',
                '-',
                '-',
                result.error or 'Unknown parsing error',
            )
            continue
        if result.success:
            delta = result.replace_line_count - result.search_line_count
            match = result.match_mode or '-'
            if result.match_line is not None:
                match = f'{match} @L{result.match_line}'

            status_label = '[green][OK][/green]'
            note = 'Applied'
            if result.status == 'already_applied':
                already_applied += 1
                status_label = '[cyan][=][/cyan]'
                note = 'Already applied'
            elif result.status == 'no_change_patch':
                no_change += 1
                status_label = '[blue][~][/blue]'
                note = 'No change'
            else:
                applied += 1

            table.add_row(
                format_patch_header(result.patch),
                status_label,
                match,
                f'{delta:+d}',
                note,
            )
        else:
            failed += 1
            error_msg = result.error or 'Unknown error'
            table.add_row(
                format_patch_header(result.patch),
                '[red][X][/red]',
                (result.match_mode or '-'),
                '-',
                error_msg,
            )

    console.print()
    console.print(table)
    console.print()

    # Summary
    if failed == 0:
        console.print(
            '[green]Summary:[/green] '
            f'Applied: {applied} | Already applied: {already_applied} | No change: {no_change}'
        )
    else:
        console.print(
            '[yellow]Summary:[/yellow] '
            f'Applied: {applied} | Already applied: {already_applied} | '
            f'No change: {no_change} | Failed: {failed}'
        )


def _truncate_patch_chunk(text: str, *, max_lines: int = 8) -> list[str]:
    """Truncate a patch body for readable terminal previews."""
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return lines
    hidden = len(lines) - max_lines
    return [*lines[:max_lines], f'(content omitted, {hidden} more lines)']


def _format_patch_preview(patch: PatchBlock) -> str:
    """Build a compact SEARCH/REPLACE preview for failed patch output."""
    preview_lines = ['<<<<<<< SEARCH']
    preview_lines.extend(_truncate_patch_chunk(patch.search_content))
    preview_lines.append('=======')
    preview_lines.extend(_truncate_patch_chunk(patch.replace_content))
    preview_lines.append('>>>>>>> REPLACE')
    return '\n'.join(preview_lines)


def _format_target_line_info(result: PatchApplyResult) -> str:
    """Format the most relevant target line information for output."""
    if result.match_line is not None:
        return f'L{result.match_line}'
    if result.related_lines:
        return ', '.join(f'L{line}' for line in result.related_lines)
    if result.patch and result.patch.line_range:
        return format_line_range(result.patch.line_range)
    return 'Full file'


def _display_failed_details(
    console: Console,
    failed_results: list[PatchApplyResult],
    bundle_path: Path,
) -> None:
    """Print detailed failure diagnostics with file and line information."""
    console.print()
    console.print('[bold yellow]Failed Patch Details[/bold yellow]')

    for index, result in enumerate(failed_results, start=1):
        console.print()
        console.print(f'[bold]Failed Patch {index}[/bold]')
        if result.patch is None:
            console.print('File: N/A')
            console.print(f'Status: {result.status}')
            console.print(f'Reason: {result.error or "Unknown parsing error"}')
            continue

        console.print(f'File: {result.patch.display_path}')
        console.print(f'Status: {result.status}')
        console.print(f'Patch line: L{result.source_line_start or result.patch.source_line_start}')
        console.print(f'Target line(s): {_format_target_line_info(result)}')
        console.print(f'Reason: {result.error or "Unknown error"}')
        console.print()
        console.print(_format_patch_preview(result.patch))
        console.print(f'Note: Full patch in {bundle_path}')


def _resolve_failed_output_path(
    output_path: Path | None,
    *,
    project_root: Path,
    in_sspec_project: bool,
) -> Path:
    """Resolve a single markdown file path for failed patch output."""
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    default_name = f'{timestamp}.md'

    if output_path is not None:
        candidate = output_path.expanduser().resolve(strict=False)
        if candidate.exists() and candidate.is_dir():
            return candidate / default_name
        if candidate.suffix:
            return candidate
        return candidate / default_name

    if in_sspec_project:
        return project_root / '.sspec' / 'tmp' / 'failed-patches' / default_name

    handle = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.md',
        prefix='sspec-failed-patches-',
        delete=False,
        encoding='utf-8',
    )
    handle.close()
    return Path(handle.name)


def _save_failed_patches(
    console: Console,
    *,
    failed_results: list[PatchApplyResult],
    raw_patch_text: str,
    parse_errors: list[str],
    output_path: Path | None,
    project_root: Path,
    in_sspec_project: bool,
) -> Path:
    """Save all failed patch information into one markdown bundle."""
    bundle_path = _resolve_failed_output_path(
        output_path,
        project_root=project_root,
        in_sspec_project=in_sspec_project,
    )
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ['# Failed Patch Bundle', '']

    if parse_errors:
        lines.extend(['## Parsing Errors', ''])
        for error in parse_errors:
            lines.append(f'- {error}')
        lines.extend(
            ['', '### Original Input', '', '```patch', raw_patch_text.rstrip('\n'), '```', '']
        )

    for index, result in enumerate(failed_results, start=1):
        if result.patch is None:
            continue

        lines.extend(
            [
                f'## Failed Patch {index}',
                '',
                f'- File: `{result.patch.display_path}`',
                f'- Status: `{result.status}`',
                f'- Patch line: `L{result.source_line_start or result.patch.source_line_start}`',
                f'- Target line(s): `{_format_target_line_info(result)}`',
                f'- Reason: {result.error or "Unknown error"}',
                '',
                '```patch',
                format_patch_header(result.patch),
                '<<<<<<< SEARCH',
                result.patch.search_content.rstrip('\n'),
                '=======',
                result.patch.replace_content.rstrip('\n'),
                '>>>>>>> REPLACE',
                '```',
                '',
            ]
        )

    bundle_path.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    console.print(f'[yellow]Failed patches saved to:[/yellow] {bundle_path}')
    return bundle_path
