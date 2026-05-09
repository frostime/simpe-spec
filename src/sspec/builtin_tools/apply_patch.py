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
from importlib.resources import as_file, files
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

PatchOperation = Literal['search', 'create', 'overwrite']


@dataclass
class PatchBlock:
    """单个 patch 块"""

    file_path: Path
    display_path: str
    operation: PatchOperation
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
        'file_exists',
        'out_of_range',
        'parse_error',
        'write_error',
        'no_change_patch',
        'overlap_conflict',
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


@dataclass
class PatchMatch:
    """Phase 1 match 结果（只读，不做任何写入）"""

    patch: PatchBlock
    abs_start: int  # 文件绝对行索引（0-based）
    abs_end: int  # exclusive
    match_mode: str  # 'exact' | 'loose'
    match_line: int  # 文件中 1-based 行号（= abs_start + 1）
    status: str  # 'matched' | 'already_applied' | 'search_not_found' | 'search_ambiguous' | 'overlap_conflict'
    error: str | None = None
    related_lines: list[int] | None = None
    search_line_count: int = 0
    replace_line_count: int = 0


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
    - 保留原始换行符（\r\n, \n, \r）
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


def read_target_text_with_encoding(file_path: Path) -> tuple[str, str]:
    """Read a target file while preserving a writable text encoding hint."""
    raw = file_path.read_bytes()

    if raw.startswith(b'\xef\xbb\xbf'):
        text = raw.decode('utf-8-sig')
        if text.startswith('\ufeff'):
            text = text[1:]
        return text, 'utf-8-sig'

    encodings = ['utf-8', 'gbk', 'cp936', 'latin1']

    for encoding in encodings:
        try:
            text = raw.decode(encoding)
            if text.startswith('\ufeff'):
                text = text[1:]
            return text, encoding
        except (UnicodeDecodeError, LookupError):
            continue

    text = raw.decode('utf-8', errors='replace')
    if text.startswith('\ufeff'):
        text = text[1:]
    return text, 'utf-8'


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


def is_patch_header_line(lines: list[str], index: int) -> bool:
    """Return whether a line is a patch header followed by a SEARCH block."""
    stripped = strip_line_ending(lines[index])
    if not stripped.startswith('# '):
        return False

    try:
        _parse_patch_header_text(stripped[2:].strip())
    except ValueError:
        return False

    next_index = index + 1
    while next_index < len(lines) and strip_line_ending(lines[next_index]).strip() == '':
        next_index += 1

    return next_index < len(lines) and strip_line_ending(lines[next_index]) in PATCH_OPEN_MARKERS


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
CREATE_MARK = '<<<<<<< CREATE'
OVERWRITE_MARK = '<<<<<<< OVERWRITE'
DELIM_MARK = '======='
REPLACE_MARK = '>>>>>>> REPLACE'

PATCH_OPEN_MARKERS: dict[str, PatchOperation] = {
    SEARCH_MARK: 'search',
    CREATE_MARK: 'create',
    OVERWRITE_MARK: 'overwrite',
}
OPERATION_TO_MARKER: dict[PatchOperation, str] = {
    operation: marker for marker, operation in PATCH_OPEN_MARKERS.items()
}


def classify_line(lines: list[str], index: int) -> str:
    """
    分类规则：
    F - File path (# path/to/file[:L10-L25])
    S - Patch opener marker (<<<<<<< SEARCH/CREATE/OVERWRITE)
    D - Delimiter (=======)
    R - Replace marker (>>>>>>> REPLACE)
    B - Blank line (仅空白)
    C - Content (其他所有内容)
    """
    stripped = strip_line_ending(lines[index])

    # 文件路径行（允许行尾空格）
    if is_patch_header_line(lines, index):
        return 'F'

    # 标记行必须精确匹配（不允许额外空格）
    if stripped in PATCH_OPEN_MARKERS:
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
    roles = [classify_line(lines, index) for index in range(len(lines))]
    schema = ''.join(roles)  # 1 char per line -> match.span 可直接映射回行数组
    return LRRResult(lines=lines, roles=roles, schema=schema)


