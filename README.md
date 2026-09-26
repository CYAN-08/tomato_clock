<div align="center"><a name="readme-top"></a>

# [Tomato Clock][github-project-link]

> Windows 11 Fluent 风格的番茄钟 | 基于 PySide6

**简体中文** · [English](./README_EN.md) · [反馈问题][github-issues-link]

<!-- SHIELD GROUP -->

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

   ```bash
   pip install -r requirements.txt
