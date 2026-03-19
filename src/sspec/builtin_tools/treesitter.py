"""
给 LLM 用的 Python 文件结构分析工具
"""

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    import click
    from tree_sitter import Node  # pyright: ignore[reportMissingImports]


__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
    'pyfile_symbols_outline',
]

TOOL_NAME = 'treesitter'
TOOL_DESCRIPTION = 'Analyze code symbols using tree-sitter, support py/ts/js (optional dependency)'

TOOL_PROMPT = """
# treesitter - Python Symbol Outline

Analyze Python / JavaScript / TypeScript file structure with tree-sitter and
print a symbol outline.

## Important

- tree-sitter dependencies are optional and not installed by default in sspec.
- Dependencies are language-specific and can be installed independently.

## Install

```
pip install tree-sitter tree-sitter-python
pip install tree-sitter tree-sitter-javascript
pip install tree-sitter tree-sitter-typescript
```

## Usage

```
sspec tool treesitter path/to/file.py
sspec tool treesitter path/to/file.ts
sspec tool treesitter path/to/file.py --depth 1
sspec tool treesitter path/to/file.ts --lang ts
sspec tool treesitter --prompt
```

- `--depth 0`: top-level symbols only
- `--depth 1`: include one nested level (for example methods in classes)
- `--lang auto` (default): infer from file suffix (.py/.js/.jsx/.ts/.tsx)
""".strip()

_LANG_HINTS = ('auto', 'py', 'js', 'ts', 'tsx')

_LANG_EXTENSIONS = {
    'py': {'.py'},
    'js': {'.js', '.jsx', '.mjs', '.cjs'},
    'ts': {'.ts', '.mts', '.cts'},
    'tsx': {'.tsx'},
}

# ================================================================
# Python Treesitter
# ================================================================


@dataclass
class SymbolNode:
    name: str
    kind: str  # class, method, function, constant, interface, type, enum
    line: int
    signature: str = ''  # (a: int) -> int 或 = "value"
    doc: str = ''
    children: list['SymbolNode'] = field(default_factory=list)


