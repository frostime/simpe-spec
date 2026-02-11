"""优化后的 SKILL 安装策略模块

核心改进：
1. 职责分离：ElevationManager 专门处理 Windows 提权
2. 统一接口：单一批量安装方法支持所有场景
3. 清晰状态：使用实例变量和结果对象
4. 消除重复：合并相似逻辑
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SkillStrategy = Literal['symlink', 'copy']


@dataclass(frozen=True)
class SkillInstallResult:
    """Skill 安装结果"""

    target: Path
    source: Path
    strategy: SkillStrategy
    success: bool = True
    error: str | None = None


class ElevationManager:
    """Windows 提权管理器（单例模式）"""

    _instance: ElevationManager | None = None

    def __new__(cls) -> ElevationManager:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._attempted = False
            instance._disabled = False
            cls._instance = instance
        return cls._instance

    @property
    def attempted(self) -> bool:
        """是否已尝试过提权"""
        return self._attempted

    @property
    def disabled(self) -> bool:
        """提权是否被禁用"""
        return self._disabled

    def mark_attempted(self) -> None:
        """标记已尝试提权"""
        self._attempted = True

    def mark_disabled(self) -> None:
        """标记提权被禁用"""
        self._disabled = True

    @staticmethod
    def is_windows_admin() -> bool:
        """检查是否已有管理员权限"""
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def try_elevated_symlinks(self, pairs: list[tuple[Path, Path]]) -> list[bool]:
        """尝试使用提权创建批量符号链接

        Args:
            pairs: (source, target) 路径对列表

        Returns:
            每个 pair 的成功状态列表
        """
        if not pairs:
            return []

        # 跳过条件检查
        if self._disabled or self.is_windows_admin() or self._attempted:
            return [False] * len(pairs)

        self.mark_attempted()

        import subprocess
        import sys
        import tempfile

        if sys.platform != 'win32':
            return [False] * len(pairs)

        # 生成 PowerShell 脚本
        ps_lines = []
        for source, target in pairs:
            ps_lines.append(
                f'$src = "{source}"; $dst = "{target}"; '
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

            # 验证每个符号链接是否创建成功
            return [target.is_symlink() for _, target in pairs]
        except Exception:
            self.mark_disabled()
            return [False] * len(pairs)
        finally:
            import os

            try:
                os.unlink(ps_path)
            except Exception:
                pass


class SkillInstaller:
    """Skill 安装器：处理 symlink/copy 策略及 hub-spoke 模式"""

    _default_installer: SkillInstaller | None = None

    def __init__(self, elevation_manager: ElevationManager | None = None):
        self._elevation = elevation_manager or ElevationManager()

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
        if target.exists():
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target)

    @staticmethod
    def _add_to_gitignore(target: Path) -> None:
        """将 skill 目录添加到父目录的 .gitignore"""
        gitignore_path = target.parent / '.gitignore'
        skill_name = target.name

        if gitignore_path.exists():
            with gitignore_path.open('r', encoding='utf-8') as f:
                lines = f.read().splitlines()
        else:
            lines = []

        pattern = f'{skill_name}/**'
        if pattern not in lines:
            lines.append(pattern)
            with gitignore_path.open('w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

    def _try_create_symlink(self, source: Path, target: Path) -> bool:
        """尝试创建符号链接（不提权）"""
        try:
            target.symlink_to(source, target_is_directory=True)
            return True
        except (OSError, NotImplementedError):
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

        # 优先 symlink：第一轮尝试不提权
        failed_pairs: list[tuple[Path, Path]] = []
        for source, target in items:
            if self._try_create_symlink(source, target):
                self._add_to_gitignore(target)
                results.append(SkillInstallResult(target, source, 'symlink'))
            else:
                failed_pairs.append((source, target))

        # 第二轮：Windows 提权尝试
        if failed_pairs:
            elevated_success = self._elevation.try_elevated_symlinks(failed_pairs)
            for (source, target), success in zip(failed_pairs, elevated_success, strict=True):
                if success:
                    self._add_to_gitignore(target)
                    results.append(SkillInstallResult(target, source, 'symlink'))
                else:
                    # 最终回退到 copy
                    shutil.copytree(source, target)
                    self._add_to_gitignore(target)
                    results.append(SkillInstallResult(target, source, 'copy'))

        return results

    def install_hub_and_spokes_batch(
        self,
        items: list[tuple[Path, Path, list[Path]]],
        prefer_symlink: bool = True,
    ) -> dict[Path, SkillStrategy]:
        """批量 hub-spoke 安装（返回字典格式以兼容旧代码）

        Args:
            items: (source, hub, spokes) 三元组列表
            prefer_symlink: spokes 是否优先使用符号链接

        Returns:
            {target_path: strategy} 字典
        """
        result_dict: dict[Path, SkillStrategy] = {}

        # 第一步：安装所有 hubs（总是复制）
        for source, hub, _spokes in items:
            self._prepare_target(hub)
            shutil.copytree(source, hub)
            self._add_to_gitignore(hub)
            result_dict[hub] = 'copy'

        # 第二步：收集所有 spokes 对，批量创建 symlink（只提权一次）
        all_spoke_pairs: list[tuple[Path, Path]] = []
        for _source, hub, spokes in items:
            for spoke in spokes:
                all_spoke_pairs.append((hub, spoke))

        if all_spoke_pairs:
            spoke_results = self.install_batch(all_spoke_pairs, prefer_symlink)
            for result in spoke_results:
                result_dict[result.target] = result.strategy

        return result_dict

    def update_skill(self, source: Path, target: Path, strategy: SkillStrategy) -> None:
        """更新已安装的 skill

        Args:
            source: 模板 skill 目录
            target: 已安装的 skill 目录
            strategy: 记录的安装策略
        """
        if strategy == 'symlink':
            # 符号链接：确保链接有效且指向正确
            if target.is_symlink():
                try:
                    if target.exists() and target.resolve() == source.resolve():
                        return  # 已是正确的符号链接
                except OSError:
                    pass  # 损坏的链接，下面重建
                target.unlink(missing_ok=True)
            elif target.exists():
                shutil.rmtree(target)

            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=True)
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
        installs: list[tuple[Path, Path]], prefer_symlink: bool = True
    ) -> list[tuple[Path, Path, SkillStrategy]]:
        """兼容旧 API：批量安装

        Args:
            installs: (source, target) 路径对列表
            prefer_symlink: 优先使用符号链接

        Returns:
            (target, source, strategy) 三元组列表
        """
        installer = SkillInstaller._get_installer()
        results = installer.install_batch(installs, prefer_symlink)
        return [(r.target, r.source, r.strategy) for r in results]

    @staticmethod
    def install_hub_and_links_batch(
        installs: list[tuple[Path, Path, list[Path]]],
        prefer_symlink: bool = True,
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
