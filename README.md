<div align="center"><a name="readme-top"></a>

# [Tomato Clock][github-project-link]

> Windows 11 Fluent 风格的番茄钟 | 基于 PySide6

**简体中文** · [English](./README_EN.md) · [反馈问题][github-issues-link]

[![GitHub stars][github-stars-shield]][github-stars-link]
[![GitHub forks][github-forks-shield]][github-forks-link]
[![GitHub issues][github-issues-shield]][github-issues-link]
[![license MIT][github-license-shield]][github-license-link]
[![Python][python-shield]][python-link]
[![PySide6][pyside6-shield]][pyside6-link]

</div>

> [!warning]
> 本项目仅用于个人学习与日常使用，不保证在所有环境下都能完美运行。

<details>
<summary><kbd>目录树</kbd></summary>

#### TOC
- [🌟 功能特性](#-功能特性)
- [🌐 兼容环境](#-兼容环境)
- [💻 安装指南](#-安装指南)
- [🔧 使用说明](#-使用说明)
- [🔄 更新日志](#-更新日志)
- [📌 待办事项](#-待办事项)
- [🤝 参与贡献](#-参与贡献)
- [🖼️ 效果预览](#-效果预览)
- [📈 项目统计](#-项目统计)
</details>

## 🌟 功能特性

- [x] 专注 / 短休息 / 长休息三种模式，每 4 个番茄进入长休息
- [x] 每个模式独立记忆剩余时间，切换不丢失
- [x] 一言语录，显示出处，点击卡片换一句
- [x] 系统托盘，关闭窗口后继续后台计时
- [x] 完成时系统通知
- [x] 自定义三个阶段的时长
- [x] 主题：浅色 / 深色 / 跟随系统
- [x] 自定义背景（本地图片 / 必应每日壁纸）
- [x] 窗口透明度、全屏
- [x] 配置自动保存到系统标准目录

## 🌐 兼容环境

系统              | 支持情况
:---------------: | :------:
Windows 10/11     | ✅ 完全支持
macOS             | ✅ 支持（托盘和通知正常）
Linux             | ✅ 支持（需桌面环境支持系统托盘）

## 💻 安装指南

1. 安装依赖：

   pip install -r requirements.txt

   或手动安装：

   pip install pyside6 requests qtawesome

2. 运行：

   python tomato_clock.py

### 打包成 exe（Windows）

pip install pyinstaller
pyinstaller --onefile --windowed --name "TomatoClock" tomato_clock.py

生成的文件在 dist/TomatoClock.exe。

## 🔧 使用说明

### 基本操作

- 开始 / 暂停：点击主按钮，或使用托盘菜单
- 重置：点击左侧重置按钮，恢复当前模式的完整时长
- 跳过：点击右侧跳过按钮，直接进入下一阶段
- 切换模式：点击顶部“专注 / 短休息 / 长休息”标签
- 自定义时长：点击“自定义”标签，拖动滑块后点保存
- 换一句语录：点击一言卡片

### 其他设置（菜单栏）

- 主题：跟随系统 / 浅色 / 深色
- 全屏显示：全屏模式
- 背景图片：选择本地图片 / 必应每日壁纸 / 随机壁纸 / 清除背景 / 背景透明度
- 窗口透明度：调整窗口整体透明度
- 打开配置目录：在文件管理器中打开配置目录
- 保存设置：手动保存当前设置

### 配置文件位置

- Windows：%APPDATA%\TomatoClock\config.json
- macOS：~/Library/Application Support/TomatoClock/config.json
- Linux：~/.config/TomatoClock/config.json

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 🔄 更新日志

### 最新版本

#### v1.0.0 (2026-09-26)

1. 首个版本发布
   - 专注 / 短休息 / 长休息三种模式
   - 一言语录（支持署名）
   - 系统托盘、完成通知
   - 自定义时长、主题、背景
   - 配置自动保存

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 📌 待办事项

1. 增加任务标签功能
2. 增加统计面板（今日 / 本周 / 本月）
3. 增加快捷键支持
4. 增加白噪音 / 背景音
5. 支持多语言

## 🤝 参与贡献

欢迎通过以下方式参与贡献：

1. 提交议题报告 Bug 或建议新功能
2. 改进代码逻辑
3. 完善文档

[![][pr-welcome-shield]][pr-welcome-link]

## 🖼️ 效果预览

> 截图待补充，可放在 screenshots/ 目录

## 📈 项目统计

<a href="https://star-history.com/#CYAN-08/tomato_clock&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=CYAN-08/tomato_clock&type=Timeline&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=CYAN-08/tomato_clock&type=Timeline" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=CYAN-08/tomato_clock&type=Timeline" width="75%" />
  </picture>
</a>

<div align="right">

[![][back-to-top]](#readme-top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
[github-project-link]: https://github.com/CYAN-08/tomato_clock "Tomato Clock"
[github-issues-link]: https://github.com/CYAN-08/tomato_clock/issues "议题"
[github-issues-shield]: https://img.shields.io/github/issues/CYAN-08/tomato_clock?style=flat-square&logo=github&label=Issue
[github-stars-link]: https://github.com/CYAN-08/tomato_clock/stargazers "星标"
[github-stars-shield]: https://img.shields.io/github/stars/CYAN-08/tomato_clock?style=flat-square&logo=github&label=Star
[github-forks-link]: https://github.com/CYAN-08/tomato_clock/network "复刻"
[github-forks-shield]: https://img.shields.io/github/forks/CYAN-08/tomato_clock?style=flat-square&logo=github&label=Fork
[github-license-link]: https://opensource.org/licenses/MIT "许可证"
[github-license-shield]: https://img.shields.io/github/license/CYAN-08/tomato_clock?style=flat-square&logo=github&label=License
[python-shield]: https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python
[python-link]: https://www.python.org/
[pyside6-shield]: https://img.shields.io/badge/PySide6-6.5+-green?style=flat-square&logo=qt
[pyside6-link]: https://pypi.org/project/PySide6/
[pr-welcome-link]: https://github.com/CYAN-08/tomato_clock/pulls
[pr-welcome-shield]: https://img.shields.io/badge/🤯_pr_welcome-%E2%86%92-ffcb47?labelColor=black&style=for-the-badge "欢迎提交 PR"
