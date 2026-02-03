"""SKILL installation strategy abstraction with symlink fallback to copy."""

from pathlib import Path
from typing import Literal

SkillStrategy = Literal['symlink', 'copy']


class SkillInstaller:
    """Handles SKILL installation with symlink + copy fallback."""

    @staticmethod
    def install_skill(
        source_dir: Path,
        target_dir: Path,
        prefer_symlink: bool = True
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
        # Ensure target parent exists
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # If target already exists, remove it
        if target_dir.exists():
            if target_dir.is_symlink():
                target_dir.unlink()
            else:
                import shutil
                shutil.rmtree(target_dir)

        # Try symlink first if preferred
        if prefer_symlink:
            try:
                target_dir.symlink_to(source_dir, target_is_directory=True)
                return 'symlink'
            except (OSError, NotImplementedError):
                # Symlink failed (permissions, unsupported OS, etc.)
                pass

        # Fallback to copy
        import shutil
        shutil.copytree(source_dir, target_dir)
        return 'copy'

    @staticmethod
    def update_skill(
        source_dir: Path,
        target_dir: Path,
        strategy: SkillStrategy
    ) -> None:
        """Update an installed skill using recorded strategy.

        Args:
            source_dir: Template skill directory
            target_dir: Installed skill location
            strategy: Strategy to use ('symlink' or 'copy')
        """
        if strategy == 'symlink':
            # Symlinked skills auto-update (pointing to template)
            # Only verify the link is still valid
            if not target_dir.exists():
                # Link broken, recreate
                target_dir.symlink_to(source_dir, target_is_directory=True)
        else:
            # Copy strategy: re-copy to update
            if target_dir.exists():
                import shutil
                shutil.rmtree(target_dir)
            import shutil
            shutil.copytree(source_dir, target_dir)