# ============ LRR Phase 2: 匹配 Patch 块 ============

# 允许：文件路径行 F 与 SEARCH 标记 S 之间有若干空行 B*
# 内容只允许 B/C（避免吞掉别的结构行）
PATCH_PATTERN = re.compile(r'F(?P<gap>B*)S(?P<search>[BC]*?)D(?P<replace>[BC]*?)R')


def parse_patch_operation(marker_line: str) -> PatchOperation:
    """Decode the concrete patch operation from the raw opener marker line."""
    stripped = strip_line_ending(marker_line)
    try:
        return PATCH_OPEN_MARKERS[stripped]
    except KeyError as e:
        raise ValueError(f'Invalid patch opener: {marker_line}') from e


def validate_patch_block(
    *,
    operation: PatchOperation,
    display_path: str,
    file_path: Path,
    line_range: tuple[int | None, int | None] | None,
    search_content: str,
) -> str | None:
    """Return an error message when a parsed block violates operation rules."""
    if file_path.exists() and not file_path.is_file():
        return f'Not a file: {display_path}'

    if operation in {'create', 'overwrite'}:
        if line_range is not None:
            return (
                f'Line range is only supported for SEARCH patches, got '
                f'{operation.upper()}: {display_path}'
            )
        if search_content.strip() != '':
            return f'{operation.upper()} upper block must be whitespace-only: {display_path}'

    if operation == 'search' and not file_path.exists():
        return f'File does not exist: {display_path}'

    return None


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
            opener_line_idx = file_line_idx + 1 + len(lrr.extract_lines(match, 'gap'))
            opener_line = strip_line_ending(lrr.lines[opener_line_idx])

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

            try:
                operation = parse_patch_operation(opener_line)
            except ValueError as e:
                errors.append(f'Line {opener_line_idx + 1}: {e}')
                continue

            # 提取 SEARCH / REPLACE 内容（不包括标记行）
            search_lines = lrr.extract_lines(match, 'search')
            replace_lines = lrr.extract_lines(match, 'replace')
            search_content = ''.join(search_lines)
            replace_content = ''.join(replace_lines)

            block_error = validate_patch_block(
                operation=operation,
                display_path=display_path,
                file_path=file_path,
                line_range=line_range,
                search_content=search_content,
            )
            if block_error is not None:
                errors.append(f'Line {file_line_idx + 1}: {block_error}')
                continue

            patches.append(
                PatchBlock(
                    file_path=file_path,
                    display_path=display_path,
                    operation=operation,
                    line_range=line_range,
                    search_content=search_content,
                    replace_content=replace_content,
                    source_line_start=file_line_idx + 1,
                )
            )

        except Exception as e:
            errors.append(f'Failed to parse patch block: {e}')

    if patch_text.strip() and not patches and not errors:
        errors.append(
            "No valid patch blocks found. Ensure each block starts with '# <path>' followed by a SEARCH/REPLACE block."
        )

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


