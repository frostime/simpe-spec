"""Tests for sspec.services.ask_service — ask creation, name normalization, conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from sspec.services.ask_service import (archive_ask, convert_ask_to_md,
                                        create_ask_template,
                                        execute_ask_prompt,
                                        extract_ask_name_from_filename,
                                        find_ask_matches, normalize_ask_name,
                                        save_ask_answer)

# ---------------------------------------------------------------------------
# normalize_ask_name
# ---------------------------------------------------------------------------


class TestNormalizeAskName:
    def test_hyphens_to_underscores(self):
        name, _ = normalize_ask_name('my-question')
        assert name == 'my_question'

    def test_special_chars_removed(self):
        name, _ = normalize_ask_name('what@about#this?')
        assert name == 'what_about_this'

    def test_returns_warning_when_changed(self):
        _, warning = normalize_ask_name('my-question')
        assert warning is not None
        assert 'converted' in warning.lower()

    def test_no_warning_when_unchanged(self):
        _, warning = normalize_ask_name('already_ok')
        assert warning is None

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            normalize_ask_name('!!!')

    def test_collapses_underscores(self):
        name, _ = normalize_ask_name('a---b___c')
        assert '__' not in name
        assert name == 'a_b_c'


# ---------------------------------------------------------------------------
# extract_ask_name_from_filename
# ---------------------------------------------------------------------------


class TestExtractAskName:
    def test_timestamped_format(self):
        assert extract_ask_name_from_filename('260101120000_my_question') == 'my_question'

    def test_plain_name(self):
        assert extract_ask_name_from_filename('plain') == 'plain'


# ---------------------------------------------------------------------------
# create_ask_template
# ---------------------------------------------------------------------------


class TestCreateAskTemplate:
    def test_creates_yml_file(self, sspec_root: Path):
        path, _ = create_ask_template(sspec_root, 'token-storage')
        assert path.exists()
        assert path.suffix == '.yml'

    def test_template_content_structure(self, sspec_root: Path):
        path, _ = create_ask_template(sspec_root, 'design-choice')
        content = path.read_text(encoding='utf-8')
        assert 'created' in content
        assert 'reason' in content
        assert 'question' in content
        assert 'user_answer' in content

    def test_name_conversion_warning(self, sspec_root: Path):
        _, warning = create_ask_template(sspec_root, 'my-question')
        assert warning is not None

    def test_conflict_handling(self, sspec_root: Path):
        p1, _ = create_ask_template(sspec_root, 'same-name')
        p2, _ = create_ask_template(sspec_root, 'same-name')
        assert p1 != p2
        assert p2.exists()


# ---------------------------------------------------------------------------
# execute_ask_prompt with pre-filled answer
# ---------------------------------------------------------------------------


class TestExecuteAskPrompt:
    def test_prefilled_answer_returned(self, sspec_root: Path):
        path, _ = create_ask_template(sspec_root, 'prefilled')
        content = path.read_text(encoding='utf-8')
        content = content.replace('USER_FILL_HERE', 'Use Redis')
        path.write_text(content, encoding='utf-8')

        answer = execute_ask_prompt(path)
        assert answer == 'Use Redis'

    def test_missing_file_with_md_fallback(self, sspec_root: Path):
        """If pending file is missing but .md exists, return a warning message."""
        asks_dir = sspec_root / 'asks'
        yml_path = asks_dir / 'completed.yml'
        md_path = asks_dir / 'completed.md'
        md_path.write_text('---\nname: completed\n---\n', encoding='utf-8')

        result = execute_ask_prompt(yml_path)
        assert 'already completed' in result.lower() or 'Warning' in result

    def test_truly_missing_file_raises(self, sspec_root: Path):
        with pytest.raises(FileNotFoundError):
            execute_ask_prompt(sspec_root / 'asks' / 'nonexistent.yml')

    def test_legacy_py_prefilled_answer_returned(self, sspec_root: Path):
        path = sspec_root / 'asks' / 'legacy.py'
        path.write_text(
            'CREATED = "2026-01-01T00:00:00"\n'
            'REASON = r"""legacy reason"""\n'
            'QUESTION = r"""legacy question"""\n'
            'USER_ANSWER = r"""Legacy Answer"""\n',
            encoding='utf-8',
        )

        answer = execute_ask_prompt(path)
        assert answer == 'Legacy Answer'


# ---------------------------------------------------------------------------
# save_ask_answer + convert_ask_to_md
# ---------------------------------------------------------------------------


class TestSaveAndConvert:
    def test_save_appends_answer(self, sspec_root: Path):
        path, _ = create_ask_template(sspec_root, 'save-test')
        content = path.read_text(encoding='utf-8')
        content = content.replace('<YOUR_QUESTION_HERE>', 'What DB to use?')
        path.write_text(content, encoding='utf-8')

        save_ask_answer(path, 'PostgreSQL')
        updated = path.read_text(encoding='utf-8')
        assert 'answer:' in updated
        assert 'PostgreSQL' in updated

    def test_convert_to_md(self, sspec_root: Path):
        path, _ = create_ask_template(sspec_root, 'convert-test')
        content = path.read_text(encoding='utf-8')
        content = content.replace('<YOUR_QUESTION_HERE>', 'Which framework?')
        content = content.replace('<brief_reason>', 'Need to decide')
        path.write_text(content, encoding='utf-8')
        save_ask_answer(path, 'FastAPI')

        md_path = convert_ask_to_md(path)
        assert md_path.exists()
        assert md_path.suffix == '.md'
        assert not path.exists()

        md_content = md_path.read_text(encoding='utf-8')
        assert 'FastAPI' in md_content
        assert 'Which framework?' in md_content

    def test_convert_legacy_py_to_md(self, sspec_root: Path):
        path = sspec_root / 'asks' / '260101120000_legacy.py'
        path.write_text(
            'CREATED = "2026-01-01T00:00:00"\n'
            'REASON = r"""legacy reason"""\n'
            'QUESTION = r"""legacy question"""\n'
            'ANSWER = r"""legacy answer"""\n',
            encoding='utf-8',
        )

        md_path = convert_ask_to_md(path)
        assert md_path.exists()
        assert not path.exists()
        assert 'legacy answer' in md_path.read_text(encoding='utf-8')


# ---------------------------------------------------------------------------
# find_ask_matches
# ---------------------------------------------------------------------------


class TestFindAskMatches:
    def test_exact_match(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        f = asks_dir / 'my_question.md'
        f.write_text('---\n---\n', encoding='utf-8')
        assert f in find_ask_matches(asks_dir, 'my_question')

    def test_suffix_match(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        f = asks_dir / '260101120000_topic.md'
        f.write_text('', encoding='utf-8')
        assert f in find_ask_matches(asks_dir, 'topic')

    def test_strips_md_extension(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        f = asks_dir / 'q.md'
        f.write_text('', encoding='utf-8')
        assert f in find_ask_matches(asks_dir, 'q.md')

    def test_no_match(self, sspec_root: Path):
        assert find_ask_matches(sspec_root / 'asks', 'nonexistent') == []


# ---------------------------------------------------------------------------
# archive_ask
# ---------------------------------------------------------------------------


class TestArchiveAsk:
    def test_moves_to_archive(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        f = asks_dir / 'done.md'
        f.write_text('completed ask', encoding='utf-8')

        dest = archive_ask(sspec_root, asks_dir, f)
        assert dest.exists()
        assert not f.exists()
        assert 'archive' in str(dest)

    def test_conflict_resolution(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        archive_dir = asks_dir / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / 'dup.md').write_text('old', encoding='utf-8')

        f = asks_dir / 'dup.md'
        f.write_text('new', encoding='utf-8')
        dest = archive_ask(sspec_root, asks_dir, f)
        assert dest.exists()
        assert dest.name != 'dup.md'  # counter appended

    def test_updates_references_inside_archive_dirs(self, sspec_root: Path):
        asks_dir = sspec_root / 'asks'
        request_archive = sspec_root / 'requests' / 'archive'
        change_archive = sspec_root / 'changes' / 'archive' / '26-02-15T00-00_demo'
        request_archive.mkdir(parents=True, exist_ok=True)
        change_archive.mkdir(parents=True, exist_ok=True)

        ask_file = asks_dir / 'topic.md'
        ask_file.write_text('ask content', encoding='utf-8')

        old_path = '.sspec/asks/topic.md'
        req_file = request_archive / 'r.md'
        change_spec = change_archive / 'spec.md'
        req_file.write_text(f'link: {old_path}\n', encoding='utf-8')
        change_spec.write_text(f'link: {old_path}\n', encoding='utf-8')

        dest = archive_ask(sspec_root, asks_dir, ask_file)
        new_path = dest.relative_to(sspec_root.parent).as_posix()

        assert new_path in req_file.read_text(encoding='utf-8')
        assert new_path in change_spec.read_text(encoding='utf-8')
