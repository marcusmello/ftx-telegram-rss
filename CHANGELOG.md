# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Documentation
- Telegram bot configuration mini tutorial
- Some tests
- CLI by [click](https://click.palletsprojects.com/en/7.x/)

### Changed

- Log instead print

### Fixed

### Removed

### Deprecated

## [0.1.1-alpha.0] - 2020-10-09

Starting point, see [release note](https://github.com/marcusmello/ftx-telegram-rss/releases/tag/0.1.1-alpha.0)

### Added

- This CHANGELOG
- .gitignore
- LICENCE
- Input of environment variables by
  [environs](https://pypi.org/project/environs/)
- Main classes (Futures, TelegramReport and CheckAndReport)

### Changed

- README.md instead of .srt
- Author and some others details on pyproject

### Fixed

### Removed

- Some debug prints
- Methods '_future' and '_original_funding_rate_list', replaced by
  'funding_rate_top_bottom_rich_list'

### Deprecated
