from __future__ import annotations

import os
from pathlib import Path

from sspec.builtin_tools.pack_zip import GitignoreParser


def test_gitignore_parser_skips_missing_dirs_during_walk(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / 'repo'
    root.mkdir()
    (root / '.gitignore').write_text('dist/\n', encoding='utf-8')
    visible = root / 'src'
    visible.mkdir()
    (visible / '.gitignore').write_text('*.pyc\n', encoding='utf-8')

    original_walk = os.walk

    def flaky_walk(top, topdown=True, onerror=None, followlinks=False):
        top_path = Path(top).resolve()
        if top_path == root.resolve():
            yield str(root.resolve()), ['src', 'broken'], ['.gitignore']
            if onerror is not None:
                onerror(FileNotFoundError('broken link target'))
            yield str(visible.resolve()), [], ['.gitignore']
            return
        yield from original_walk(top, topdown=topdown, onerror=onerror, followlinks=followlinks)

    monkeypatch.setattr(os, 'walk', flaky_walk)

    parser = GitignoreParser(root)

    assert root.resolve() in parser.specs
    assert visible.resolve() in parser.specs
