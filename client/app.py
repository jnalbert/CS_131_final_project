import sys
from PySide6.QtWidgets import QApplication
# Import whatever your main widget class is here
# from .main_widget import MainWidget
from .camera_manager import release_camera

def main():
    app = QApplication(sys.argv)
    
    # Create your main widget
    # main_widget = MainWidget()
    # main_widget.show()
    
    # Make sure to release the camera when the app closes
    app.aboutToQuit.connect(release_camera)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 