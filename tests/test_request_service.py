"""Tests for sspec.services.request_service — create, find, link, archive requests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from sspec.libs.md_yaml import parse_frontmatter
from sspec.services.change_service import create_change
from sspec.services.request_service import (
    archive_request,
    create_request,
    extract_request_name_from_filename,
    find_request_matches,
    link_request_to_change,
    list_requests,
    normalize_request_name,
    parse_request_file,
)


# ---------------------------------------------------------------------------
# normalize_request_name
# ---------------------------------------------------------------------------


class TestNormalizeRequestName:
    def test_basic_normalization(self):
        assert normalize_request_name('My Feature!') == 'my-feature'

    def test_spaces_to_hyphens(self):
        assert normalize_request_name('add user auth') == 'add-user-auth'

    def test_special_chars_removed(self):
        assert normalize_request_name('fix@bug#123') == 'fixbug123'

    def test_already_normalized(self):
        assert normalize_request_name('already-normal') == 'already-normal'

    def test_strips_whitespace(self):
        assert normalize_request_name('  padded  ') == 'padded'


# ---------------------------------------------------------------------------
# extract_request_name_from_filename
# ---------------------------------------------------------------------------


class TestExtractRequestName:
    def test_new_format(self):
        assert extract_request_name_from_filename('26-01-02T03-04_my-request') == 'my-request'

    def test_old_format(self):
        assert extract_request_name_from_filename('250102030405-old-request') == 'old-request'

    def test_plain_name(self):
        assert extract_request_name_from_filename('simple') == 'simple'


# ---------------------------------------------------------------------------
# create_request
# ---------------------------------------------------------------------------


class TestCreateRequest:
    def test_creates_file_with_frontmatter(self, sspec_root: Path):
        path = create_request(
            sspec_root=sspec_root,
            name='Auth Feature',
            template_path=None,
            now=datetime(2026, 1, 15, 10, 30, 0),
        )
        assert path.exists()
        content = path.read_text(encoding='utf-8')
        assert content.startswith('---\n')
        assert 'status: OPEN' in content
        assert 'attach-change: null' in content
        assert '26-01-15T10-30' in path.name

    def test_invalid_name_raises(self, sspec_root: Path):
        with pytest.raises(ValueError):
            create_request(sspec_root=sspec_root, name='!!!', template_path=None)

    def test_duplicate_raises(self, sspec_root: Path):
        ts = datetime(2026, 1, 1, 0, 0, 0)
        create_request(sspec_root=sspec_root, name='dup', template_path=None, now=ts)
        with pytest.raises(FileExistsError):
            create_request(sspec_root=sspec_root, name='dup', template_path=None, now=ts)

    def test_with_template(self, sspec_root: Path, tmp_path: Path):
        tpl = tmp_path / 'request.md'
        tpl.write_text(
            '---\ncreated: {{TIME}}\nstatus: OPEN\n---\n# {{NAME}}\n',
            encoding='utf-8',
        )
        path = create_request(
            sspec_root=sspec_root,
            name='from-template',
            template_path=tpl,
            now=datetime(2026, 2, 1, 0, 0, 0),
        )
        content = path.read_text(encoding='utf-8')
        assert 'from-template' in content


# ---------------------------------------------------------------------------
# find_request_matches
# ---------------------------------------------------------------------------


class TestFindRequestMatches:
    def test_exact_match(self, sspec_root: Path):
        rd = sspec_root / 'requests'
        f = rd / 'my-request.md'
        f.write_text('---\nstatus: OPEN\n---\n', encoding='utf-8')
        assert find_request_matches(rd, 'my-request') == [f]

    def test_suffix_match_new_format(self, sspec_root: Path):
        rd = sspec_root / 'requests'
        f = rd / '26-01-01T00-00_feature.md'
        f.write_text('---\nstatus: OPEN\n---\n', encoding='utf-8')
        assert f in find_request_matches(rd, 'feature')

    def test_old_format_match(self, sspec_root: Path):
        rd = sspec_root / 'requests'
        f = rd / '250101000000-old-feat.md'
        f.write_text('---\nstatus: OPEN\n---\n', encoding='utf-8')
        matches = find_request_matches(rd, 'old-feat')
        assert f in matches

    def test_contains_fallback(self, sspec_root: Path):
        rd = sspec_root / 'requests'
        f = rd / 'add-user-authentication.md'
        f.write_text('---\nstatus: OPEN\n---\n', encoding='utf-8')
        assert f in find_request_matches(rd, 'auth')

    def test_no_match(self, sspec_root: Path):
        assert find_request_matches(sspec_root / 'requests', 'nonexistent') == []

    def test_nonexistent_dir(self, tmp_path: Path):
        assert find_request_matches(tmp_path / 'nope', 'x') == []


# ---------------------------------------------------------------------------
# parse_request_file
# ---------------------------------------------------------------------------


class TestParseRequestFile:
    def test_parses_standard_request(self, sspec_root: Path):
        f = sspec_root / 'requests' / '26-01-01T00-00_demo.md'
        f.write_text(
            '---\ncreated: 2026-01-01\nstatus: OPEN\ntldr: short summary\n---\n# Demo\n',
            encoding='utf-8',
        )
        info = parse_request_file(f)
        assert info is not None
        assert info.status == 'OPEN'
        assert info.tldr == 'short summary'

    def test_name_from_frontmatter(self, sspec_root: Path):
        f = sspec_root / 'requests' / 'whatever.md'
        f.write_text('---\nname: explicit-name\nstatus: OPEN\n---\n', encoding='utf-8')
        info = parse_request_file(f)
        assert info is not None
        assert info.name == 'explicit-name'

    def test_name_from_filename_fallback(self, sspec_root: Path):
        f = sspec_root / 'requests' / '26-01-01T00-00_inferred.md'
        f.write_text('---\nstatus: OPEN\n---\n', encoding='utf-8')
        info = parse_request_file(f)
        assert info is not None
        assert info.name == 'inferred'

    def test_tldr_fallback_from_body(self, sspec_root: Path):
        f = sspec_root / 'requests' / 'no-tldr.md'
        f.write_text('---\nstatus: OPEN\n---\nFirst meaningful line\n', encoding='utf-8')
        info = parse_request_file(f)
        assert info is not None
        assert 'First meaningful' in info.tldr

    def test_no_frontmatter_returns_none(self, sspec_root: Path):
        f = sspec_root / 'requests' / 'plain.md'
        f.write_text('No frontmatter here\n', encoding='utf-8')
        assert parse_request_file(f) is None

    def test_status_alias_normalized(self, sspec_root: Path):
        f = sspec_root / 'requests' / 'alias.md'
        f.write_text('---\nstatus: TODO\n---\n', encoding='utf-8')
        info = parse_request_file(f)
        assert info is not None
        assert info.status == 'OPEN'


# ---------------------------------------------------------------------------
# list_requests
# ---------------------------------------------------------------------------


class TestListRequests:
    def test_empty_project(self, sspec_root: Path):
        assert list_requests(sspec_root) == []

    def test_lists_active_requests(self, sspec_root: Path):
        create_request(sspec_root=sspec_root, name='req-a', template_path=None)
        create_request(sspec_root=sspec_root, name='req-b', template_path=None)
        reqs = list_requests(sspec_root)
        assert len(reqs) == 2

    def test_excludes_archived_by_default(self, sspec_root: Path):
        path = create_request(sspec_root=sspec_root, name='to-archive', template_path=None)
        info = parse_request_file(path)
        archive_request(sspec_root, info)
        assert len(list_requests(sspec_root)) == 0

    def test_includes_archived_when_requested(self, sspec_root: Path):
        path = create_request(sspec_root=sspec_root, name='arch-incl', template_path=None)
        info = parse_request_file(path)
        archive_request(sspec_root, info)
        reqs = list_requests(sspec_root, include_archived=True)
        assert any(r.archived for r in reqs)


# ---------------------------------------------------------------------------
# link_request_to_change
# ---------------------------------------------------------------------------


class TestLinkRequestToChange:
    def test_updates_request_frontmatter(self, sspec_root: Path):
        req_path = create_request(sspec_root=sspec_root, name='link-test', template_path=None)
        change_path = create_change(sspec_root, 'my-change')

        link_request_to_change(
            sspec_root=sspec_root,
            request_file=req_path,
            change_path=change_path,
        )

        content = req_path.read_text(encoding='utf-8')
        meta, _ = parse_frontmatter(content)
        assert meta['status'] == 'DOING'
        assert 'spec.md' in str(meta.get('attach-change', ''))

    def test_adds_reference_to_change_spec(self, sspec_root: Path):
        req_path = create_request(sspec_root=sspec_root, name='ref-test', template_path=None)
        change_path = create_change(sspec_root, 'ref-change')

        link_request_to_change(
            sspec_root=sspec_root,
            request_file=req_path,
            change_path=change_path,
        )

        spec_content = (change_path / 'spec.md').read_text(encoding='utf-8')
        meta, _ = parse_frontmatter(spec_content)
        assert 'reference' in meta
        refs = meta['reference']
        assert any(r.get('type') == 'request' for r in refs)

    def test_no_duplicate_references(self, sspec_root: Path):
        req_path = create_request(sspec_root=sspec_root, name='nodup', template_path=None)
        change_path = create_change(sspec_root, 'nodup-change')

        # Link twice
        link_request_to_change(
            sspec_root=sspec_root, request_file=req_path, change_path=change_path
        )
        link_request_to_change(
            sspec_root=sspec_root, request_file=req_path, change_path=change_path
        )

        spec_content = (change_path / 'spec.md').read_text(encoding='utf-8')
        meta, _ = parse_frontmatter(spec_content)
        assert len(meta['reference']) == 1

    def test_missing_change_raises(self, sspec_root: Path):
        req_path = create_request(sspec_root=sspec_root, name='bad-link', template_path=None)
        with pytest.raises(FileNotFoundError):
            link_request_to_change(
                sspec_root=sspec_root,
                request_file=req_path,
                change_path=sspec_root / 'changes' / 'nonexistent',
            )


# ---------------------------------------------------------------------------
# archive_request
# ---------------------------------------------------------------------------


class TestArchiveRequest:
    def test_moves_to_archive(self, sspec_root: Path):
        path = create_request(sspec_root=sspec_root, name='to-arch', template_path=None)
        info = parse_request_file(path)
        dest = archive_request(sspec_root, info)
        assert dest.exists()
        assert not path.exists()
        assert 'archive' in str(dest)

    def test_adds_archived_timestamp(self, sspec_root: Path):
        path = create_request(sspec_root=sspec_root, name='ts-arch', template_path=None)
        info = parse_request_file(path)
        dest = archive_request(sspec_root, info)
        content = dest.read_text(encoding='utf-8')
        assert 'archived:' in content

    def test_conflict_resolution(self, sspec_root: Path):
        """Pre-existing file in archive with same name should not cause failure."""
        path = create_request(sspec_root=sspec_root, name='conflict', template_path=None)

        # Pre-populate archive with same filename
        archive_dir = sspec_root / 'requests' / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / path.name).write_text('old', encoding='utf-8')

        info = parse_request_file(path)
        dest = archive_request(sspec_root, info)
        assert dest.exists()
        # Should have a counter suffix
        assert dest.stem != path.stem