def _match_patch(
    patch: PatchBlock,
    file_lines: list[str],
    file_newline: str,
    content: str,
    file_encoding: str,
) -> PatchMatch:
    """Phase 1: 在原始文件内容上定位 patch 的 match 位置（只读）。"""
    total_lines = len(file_lines)
    search_text = convert_newlines(patch.search_content, file_newline)
    search_lines = split_lines_keepends(search_text)
    replace_text = convert_newlines(patch.replace_content, file_newline)
    replace_lines = split_lines_keepends(replace_text)

    def _fail(status: str, error: str | None = None, **kw: object) -> PatchMatch:
        return PatchMatch(
            patch=patch,
            abs_start=0,
            abs_end=0,
            match_mode='',
            match_line=0,
            status=status,
            error=error,
            **kw,  # type: ignore[arg-type]
            search_line_count=len(search_lines),
            replace_line_count=len(replace_lines),
        )

    is_empty_file = content == ''
    is_empty_search = len(search_lines) == 0

    if is_empty_search and not is_empty_file:
        return _fail(
            'parse_error',
            'SEARCH content is empty, this is not allowed when the target file is non-empty (ambiguous match)',
        )
    if is_empty_search and is_empty_file:
        if replace_text == content:
            return _fail('no_change_patch', 'SEARCH is empty and REPLACE would not change the file')
        return _fail('matched')
    if search_text == replace_text:
        return _fail('no_change_patch', 'SEARCH and REPLACE are identical')

    # 确定搜索范围
    if patch.line_range:
        try:
            normalized_range = normalize_line_range(patch.line_range, total_lines)
            if normalized_range is None:
                raise ValueError('Resolved line range is empty')
            scope_start, scope_end = normalized_range
        except ValueError as e:
            return _fail('invalid_line_range', str(e))
        start_idx = scope_start - 1
        end_idx_excl = scope_end
        if start_idx < 0 or end_idx_excl > total_lines:
            return _fail(
                'out_of_range',
                f'Line range {format_line_range(patch.line_range)} is outside file bounds (1-{total_lines})',
            )
        prefix_len = start_idx
        region = file_lines[start_idx:end_idx_excl]
    else:
        prefix_len = 0
        region = file_lines

    search_matches, search_mode = find_preferred_matches(region, search_lines)
    replace_matches, replace_mode = find_preferred_matches(region, replace_lines)

    if len(search_matches) == 1:
        abs_start = prefix_len + search_matches[0]
        return PatchMatch(
            patch=patch,
            abs_start=abs_start,
            abs_end=abs_start + len(search_lines),
            match_mode=search_mode or '',
            match_line=abs_start + 1,
            status='matched',
            search_line_count=len(search_lines),
            replace_line_count=len(replace_lines),
        )

    if len(search_matches) > 1:
        related = [prefix_len + m + 1 for m in search_matches]
        return _fail(
            'search_replace_coexist' if replace_matches else 'search_ambiguous',
            'SEARCH and REPLACE both exist in scope; narrow the line range'
            if replace_matches
            else 'SEARCH matched multiple locations; narrow the line range',
            match_mode=search_mode or '',
            related_lines=related,
        )

    # search 0 matches — 检查 replace 是否已存在
    if len(replace_matches) == 1:
        return PatchMatch(
            patch=patch,
            abs_start=0,
            abs_end=0,
            match_mode=replace_mode or '',
            match_line=prefix_len + replace_matches[0] + 1,
            status='already_applied',
            error='SEARCH not found, but REPLACE already exists',
            search_line_count=len(search_lines),
            replace_line_count=len(replace_lines),
        )
    if len(replace_matches) > 1:
        related = [prefix_len + m + 1 for m in replace_matches]
        return _fail(
            'replace_ambiguous',
            'SEARCH not found, and REPLACE matched multiple locations',
            match_mode=replace_mode or '',
            related_lines=related,
        )
    return _fail('search_not_found', 'SEARCH content not found in scope')


def _match_to_result(m: PatchMatch) -> PatchApplyResult:
    """PatchMatch → PatchApplyResult（用于 batch 失败路径和 already_applied）。"""
    return PatchApplyResult(
        patch=m.patch,
        success=m.status in ('matched', 'already_applied', 'no_change_patch'),
        status=m.status,
        error=m.error,
        match_mode=m.match_mode or None,
        match_line=m.match_line if m.match_line else None,
        related_lines=m.related_lines,
        source_line_start=m.patch.source_line_start,
        search_line_count=m.search_line_count,
        replace_line_count=m.replace_line_count,
    )


