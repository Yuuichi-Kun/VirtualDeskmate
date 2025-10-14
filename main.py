import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QAction, QStyle, QPushButton, QFileDialog, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import Qt, QPoint, QSettings
import weakref

# Helper to get correct path for assets both in dev and PyInstaller bundle
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class CharacterWidget(QWidget):
    # Single shared tray icon and references
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
        CharacterWidget.current_ref = weakref.ref(self)
        if launcher is not None:
            CharacterWidget.launcher_ref = weakref.ref(launcher)
        
        # --- WINDOW SETUP ---
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- CHARACTER ANIMATION ---
        self.character_label = QLabel(self)
        
        # Load the GIF
        if not gif_path:
            gif_path = resource_path('Dance-Evernight-unscreen.gif')
        self.movie = QMovie(gif_path)
        
        # Enable transparency for the movie
        self.movie.setCacheMode(QMovie.CacheAll)
        
        # Set the movie on the label
        self.character_label.setMovie(self.movie)
        
        # Make the label background transparent and pass mouse events to parent for dragging
        self.character_label.setStyleSheet("background: transparent;")
        self.character_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Start the animation
        self.movie.start()

        # --- RESIZING THE GIF ---
        # Allow the label to scale its contents
        self.character_label.setScaledContents(True) 
        
        # Set the size you want for the character
        new_width = 250
        new_height = 250
        self.character_label.setFixedSize(new_width, new_height)
        self.setFixedSize(new_width, new_height) # Resize the main window to match

        # --- MAKING IT DRAGGABLE ---
        self.old_pos = self.pos()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

        # --- SYSTEM TRAY ICON (Singleton) ---
        if QSystemTrayIcon.isSystemTrayAvailable():
            if CharacterWidget.tray_icon is None:
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

                # Wire actions to operate on the current instance/launcher via weakrefs
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

                CharacterWidget.tray_menu.addAction(CharacterWidget.action_show)
                CharacterWidget.tray_menu.addAction(CharacterWidget.action_hide)
                CharacterWidget.tray_menu.addAction(CharacterWidget.action_show_launcher)
                CharacterWidget.tray_menu.addSeparator()
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


class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VirtualDeskmate Launcher')
        self.setFixedSize(480, 140)
        self.settings = QSettings('VirtualPartner', 'VirtualDeskmate')

        self.gif_path_input = QLineEdit(self)
        self.gif_path_input.setPlaceholderText('Choose a GIF (transparent recommended)')
        last_path = self.settings.value('lastGifPath', type=str)
        if last_path and os.path.exists(last_path):
            self.gif_path_input.setText(last_path)

        browse_btn = QPushButton('Browse...', self)
        show_btn = QPushButton('Show Deskmate', self)

        browse_btn.clicked.connect(self.on_browse)
        show_btn.clicked.connect(self.on_show)

        path_row = QHBoxLayout()
        path_row.addWidget(self.gif_path_input)
        path_row.addWidget(browse_btn)

        root_layout = QVBoxLayout()
        root_layout.addLayout(path_row)
        root_layout.addWidget(show_btn)

        self.setLayout(root_layout)

    def on_browse(self):
        start_dir = os.path.expanduser('~')
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select GIF', start_dir, 'GIF Files (*.gif)')
        if file_path:
            self.gif_path_input.setText(file_path)
            self.settings.setValue('lastGifPath', file_path)

    def on_show(self):
        path = self.gif_path_input.text().strip()
        if not path or not os.path.exists(path):
            # Fall back to bundled default if invalid
            path = resource_path('Dance-Evernight-unscreen.gif')
        else:
            self.settings.setValue('lastGifPath', path)

        self.deskmate = CharacterWidget(path, launcher=self)
        self.deskmate.show()
        self.hide()

    def closeEvent(self, event):
        # Minimize to tray on close
        event.ignore()
        self.hide()

# --- RUN THE APPLICATION ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Keep app running when all windows are hidden (required for tray-only apps)
    app.setQuitOnLastWindowClosed(False)
    launcher = LauncherWindow()
    launcher.show()
    sys.exit(app.exec_())