class _PythonStructureParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.source_code = b''
        import tree_sitter_python as tspython  # pyright: ignore[reportMissingImports]
        from tree_sitter import (  # pyright: ignore[reportMissingImports]
            Language,
            Node,
            Parser,
        )

        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def _read_file(self):
        with open(self.file_path, 'rb') as f:
            self.source_code = f.read()

    def _text(self, node: 'Node | None') -> str: # pyright: ignore[reportGeneralTypeIssues]
        if node is None:
            return ''
        return self.source_code[node.start_byte : node.end_byte].decode('utf-8')

    def _clean_doc(self, raw_doc: str) -> str:
        """清理文档：去除引号，去除换行，截断长度"""
        if not raw_doc:
            return ''
        # 去除引号
        content = raw_doc.strip().strip('"""').strip("'''").strip()
        # 替换换行为空格，压缩多余空格
        content = ' '.join(content.split())
        # 限制长度
        if len(content) > 100:
            content = content[:97] + '...'
        return content

    def _get_docstring(self, body_node: 'Node | None') -> str: # pyright: ignore[reportGeneralTypeIssues]
        if not body_node:
            return ''
        for child in body_node.children:
            if child.type == 'expression_statement':
                expr = child.child(0)
                if expr.type == 'string': # pyright: ignore[reportOptionalMemberAccess] #
                    return self._clean_doc(self._text(expr))
            elif child.type not in ('comment', 'string'):
                break
        return ''

    def _visit(self, node: 'Node | None', parent_kind: str = 'root') -> Optional[SymbolNode]: # pyright: ignore[reportGeneralTypeIssues]
        if node is None:
            return None
        # 1. 穿透装饰器 (@tool def ...)
        if node.type == 'decorated_definition':
            definition = node.child(node.child_count - 1)
            return self._visit(definition, parent_kind)

        # 2. Class 定义
        if node.type == 'class_definition':
            name = self._text(node.child_by_field_name('name'))
            body = node.child_by_field_name('body')
            doc = self._get_docstring(body)

            symbol = SymbolNode(name, 'class', node.start_point[0] + 1, doc=doc)

            if body:
                for child in body.children:
                    child_sym = self._visit(child, 'class')
                    if child_sym:
                        symbol.children.append(child_sym)
            return symbol

        # 3. Function / Method 定义
        if node.type == 'function_definition':
            name = self._text(node.child_by_field_name('name'))
            # 过滤私有方法，但保留 __init__
            if name.startswith('_') and name != '__init__':
                return None

            kind = 'method' if parent_kind == 'class' else 'function'

            # 构建签名
            params = self._text(node.child_by_field_name('parameters') or node)
            ret_node = node.child_by_field_name('return_type')
            ret_str = f' -> {self._text(ret_node)}' if ret_node else ''

            body = node.child_by_field_name('body')
            doc = self._get_docstring(body)

            return SymbolNode(
                name, kind, node.start_point[0] + 1, f'{params}{ret_str}', doc
            )

        # 4. 常量 (Assignment / Annotated Assignment)
        # 匹配 API_KEY = ... 或 API_KEY: str = ...
        if node.type in ('assignment', 'annotated_assignment'):
            left = node.child_by_field_name('left')  # 对于 assignment
            if not left:  # 对于 annotated_assignment, 结构不同，这里简化处理
                # tree-sitter python 这里的结构略有不同，简单起见只处理普通赋值
                # 如果需要非常严谨，需要分别处理 assignment(left=pattern) 和 annotated(left=identifier)
                if node.child(0).type == 'identifier': # type: ignore
                    left = node.child(0)

            if left and left.type == 'identifier':
                var_name = self._text(left)
                if var_name.isupper():  # 只提取全大写常量
                    right = node.child_by_field_name('right') or node.child(
                        node.child_count - 1
                    )
                    val = self._text(right)
                    if len(val) > 20:
                        val = val[:20] + '...'
                    return SymbolNode(
                        var_name, 'constant', node.start_point[0] + 1, f'= {val}'
                    )

        return None

    def parse(self) -> list[SymbolNode]:
        self._read_file()
        tree = self.parser.parse(self.source_code)
        return [s for child in tree.root_node.children if (s := self._visit(child))]


class _JsTsStructureParser:
    def __init__(self, file_path: str, lang: str):
        self.file_path = file_path
        self.lang = lang
        self.source_code = b''

        from tree_sitter import Language, Parser  # pyright: ignore[reportMissingImports]

        self.language = _resolve_ts_language(lang, Language)
        self.parser = Parser(self.language)

    def _read_file(self):
        with open(self.file_path, 'rb') as f:
            self.source_code = f.read()

    def _text(self, node: 'Node') -> str:
        return self.source_code[node.start_byte : node.end_byte].decode('utf-8')

    def _visit(self, node: 'Node', parent_kind: str = 'root') -> Optional[SymbolNode]:
        if node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            body = node.child_by_field_name('body')
            symbol = SymbolNode(
                self._text(name_node),
                'class',
                node.start_point[0] + 1,
            )

            if body:
                for child in body.children:
                    child_sym = self._visit(child, 'class')
                    if child_sym:
                        symbol.children.append(child_sym)
            return symbol

        if node.type == 'method_definition' and parent_kind == 'class':
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            params = node.child_by_field_name('parameters')
            signature = self._text(params) if params else '()'
            return SymbolNode(
                self._text(name_node),
                'method',
                node.start_point[0] + 1,
                signature,
            )

        if node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            params = node.child_by_field_name('parameters')
            signature = self._text(params) if params else '()'
            return SymbolNode(
                self._text(name_node),
                'function',
                node.start_point[0] + 1,
                signature,
            )

        if node.type in (
            'interface_declaration',
            'type_alias_declaration',
            'enum_declaration',
        ):
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            kind_map = {
                'interface_declaration': 'interface',
                'type_alias_declaration': 'type',
                'enum_declaration': 'enum',
            }
            return SymbolNode(
                self._text(name_node),
                kind_map[node.type],
                node.start_point[0] + 1,
            )

        if node.type in ('lexical_declaration', 'variable_declaration'):
            for child in node.children:
                if child.type != 'variable_declarator':
                    continue

                name_node = child.child_by_field_name('name')
                if not name_node:
                    continue

                name = self._text(name_node)
                value_node = child.child_by_field_name('value')

                if value_node and value_node.type in (
                    'arrow_function',
                    'function',
                    'function_expression',
                ):
                    params = value_node.child_by_field_name('parameters')
                    signature = self._text(params) if params else '()'
                    return SymbolNode(
                        name,
                        'function',
                        node.start_point[0] + 1,
                        signature,
                    )

                if name.isupper() and value_node:
                    value = self._text(value_node)
                    if len(value) > 20:
                        value = value[:20] + '...'
                    return SymbolNode(
                        name,
                        'constant',
                        node.start_point[0] + 1,
                        f'= {value}',
                    )

        return None

    def parse(self) -> list[SymbolNode]:
        self._read_file()
        tree = self.parser.parse(self.source_code)
        return [s for child in tree.root_node.children if (s := self._visit(child))]


