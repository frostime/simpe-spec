"""SKILL installation strategy abstraction with symlink fallback to copy."""

from pathlib import Path
from typing import Literal

SkillStrategy = Literal['symlink', 'copy']


class SkillInstaller:
    """Handles SKILL installation with symlink + copy fallback."""

    _elevation_attempted = False
    _elevation_disabled = False

    @staticmethod
    def _is_windows_admin() -> bool:
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    @staticmethod
    def _ps_escape(value: str) -> str:
        return value.replace('`', '``').replace('"', '`"')

    @staticmethod
    def _try_symlink_with_elevation(source_dir: Path, target_dir: Path) -> bool:
        if SkillInstaller._elevation_disabled:
            return False
        if SkillInstaller._is_windows_admin():
            return False
        if SkillInstaller._elevation_attempted:
            return False

        SkillInstaller._elevation_attempted = True

        import subprocess
        import tempfile

        source_path = str(source_dir)
        target_path = str(target_dir)

        ps_content = (
            f'$src = "{source_path}"; $dst = "{target_path}"; '
            f'if (Test-Path -LiteralPath $dst) {{ '
            f'Remove-Item -LiteralPath $dst -Recurse -Force }}; '
            f'New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null'
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_content)
            ps_path = f.name

        try:
            cmd = [
                'powershell',
                '-Command',
                f'Start-Process -Verb RunAs powershell.exe '
                f'-ArgumentList "-NoProfile","-File","{ps_path}" -Wait',
            ]
            subprocess.run(cmd, check=True)
            return target_dir.is_symlink()
        except Exception:
            SkillInstaller._elevation_disabled = True
            return False
        finally:
            import os

            try:
                os.unlink(ps_path)
            except Exception:
                pass

    @staticmethod
    def install_skills_batch(
        installs: list[tuple[Path, Path]], prefer_symlink: bool = True
    ) -> list[tuple[Path, Path, SkillStrategy]]:
        """Install multiple skills with single elevation prompt on Windows.

        Args:
            installs: List of (source_dir, target_dir) tuples
            prefer_symlink: Try symlink first if True

        Returns:
            List of (target_dir, source_dir, strategy) tuples for each install
        """
        if not installs:
            return []

        import shutil
        import sys

        result: list[tuple[Path, Path, SkillStrategy]] = []

        # Prepare all targets first (create parents, remove existing)
        for _source_dir, target_dir in installs:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_dir.exists():
                if target_dir.is_symlink():
                    target_dir.unlink()
                else:
                    shutil.rmtree(target_dir)

        if prefer_symlink:
            # First pass: try creating all symlinks without elevation
            symlink_candidates: list[tuple[Path, Path]] = []
            failed_indices: list[int] = []

            for idx, (source_dir, target_dir) in enumerate(installs):
                try:
                    target_dir.symlink_to(source_dir, target_is_directory=True)
                    SkillInstaller.add_skill_to_gitignore(target_dir)
                    result.append((target_dir, source_dir, 'symlink'))
                except (OSError, NotImplementedError):
                    symlink_candidates.append((source_dir, target_dir))
                    failed_indices.append(idx)

            # Second pass: try elevation for remaining (Windows only)
            if symlink_candidates and sys.platform == 'win32':
                elevated_success = SkillInstaller._try_elevated_symlinks_batch(symlink_candidates)
                for (source_dir, target_dir), success in zip(
                    symlink_candidates, elevated_success, strict=True
                ):
                    if success:
                        SkillInstaller.add_skill_to_gitignore(target_dir)
                        result.append((target_dir, source_dir, 'symlink'))
                    else:
                        # Fall through to copy
                        installs_to_copy = [
                            (s, t)
                            for i, (s, t) in enumerate(symlink_candidates)
                            if not elevated_success[i]
                        ]
                        if installs_to_copy:
                            for copy_source, copy_target in installs_to_copy:
                                shutil.copytree(copy_source, copy_target)
                                SkillInstaller.add_skill_to_gitignore(copy_target)
                                result.append((copy_target, copy_source, 'copy'))
                        break

            # Fallback remaining to copy (if not handled above)
            if len(result) < len(installs):
                for _idx, (source_dir, target_dir) in enumerate(installs):
                    if _idx >= len(result) or result[_idx][2] != 'symlink':
                        shutil.copytree(source_dir, target_dir)
                        SkillInstaller.add_skill_to_gitignore(target_dir)
                        result.append((target_dir, source_dir, 'copy'))
        else:
            # No symlink preference: copy all
            for source_dir, target_dir in installs:
                shutil.copytree(source_dir, target_dir)
                SkillInstaller.add_skill_to_gitignore(target_dir)
                result.append((target_dir, source_dir, 'copy'))

        return result

    @staticmethod
    def install_hub_and_links_batch(
        installs: list[tuple[Path, Path, list[Path]]],
        prefer_symlink: bool = True,
    ) -> dict[Path, SkillStrategy]:
        """Batch install skills to hub directories, then symlink to other locations.

        Args:
            installs: List of (source_dir, hub_dir, link_dirs) tuples
            prefer_symlink: Try symlink for links if True

        Returns:
            Dict mapping target directories to strategies used
        """
        import shutil

        result: dict[Path, SkillStrategy] = {}

        # Prepare all hubs and link directories first
        hub_targets: list[tuple[Path, Path]] = []
        all_link_dirs: list[tuple[Path, Path]] = []

        for source_dir, hub_dir, link_dirs in installs:
            # Prepare hub
            hub_dir.parent.mkdir(parents=True, exist_ok=True)
            if hub_dir.exists():
                if hub_dir.is_symlink():
                    hub_dir.unlink()
                else:
                    shutil.rmtree(hub_dir)
            hub_targets.append((source_dir, hub_dir))

            # Prepare link dirs
            for link_dir in link_dirs:
                link_dir.parent.mkdir(parents=True, exist_ok=True)
                if link_dir.exists():
                    if link_dir.is_symlink():
                        link_dir.unlink()
                    else:
                        shutil.rmtree(link_dir)
                all_link_dirs.append((hub_dir, link_dir))

        # Copy all hubs first
        for source_dir, hub_dir in hub_targets:
            shutil.copytree(source_dir, hub_dir)
            SkillInstaller.add_skill_to_gitignore(hub_dir)
            result[hub_dir] = 'copy'

        # Create all symlinks to hubs
        if prefer_symlink:
            # First pass: try creating all symlinks without elevation
            failed_links: list[tuple[Path, Path]] = []
            for hub_dir, link_dir in all_link_dirs:
                try:
                    link_dir.symlink_to(hub_dir, target_is_directory=True)
                    SkillInstaller.add_skill_to_gitignore(link_dir)
                    result[link_dir] = 'symlink'
                except (OSError, NotImplementedError):
                    failed_links.append((hub_dir, link_dir))

            # Second pass: try elevation for failed links (Windows only)
            if failed_links:
                import sys

                if sys.platform == 'win32' and not SkillInstaller._elevation_attempted:
                    elevated_success = SkillInstaller._try_elevated_hub_links_batch(failed_links)
                    for (hub, link), success in zip(failed_links, elevated_success, strict=True):
                        if success:
                            SkillInstaller.add_skill_to_gitignore(link)
                            result[link] = 'symlink'
                        else:
                            # Fallback to copy
                            shutil.copytree(hub, link)
                            SkillInstaller.add_skill_to_gitignore(link)
                            result[link] = 'copy'
                else:
                    # Non-Windows or elevation disabled: copy remaining
                    for hub, link in failed_links:
                        shutil.copytree(hub, link)
                        SkillInstaller.add_skill_to_gitignore(link)
                        result[link] = 'copy'
        else:
            # No symlink preference: copy to all link locations
            for hub_dir, link_dir in all_link_dirs:
                shutil.copytree(hub_dir, link_dir)
                SkillInstaller.add_skill_to_gitignore(link_dir)
                result[link_dir] = 'copy'

        return result

    @staticmethod
    def install_hub_and_links(
        source_dir: Path,
        hub_dir: Path,
        link_dirs: list[Path],
        prefer_symlink: bool = True,
    ) -> dict[Path, SkillStrategy]:
        """Install skills to a central hub directory, then symlink to other locations.

        Args:
            source_dir: Template skill directory to install from
            hub_dir: Target hub location (copy mode)
            link_dirs: Target link locations (symlink mode)
            prefer_symlink: Try symlink for links if True

        Returns:
            Dict mapping target directories to strategies used
        """
        return SkillInstaller.install_hub_and_links_batch(
            installs=[(source_dir, hub_dir, link_dirs)],
            prefer_symlink=prefer_symlink,
        )

    @staticmethod
    def _try_elevated_hub_links_batch(pairs: list[tuple[Path, Path]]) -> list[bool]:
        """Try to create multiple symlinks to hubs with single elevation prompt.

        Args:
            pairs: List of (hub_dir, link_dir) tuples

        Returns:
            List of booleans indicating success for each pair
        """
        if not pairs:
            return []

        if SkillInstaller._elevation_disabled:
            return [False] * len(pairs)

        if SkillInstaller._is_windows_admin():
            return [False] * len(pairs)

        if SkillInstaller._elevation_attempted:
            return [False] * len(pairs)

        SkillInstaller._elevation_attempted = True

        import subprocess
        import tempfile

        ps_lines = []
        for hub_dir, link_dir in pairs:
            hub_path = str(hub_dir)
            link_path = str(link_dir)
            ps_lines.append(
                f'$src = "{hub_path}"; $dst = "{link_path}"; '
                f'if (Test-Path -LiteralPath $dst) {{ '
                f'Remove-Item -LiteralPath $dst -Recurse -Force }}; '
                f'New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null'
            )

        ps_content = '\n'.join(ps_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_content)
            ps_path = f.name

        try:
            cmd = [
                'powershell',
                '-Command',
                f'Start-Process -Verb RunAs powershell.exe '
                f'-ArgumentList "-NoProfile","-File","{ps_path}" -Wait',
            ]
            subprocess.run(cmd, check=True)

            results = []
            for _hub_dir, link_dir in pairs:
                results.append(link_dir.is_symlink())
            return results
        except Exception:
            SkillInstaller._elevation_disabled = True
            return [False] * len(pairs)
        finally:
            import os

            try:
                os.unlink(ps_path)
            except Exception:
                pass

        return results

    @staticmethod
    def _try_elevated_symlinks_batch(pairs: list[tuple[Path, Path]]) -> list[bool]:
        """Try to create multiple symlinks with single elevation prompt.

        Args:
            pairs: List of (source_dir, target_dir) tuples

        Returns:
            List of booleans indicating success for each pair
        """
        if not pairs:
            return []

        if SkillInstaller._elevation_disabled:
            return [False] * len(pairs)

        if SkillInstaller._is_windows_admin():
            return [False] * len(pairs)

        if SkillInstaller._elevation_attempted:
            return [False] * len(pairs)

        SkillInstaller._elevation_attempted = True

        import subprocess
        import tempfile

        ps_lines = []
        for source_dir, target_dir in pairs:
            source_path = str(source_dir)
            target_path = str(target_dir)
            ps_lines.append(
                f'$src = "{source_path}"; $dst = "{target_path}"; '
                f'if (Test-Path -LiteralPath $dst) {{ '
                f'Remove-Item -LiteralPath $dst -Recurse -Force }}; '
                f'New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null'
            )

        ps_content = '\n'.join(ps_lines)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_content)
            ps_path = f.name

        try:
            cmd = [
                'powershell',
                '-Command',
                f'Start-Process -Verb RunAs powershell.exe '
                f'-ArgumentList "-NoProfile","-File","{ps_path}" -Wait',
            ]
            subprocess.run(cmd, check=True)

            results = []
            for _source_dir, target_dir in pairs:
                results.append(target_dir.is_symlink())
            return results
        except Exception:
            SkillInstaller._elevation_disabled = True
            return [False] * len(pairs)
        finally:
            import os

            try:
                os.unlink(ps_path)
            except Exception:
                pass

    @staticmethod
    def install_skill(
        source_dir: Path, target_dir: Path, prefer_symlink: bool = True
    ) -> SkillStrategy:
        """Install a skill directory using best available strategy.

        Args:
            source_dir: Template skill directory to install from
            target_dir: Target location to install to
            prefer_symlink: Try symlink first if True

        Returns:
            Strategy used: 'symlink' or 'copy'

        Raises:
            OSError: If both symlink and copy fail
        """
        results = SkillInstaller.install_skills_batch([(source_dir, target_dir)], prefer_symlink)
        if results:
            return results[0][2]
        raise OSError('Failed to install skill')

    @staticmethod
    def add_skill_to_gitignore(target_dir: Path) -> None:
        """Add the skill directory name to .gitignore in the parent directory.

        Args:
            target_dir: The installed skill directory path.
        """
        gitignore_path = target_dir.parent / '.gitignore'
        skill_name = target_dir.name
        if gitignore_path.exists():
            with gitignore_path.open('r', encoding='utf-8') as f:
                lines = f.read().splitlines()
        else:
            lines = []
        if skill_name not in lines:
            lines.append(f'{skill_name}/**')
            with gitignore_path.open('w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

    @staticmethod
    def update_skill(source_dir: Path, target_dir: Path, strategy: SkillStrategy) -> None:
        """Update an installed skill using recorded strategy.

        Args:
            source_dir: Template skill directory
            target_dir: Installed skill location
            strategy: Strategy to use ('symlink' or 'copy')
        """
        if strategy == 'symlink':
            # Symlinked skills auto-update (pointing to template).
            # Ensure the link exists and points to the expected source.
            if target_dir.is_symlink():
                try:
                    if target_dir.exists() and target_dir.resolve() == source_dir.resolve():
                        return
                except OSError:
                    # Broken symlink or resolution error, recreate below.
                    pass
                target_dir.unlink(missing_ok=True)
            elif target_dir.exists():
                # Existing real directory/file at target path.
                import shutil

                shutil.rmtree(target_dir)

            target_dir.parent.mkdir(parents=True, exist_ok=True)
            target_dir.symlink_to(source_dir, target_is_directory=True)
            return

        else:
            # Copy strategy: re-copy to update
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)
            import shutil

            shutil.copytree(source_dir, target_dir)
