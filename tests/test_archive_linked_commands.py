"""Tests for linked archive options in request/change commands."""

from __future__ import annotations

import pytest

try:
    from sspec.commands.change import _archive_single_change
    from sspec.commands.request import _archive_single_request
    from sspec.services.change_service import create_change, parse_change
    from sspec.services.request_service import (
        create_request,
        link_request_to_change,
        parse_request_file,
    )

    HAS_COMMANDS = True
except ImportError:
    HAS_COMMANDS = False

pytestmark = pytest.mark.skipif(not HAS_COMMANDS, reason='questionary not installed')


class TestLinkedArchiveFromRequest:
    def test_with_change_archives_linked_change(self, sspec_root, monkeypatch):
        monkeypatch.chdir(sspec_root.parent)
        request_path = create_request(
            sspec_root=sspec_root,
            name='archive-with-change',
            template_path=None,
        )
        change_path = create_change(sspec_root, 'linked-change')
        link_request_to_change(
            sspec_root=sspec_root,
            request_file=request_path,
            change_path=change_path,
        )

        request_info = parse_request_file(request_path)
        assert request_info is not None

        _archive_single_request(
            sspec_root=sspec_root,
            request_info=request_info,
            auto_yes=True,
            with_change=True,
        )

        assert not request_path.exists()
        assert not change_path.exists()
        archived_request_files = list((sspec_root / 'requests' / 'archive').glob('*.md'))
        assert archived_request_files
        assert (sspec_root / 'changes' / 'archive' / change_path.name).exists()


class TestLinkedArchiveFromChange:
    def test_with_request_archives_linked_request(self, sspec_root, monkeypatch):
        monkeypatch.chdir(sspec_root.parent)
        request_path = create_request(
            sspec_root=sspec_root,
            name='archive-with-request',
            template_path=None,
        )
        change_path = create_change(sspec_root, 'linked-request')
        link_request_to_change(
            sspec_root=sspec_root,
            request_file=request_path,
            change_path=change_path,
        )

        change_info = parse_change(change_path)

        _archive_single_change(
            sspec_root=sspec_root,
            change_info=change_info,
            yes=True,
            with_request=True,
        )

        assert not change_path.exists()
        assert not request_path.exists()
        assert (sspec_root / 'changes' / 'archive' / change_path.name).exists()
        archived_request_files = list((sspec_root / 'requests' / 'archive').glob('*.md'))
        assert archived_request_files
