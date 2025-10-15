from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor

try:
    from .settings_helper import SettingsHelper  # type: ignore
    from .utils import ChatClient  # type: ignore
except Exception:
    from settings_helper import SettingsHelper  # type: ignore
    from utils import ChatClient  # type: ignore


class ChatWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.settings = SettingsHelper()
        self.chat_name = self.settings.get_chat_name()
        self.setWindowTitle(f'{self.chat_name} — Chat')
        self.setMinimumSize(520, 620)
        self.client = ChatClient(self.settings.get_api_key(), self.settings.get_model())
        self.system_prompt = self.settings.get_persona()

        # --- Widgets ---
        self.history_view = QTextEdit(self)
        self.history_view.setReadOnly(True)
        self.history_view.setPlaceholderText('Conversation will appear here...')
        self.input = QLineEdit(self)
        self.input.setPlaceholderText('Type a message...')
        self.input.setMinimumHeight(32)
        self.send_btn = QPushButton('Send', self)
        self.send_btn.setMinimumHeight(32)
        self.send_btn.clicked.connect(self.on_send)
        self.input.returnPressed.connect(self.on_send)

        # Header with name and model
        title = QLabel(self.chat_name)
        title.setObjectName('chatTitle')
        subtitle = QLabel(self.settings.get_model())
        subtitle.setObjectName('chatSubtitle')

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.addWidget(title, 0)
        header.addStretch(1)
        header.addWidget(subtitle, 0, Qt.AlignRight)
        root.addLayout(header)
        root.addWidget(self.history_view, 1)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self.input, 1)
        row.addWidget(self.send_btn, 0)
        root.addLayout(row)
        self.setLayout(root)

        self.messages = []
        if self.system_prompt:
            self.messages.append({'role': 'system', 'content': self.system_prompt})

        # --- Styles ---
        self.setStyleSheet(
            """
            QWidget { background-color: #0f1226; color: #e5e7ff; font-family: 'Segoe UI', 'Bahnschrift', sans-serif; }
            #chatTitle { font-size: 18px; font-weight: 700; color: #f5f6ff; }
            #chatSubtitle { font-size: 12px; color: #9aa3ff; padding-top: 4px; }
            QTextEdit { background: #181b34; border: 2px solid #2a2f55; border-radius: 12px; padding: 10px; color: #e5e7ff; }
            QLineEdit { background: #181b34; border: 2px solid #2a2f55; border-radius: 12px; padding: 10px 12px; color: #e5e7ff; selection-background-color: #6c7bff; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6c7bff, stop:1 #b26cff); border: none; border-radius: 12px; padding: 10px 16px; color: white; font-weight: 600; }
            QPushButton:hover { filter: brightness(1.1); }
            QPushButton:pressed { background: #5b66e6; }
            QPushButton:disabled { background: #2a2f55; color: #98a0d6; }
            """
        )

        # --- Typing animation state ---
        self._typing_timer = QTimer(self)
        self._typing_timer.setInterval(12)
        self._typing_timer.timeout.connect(self._on_type_tick)
        self._typing_text = ''
        self._typing_index = 0
        self._typing_active = False

    def on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.append_line('You', text)
        self.messages.append({'role': 'user', 'content': text})
        self._set_busy(True)
        try:
            reply = self.client.chat(self.messages)
            self.messages.append({'role': 'assistant', 'content': reply})
            self.animate_assistant(reply)
        except Exception as e:
            self.append_line('Error', str(e))
            self._set_busy(False)

    def append_line(self, speaker: str, content: str):
        label = self.chat_name if speaker == 'DeskMate' else speaker
        self.history_view.append(f"<b>{label}:</b> {content}")
        self.history_view.moveCursor(self.history_view.textCursor().End)

    def _set_busy(self, is_busy: bool):
        self.input.setDisabled(is_busy)
        self.send_btn.setDisabled(is_busy)
        self.send_btn.setText('Sending...' if is_busy else 'Send')

    def animate_assistant(self, content: str):
        # Prepare a new line with label, then type the content
        if self._typing_active:
            self._typing_timer.stop()
            self._typing_active = False
        label = self.chat_name
        # Ensure cursor at end, insert bold label and a space
        cursor = self.history_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.history_view.setTextCursor(cursor)
        # Start a fresh paragraph for the assistant so it doesn't join the user's line
        cursor.insertBlock()
        self.history_view.setTextCursor(cursor)
        self.history_view.insertHtml(f"<b>{label}:</b> ")
        self._typing_text = content
        self._typing_index = 0
        self._typing_active = True
        self._typing_timer.start()

    def _on_type_tick(self):
        if not self._typing_active:
            return
        # Type in small chunks for smoother effect
        chunk_size = 3
        typed = 0
        while typed < chunk_size and self._typing_index < len(self._typing_text):
            ch = self._typing_text[self._typing_index]
            self._typing_index += 1
            typed += 1
            if ch == '\r':
                # ignore CR in CRLF
                continue
            if ch == '\n':
                # Start a new block for a visible line break
                cursor = self.history_view.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.history_view.setTextCursor(cursor)
                cursor.insertBlock()
            else:
                self.history_view.insertPlainText(ch)
            self.history_view.moveCursor(self.history_view.textCursor().End)
        if self._typing_index >= len(self._typing_text):
            self._typing_timer.stop()
            self._typing_active = False
            # Finish the line with a newline for spacing
            self.history_view.append("")
            self._set_busy(False)


