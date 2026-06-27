# Changelog

All notable changes to sspec will be documented in this file.

This project follows the structure of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Historical versions before `2.8.0` are not backfilled.

## [Unreleased]

## [2.8.0] - 2026-06-27

### Added
- Added managed `.sspec/SSPEC.rule.md` as the full sspec workflow rule for initialized projects.
- Added update tracking for `.sspec/SSPEC.rule.md`, including hash metadata and modified-file protection.
- Added 6.2-to-7.0 project update coverage for router/rule migration.

### Changed
- Changed root `AGENTS.md` from the full sspec protocol into a lightweight router.
- Bumped sspec protocol schema from `6.2` to `7.0`.
- Kept `.sspec/project.md` as the default project context entry before task-specific spec-docs or workflow rules.
- Updated `sspec portable read rule:sspec` to keep returning the full protocol from `SSPEC.rule.md`.

### Fixed
- Updated stale documentation and examples that treated root `AGENTS.md` as the full protocol source.
