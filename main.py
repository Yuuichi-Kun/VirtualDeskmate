import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
try:
    from PyQt5.QtNetwork import QLocalServer, QLocalSocket
except Exception:
    QLocalServer = None  # type: ignore
    QLocalSocket = None  # type: ignore

# Support running as a script or as a package module
try:
    from .utils import setup_logging  # type: ignore
    from .launcher_window import LauncherWindow  # type: ignore
except Exception:
    from utils import setup_logging  # type: ignore
    from launcher_window import LauncherWindow  # type: ignore

 

# --- RUN THE APPLICATION ---
if __name__ == '__main__':
    # High-DPI scaling for Windows/HiDPI screens
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    setup_logging()

    app = QApplication(sys.argv)

    # --- Single-instance guard ---
    if QLocalServer is not None and QLocalSocket is not None:
        instance_key = 'VirtualDeskmate_Launcher_Instance_Key'
        server = QLocalServer()
        if not server.listen(instance_key):
            # Another instance exists; try to activate it and exit
            socket = QLocalSocket()
            socket.connectToServer(instance_key)
            if socket.waitForConnected(500):
                # Send a simple activation message
                socket.write(b'activate')
                socket.flush()
                socket.waitForBytesWritten(200)
                socket.disconnectFromServer()
            sys.exit(0)

        def on_new_connection():
            sock = server.nextPendingConnection()
            if sock:
                sock.waitForReadyRead(100)
                data = bytes(sock.readAll()).decode('utf-8', errors='ignore')
                if 'activate' in data:
                    if launcher.isHidden():
                        launcher.show()
                    launcher.raise_()
                    launcher.activateWindow()
                sock.disconnectFromServer()
        server.newConnection.connect(on_new_connection)
    # Keep app running when all windows are hidden (required for tray-only apps)
    app.setQuitOnLastWindowClosed(False)
    launcher = LauncherWindow()
    launcher.show()
    sys.exit(app.exec_())