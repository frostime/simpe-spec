"""SKILL install helpers for hub-spoke sync.

Public strategy contract is `link|copy`.
Internal link handling still distinguishes symlink and junction where needed.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SkillStrategy = Literal['link', 'copy']
LegacySkillStrategy = Literal['symlink', 'junction', 'link', 'copy']
LinkKind = Literal['none', 'symlink', 'junction']

GITIGNORE_FENCE_START = '# >>> sspec-managed skills >>>'
GITIGNORE_FENCE_END = '# <<< sspec-managed skills <<<'


def normalize_legacy_strategy(raw: str | None) -> SkillStrategy:
    """Normalize strategy values into the public `link|copy` contract."""
    if raw in {'symlink', 'junction', 'link'}:
        return 'link'
    return 'copy'


def _is_junction(path: Path) -> bool:
    """Detect Windows junction directory.

    Junction is a reparse-point directory that is not treated as symlink by
    ``Path.is_symlink()`` in many environments.
    """
    if sys.platform != 'win32':
        return False

    try:
        if not path.exists() or path.is_symlink() or not path.is_dir():
            return False

        attrs = os.lstat(path).st_file_attributes
        reparse_flag = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
        return bool(attrs & reparse_flag)
    except (AttributeError, OSError):
        return False


def detect_path_link(path: Path) -> LinkKind:
    """Return path link kind for symlink/junction aware operations."""
    if path.is_symlink():
        return 'symlink'
    if _is_junction(path):
        return 'junction'
    return 'none'


def check_path_link(path: Path, expected_target: Path | None = None) -> bool:
    """Check whether a path is a link-like directory and optionally points to target.

    Supports symbolic link and Windows junction.
    """
    kind = detect_path_link(path)
    if kind == 'none':
        return False

    if expected_target is None:
        return True

    try:
        return path.resolve(strict=False) == expected_target.resolve()
    except OSError:
        return False


def remove_path_link(path: Path) -> bool:
    """Remove symlink/junction path without touching source directory content."""
    kind = detect_path_link(path)
    if kind == 'none':
        return False

    if kind == 'symlink':
        path.unlink(missing_ok=True)
        return True

    path.rmdir()
    return True


@dataclass(frozen=True)
class SkillInstallResult:
    """Skill 安装结果"""

    target: Path
    source: Path
    strategy: SkillStrategy
    success: bool = True
    error: str | None = None


class SkillInstaller:
    """Skill 安装器：处理 link/copy 策略及 hub-spoke 模式"""

    _default_installer: SkillInstaller | None = None

    def __init__(self):
        pass

    @classmethod
    def _get_installer(cls) -> SkillInstaller:
        """获取默认安装器实例"""
        if cls._default_installer is None:
            cls._default_installer = cls()
        return cls._default_installer

    @staticmethod
    def _prepare_target(target: Path) -> None:
        """准备目标路径：创建父目录，清理已存在内容"""
        target.parent.mkdir(parents=True, exist_ok=True)
        if check_path_link(target):
            remove_path_link(target)
        elif target.exists():
            shutil.rmtree(target)

    @staticmethod
    def _read_gitignore_state(gitignore_path: Path) -> tuple[str, list[str], list[str]]:
        """Read .gitignore and split preserved lines from managed fenced entries."""
        before = gitignore_path.read_text(encoding='utf-8') if gitignore_path.exists() else ''
        lines = before.splitlines()

        managed_entries: list[str] = []
        in_managed = False
        preserved: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped == GITIGNORE_FENCE_START:
                in_managed = True
                continue
            if stripped == GITIGNORE_FENCE_END:
                in_managed = False
                continue

            if in_managed:
                if stripped:
                    managed_entries.append(stripped)
                continue

            preserved.append(line)

        return before, preserved, managed_entries

    @staticmethod
    def _render_gitignore_content(preserved: list[str], managed_entries: list[str]) -> str:
        """Render .gitignore content with preserved lines and an optional managed block."""
        rendered = preserved.copy()

        while rendered and rendered[-1] == '':
            rendered.pop()

        normalized_entries = sorted(
            {entry.strip() for entry in managed_entries if isinstance(entry, str) and entry.strip()}
        )

        if normalized_entries:
            if rendered:
                rendered.append('')
            rendered.append(GITIGNORE_FENCE_START)
            rendered.extend(normalized_entries)
            rendered.append(GITIGNORE_FENCE_END)

        if not rendered:
            return ''

        return '\n'.join(rendered) + '\n'

    @staticmethod
    def sync_managed_gitignore_entries(
        gitignore_path: Path, entries: list[str], dry_run: bool = False
    ) -> bool:
        """Replace the sspec-managed fenced block with exactly the provided entries."""
        before, preserved, _managed_entries = SkillInstaller._read_gitignore_state(gitignore_path)
        after = SkillInstaller._render_gitignore_content(preserved, entries)
        changed = after != before

        if not changed or dry_run:
            return changed

        if after:
            gitignore_path.parent.mkdir(parents=True, exist_ok=True)
            gitignore_path.write_text(after, encoding='utf-8')
        else:
            gitignore_path.unlink(missing_ok=True)

        return True

    @staticmethod
    def _upsert_gitignore_fence(gitignore_path: Path, entry: str) -> None:
        """Insert or update sspec managed block in .gitignore."""
        _before, _preserved, managed_entries = SkillInstaller._read_gitignore_state(gitignore_path)
        SkillInstaller.sync_managed_gitignore_entries(
            gitignore_path,
            [*managed_entries, entry],
            dry_run=False,
        )

    @staticmethod
    def _add_to_gitignore(target: Path) -> None:
        """将 spoke 的 `skills` 目录添加到父目录的 .gitignore。"""
        gitignore_path = target.parent / '.gitignore'
        skill_name = target.name
        SkillInstaller._upsert_gitignore_fence(gitignore_path, skill_name)

    @staticmethod
    def _add_hub_skills_to_gitignore(sspec_root: Path, skill_names: list[str]) -> None:
        """Write managed hub skill ignores into `.sspec/.gitignore`."""
        entries = [
            f'skills/{name.strip()}'
            for name in skill_names
            if isinstance(name, str) and name.strip()
        ]
        SkillInstaller.sync_managed_gitignore_entries(
            sspec_root / '.gitignore',
            entries,
            dry_run=False,
        )

    def _try_create_symlink(self, source: Path, target: Path) -> bool:
        """尝试创建符号链接（不提权）"""
        try:
            target.symlink_to(source, target_is_directory=True)
            return check_path_link(target, expected_target=source)
        except (OSError, NotImplementedError):
            return False

    def _try_create_junction(self, source: Path, target: Path) -> bool:
        """Try create Windows junction link without elevation."""
        if sys.platform != 'win32':
            return False

        cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            (
                '$ErrorActionPreference="Stop"; '
                f'New-Item -ItemType Junction -Path "{target}" '
                f'-Target "{source}" | Out-Null'
            ),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return check_path_link(target, expected_target=source)
        except Exception:
            return False

    def install_batch(
        self,
        items: list[tuple[Path, Path]],
        prefer_symlink: bool = True,
    ) -> list[SkillInstallResult]:
        """批量安装 skills

        Args:
            items: (source, target) 路径对列表
            prefer_symlink: 优先使用符号链接

        Returns:
            安装结果列表
        """
        if not items:
            return []

        results: list[SkillInstallResult] = []

        # 准备所有目标路径
        for _source, target in items:
            self._prepare_target(target)

        if not prefer_symlink:
            # 直接全部复制
            for source, target in items:
                shutil.copytree(source, target)
                self._add_to_gitignore(target)
                results.append(SkillInstallResult(target, source, 'copy'))
            return results

        for source, target in items:
            linked = (
                self._try_create_junction(source, target)
                if sys.platform == 'win32'
                else self._try_create_symlink(source, target)
            )
            if linked:
                self._add_to_gitignore(target)
                results.append(SkillInstallResult(target, source, 'link'))
                continue

            shutil.copytree(source, target)
            self._add_to_gitignore(target)
            results.append(SkillInstallResult(target, source, 'copy'))

        return results

    def _recreate_link(self, source: Path, target: Path) -> None:
        """Recreate platform-preferred link (junction on Windows, symlink otherwise)."""
        target.parent.mkdir(parents=True, exist_ok=True)

        if sys.platform == 'win32':
            if not self._try_create_junction(source, target):
                raise OSError(f'Failed to create junction for {target}')
            return

        if not self._try_create_symlink(source, target):
            raise OSError(f'Failed to create symlink for {target}')

    def update_skill(self, source: Path, target: Path, strategy: LegacySkillStrategy) -> None:
        """更新已安装的 skill

        Args:
            source: 模板 skill 目录
            target: 已安装的 skill 目录
            strategy: 记录的安装策略
        """
        if normalize_legacy_strategy(strategy) == 'link':
            # link 策略：确保链接有效且指向正确
            if check_path_link(target, expected_target=source):
                return

            if check_path_link(target):
                remove_path_link(target)
            elif target.exists():
                shutil.rmtree(target)

            self._recreate_link(source, target)
        else:
            # 复制策略：重新复制
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)

    # ========================================================================
    # 向后兼容的类方法接口
    # ========================================================================

    @staticmethod
    def install_skills_batch(
        installs: list[tuple[Path, Path]],
        prefer_symlink: bool = True,
        allow_elevation: bool = True,
        prefer_junction_on_windows: bool = False,
    ) -> list[tuple[Path, Path, SkillStrategy]]:
        """兼容旧 API：批量安装

        Args:
            installs: (source, target) 路径对列表
            prefer_symlink: 优先使用符号链接

        Returns:
            (target, source, strategy) 三元组列表
        """
        del allow_elevation, prefer_junction_on_windows
        installer = SkillInstaller._get_installer()
        results = installer.install_batch(installs, prefer_symlink=prefer_symlink)
        return [(r.target, r.source, r.strategy) for r in results]

    @staticmethod
    def install_hub_and_links_batch(
        installs: list[tuple[Path, Path, list[Path]]], prefer_symlink: bool = True
    ) -> dict[Path, SkillStrategy]:
        """兼容旧 API：批量 hub-spoke 安装

        Args:
            installs: (source, hub, spokes) 三元组列表
            prefer_symlink: spokes 是否优先使用符号链接

        Returns:
            {target_path: strategy} 字典
        """
        installer = SkillInstaller._get_installer()
        return installer.install_hub_and_spokes_batch(installs, prefer_symlink)

    @staticmethod
    def install_skill(
        source_dir: Path, target_dir: Path, prefer_symlink: bool = True
    ) -> SkillStrategy:
        """兼容旧 API：单个安装

        Args:
            source_dir: 模板 skill 目录
            target_dir: 目标安装位置
            prefer_symlink: 优先使用符号链接

        Returns:
            使用的安装策略
        """
        results = SkillInstaller.install_skills_batch([(source_dir, target_dir)], prefer_symlink)
        if results:
            return results[0][2]
        raise OSError('Failed to install skill')

    @staticmethod
    def add_skill_to_gitignore(target_dir: Path) -> None:
        """兼容旧 API：添加到 gitignore

        Args:
            target_dir: skill 目录路径
        """
        SkillInstaller._add_to_gitignore(target_dir)

    @staticmethod
    def add_hub_skills_to_gitignore(sspec_root: Path, skill_names: list[str]) -> None:
        """Maintain hub-managed skill ignores in `.sspec/.gitignore`."""
        SkillInstaller._add_hub_skills_to_gitignore(sspec_root, skill_names)

    def install_hub_and_spokes_batch(
        self, items: list[tuple[Path, Path, list[Path]]], prefer_symlink: bool = True
    ) -> dict[Path, SkillStrategy]:
        """批量 hub-spoke 安装（返回字典格式以兼容旧代码）

        Args:
            items: (source, hub, spokes) 三元组列表
            prefer_symlink: spokes 是否优先使用符号链接

        Returns:
            {target_path: strategy} 字典
        """
        result_dict: dict[Path, SkillStrategy] = {}
        hub_skill_names: list[str] = []
        hub_sspec_root: Path | None = None

        # 第一步：安装所有 hubs（总是复制）
        for source, hub, _spokes in items:
            self._prepare_target(hub)
            shutil.copytree(source, hub)
            hub_skill_names.append(hub.name)
            if hub_sspec_root is None:
                hub_sspec_root = hub.parent.parent
            result_dict[hub] = 'copy'

        if hub_sspec_root is not None:
            self._add_hub_skills_to_gitignore(hub_sspec_root, hub_skill_names)

        # 第二步：收集所有 spokes 对，按平台创建 link。
        all_spoke_pairs: list[tuple[Path, Path]] = []
        for _source, hub, spokes in items:
            for spoke in spokes:
                all_spoke_pairs.append((hub, spoke))

        if all_spoke_pairs:
            spoke_results = self.install_batch(
                all_spoke_pairs,
                prefer_symlink=prefer_symlink,
            )
            for result in spoke_results:
                result_dict[result.target] = result.strategy

        return result_dict
