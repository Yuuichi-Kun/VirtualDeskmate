import os
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog, QLineEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import QSettings, Qt
# Support package and script imports
try:
    from .settings_helper import SettingsHelper  # type: ignore
    from .character_widget import CharacterWidget  # type: ignore
    from .utils import resource_path  # type: ignore
except Exception:
    from settings_helper import SettingsHelper  # type: ignore
    from character_widget import CharacterWidget  # type: ignore
    from utils import resource_path  # type: ignore


class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VirtualDeskmate Launcher')
        self.setFixedSize(1080, 600)
        self.settings = QSettings('VirtualPartner', 'VirtualDeskmate')
        self.settings_helper = SettingsHelper()

        # --- Title / Subtitle ---
        self.title_label = QLabel('Virtual Deskmate')
        self.subtitle_label = QLabel('Summon your desk companion (choose a transparent GIF)')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.subtitle_label.setFont(QFont('Segoe UI', 10))

        # --- Preview ---
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(280, 280)
        self.preview_label.setScaledContents(True)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_movie = None

        self.gif_path_input = QLineEdit(self)
        self.gif_path_input.setPlaceholderText('Choose a GIF (transparent recommended)')
        last_path = self.settings_helper.get_last_gif_path()
        if last_path and os.path.exists(last_path):
            self.gif_path_input.setText(last_path)
            self.update_preview(last_path)
        else:
            self.update_preview(resource_path('Dance-Evernight-unscreen.gif'))

        browse_btn = QPushButton('Browse...', self)
        show_btn = QPushButton('Show Deskmate', self)
        open_chat_btn = QPushButton('Open Chat', self)

        browse_btn.clicked.connect(self.on_browse)
        show_btn.clicked.connect(self.on_show)
        open_chat_btn.clicked.connect(self.on_open_chat)

        path_row = QHBoxLayout()
        path_row.addWidget(self.gif_path_input)
        path_row.addWidget(browse_btn)

        left_col = QVBoxLayout()
        left_col.addWidget(self.title_label)
        left_col.addWidget(self.subtitle_label)
        left_col.addLayout(path_row)
        # --- Chat settings ---
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText('OpenAI API Key')
        self.api_key_input.setText(self.settings_helper.get_api_key())
        self.api_key_input.textChanged.connect(self.settings_helper.set_api_key)

        self.model_input = QLineEdit(self)
        self.model_input.setPlaceholderText('Model (e.g., gpt-4o-mini)')
        self.model_input.setText(self.settings_helper.get_model())
        self.model_input.textChanged.connect(self.settings_helper.set_model)

        self.persona_input = QTextEdit(self)
        self.persona_input.setPlaceholderText('Persona/system prompt...')
        self.persona_input.setFixedHeight(110)
        self.persona_input.setText(self.settings_helper.get_persona())
        self.persona_input.textChanged.connect(lambda: self.settings_helper.set_persona(self.persona_input.toPlainText()))

        self.chat_name_input = QLineEdit(self)
        self.chat_name_input.setPlaceholderText('Chatbot display name (e.g., DeskMate, Paimon)')
        self.chat_name_input.setText(self.settings_helper.get_chat_name())
        self.chat_name_input.textChanged.connect(self.settings_helper.set_chat_name)

        left_col.addWidget(QLabel('OpenAI Settings'))
        # Group: API & Model
        api_model_row = QHBoxLayout()
        api_model_row.addWidget(self.api_key_input, 1)
        api_model_row.addWidget(self.model_input, 1)
        left_col.addLayout(api_model_row)

        # Persona block (full-width)
        left_col.addWidget(QLabel('Persona'))
        left_col.addWidget(self.persona_input)

        # Chatbot name placed below persona with spacing
        left_col.addSpacing(6)
        left_col.addWidget(QLabel('Chatbot Name'))
        left_col.addWidget(self.chat_name_input)

        left_col.addStretch(1)
        left_col.addWidget(show_btn)
        left_col.addWidget(open_chat_btn)

        main_row = QHBoxLayout()
        main_row.setSpacing(16)
        main_row.addLayout(left_col, 1)
        main_row.addWidget(self.preview_label, 0, Qt.AlignCenter)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        root_layout.addLayout(main_row)
        self.setLayout(root_layout)

        self.apply_theme()
        self.add_shadow()

    def on_browse(self):
        start_dir = os.path.expanduser('~')
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select GIF', start_dir, 'GIF Files (*.gif)')
        if file_path:
            self.gif_path_input.setText(file_path)
            self.settings_helper.set_last_gif_path(file_path)
            self.update_preview(file_path)

    def on_show(self):
        path = self.gif_path_input.text().strip()
        if not path or not os.path.exists(path):
            path = resource_path('Dance-Evernight-unscreen.gif')
        else:
            self.settings_helper.set_last_gif_path(path)

        self.deskmate = CharacterWidget(path, launcher=self)
        self.deskmate.show()
        self.hide()

    def on_open_chat(self):
        try:
            from chat_window import ChatWindow  # local import to avoid circular
        except Exception:
            from .chat_window import ChatWindow  # type: ignore
        self.chat = ChatWindow()
        self.chat.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # --- UI helpers ---
    def update_preview(self, path: str):
        try:
            if self.preview_movie:
                self.preview_movie.stop()
            self.preview_movie = QMovie(path)
            self.preview_label.setMovie(self.preview_movie)
            self.preview_movie.start()
        except Exception:
            self.preview_movie = None
            self.preview_label.setText('No preview')

    def apply_theme(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #0f1226;
                color: #e5e7ff;
                font-family: 'Segoe UI', 'Bahnschrift', sans-serif;
            }
            QLineEdit {
                background: #181b34;
                border: 2px solid #2a2f55;
                border-radius: 10px;
                padding: 8px 10px;
                color: #e5e7ff;
                selection-background-color: #6c7bff;
            }
            QTextEdit {
                background: #181b34;
                border: 2px solid #2a2f55;
                border-radius: 10px;
                padding: 8px 10px;
                color: #e5e7ff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #6c7bff, stop:1 #b26cff);
                border: none;
                border-radius: 12px;
                padding: 10px 14px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                filter: brightness(1.1);
            }
            QPushButton:pressed {
                background: #5b66e6;
            }
            QLabel#title {
                color: #f5f6ff;
            }
            """
        )
        self.title_label.setObjectName('title')

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


