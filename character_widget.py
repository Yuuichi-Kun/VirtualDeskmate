import os
import logging
import weakref
from PyQt5.QtWidgets import QWidget, QLabel, QSystemTrayIcon, QMenu, QAction, QStyle, QShortcut
from PyQt5.QtGui import QMovie, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QTimer
try:
    from .settings_helper import SettingsHelper  # type: ignore
    from .utils import resource_path  # type: ignore
    from .startup_windows import WindowsStartupManager  # type: ignore
except Exception:
    from settings_helper import SettingsHelper  # type: ignore
    from utils import resource_path  # type: ignore
    from startup_windows import WindowsStartupManager  # type: ignore
from PyQt5.QtWidgets import QApplication


class CharacterWidget(QWidget):
    tray_icon = None
    tray_menu = None
    action_show = None
    action_hide = None
    action_show_launcher = None
    action_quit = None
    current_ref = None
    launcher_ref = None

    def __init__(self, gif_path: str = None, launcher: QWidget = None):
        super().__init__()
        self.launcher = launcher
        self.settings_helper = SettingsHelper()
        CharacterWidget.current_ref = weakref.ref(self)
        if launcher is not None:
            CharacterWidget.launcher_ref = weakref.ref(launcher)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.character_label = QLabel(self)
        if not gif_path:
            candidate = resource_path('Dance-Evernight-unscreen.gif')
            gif_path = candidate if os.path.exists(candidate) else ''
        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.character_label.setMovie(self.movie)
        self.character_label.setStyleSheet("background: transparent;")
        self.character_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.movie.start()

        self.character_label.setScaledContents(True)
        saved_size = self.settings_helper.get_size()
        new_width = saved_size
        new_height = saved_size
        self.character_label.setFixedSize(new_width, new_height)
        self.setFixedSize(new_width, new_height)

        self.old_pos = self.pos()
        self.drag_locked = self.settings_helper.get_lock_position()
        # Always allow interaction; click-through removed
        self.setWindowOpacity(self.settings_helper.get_opacity())

        self.idle_enabled = bool(self.settings_helper.settings.value('behavior/idleEnabled', False, type=bool))
        self.bob_timer = QTimer(self)
        self.bob_timer.setInterval(50)
        self._bob_phase = 0
        if self.idle_enabled:
            self.bob_timer.timeout.connect(self._on_bob)
            self.bob_timer.start()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        self.shortcut_toggle_visibility = QShortcut(QKeySequence('Ctrl+Shift+H'), self)
        self.shortcut_toggle_visibility.activated.connect(self._toggle_visibility)
        # Click-through shortcut removed
        self.shortcut_cycle_size = QShortcut(QKeySequence('Ctrl+Shift+S'), self)
        self.shortcut_cycle_size.activated.connect(self._cycle_size)

        # Ensure the system tray is initialized immediately so controls are available
        self._ensure_tray_initialized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.drag_locked:
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_locked:
            delta = QPoint(event.globalPos() - self.old_pos)
            new_x = self.x() + delta.x()
            new_y = self.y() + delta.y()
            screen = QApplication.primaryScreen()
            if screen:
                avail = screen.availableGeometry()
                new_x = max(avail.left(), min(new_x, avail.right() - self.width()))
                new_y = max(avail.top(), min(new_y, avail.bottom() - self.height()))
            self.move(new_x, new_y)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.drag_locked:
            screen = QApplication.primaryScreen()
            if screen:
                avail = screen.availableGeometry()
                left_dist = abs(self.x() - avail.left())
                right_dist = abs(avail.right() - (self.x() + self.width()))
                if left_dist < right_dist:
                    self.move(avail.left(), self.y())
                else:
                    self.move(avail.right() - self.width(), self.y())
        # Always ensure tray exists regardless of mouse interactions
        self._ensure_tray_initialized()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            delta = event.angleDelta().y()
            step = 10 if delta > 0 else -10
            new_size = self.width() + step
            new_size = max(96, min(600, new_size))
            self.character_label.setFixedSize(new_size, new_size)
            self.setFixedSize(new_size, new_size)
            self.settings_helper.set_size(new_size)
            event.accept()
        else:
            event.ignore()

    def hideEvent(self, event):
        try:
            if self.movie:
                self.movie.setPaused(True)
        except Exception:
            pass
        self._sync_tray_state()
        super().hideEvent(event)

    def showEvent(self, event):
        try:
            if self.movie:
                self.movie.setPaused(False)
        except Exception:
            pass
        # Ensure tray is present when the widget is shown
        self._ensure_tray_initialized()
        self._sync_tray_state()
        super().showEvent(event)

    def _ensure_tray_initialized(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        if CharacterWidget.tray_icon is not None:
            return
        CharacterWidget.tray_icon = QSystemTrayIcon()
        icon_path = resource_path('Icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        CharacterWidget.tray_icon.setIcon(icon)
        self.setWindowIcon(icon)
        CharacterWidget.tray_icon.setToolTip('VirtualDeskmate')

        CharacterWidget.tray_menu = QMenu()
        CharacterWidget.action_show = QAction('Show')
        CharacterWidget.action_hide = QAction('Hide')
        CharacterWidget.action_show_launcher = QAction('Show Launcher')
        CharacterWidget.action_quit = QAction('Quit')
        CharacterWidget.action_chat = QAction('Open Chat')

        def _show_current():
            w = CharacterWidget.current_ref() if CharacterWidget.current_ref else None
            if w is not None:
                w.showNormal()

        def _hide_current():
            w = CharacterWidget.current_ref() if CharacterWidget.current_ref else None
            if w is not None:
                w.hide()

        def _show_launcher():
            l = CharacterWidget.launcher_ref() if CharacterWidget.launcher_ref else None
            if l is not None:
                l.show()
                l.raise_()
                l.activateWindow()

        CharacterWidget.action_show.triggered.connect(_show_current)
        CharacterWidget.action_hide.triggered.connect(_hide_current)
        CharacterWidget.action_show_launcher.triggered.connect(_show_launcher)
        CharacterWidget.action_quit.triggered.connect(QApplication.instance().quit)

        CharacterWidget.action_startup = QAction('Start with Windows', self, checkable=True)
        CharacterWidget.action_startup.setChecked(WindowsStartupManager.is_enabled())

        def _toggle_startup(enabled):
            WindowsStartupManager.set_enabled(enabled)
        CharacterWidget.action_startup.toggled.connect(_toggle_startup)

        CharacterWidget.tray_menu.addAction(CharacterWidget.action_show)
        CharacterWidget.tray_menu.addAction(CharacterWidget.action_hide)
        CharacterWidget.tray_menu.addAction(CharacterWidget.action_show_launcher)
        CharacterWidget.tray_menu.addAction(CharacterWidget.action_startup)
        CharacterWidget.tray_menu.addSeparator()
        CharacterWidget.tray_menu.addAction(CharacterWidget.action_chat)
        CharacterWidget.tray_menu.addAction(CharacterWidget.action_quit)
        CharacterWidget.tray_icon.setContextMenu(CharacterWidget.tray_menu)

        def on_tray_activated(reason):
            if reason == QSystemTrayIcon.Trigger:
                w = CharacterWidget.current_ref() if CharacterWidget.current_ref else None
                if w is not None:
                    if w.isHidden():
                        w.showNormal()
                    else:
                        w.hide()
        CharacterWidget.tray_icon.activated.connect(on_tray_activated)
        CharacterWidget.tray_icon.show()

        def _open_chat():
            try:
                from chat_window import ChatWindow
            except Exception:
                from .chat_window import ChatWindow  # type: ignore
            l = CharacterWidget.launcher_ref() if CharacterWidget.launcher_ref else None
            # Always open as a top-level window
            w = ChatWindow()
            w.show()
        CharacterWidget.action_chat.triggered.connect(_open_chat)

    def _on_bob(self):
        self._bob_phase = (self._bob_phase + 1) % 120
        offset = int(3 * __import__('math').sin(self._bob_phase / 120.0 * 2 * __import__('math').pi))
        self.move(self.x(), self.y() + offset)

    def _toggle_visibility(self):
        if self.isHidden():
            self.showNormal()
        else:
            self.hide()

    def _cycle_size(self):
        presets = [160, 250, 360, 480]
        current = self.width()
        for p in presets:
            if p > current:
                self.set_size(p)
                return
        self.set_size(presets[0])

    def open_context_menu(self, pos):
        menu = QMenu(self)
        opacity_menu = menu.addMenu('Opacity')
        for label, value in [('100%', 1.0), ('80%', 0.8), ('60%', 0.6), ('40%', 0.4)]:
            act = QAction(label, self, checkable=False)
            def make_setter(v):
                return lambda: self.set_opacity(v)
            act.triggered.connect(make_setter(value))
            opacity_menu.addAction(act)

        size_menu = menu.addMenu('Size')
        for label, value in [('Small', 160), ('Medium', 250), ('Large', 360), ('Huge', 480)]:
            act = QAction(label, self)
            def make_size_setter(v):
                return lambda: self.set_size(v)
            act.triggered.connect(make_size_setter(value))
            size_menu.addAction(act)

        act_lock = QAction('Lock Position', self, checkable=True)
        act_lock.setChecked(self.drag_locked)
        act_lock.toggled.connect(self.set_lock_position)
        menu.addAction(act_lock)

        # Click-through removed

        act_idle = QAction('Idle Bobbing', self, checkable=True)
        act_idle.setChecked(self.idle_enabled)
        act_idle.toggled.connect(self.set_idle_enabled)
        menu.addAction(act_idle)

        act_launcher = QAction('Show Launcher', self)
        act_launcher.triggered.connect(lambda: CharacterWidget.launcher_ref() and CharacterWidget.launcher_ref().show())
        menu.addAction(act_launcher)

        menu.exec_(self.mapToGlobal(pos))

    def set_opacity(self, value: float):
        self.setWindowOpacity(value)
        self.settings_helper.set_opacity(value)
        self._sync_tray_state()

    def set_size(self, size: int):
        size = max(96, min(600, int(size)))
        self.character_label.setFixedSize(size, size)
        self.setFixedSize(size, size)
        self.settings_helper.set_size(size)

    def set_lock_position(self, locked: bool):
        self.drag_locked = bool(locked)
        self.settings_helper.set_lock_position(self.drag_locked)
        self._sync_tray_state()

    # Click-through removed

    def set_idle_enabled(self, enabled: bool):
        self.idle_enabled = bool(enabled)
        self.settings_helper.settings.setValue('behavior/idleEnabled', self.idle_enabled)
        if self.idle_enabled:
            if not self.bob_timer.isActive():
                self.bob_timer.timeout.connect(self._on_bob)
                self.bob_timer.start()
        else:
            self.bob_timer.stop()

    # Click-through removed

    def _sync_tray_state(self):
        if CharacterWidget.tray_icon is not None:
            state = []
            if self.drag_locked:
                state.append('Locked')
            # Click-through removed
            state.append(f"{int(self.windowOpacity()*100)}%")
            CharacterWidget.tray_icon.setToolTip('VirtualDeskmate - ' + ', '.join(state))