def apply_patch(patch: PatchBlock, *, dry_run: bool = False) -> PatchApplyResult:
    """应用单个 patch。"""
    try:
        if patch.operation == 'create':
            replace_text = convert_newlines(patch.replace_content, '\n')
            replace_lines = split_lines_keepends(replace_text)

            if patch.file_path.exists():
                if not patch.file_path.is_file():
                    return PatchApplyResult(
                        patch=patch,
                        success=False,
                        status='not_a_file',
                        error=f'Not a file: {patch.display_path}',
                        source_line_start=patch.source_line_start,
                        replace_line_count=len(replace_lines),
                    )

                existing_content, _ = read_target_text_with_encoding(patch.file_path)
                normalized_existing = convert_newlines(existing_content, '\n')
                if normalized_existing == replace_text:
                    return PatchApplyResult(
                        patch=patch,
                        success=True,
                        status='already_applied',
                        error='CREATE target already exists with identical content',
                        source_line_start=patch.source_line_start,
                        replace_line_count=len(replace_lines),
                    )
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    status='file_exists',
                    error='CREATE target already exists with different content',
                    source_line_start=patch.source_line_start,
                    replace_line_count=len(replace_lines),
                )

            if not dry_run:
                patch.file_path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(patch.file_path, replace_text, encoding='utf-8')

            return PatchApplyResult(
                patch=patch,
                success=True,
                status='applied',
                source_line_start=patch.source_line_start,
                replace_line_count=len(replace_lines),
            )

        if not patch.file_path.exists():
            return PatchApplyResult(
                patch=patch,
                success=False,
                status='missing_file',
                error=f'File does not exist: {patch.display_path}',
                source_line_start=patch.source_line_start,
            )

        if not patch.file_path.is_file():
            return PatchApplyResult(
                patch=patch,
                success=False,
                status='not_a_file',
                error=f'Not a file: {patch.display_path}',
                source_line_start=patch.source_line_start,
            )

        content, file_encoding = read_target_text_with_encoding(patch.file_path)
        file_newline = detect_newline_style(content)
        replace_text = convert_newlines(patch.replace_content, file_newline)
        replace_lines = split_lines_keepends(replace_text)

        if patch.operation == 'overwrite':
            if content == replace_text:
                return PatchApplyResult(
                    patch=patch,
                    success=True,
                    status='no_change_patch',
                    error='OVERWRITE would not change the file',
                    source_line_start=patch.source_line_start,
                    replace_line_count=len(replace_lines),
                )
            if not dry_run:
                atomic_write_text(patch.file_path, replace_text, encoding=file_encoding)
            return PatchApplyResult(
                patch=patch,
                success=True,
                status='applied',
                source_line_start=patch.source_line_start,
                replace_line_count=len(replace_lines),
            )

        # SEARCH: 用 _match_patch 定位，再 splice + write
        file_lines = split_lines_keepends(content)
        m = _match_patch(patch, file_lines, file_newline, content, file_encoding)

        if m.status != 'matched':
            return _match_to_result(m)

        replace_text_conv = convert_newlines(patch.replace_content, file_newline)
        replace_lines = split_lines_keepends(replace_text_conv)
        new_content = ''.join(file_lines[: m.abs_start] + replace_lines + file_lines[m.abs_end :])
        if not dry_run:
            atomic_write_text(patch.file_path, new_content, encoding=file_encoding)
        return PatchApplyResult(
            patch=patch,
            success=True,
            status='applied',
            match_mode=m.match_mode,
            match_line=m.match_line,
            source_line_start=patch.source_line_start,
            search_line_count=m.search_line_count,
            replace_line_count=m.replace_line_count,
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


def _check_overlap(matches: list[PatchMatch]) -> list[tuple[PatchMatch, PatchMatch]]:
    """基于绝对行索引返回所有重叠的 match 对"""
    matched = [m for m in matches if m.status == 'matched']
    overlaps: list[tuple[PatchMatch, PatchMatch]] = []
    for i in range(len(matched)):
        for j in range(i + 1, len(matched)):
            a, b = matched[i], matched[j]
            if a.abs_start < b.abs_end and b.abs_start < a.abs_end:
                overlaps.append((a, b))
    return overlaps


def _apply_search_patches_batch(
    patches: list[PatchBlock],
    *,
    dry_run: bool = False,
) -> list[PatchApplyResult]:
    """同文件多条 search patch 的协调 apply。

    Phase 1: 所有 patch 基于原始文件内容 match（只读）
    Phase 2: 验证无 overlap → 从后往前 splice
    """
    if not patches:
        return []

    file_path = patches[0].file_path

    if not file_path.exists():
        return [
            PatchApplyResult(
                patch=p,
                success=False,
                status='missing_file',
                error=f'File does not exist: {p.display_path}',
                source_line_start=p.source_line_start,
            )
            for p in patches
        ]
    if not file_path.is_file():
        return [
            PatchApplyResult(
                patch=p,
                success=False,
                status='not_a_file',
                error=f'Not a file: {p.display_path}',
                source_line_start=p.source_line_start,
            )
            for p in patches
        ]

    content, file_encoding = read_target_text_with_encoding(file_path)
    file_newline = detect_newline_style(content)
    file_lines = split_lines_keepends(content)

    # Phase 1: match all
    matches = [_match_patch(p, file_lines, file_newline, content, file_encoding) for p in patches]

    # Overlap 检测
    overlaps = _check_overlap(matches)
    if overlaps:
        for m in matches:
            if m.status == 'matched':
                m.status = 'overlap_conflict'
                m.error = 'Overlapping match with another patch in the same batch'

    # 有任何 failure → 全部返回各自结果（matched 但未写入的也标记为失败）
    if any(m.status not in ('matched', 'already_applied', 'no_change_patch') for m in matches):
        results: list[PatchApplyResult] = []
        for m in matches:
            if m.status == 'matched':
                results.append(PatchApplyResult(
                    patch=m.patch,
                    success=False,
                    status='write_error',
                    error='Not applied: another patch in the same batch failed',
                    match_mode=m.match_mode or None,
                    match_line=m.match_line if m.match_line else None,
                    source_line_start=m.patch.source_line_start,
                    search_line_count=m.search_line_count,
                    replace_line_count=m.replace_line_count,
                ))
            else:
                results.append(_match_to_result(m))
        return results

    # Phase 2: 从后往前 splice
    matched = sorted(
        [m for m in matches if m.status == 'matched'],
        key=lambda m: m.abs_start,
        reverse=True,
    )

    new_lines = file_lines[:]
    for m in matched:
        replace_text = convert_newlines(m.patch.replace_content, file_newline)
        replace_lines = split_lines_keepends(replace_text)
        new_lines[m.abs_start : m.abs_end] = replace_lines

    if not dry_run:
        atomic_write_text(file_path, ''.join(new_lines), encoding=file_encoding)

    return [
        PatchApplyResult(
            patch=m.patch,
            success=True,
            status='applied' if m.status == 'matched' else 'already_applied',
            error=m.error,
            match_mode=m.match_mode or None,
            match_line=m.match_line if m.match_line else None,
            source_line_start=m.patch.source_line_start,
            search_line_count=m.search_line_count,
            replace_line_count=m.replace_line_count,
        )
        for m in matches
    ]


def apply_patches(
    patch_text: str,
    *,
    project_root: Path | None = None,
    dry_run: bool = False,
) -> BatchApplyResult:
    """解析并批量应用 patches。

    同文件多条 search patch 走 batch 模式（two-phase match + apply）。
    """
    parse_result = parse_patches(patch_text, project_root=project_root)

    if parse_result.errors:
        return BatchApplyResult(
            results=[
                PatchApplyResult(patch=None, success=False, status='parse_error', error=err)
                for err in parse_result.errors
            ]
        )

    return BatchApplyResult(results=_apply_parsed_patches(parse_result.patches, dry_run=dry_run))


def _apply_parsed_patches(
    patches: list[PatchBlock],
    *,
    dry_run: bool = False,
) -> list[PatchApplyResult]:
    """对已解析的 patch 列表执行 group + batch apply。

    同文件多条 search patch 走 two-phase batch，其余独立 apply。
    返回结果顺序与输入 patches 一致。
    """
    indexed_results: list[tuple[int, PatchApplyResult]] = []
    file_search_patches: dict[Path, list[tuple[int, PatchBlock]]] = {}

    for idx, p in enumerate(patches):
        if p.operation == 'search':
            file_search_patches.setdefault(p.file_path, []).append((idx, p))
        else:
            indexed_results.append((idx, apply_patch(p, dry_run=dry_run)))

    for _file_path, indexed_search_ps in file_search_patches.items():
        if len(indexed_search_ps) == 1:
            orig_idx, p = indexed_search_ps[0]
            indexed_results.append((orig_idx, apply_patch(p, dry_run=dry_run)))
        else:
            search_ps = [p for _, p in indexed_search_ps]
            batch_results = _apply_search_patches_batch(search_ps, dry_run=dry_run)
            for (orig_idx, _), result in zip(indexed_search_ps, batch_results, strict=True):
                indexed_results.append((orig_idx, result))

    indexed_results.sort(key=lambda x: x[0])
    return [r for _, r in indexed_results]


# ============ Prompt 模板 ============

PATCH_PROMPT = r"""# Use CLI `sspec tool patch`

It accepts structured patch blocks for local file edit.

## Patch Block | 3 Type

1) Targeted edit by str replace
````patch
# <path>[:<range>]
<<<<<<< SEARCH
old content
=======
new content
>>>>>>> REPLACE
````
Line range (optional): 1based; `L10-L25`, `L10-`, `-L25`; only in SEARCH method.

2) Create new file
````patch
# <path>
<<<<<<< CREATE
=======
new file content
>>>>>>> REPLACE
````
3) Full overwrite
````patch
# <path>
<<<<<<< OVERWRITE
=======
full replacement content
>>>>>>> REPLACE
````

---

- Markers ('<<<<<<<', '=======', '>>>>>>>') MUST appear alone per line
- Section before '===' of CREATE and OVERWRITE MUST be empty

## Multi-block bundles

Multi-blocks patch is allowed to include concise human-readable explanations surrounding patch blocks. i.e. A text report includes patch blocks.

````example
First, xxx

[[Patch Block]]

Next, xxx

[[Patch Block]]
````

WARN: Multi-blocks targeting the same file are matched against the original content. Overlapping matches cause all related blocks to fail.

## Local reference
"""


def build_patch_prompt() -> str:
    """Build the prompt text with an installed-package local reference when available."""
    try:
        resource = files('sspec').joinpath('templates/skills/write-patch/SKILL.md')
        with as_file(resource) as skill_path:
            return PATCH_PROMPT + f'\n\nLocal reference (if readable): {skill_path}'
    except Exception:
        return PATCH_PROMPT


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
        help='Simulate patch application without modifying files',
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
            console.print(build_patch_prompt())
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
        elif not yes:
            if not click.confirm('Apply these patches?', default=False):
                console.print('[yellow]Aborted.[/yellow]')
                raise click.Abort()

        # Apply patches
        console.print(
            '[cyan]Applying patches...[/cyan]'
            if not dry_run
            else '[cyan]Simulating patches...[/cyan]'
        )
        results = _apply_parsed_patches(parse_result.patches, dry_run=dry_run)

        # Display results
        _display_results(console, results, dry_run=dry_run)

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


def _display_results(
    console: Console,
    results: list[PatchApplyResult],
    *,
    dry_run: bool = False,
) -> None:
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
            note = 'Would apply' if dry_run and result.status == 'applied' else 'Applied'
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
    action_label = 'Would apply' if dry_run else 'Applied'
    if failed == 0:
        console.print(
            '[green]Summary:[/green] '
            f'{action_label}: {applied} | Already applied: {already_applied} | No change: {no_change}'
        )
    else:
        console.print(
            '[yellow]Summary:[/yellow] '
            f'{action_label}: {applied} | Already applied: {already_applied} | '
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
    """Build a compact patch preview for failed patch output."""
    opener = OPERATION_TO_MARKER[patch.operation]
    preview_lines = [opener]
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
                OPERATION_TO_MARKER[result.patch.operation],
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