def _resolve_ts_language(lang: str, language_cls):
    """Resolve tree-sitter language object by language hint."""
    if lang == 'py':
        import tree_sitter_python as tspython  # pyright: ignore[reportMissingImports]

        return language_cls(tspython.language())

    if lang == 'js':
        import tree_sitter_javascript as tsjavascript  # pyright: ignore[reportMissingImports]

        return language_cls(tsjavascript.language())

    import tree_sitter_typescript as tsts  # pyright: ignore[reportMissingImports]

    if lang == 'ts':
        return language_cls(tsts.language_typescript())

    return language_cls(tsts.language_tsx())


def _check_tree_sitter_dependency(lang: str) -> tuple[bool, str | None]:
    """Check optional language dependencies and return install guidance."""
    try:
        __import__('tree_sitter')

        package_map = {
            'py': 'tree_sitter_python',
            'js': 'tree_sitter_javascript',
            'ts': 'tree_sitter_typescript',
            'tsx': 'tree_sitter_typescript',
        }
        __import__(package_map[lang])
    except ImportError:
        install_hint = {
            'py': 'pip install tree-sitter tree-sitter-python',
            'js': 'pip install tree-sitter tree-sitter-javascript',
            'ts': 'pip install tree-sitter tree-sitter-typescript',
            'tsx': 'pip install tree-sitter tree-sitter-typescript',
        }[lang]
        return (
            False,
            f"tree-sitter dependencies for '{lang}' are not installed. "
            f'Please run: {install_hint}',
        )

    return True, None


def _resolve_language(path: Path, lang_hint: str) -> str | None:
    """Resolve analysis language from hint or file suffix."""
    if lang_hint != 'auto':
        return lang_hint

    suffix = path.suffix.lower()
    for lang, suffixes in _LANG_EXTENSIONS.items():
        if suffix in suffixes:
            return lang

    return None


def _render_outline(
    symbols: list[dict[str, Any]],
    max_depth: int,
    current_depth: int = 0,
    parent_prefix: str = '',
) -> str:
    def append_tree_text(
        lines: list[str],
        first_prefix: str,
        continuation_prefix: str,
        text: str,
    ) -> None:
        parts = text.splitlines() or ['']

        lines.append(f'{first_prefix}{parts[0]}')
        for part in parts[1:]:
            lines.append(f'{continuation_prefix}{part}')

    lines = []
    for i, sym in enumerate(symbols):
        is_last = i == len(symbols) - 1
        branch = '└─ ' if is_last else '├─ '
        child_prefix = parent_prefix + ('   ' if is_last else '│  ')
        first_prefix = parent_prefix + branch
        continuation_prefix = child_prefix + ' '

        # 格式: [类型] 名字 签名 [Ln X]
        # 类型简写: C=Class, M=Method, F=Function, K=Const
        kind_map = {
            'class': '[Cls]',
            'method': '[Method]',
            'function': '[Fun]',
            'constant': '[Const]',
            'interface': '[Interface]',
            'type': '[Type]',
            'enum': '[Enum]',
        }
        k_tag = kind_map.get(sym['kind'], '[?]')

        append_tree_text(
            lines,
            first_prefix,
            continuation_prefix,
            f'{k_tag} {sym["name"]}{sym["signature"]} [Ln {sym["line"]}]',
        )

        # 文档显示 (如果有)
        if sym['doc']:
            lines.append(f'{child_prefix}  "{sym["doc"]}"')

        # 递归
        if sym['children'] and current_depth < max_depth:
            child_output = _render_outline(
                sym['children'],
                max_depth,
                current_depth + 1,
                child_prefix,
            )
            lines.append(child_output)

    return '\n'.join(lines)


