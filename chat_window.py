from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt

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
        self.setMinimumSize(420, 520)
        self.client = ChatClient(self.settings.get_api_key(), self.settings.get_model())
        self.system_prompt = self.settings.get_persona()

        self.history_view = QTextEdit(self)
        self.history_view.setReadOnly(True)
        self.history_view.setStyleSheet("padding: 8px;")
        self.input = QLineEdit(self)
        self.input.setPlaceholderText('Type a message...')
        self.input.setMinimumHeight(32)
        self.send_btn = QPushButton('Send', self)
        self.send_btn.setMinimumHeight(32)
        self.send_btn.clicked.connect(self.on_send)

        root = QVBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)
        root.addWidget(QLabel('Chatting as persona'))
        root.addWidget(self.history_view, 1)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self.input, 1)
        row.addWidget(self.send_btn, 0)
        root.addLayout(row)
        self.setLayout(root)

        self.messages = []
        if self.system_prompt:
            self.messages.append({'role': 'system', 'content': self.system_prompt})

    def on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.append_line('You', text)
        self.messages.append({'role': 'user', 'content': text})
        try:
            reply = self.client.chat(self.messages)
            self.messages.append({'role': 'assistant', 'content': reply})
            self.append_line('DeskMate', reply)
        except Exception as e:
            self.append_line('Error', str(e))

    def append_line(self, speaker: str, content: str):
        label = self.chat_name if speaker == 'DeskMate' else speaker
        self.history_view.append(f"<b>{label}:</b> {content}")


