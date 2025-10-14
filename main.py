import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import Qt, QPoint

# Helper to get correct path for assets both in dev and PyInstaller bundle
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class CharacterWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- WINDOW SETUP ---
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.SplashScreen
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- CHARACTER ANIMATION ---
        self.character_label = QLabel(self)
        
        # Load the GIF
        gif_path = resource_path('Dance-Evernight-unscreen.gif')
        self.movie = QMovie(gif_path)
        
        # Enable transparency for the movie
        self.movie.setCacheMode(QMovie.CacheAll)
        
        # Set the movie on the label
        self.character_label.setMovie(self.movie)
        
        # Make the label background transparent
        self.character_label.setStyleSheet("background: transparent;")
        
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

        # --- SYSTEM TRAY ICON ---
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)

            icon_path = resource_path('Icon.png')
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
            self.setWindowIcon(icon)
            self.tray_icon.setToolTip('VirtualDeskmate')

            tray_menu = QMenu()
            action_show = QAction('Show', self)
            action_show.triggered.connect(self.showNormal)
            action_hide = QAction('Hide', self)
            action_hide.triggered.connect(self.hide)
            action_quit = QAction('Quit', self)
            action_quit.triggered.connect(QApplication.instance().quit)

            tray_menu.addAction(action_show)
            tray_menu.addAction(action_hide)
            tray_menu.addSeparator()
            tray_menu.addAction(action_quit)
            self.tray_icon.setContextMenu(tray_menu)

            # Left-click tray icon toggles show/hide
            def on_tray_activated(reason):
                if reason == QSystemTrayIcon.Trigger:
                    if self.isHidden():
                        self.showNormal()
                    else:
                        self.hide()
            self.tray_icon.activated.connect(on_tray_activated)
            self.tray_icon.show()

    def closeEvent(self, event):
        # Minimize to tray on close
        event.ignore()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

# --- RUN THE APPLICATION ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Keep app running when all windows are hidden (required for tray-only apps)
    app.setQuitOnLastWindowClosed(False)
    widget = CharacterWidget()
    widget.show()
    sys.exit(app.exec_())