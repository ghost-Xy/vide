import sys
from PyQt5.QtWidgets import QApplication
from editor_ui import AutoVideoEditor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoVideoEditor()
    window.show()
    sys.exit(app.exec_())