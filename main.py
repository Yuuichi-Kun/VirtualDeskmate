import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QPoint

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
        self.movie = QMovie('Dance-Evernight-Unscreen.gif')
        
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
    widget = CharacterWidget()
    widget.show()
    sys.exit(app.exec_())