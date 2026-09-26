import sys
import os
import json
import time
import threading
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QDialog, QFileDialog,
    QFrame, QStackedWidget, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QUrl
from PySide6.QtGui import (
    QFont, QFontDatabase, QAction, QActionGroup, QPixmap, QPainter, QIcon
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import qtawesome as qta

# ==================== 配置 ====================
DEFAULT_DURATIONS = {"focus": 25, "short": 5, "long": 15}
LABELS = {"focus": "专注", "short": "短休息", "long": "长休息"}

THEME = {
    "focus": {"accent": "#0078D4", "light": "#E5F1FB"},
    "short": {"accent": "#107C10", "light": "#E6F4E6"},
    "long":  {"accent": "#C239B3", "light": "#F9E6F6"},
}

QUOTE_APIS = [
    "https://uapis.cn/api/v1/saying/random",
    "https://v1.hitokoto.cn/?encode=json",
    "https://uapis.cn/api/v1/saying",
]

BING_DAILY_API = "https://uapis.cn/api/v1/image/bing-daily"

LIGHT_STYLE = {
    "bg": "#F3F3F3", "text": "#1A1A1A", "text_sec": "#5D5D5D", "text_ter": "#8A8A8A",
    "card_bg": "#FFFFFF", "card_border": "#E5E5E5",
    "btn_bg": "#FDFDFD", "btn_hover": "#F0F0F0", "btn_pressed": "#E0E0E0"
}
DARK_STYLE = {
    "bg": "#1F1F1F", "text": "#FFFFFF", "text_sec": "#B0B0B0", "text_ter": "#8A8A8A",
    "card_bg": "#2D2D2D", "card_border": "#3F3F3F",
    "btn_bg": "#333333", "btn_hover": "#3F3F3F", "btn_pressed": "#4A4A4A"
}


# ==================== 跨平台配置目录 ====================
def get_config_dir():
    """按平台返回标准配置目录"""
    app_name = "TomatoClock"

    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / app_name

    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name

    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        return Path(base) / app_name


CONFIG_DIR = get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"


# ==================== 配置管理 ====================
class Config:
    """负责读写用户设置，只在启动和关闭时碰文件"""

    @staticmethod
    def load():
        # 确保配置目录存在
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[配置] 目录: {CONFIG_DIR}")

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[配置] 读取失败: {e}")
        else:
            print(f"[配置] 未找到配置文件，将使用默认值")
        return {}

    @staticmethod
    def save(data):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[配置] 已保存到 {CONFIG_FILE}")
        except Exception as e:
            print(f"[配置] 保存失败: {e}")


class PomodoroWindow(QMainWindow):
    quote_ready = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tomato clock")
        self.setFixedSize(480, 780)

        self._setup_fonts()

        # ---- 从配置加载 ----
        cfg = Config.load()

        self.durations = cfg.get("durations", dict(DEFAULT_DURATIONS))
        self.theme_mode = cfg.get("theme_mode", "system")
        self.completed = cfg.get("completed", 0)
        self.bg_path = cfg.get("bg_path", "")
        self.bg_opacity = cfg.get("bg_opacity", 1.0)

        self.mode = "focus"
        self.view = "timer"
        self.running = False
        self.accent = THEME["focus"]["accent"]
        self.end_time = 0.0

        self.mode_states = {
            "focus": {"total": self.durations["focus"] * 60,
                      "remaining": self.durations["focus"] * 60},
            "short": {"total": self.durations["short"] * 60,
                      "remaining": self.durations["short"] * 60},
            "long":  {"total": self.durations["long"] * 60,
                      "remaining": self.durations["long"] * 60},
        }

        self.total = self.mode_states[self.mode]["total"]
        self.remaining = self.mode_states[self.mode]["remaining"]

        self.is_dark = self._detect_system_dark()

        # ---- 背景 ----
        self.bg_pixmap = None
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_bg_downloaded)

        self.quote_cache = []

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        # ---- 系统托盘 ----
        self._create_tray()

        self._create_menubar()
        self._build_ui()

        # 加载本地背景
        if self.bg_path and os.path.exists(self.bg_path):
            pix = QPixmap(self.bg_path)
            if not pix.isNull():
                self.bg_pixmap = pix

        self._apply_style()
        self._render()

        self.quote_ready.connect(self._update_quote)
        threading.Thread(target=self._fetch_quote, daemon=True).start()

    # ==================== 字体 ====================
    def _setup_fonts(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for fname in ["msyh.ttc", "msyhbd.ttc", "SourceHanSansSC-Regular.otf"]:
            fpath = os.path.join(base_dir, fname)
            if os.path.exists(fpath):
                QFontDatabase.addApplicationFont(fpath)

        families = QFontDatabase.families()
        for f in ["Microsoft YaHei UI", "Microsoft YaHei", "微软雅黑",
                  "Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC",
                  "SimHei", "SimSun"]:
            if f in families:
                self.base_font_family = f
                break
        else:
            self.base_font_family = "Microsoft YaHei UI"
        print(f"[字体] 使用: {self.base_font_family}")

    # ==================== 系统托盘 ====================
    def _create_tray(self):
        self.tray = QSystemTrayIcon(self)

        pix = qta.icon('fa6s.stopwatch', color="#C0392B").pixmap(QSize(64, 64))
        self.tray.setIcon(QIcon(pix))
        self.tray.setToolTip("Tomato clock")

        tray_menu = QMenu()

        self.tray_show_action = QAction("显示主窗口", self)
        self.tray_show_action.triggered.connect(self._restore_window)
        tray_menu.addAction(self.tray_show_action)

        self.tray_start_action = QAction("开始 / 暂停", self)
        self.tray_start_action.triggered.connect(self.toggle_timer)
        tray_menu.addAction(self.tray_start_action)

        tray_menu.addSeparator()

        tray_quit_action = QAction("退出", self)
        tray_quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(tray_quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._restore_window()

    def _restore_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_app(self):
        self._save_config()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """点 X 时最小化到托盘"""
        if self.tray.isVisible():
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "Tomato clock",
                "已最小化到托盘，双击图标可恢复",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self._save_config()
            event.accept()

    # ==================== 配置保存 ====================
    def _save_config(self):
        Config.save({
            "durations": self.durations,
            "theme_mode": self.theme_mode,
            "completed": self.completed,
            "bg_path": self.bg_path,
            "bg_opacity": self.bg_opacity,
        })

    # ==================== 完成通知 ====================
    def _notify(self, title, message):
        if self.tray.isVisible():
            self.tray.showMessage(
                title, message,
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )

    # ==================== 菜单栏 ====================
    def _create_menubar(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("其他设置")

        theme_menu = settings_menu.addMenu("主题")
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        for name, value in [("跟随系统", "system"), ("浅色", "light"), ("深色", "dark")]:
            action = QAction(name, self, checkable=True)
            action.setData(value)
            if value == self.theme_mode:
                action.setChecked(True)
            action.triggered.connect(lambda checked, v=value: self._set_theme(v))
            theme_menu.addAction(action)
            self.theme_group.addAction(action)

        settings_menu.addSeparator()

        self.fullscreen_action = QAction("全屏显示", self, checkable=True)
        self.fullscreen_action.triggered.connect(self._toggle_fullscreen)
        settings_menu.addAction(self.fullscreen_action)

        settings_menu.addSeparator()

        bg_menu = settings_menu.addMenu("背景图片")
        bg_menu.addAction("选择本地图片...", self._choose_local_bg)
        bg_menu.addAction("使用必应每日壁纸", self._use_bing_daily)
        bg_menu.addAction("随机必应壁纸", self._use_bing_random)
        bg_menu.addSeparator()
        self.clear_bg_action = QAction("清除背景", self)
        self.clear_bg_action.triggered.connect(self._clear_bg)
        bg_menu.addAction(self.clear_bg_action)
        bg_menu.addSeparator()
        bg_menu.addAction("背景透明度...", self._open_bg_opacity_dialog)

        settings_menu.addSeparator()
        settings_menu.addAction("窗口透明度...", self._open_opacity_dialog)

        settings_menu.addSeparator()
        settings_menu.addAction("打开配置目录", self._open_config_dir)
        settings_menu.addAction("保存设置", self._save_config)

    def _open_config_dir(self):
        """在文件管理器中打开配置目录"""
        try:
            # 先确保目录存在
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            if sys.platform == "win32":
                os.startfile(CONFIG_DIR)
            elif sys.platform == "darwin":
                os.system(f'open "{CONFIG_DIR}"')
            else:
                os.system(f'xdg-open "{CONFIG_DIR}"')
        except Exception as e:
            print(f"[配置] 打开目录失败: {e}")

    # ==================== UI 构建 ====================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(32, 16, 32, 28)
        root.setSpacing(0)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        self.title_icon = QLabel()
        self.title_icon.setFixedSize(28, 28)
        title_row.addWidget(self.title_icon)

        self.title_label = QLabel("Tomato clock")
        title_row.addWidget(self.title_label)
        title_row.addStretch()

        self.gear_btn = QPushButton()
        self.gear_btn.setFixedSize(32, 32)
        self.gear_btn.setCursor(Qt.PointingHandCursor)
        self.gear_btn.clicked.connect(lambda: self._on_tab_click("settings"))
        title_row.addWidget(self.gear_btn)

        root.addLayout(title_row)
        root.addSpacing(16)

        seg = QHBoxLayout()
        seg.setSpacing(0)
        self.seg_buttons = {}
        tabs = [("focus", "专注"), ("short", "短休息"),
                ("long", "长休息"), ("settings", "自定义")]
        for key, text in tabs:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._on_tab_click(k))
            seg.addWidget(btn)
            self.seg_buttons[key] = btn
        root.addLayout(seg)
        root.addSpacing(20)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        # ========== 计时页 ==========
        timer_page = QWidget()
        tp_layout = QVBoxLayout(timer_page)
        tp_layout.setContentsMargins(0, 0, 0, 0)
        tp_layout.setSpacing(0)

        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        tp_layout.addWidget(self.time_label)

        self.phase_label = QLabel("专注")
        self.phase_label.setAlignment(Qt.AlignCenter)
        tp_layout.addWidget(self.phase_label)
        tp_layout.addSpacing(4)

        self.count_label = QLabel("已完成 0 个番茄")
        self.count_label.setAlignment(Qt.AlignCenter)
        tp_layout.addWidget(self.count_label)
        tp_layout.addSpacing(20)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(12)
        ctrl.addStretch()

        self.reset_btn = QPushButton()
        self.reset_btn.setFixedSize(46, 46)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_timer)
        ctrl.addWidget(self.reset_btn)

        self.start_btn = QPushButton("开始")
        self.start_btn.setFixedSize(150, 48)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.toggle_timer)
        ctrl.addWidget(self.start_btn)

        self.skip_btn = QPushButton()
        self.skip_btn.setFixedSize(46, 46)
        self.skip_btn.setCursor(Qt.PointingHandCursor)
        self.skip_btn.clicked.connect(self._skip)
        ctrl.addWidget(self.skip_btn)
        ctrl.addStretch()
        tp_layout.addLayout(ctrl)
        tp_layout.addSpacing(20)

        self.quote_card = QFrame()
        self.quote_card.setCursor(Qt.PointingHandCursor)
        self.quote_card.mousePressEvent = lambda e: self._on_quote_click()
        card_layout = QVBoxLayout(self.quote_card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(8)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(6)
        hint_row.addStretch()

        self.quote_icon = QLabel()
        self.quote_icon.setFixedSize(14, 14)
        hint_row.addWidget(self.quote_icon)

        self.quote_hint = QLabel("点击卡片换一句")
        self.quote_hint.setAlignment(Qt.AlignCenter)
        hint_row.addWidget(self.quote_hint)
        hint_row.addStretch()
        card_layout.addLayout(hint_row)

        self.quote_label = QLabel("正在获取语录…")
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.quote_label)

        self.quote_from = QLabel("")
        self.quote_from.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.quote_from)

        tp_layout.addWidget(self.quote_card)
        tp_layout.addStretch()

        self.stack.addWidget(timer_page)

        # ========== 设置页 ==========
        settings_page = QWidget()
        sp_layout = QVBoxLayout(settings_page)
        sp_layout.setContentsMargins(0, 8, 0, 0)
        sp_layout.setSpacing(18)

        self.sliders = {}
        self.value_labels = {}

        def make_slider_row(key, label_text, min_v, max_v):
            row = QFrame()
            row.setObjectName("settingRow")
            rl = QVBoxLayout(row)
            rl.setContentsMargins(18, 14, 18, 14)
            rl.setSpacing(8)

            top = QHBoxLayout()
            name = QLabel(label_text)
            name.setObjectName("settingName")
            top.addWidget(name)
            top.addStretch()
            val = QLabel(f"{self.durations[key]} 分钟")
            val.setObjectName("settingValue")
            top.addWidget(val)
            rl.addLayout(top)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(self.durations[key])
            slider.valueChanged.connect(
                lambda v, k=key: self._on_slider_change(k, v))
            rl.addWidget(slider)

            self.sliders[key] = slider
            self.value_labels[key] = val
            return row

        sp_layout.addWidget(make_slider_row("focus", "专注时长", 1, 120))
        sp_layout.addWidget(make_slider_row("short", "短休息时长", 1, 60))
        sp_layout.addWidget(make_slider_row("long", "长休息时长", 1, 60))

        sp_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.reset_defaults_btn = QPushButton("恢复默认")
        self.reset_defaults_btn.setFixedHeight(40)
        self.reset_defaults_btn.setCursor(Qt.PointingHandCursor)
        self.reset_defaults_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(self.reset_defaults_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setMinimumWidth(110)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_settings)
        btn_row.addWidget(self.save_btn)

        sp_layout.addLayout(btn_row)
        sp_layout.addStretch()

        self.stack.addWidget(settings_page)
        self.stack.setCurrentIndex(0)

    # ==================== 背景 ====================
    def _choose_local_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self.bg_pixmap = pix
                self.bg_path = path
                self.bg_opacity = 1.0
                self._apply_style()
                self.update()

    def _use_bing_daily(self):
        self._download_bg(BING_DAILY_API)

    def _use_bing_random(self):
        self._download_bg(BING_DAILY_API + "?random=true")

    def _download_bg(self, url):
        print(f"[背景] 下载中: {url}")
        request = QNetworkRequest(QUrl(url))
        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy
        )
        self.network_manager.get(request)

    def _on_bg_downloaded(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pix = QPixmap()
            if pix.loadFromData(data):
                self.bg_pixmap = pix
                self.bg_path = ""
                self.bg_opacity = 1.0
                self._apply_style()
                self.update()
                print(f"[背景] 下载成功 ({pix.width()}x{pix.height()})")
            else:
                print("[背景] 图片解析失败")
        else:
            print(f"[背景] 下载失败: {reply.errorString()}")
        reply.deleteLater()

    def _clear_bg(self):
        self.bg_pixmap = None
        self.bg_path = ""
        self._apply_style()
        self.update()

    def _open_bg_opacity_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("背景透明度")
        dlg.setFixedSize(320, 160)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("调整背景图片透明度 (10% - 100%)"))

        slider = QSlider(Qt.Horizontal)
        slider.setRange(10, 100)
        slider.setValue(int(self.bg_opacity * 100))
        layout.addWidget(slider)

        def on_change(v):
            self.bg_opacity = v / 100.0
            self.update()

        slider.valueChanged.connect(on_change)

        btn = QPushButton("确定")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter = QPainter(self)
            painter.setOpacity(self.bg_opacity)
            scaled = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)
            painter.end()

    # ==================== 标签点击 ====================
    def _on_tab_click(self, key):
        if key == "settings":
            self.view = "settings"
            self.stack.setCurrentIndex(1)
            self._apply_style()
            self._render()
        else:
            self.view = "timer"
            self.stack.setCurrentIndex(0)
            if key != self.mode:
                self.switch_mode(key)
            else:
                self._apply_style()
                self._render()

    # ==================== 样式 ====================
    def _apply_style(self):
        if self.theme_mode == "system":
            self.is_dark = self._detect_system_dark()
        else:
            self.is_dark = (self.theme_mode == "dark")

        colors = DARK_STYLE if self.is_dark else LIGHT_STYLE
        self.colors = colors
        accent = THEME[self.mode]["accent"]
        self.accent = accent

        card_bg = colors['card_bg']
        if self.bg_pixmap:
            card_bg = "rgba(255,255,255,0.85)" if not self.is_dark else "rgba(45,45,45,0.85)"

        self.setStyleSheet(f"""
            QMainWindow {{ background: {colors['bg']}; }}
            QWidget {{ color: {colors['text']}; }}
            QLabel {{ background: transparent; }}
            QMenuBar {{ background: {colors['bg']}; color: {colors['text']}; }}
            QMenuBar::item:selected {{ background: {colors['btn_hover']}; }}
            QMenu {{ background: {colors['card_bg']}; color: {colors['text']}; border: 1px solid {colors['card_border']}; }}
            QMenu::item:selected {{ background: {colors['btn_hover']}; }}
            QSlider::groove:horizontal {{
                height: 4px; background: {colors['card_border']};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {accent}; width: 16px; height: 16px;
                margin: -6px 0; border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent}; border-radius: 2px;
            }}
        """)

        base_font = QFont(self.base_font_family)

        f_title = QFont(base_font); f_title.setPointSize(20); f_title.setBold(True)
        self.title_label.setFont(f_title)
        f_time = QFont(base_font); f_time.setPointSize(56); f_time.setBold(True)
        self.time_label.setFont(f_time)
        f_phase = QFont(base_font); f_phase.setPointSize(12)
        self.phase_label.setFont(f_phase)
        f_count = QFont(base_font); f_count.setPointSize(10)
        self.count_label.setFont(f_count)
        f_hint = QFont(base_font); f_hint.setPointSize(8)
        self.quote_hint.setFont(f_hint)
        f_quote = QFont(base_font); f_quote.setPointSize(11)
        self.quote_label.setFont(f_quote)
        f_from = QFont(base_font); f_from.setPointSize(9)
        self.quote_from.setFont(f_from)

        self.title_icon.setPixmap(
            qta.icon('fa6s.stopwatch', color=accent).pixmap(QSize(26, 26))
        )

        self.gear_btn.setIcon(qta.icon('fa6s.gear', color=colors['text_sec']))
        self.gear_btn.setIconSize(QSize(16, 16))
        self.gear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; border-radius: 16px;
            }}
            QPushButton:hover {{ background: {colors['btn_hover']}; }}
            QPushButton:pressed {{ background: {colors['btn_pressed']}; }}
        """)

        active_key = "settings" if self.view == "settings" else self.mode
        f_seg = QFont(base_font); f_seg.setPointSize(11)
        for key, btn in self.seg_buttons.items():
            btn.setFont(f_seg)
            if key == active_key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {colors['card_bg']}; color: {accent};
                        border: none; border-bottom: 3px solid {accent};
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {colors['btn_hover']}; color: {colors['text_sec']};
                        border: none; border-bottom: 3px solid {colors['card_border']};
                    }}
                    QPushButton:hover {{ background: {colors['btn_pressed']}; }}
                """)

        f_start = QFont(base_font); f_start.setPointSize(14); f_start.setBold(True)
        self.start_btn.setFont(f_start)

        self.reset_btn.setIcon(qta.icon('fa6s.rotate-left', color=colors['text']))
        self.reset_btn.setIconSize(QSize(20, 20))
        self.skip_btn.setIcon(qta.icon('fa6s.forward', color=colors['text']))
        self.skip_btn.setIconSize(QSize(20, 20))

        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white;
                border: none; border-radius: 24px; font-weight: bold;
                padding-left: 8px;
            }}
            QPushButton:hover {{ background: {self._darken(accent, 0.9)}; }}
            QPushButton:pressed {{ background: {self._darken(accent, 0.8)}; }}
        """)
        for btn in (self.reset_btn, self.skip_btn):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {colors['btn_bg']}; color: {colors['text']};
                    border: 1px solid {colors['card_border']}; border-radius: 23px;
                }}
                QPushButton:hover {{ background: {colors['btn_hover']}; }}
                QPushButton:pressed {{ background: {colors['btn_pressed']}; }}
            """)

        self.quote_icon.setPixmap(
            qta.icon('fa6s.quote-left', color=colors['text_ter']).pixmap(QSize(12, 12))
        )
        self.quote_card.setStyleSheet(f"""
            QFrame {{
                background: {card_bg};
                border: 1px solid {colors['card_border']};
                border-radius: 10px;
            }}
            QLabel {{ background: transparent; border: none; color: {colors['text']}; }}
        """)
        self.quote_hint.setStyleSheet(f"color: {colors['text_ter']}; background: transparent; border: none;")
        self.quote_from.setStyleSheet(f"color: {colors['text_sec']}; background: transparent; border: none;")

        for row in self.stack.widget(1).findChildren(QFrame):
            if row.objectName() == "settingRow":
                row.setStyleSheet(f"""
                    QFrame#settingRow {{
                        background: {card_bg};
                        border: 1px solid {colors['card_border']};
                        border-radius: 10px;
                    }}
                """)
        for lbl in self.stack.widget(1).findChildren(QLabel):
            if lbl.objectName() == "settingName":
                f = QFont(base_font); f.setPointSize(11)
                lbl.setFont(f)
                lbl.setStyleSheet(f"color: {colors['text']}; background: transparent;")
            elif lbl.objectName() == "settingValue":
                f = QFont(base_font); f.setPointSize(11); f.setBold(True)
                lbl.setFont(f)
                lbl.setStyleSheet(f"color: {accent}; background: transparent;")

        self.reset_defaults_btn.setStyleSheet(f"""
            QPushButton {{
                background: {colors['btn_bg']}; color: {colors['text']};
                border: 1px solid {colors['card_border']}; border-radius: 6px;
                padding: 6px 18px;
            }}
            QPushButton:hover {{ background: {colors['btn_hover']}; }}
            QPushButton:pressed {{ background: {colors['btn_pressed']}; }}
        """)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white;
                border: none; border-radius: 6px;
                padding: 6px 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {self._darken(accent, 0.9)}; }}
            QPushButton:pressed {{ background: {self._darken(accent, 0.8)}; }}
        """)

    # ==================== 工具 ====================
    @staticmethod
    def _darken(hex_color, factor=0.9):
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"

    def _detect_system_dark(self):
        try:
            if os.name == 'nt':
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0
        except Exception:
            pass
        return False

    # ==================== 设置页逻辑 ====================
    def _on_slider_change(self, key, value):
        self.value_labels[key].setText(f"{value} 分钟")

    def _reset_defaults(self):
        for key, v in DEFAULT_DURATIONS.items():
            self.sliders[key].setValue(v)

    def _save_settings(self):
        for key in self.durations:
            self.durations[key] = self.sliders[key].value()

        for key in ("focus", "short", "long"):
            new_total = self.durations[key] * 60
            self.mode_states[key]["total"] = new_total
            if key == self.mode and self.running:
                ratio = self.remaining / self.total if self.total else 0
                self.remaining = int(new_total * ratio)
                self.mode_states[key]["remaining"] = self.remaining
                self.total = new_total
                self.end_time = time.time() + self.remaining
            else:
                self.mode_states[key]["remaining"] = new_total

        if self.mode in self.mode_states:
            self.total = self.mode_states[self.mode]["total"]
            if not self.running:
                self.remaining = self.mode_states[self.mode]["remaining"]

        self.view = "timer"
        self.stack.setCurrentIndex(0)
        self._apply_style()
        self._render()
        self._save_config()

    # ==================== 渲染 ====================
    def _render(self):
        m, s = divmod(max(0, self.remaining), 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")
        self.phase_label.setText(LABELS[self.mode])
        self.count_label.setText(f"已完成 {self.completed} 个番茄")

        if self.running:
            self.start_btn.setText("暂停")
            self.start_btn.setIcon(qta.icon('fa6s.pause', color='white'))
        else:
            self.start_btn.setText("开始")
            self.start_btn.setIcon(qta.icon('fa6s.play', color='white'))
        self.start_btn.setIconSize(QSize(14, 14))

        if self.tray.isVisible():
            self.tray.setToolTip(f"Tomato clock - {LABELS[self.mode]} {m:02d}:{s:02d}")

    # ==================== 计时 ====================
    def toggle_timer(self):
        self.stop_timer() if self.running else self.start_timer()

    def start_timer(self):
        if self.running:
            return
        self.running = True
        self.end_time = time.time() + self.remaining
        self.timer.start(200)
        self._render()

    def stop_timer(self):
        if self.running:
            self.remaining = max(0, int(self.end_time - time.time()))
            self.mode_states[self.mode]["remaining"] = self.remaining
        self.running = False
        self.timer.stop()
        self._render()

    def _tick(self):
        if not self.running:
            return
        self.remaining = max(0, int(self.end_time - time.time()))
        self.mode_states[self.mode]["remaining"] = self.remaining
        self._render()
        if self.remaining <= 0:
            self._on_complete()

    def reset_timer(self):
        self.stop_timer()
        self.remaining = self.total
        self.mode_states[self.mode]["remaining"] = self.remaining
        self._render()

    def _skip(self):
        self._on_complete()

    def _on_complete(self):
        self.stop_timer()
        QApplication.beep()

        finished_mode = self.mode

        if self.mode == "focus":
            self.completed += 1
            next_mode = "long" if self.completed % 4 == 0 else "short"
            self.mode_states[self.mode]["remaining"] = self.mode_states[self.mode]["total"]
            self.switch_mode(next_mode)
            self._notify(
                "专注完成",
                f"已完成 {self.completed} 个番茄，进入{LABELS[next_mode]}"
            )
        else:
            self.mode_states[self.mode]["remaining"] = self.mode_states[self.mode]["total"]
            self.switch_mode("focus")
            self._notify(
                f"{LABELS[finished_mode]}结束",
                "休息结束，准备开始下一个专注"
            )

        self._save_config()

    # ==================== 模式切换（不自动开始） ====================
    def switch_mode(self, new_mode):
        self.mode_states[self.mode]["remaining"] = self.remaining
        self.mode_states[self.mode]["total"] = self.total

        self.stop_timer()

        self.mode = new_mode
        state = self.mode_states[new_mode]
        self.total = state["total"]
        self.remaining = state["remaining"]

        self._apply_style()
        self._render()

    # ==================== 主题/全屏/透明度 ====================
    def _set_theme(self, mode):
        self.theme_mode = mode
        self._apply_style()
        self._save_config()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self.fullscreen_action.setChecked(True)

    def _open_opacity_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("窗口透明度")
        dlg.setFixedSize(320, 160)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("调整窗口透明度 (10% - 100%)"))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(10, 100)
        slider.setValue(int(self.windowOpacity() * 100))
        layout.addWidget(slider)
        slider.valueChanged.connect(lambda v: self.setWindowOpacity(v / 100.0))
        btn = QPushButton("确定")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    # ==================== 一言 ====================
    def _on_quote_click(self):
        threading.Thread(target=self._fetch_quote, daemon=True).start()

    def _fetch_quote(self):
        for _ in range(3):
            for url in QUOTE_APIS:
                try:
                    res = requests.get(url, timeout=6)
                    res.raise_for_status()
                    data = res.json()
                except Exception:
                    continue

                text, source = self._parse_quote(data)

                if text and text not in self.quote_cache:
                    self.quote_cache.append(text)
                    if len(self.quote_cache) > 20:
                        self.quote_cache.pop(0)
                    self.quote_ready.emit(text, source)
                    return

        self.quote_ready.emit("语录获取失败，点击重试", "")

    @staticmethod
    def _parse_quote(data):
        text = (data.get("content") or data.get("text")
                or data.get("hitokoto") or data.get("saying") or "")

        origin = (data.get("source") or data.get("from")
                  or data.get("origin") or "")
        author = (data.get("author") or data.get("from_who")
                  or data.get("creator") or "")

        if origin and author:
            source = f"{origin} · {author}"
        elif origin:
            source = origin
        elif author:
            source = author
        else:
            source = ""

        return text, source

    def _update_quote(self, text, source):
        self.quote_label.setText(text)
        if source:
            self.quote_from.setText(f"— {source}")
        else:
            self.quote_from.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamilies([
        "Microsoft YaHei UI", "Microsoft YaHei", "Source Han Sans SC",
        "Noto Sans CJK SC", "PingFang SC", "SimHei", "SimSun",
    ])
    app.setFont(font)

    app.setQuitOnLastWindowClosed(False)

    window = PomodoroWindow()
    window.show()
    sys.exit(app.exec())