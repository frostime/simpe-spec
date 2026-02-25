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
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

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
    line_range: tuple[int, int] | None  # (start, end) 1-based, inclusive
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
    error: str | None = None
    match_mode: str | None = None  # exact | loose
    match_line: int | None = None  # 1-based line number in file
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


def safe_resolve_under_root(root: Path, user_path: str) -> Path:
    """
    将 patch 里的相对路径解析到 root 下：
    - 禁止绝对路径
    - 禁止 .. 越界
    """
    p = Path(user_path)
    if p.is_absolute():
        raise ValueError(f'不允许绝对路径: {user_path}')

    root_abs = root.resolve()
    resolved = (root_abs / p).resolve()

    try:
        resolved.relative_to(root_abs)
    except ValueError:
        raise ValueError(f'路径越界（疑似使用 ..）: {user_path}') from None

    return resolved


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

FILE_PATH_PATTERN = re.compile(r'^#\s+(\S+?)(?::L?(\d+)-L?(\d+))?\s*$')

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
    if FILE_PATH_PATTERN.match(stripped):
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
            m = FILE_PATH_PATTERN.match(file_line)
            if not m:
                errors.append(f'Line {file_line_idx + 1}: 无法解析文件路径: {file_line}')
                continue

            file_path_str, start_str, end_str = m.groups()
            display_path = file_path_str

            # 安全解析路径
            try:
                file_path = safe_resolve_under_root(root, file_path_str)
            except Exception as e:
                errors.append(f'Line {file_line_idx + 1}: 路径不合法: {display_path} ({e})')
                continue

            # 检查文件是否存在
            if not file_path.exists():
                errors.append(f'Line {file_line_idx + 1}: 文件不存在: {display_path}')
                continue
            if not file_path.is_file():
                errors.append(f'Line {file_line_idx + 1}: 不是文件: {display_path}')
                continue

            line_range = None
            if start_str and end_str:
                start_i, end_i = int(start_str), int(end_str)
                if start_i <= 0 or end_i <= 0 or end_i < start_i:
                    errors.append(f'Line {file_line_idx + 1}: 非法行范围: {start_str}-{end_str}')
                    continue
                line_range = (start_i, end_i)

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
            errors.append(f'解析 patch 块失败: {e}')

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


def apply_patch(patch: PatchBlock) -> PatchApplyResult:
    """应用单个 patch"""
    try:
        # 保留原文件换行
        with patch.file_path.open('r', encoding='utf-8', newline='') as f:
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
                    error=f'行范围 {patch.line_range} 超出文件范围 (1-{len(file_lines)})',
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
                error='SEARCH 内容为空：为避免误改，拒绝应用该 patch',
            )

        # 1) 精确匹配
        exact = find_block_matches(region, search_lines, loose=False)
        if len(exact) == 1:
            match_start = exact[0]
            match_mode = 'exact'
        elif len(exact) > 1:
            return PatchApplyResult(
                patch=patch,
                success=False,
                error=f'找到 {len(exact)} 处精确匹配，存在歧义（建议加行范围限定）',
                search_line_count=len(search_lines),
                replace_line_count=len(replace_lines),
            )
        else:
            # 2) 容忍匹配（行尾空白/纯空白行）
            loose = find_block_matches(region, search_lines, loose=True)
            if len(loose) == 1:
                match_start = loose[0]
                match_mode = 'loose'
            elif len(loose) > 1:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    error=(
                        f'找到 {len(loose)} 处匹配（忽略行尾空白后），存在歧义（建议加行范围限定）'
                    ),
                    search_line_count=len(search_lines),
                    replace_line_count=len(replace_lines),
                )
            else:
                return PatchApplyResult(
                    patch=patch,
                    success=False,
                    error='未找到匹配的 SEARCH 内容',
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
            match_mode=match_mode,
            match_line=match_line,
            search_line_count=len(search_lines),
            replace_line_count=len(replace_lines),
        )

    except Exception as e:
        return PatchApplyResult(
            patch=patch,
            success=False,
            error=f'应用 patch 失败: {e}',
        )


def format_patch_header(patch: PatchBlock) -> str:
    header = f'# {patch.display_path}'
    if patch.line_range:
        header += f':L{patch.line_range[0]}-L{patch.line_range[1]}'
    return header


def apply_patches(patch_text: str, *, project_root: Path | None = None) -> BatchApplyResult:
    """解析并批量应用 patches（保持原语义：解析阶段出现错误则不应用）"""
    parse_result = parse_patches(patch_text, project_root=project_root)

    if parse_result.errors:
        return BatchApplyResult(
            results=[
                PatchApplyResult(patch=None, success=False, error=err)
                for err in parse_result.errors
            ]
        )

    results = [apply_patch(p) for p in parse_result.patches]
    return BatchApplyResult(results=results)


