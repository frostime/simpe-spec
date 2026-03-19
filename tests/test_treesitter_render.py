"""Rendering tests for treesitter outline output."""

from sspec.builtin_tools.treesitter import _render_outline


def test_render_outline_keeps_tree_prefix_for_multiline_signature() -> None:
    symbols = [
        {
            'name': 'compute',
            'kind': 'method',
            'line': 12,
            'signature': '(\n    self,\n    value: int,\n) -> int',
            'doc': '',
            'children': [],
        }
    ]

    output = _render_outline(symbols, max_depth=0)
    lines = output.splitlines()

    assert lines[0] == '└─ [Method] compute('
    assert lines[1].strip() == 'self,'
    assert lines[2].strip() == 'value: int,'
    assert lines[3].strip() == ') -> int [Ln 12]'
    assert '└─' not in lines[1]
    assert '├─' not in lines[1]


def test_render_outline_last_parent_does_not_leak_vertical_line() -> None:
    symbols = [
        {
            'name': 'Parent',
            'kind': 'class',
            'line': 1,
            'signature': '',
            'doc': '',
            'children': [
                {
                    'name': 'child',
                    'kind': 'method',
                    'line': 2,
                    'signature': '() -> None',
                    'doc': '',
                    'children': [],
                }
            ],
        }
    ]

    output = _render_outline(symbols, max_depth=1)
    lines = output.splitlines()

    assert lines[0] == '└─ [Cls] Parent [Ln 1]'
    assert lines[1].startswith('   └─ [Method] child() -> None [Ln 2]')
    assert not lines[1].startswith('│')
