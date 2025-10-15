Virtual Deskmate (PyQt5)

DISCLAIMER: THIS PROGRAM IS STILL IN EARLY-DEVELOPMENT!

A lightweight desktop companion that floats on your screen as a translucent animated character. Includes a styled launcher with live GIF preview, tray controls, hotkeys, edge snapping, optional Start with Windows, and an integrated OpenAI‑powered chat with persona and custom chatbot name.

Features
- Anime‑styled launcher UI with live GIF preview
- Transparent, always‑on‑top animated character (GIF)
- Drag to move with screen‑edge clamping and snapping
- Context menu on character:
  - Opacity presets: 100/80/60/40%
  - Size presets: Small/Medium/Large/Huge
  - Lock Position
  - Idle Bobbing (gentle motion)
  - Show Launcher
- System tray menu: Show/Hide, Show Launcher, Start with Windows, Open Chat, Quit
- Hotkeys (while character window focused):
  - Ctrl+Shift+H: Toggle show/hide
  - Ctrl+Shift+S: Cycle size presets
- Ctrl+MouseWheel: Resize character (min 96px, max 600px)
- Remembers last GIF, size, opacity, and toggles via QSettings
- Integrated chat window powered by OpenAI (API) with:
  - Fields in launcher for API key, model (e.g., gpt‑4o‑mini), persona prompt, and chatbot name
  - “Open Chat” button in launcher and tray
- Single‑instance launcher guard
- Logging to %APPDATA%\VirtualDeskmate\logs\app.log

Project structure
```
VirtualDeskmate/
  main.py                 # App entry, HiDPI, logging, single‑instance, launcher
  character_widget.py     # Character window (tray, menu, drag/snap, hotkeys)
  launcher_window.py      # Styled launcher with live GIF preview & OpenAI settings
  settings_helper.py      # QSettings wrapper
  startup_windows.py      # Windows Run key manager
  utils.py                # resource_path(), setup_logging(), ChatClient (OpenAI SDK or HTTP fallback)
  chat_window.py          # Simple chat UI (history, input, send)
  Dance-Evernight-unscreen.gif   # Default character (optional, add your own)
  Icon.png                       # Tray icon (optional)
```

Requirements
- Python 3.8+
- PyQt5
- OpenAI (optional; if not installed, an HTTP fallback to /v1/chat/completions is used)

Install:
```bash
pip install PyQt5
# Optional (preferred):
pip install openai
```

Running
From the project directory:
```bash
# Option A: run as a script (works after we added import fallbacks)
python main.py

# Option B: run as a package (recommended once you add __init__.py)
python -m VirtualDeskmate.main
```
If you see import errors, ensure you’re running inside the project folder and that PyQt5 is installed for the active interpreter.

Usage
1. In the launcher, click Browse and pick a transparent GIF (recommended).
2. See the live preview; click “Show Deskmate.”
3. Right‑click the character for quick controls.
4. Use hotkeys for quick toggles while the character window is focused.
5. Use the tray icon to show/hide, open chat, or enable “Start with Windows.”

Chat
1. In the launcher, enter your OpenAI API key and model (e.g., gpt‑4o‑mini).
2. Set Persona (system prompt) to define how the character speaks.
3. Set Chatbot Name (used in the chat window title and assistant label).
4. Click “Open Chat” in the launcher or use the tray “Open Chat.”

Packaging (PyInstaller)
Create a distributable EXE (Windows):
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed ^
  --name VirtualDeskmate ^
  --add-data "Dance-Evernight-unscreen.gif;." ^
  --add-data "Icon.png;." ^
  main.py
```
Notes:
- Use `;` as the separator on Windows for `--add-data`.
- If you created a package directory, you can set the entry‑point to `main.py` inside it.
- When frozen, `resource_path()` automatically resolves bundled files (via `sys._MEIPASS`).

Settings location
- Stored via QSettings under organization `VirtualPartner`, app `VirtualDeskmate`.
- Common keys:
  - `paths/lastGif`
  - `ui/size`, `ui/opacity`
  - `behavior/lockPosition`, `behavior/idleEnabled`
  - `chat/apiKey`, `chat/model`, `chat/persona`, `chat/name`

Troubleshooting
- “Attempted relative import with no known parent package”: run `python main.py` from the project folder or add `__init__.py` to make the folder a package and run `python -m VirtualDeskmate.main`.
- PyQt5 “could not be resolved” in IDE: select the interpreter with PyQt5 installed; it’s a hint, not a runtime error if PyQt5 is present.
- No tray icon: ensure the OS tray is available and `Icon.png` is present; otherwise a default icon is used.
- PyInstaller PermissionError on rebuild (Windows): the old EXE may be running or locked.
  - Quit from the tray or run `taskkill /IM VirtualDeskmate.exe /F`
  - Then delete `dist/VirtualDeskmate.exe` and rebuild

License
This project is provided as‑is. Ensure you have the right to distribute any GIFs you bundle.