# ============ Prompt 模板 ============

PATCH_PROMPT = """Please return the code changes as patches, following the SEARCH/REPLACE specification below:

## Format Specification

Each patch block consists of two parts:

1) File path line (SEARCH must immediately follow; blank lines are allowed in between, but do not insert other text)

Format A (Recommended, common case):
# path/to/file.py

Format B (Optional, used only when the SEARCH fragment is too short and may match multiple locations):
# path/to/file.py:10-25
or
# path/to/file.py:L10-L25

Notes:
- Line number ranges are optional and only used to narrow the search scope to avoid multiple matches
- Line numbers are 1-based and inclusive (including both start and end lines)

2) SEARCH/REPLACE block (marker lines must be on their own line without extra spaces)

#### Example A: Without line number range (most common)

```example
# src/utils.py
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

#### Example B: With line number range (without L)

```example
# src/utils.py:10-25
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

#### Example C: With line number range (with L)

```example
# src/utils.py:L10-L25
<<<<<<< SEARCH
return x * 2
=======
return x * 3
>>>>>>> REPLACE
```

## Important Rules

1. Exact match priority: SEARCH content should exactly match the code in the file (including indentation)
2. Whitespace tolerance fallback: Differences in trailing whitespace/tabs and pure blank lines are ignored during matching, but leading indentation must be consistent
3. Unique match: If multiple matches are found, the operation will fail (recommend using line range restrictions)
4. Path safety: Must be relative to the project root directory; absolute paths and ".." boundary violations are prohibited
5. File existence: Files will be checked for existence before applying patches
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
        '--output-failed',
        type=click.Path(path_type=Path),
        help='Custom directory for failed patches (default: .sspec/tmp/failed-patches/<timestamp>)',
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
        input_mode: bool,
        dry_run: bool,
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
        if input_mode and file_sources:
            console.print('[red]Error:[/red] Use either --input or --file/PATCH_FILE, not both.')
            raise click.Abort()
        if len(file_sources) > 1:
            console.print(
                '[red]Error:[/red] Provide only one patch file source (PATCH_FILE or --file).'
            )
            raise click.Abort()

        use_input = input_mode or (not file_sources)

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
        if use_input:
            from sspec.builtin_tools.prompt import run_interactive_editor

            console.print(
                '[cyan]Interactive input:[/cyan] paste/write patch text, then Esc+Enter to submit.'
            )
            text, _ = run_interactive_editor(root_dir=project_root)
            patch_text = text

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
            raise click.Abort()

        patches = parse_result.patches
        console.print(f'[green][OK][/green] Found {len(patches)} patch(es)\n')

        # Always show preview table (helps understand what will happen)
        table = Table(title='Patches', show_header=True)
        table.add_column('# header', style='cyan', no_wrap=True)
        table.add_column('Scope', style='dim')

        for patch in patches:
            scope = (
                f'L{patch.line_range[0]}-L{patch.line_range[1]}'
                if patch.line_range
                else 'Full file'
            )
            table.add_row(format_patch_header(patch), scope)

        console.print(table)
        console.print()

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
            _save_failed_patches(console, failed_results, output_failed, project_root)

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

    succeeded = 0
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
            succeeded += 1
            match = result.match_mode or '-'
            if result.match_line is not None:
                match = f'{match} @L{result.match_line}'

            delta = result.replace_line_count - result.search_line_count
            table.add_row(
                format_patch_header(result.patch),
                '[green][OK][/green]',
                match,
                f'{delta:+d}',
                'Applied',
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
        console.print(f'[green]Summary:[/green] All {succeeded} patch(es) applied successfully')
    else:
        console.print(f'[yellow]Summary:[/yellow] {succeeded} succeeded, {failed} failed')


def _save_failed_patches(
    console: Console,
    failed_results: list[PatchApplyResult],
    output_dir: Path | None,
    project_root: Path,
) -> None:
    """Save failed patches to a timestamped directory."""
    from datetime import datetime

    if output_dir is None:
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        output_dir = project_root / '.sspec' / 'tmp' / 'failed-patches' / timestamp

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, result in enumerate(failed_results, start=1):
        if result.patch:
            # Reconstruct patch text
            patch_text = f'# {result.patch.display_path}'
            if result.patch.line_range:
                patch_text += f':L{result.patch.line_range[0]}-L{result.patch.line_range[1]}'
            patch_text += '\n'
            patch_text += '<<<<<<< SEARCH\n'
            patch_text += result.patch.search_content
            patch_text += '=======\n'
            patch_text += result.patch.replace_content
            patch_text += '>>>>>>> REPLACE\n'

            # Save to file
            filename = f'patch_{i:02d}.md'
            (output_dir / filename).write_text(patch_text, encoding='utf-8')

    console.print(f'[yellow]Failed patches saved to:[/yellow] {output_dir}')