def pyfile_symbols_outline(file_path: str, max_depth: int = 0) -> str:
    """打印 python 代码文件的符号定义大纲

    Args:
        file_path (str): 文件路径
        max_depth (int): 0=只看顶层, 1=展开一层(如类内方法), 2=展开更多

    Returns:
        List[dict]: 符号大纲列表
    """
    try:
        import tree_sitter_python as tspython  # pyright: ignore[reportMissingImports]
        from tree_sitter import Language, Node, Parser  # pyright: ignore[reportMissingImports]
    except ImportError:
        return (
            'Error: Required libraries not found. '
            "Please ask user to install with "
            "'pip install tree-sitter tree-sitter-python'."
        )
    parser = _PythonStructureParser(file_path)
    symbols = parser.parse()
    symbols = [asdict(s) for s in symbols]
    tree_str = _render_outline(symbols, max_depth=max_depth)

    output = f'FILE ANALYSIS: {os.path.basename(file_path)}\n'
    output += '-' * 30 + '\n'
    output += tree_str + '\n'

    return output


def jstsfile_symbols_outline(file_path: str, max_depth: int, lang: str) -> str:
    """Print JS/TS code symbol outline."""
    try:
        from tree_sitter import Language  # pyright: ignore[reportMissingImports]

        _resolve_ts_language(lang, Language)
    except ImportError:
        return (
            'Error: Required libraries not found. '
            "Please install tree-sitter runtime and target language package."
        )

    parser = _JsTsStructureParser(file_path, lang)
    symbols = parser.parse()
    symbols = [asdict(s) for s in symbols]
    tree_str = _render_outline(symbols, max_depth=max_depth)

    output = f'FILE ANALYSIS: {os.path.basename(file_path)} ({lang})\n'
    output += '-' * 30 + '\n'
    output += tree_str + '\n'

    return output


def register_command(group: 'click.Group') -> None:
    """Register treesitter as a Click subcommand."""
    import click

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument('file_path', required=False)
    @click.option(
        '--depth',
        default=1,
        show_default=True,
        type=click.IntRange(0, 8),
        help='Outline depth: 0=top-level only, 1+=include nested symbols.',
    )
    @click.option(
        '--lang',
        'lang_hint',
        default='auto',
        show_default=True,
        type=click.Choice(_LANG_HINTS, case_sensitive=False),
        help='Language hint: auto|py|js|ts|tsx.',
    )
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show LLM-oriented tool description.',
    )
    def treesitter_command(
        file_path: str | None,
        depth: int,
        lang_hint: str,
        show_prompt: bool,
    ) -> None:
        """Analyze a Python file and print symbol outline."""
        if show_prompt:
            click.echo(TOOL_PROMPT)
            return

        if not file_path:
            raise click.ClickException('Missing argument: FILE_PATH')

        target = Path(file_path)
        if not target.exists() or target.is_dir():
            raise click.ClickException(f'File not found: {target}')

        lang = _resolve_language(target, lang_hint.lower())
        if not lang:
            raise click.ClickException(
                'Cannot infer language from suffix. Use --lang py|js|ts|tsx.'
            )

        ok, err = _check_tree_sitter_dependency(lang)
        if not ok:
            raise click.ClickException(err or 'Missing tree-sitter dependencies.')

        if lang == 'py':
            output = pyfile_symbols_outline(str(target), max_depth=depth)
        else:
            output = jstsfile_symbols_outline(str(target), max_depth=depth, lang=lang)

        if output.startswith('Error:'):
            raise click.ClickException(output)

        click.echo(output.rstrip())
