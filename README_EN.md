<div align="center"><a name="readme-top"></a>

# [Tomato Clock][github-project-link]

> A Windows 11 Fluent-style Pomodoro timer built with PySide6

[简体中文](./README.md) · **English** · [Report Issue][github-issues-link]

[![GitHub stars][github-stars-shield]][github-stars-link]
[![GitHub forks][github-forks-shield]][github-forks-link]
[![GitHub issues][github-issues-shield]][github-issues-link]
[![license MIT][github-license-shield]][github-license-link]
[![Python][python-shield]][python-link]
[![PySide6][pyside6-shield]][pyside6-link]

</div>

> [!warning]
> This project is for personal learning and daily use. It may not work perfectly in all environments.

<details>
<summary><kbd>Table of Contents</kbd></summary>

#### TOC
- [🌟 Features](#-features)
- [🌐 Compatibility](#-compatibility)
- [💻 Installation](#-installation)
- [🔧 Usage](#-usage)
- [🔄 Changelog](#-changelog)
- [📌 TODO](#-todo)
- [🤝 Contributing](#-contributing)
- [🖼️ Preview](#-preview)
- [📈 Stats](#-stats)
</details>

## 🌟 Features

- [x] Focus / Short Break / Long Break modes, long break every 4 pomodoros
- [x] Each mode remembers its own remaining time across switches
- [x] Hitokoto quotes with attribution, click card to refresh
- [x] System tray, keeps running in background after closing window
- [x] System notification on completion
- [x] Customizable durations for all three phases
- [x] Theme: System / Light / Dark
- [x] Custom background (local image / Bing daily wallpaper)
- [x] Window opacity and fullscreen
- [x] Auto-save config to system standard directory

## 🌐 Compatibility

OS                | Status
:---------------: | :------:
Windows 10/11     | ✅ Fully supported
macOS             | ✅ Supported (tray & notification work)
Linux             | ✅ Supported (requires desktop environment with tray support)

## 💻 Installation

1. Install dependencies:

   pip install -r requirements.txt

   Or manually:

   pip install pyside6 requests qtawesome

2. Run:

   python tomato_clock.py

### Build exe (Windows)

pip install pyinstaller
pyinstaller --onefile --windowed --name "TomatoClock" tomato_clock.py

The output is dist/TomatoClock.exe.

## 🔧 Usage

### Basic Operations

- Start / Pause: click the main button, or use tray menu
- Reset: click the reset button on the left, restore full duration of current mode
- Skip: click the skip button on the right, jump to next phase
- Switch mode: click the "Focus / Short Break / Long Break" tabs at the top
- Custom duration: click "Custom" tab, drag sliders and save
- Refresh quote: click the quote card

### Other Settings (Menu Bar)

- Theme: System / Light / Dark
- Fullscreen: fullscreen mode
- Background Image: choose local image / Bing daily wallpaper / random wallpaper / clear / background opacity
- Window Opacity: adjust overall window opacity
- Open Config Directory: open config directory in file manager
- Save Settings: manually save current settings

### Config File Locations

- Windows: %APPDATA%\TomatoClock\config.json
- macOS: ~/Library/Application Support/TomatoClock/config.json
- Linux: ~/.config/TomatoClock/config.json

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 🔄 Changelog

### Latest

#### v1.0.0 (2026-09-26)

1. Initial release
   - Focus / Short Break / Long Break modes
   - Hitokoto quotes with attribution
   - System tray, completion notification
   - Custom durations, themes, backgrounds
   - Auto-save config

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 📌 TODO

1. Task tag feature
2. Statistics panel (today / week / month)
3. Keyboard shortcuts
4. White noise / background sound
5. Multi-language support

## 🤝 Contributing

Contributions are welcome:

1. Open an issue to report bugs or suggest features
2. Improve code logic
3. Improve documentation

[![][pr-welcome-shield]][pr-welcome-link]

## 🖼️ Preview

> Screenshots coming soon. Place them in screenshots/.

## 📈 Stats

<a href="https://star-history.com/#your-username/your-repo&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=your-username/your-repo&type=Timeline&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=your-username/your-repo&type=Timeline" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=your-username/your-repo&type=Timeline" width="75%" />
  </picture>
</a>

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
[github-project-link]: https://github.com/your-username/your-repo "Tomato Clock"
[github-issues-link]: https://github.com/your-username/your-repo/issues "Issues"
[github-issues-shield]: https://img.shields.io/github/issues/your-username/your-repo?style=flat-square&logo=github&label=Issue
[github-stars-link]: https://github.com/your-username/your-repo/stargazers "Stars"
[github-stars-shield]: https://img.shields.io/github/stars/your-username/your-repo?style=flat-square&logo=github&label=Star
[github-forks-link]: https://github.com/your-username/your-repo/network "Forks"
[github-forks-shield]: https://img.shields.io/github/forks/your-username/your-repo?style=flat-square&logo=github&label=Fork
[github-license-link]: https://opensource.org/licenses/MIT "License"
[github-license-shield]: https://img.shields.io/github/license/your-username/your-repo?style=flat-square&logo=github&label=License
[python-shield]: https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python
[python-link]: https://www.python.org/
[pyside6-shield]: https://img.shields.io/badge/PySide6-6.5+-green?style=flat-square&logo=qt
[pyside6-link]: https://pypi.org/project/PySide6/
[pr-welcome-link]: https://github.com/your-username/your-repo/pulls
[pr-welcome-shield]: https://img.shields.io/badge/🤯_pr_welcome-%E2%86%92-ffcb47?labelColor=black&style=for-the-badge "PR Welcome"