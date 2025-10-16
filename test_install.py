import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

print("✓ Python funcionando")
print(f"✓ Versión: {sys.version}")

try:
    from PyQt6 import QtCore
    print("✓ PyQt6 instalado correctamente")
except ImportError:
    print("✗ Error con PyQt6")

try:
    import sqlalchemy
    print("✓ SQLAlchemy instalado correctamente")
except ImportError:
    print("✗ Error con SQLAlchemy")

# Prueba ventana simple
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Test de Instalación")
window.setGeometry(100, 100, 400, 200)
label = QLabel("¡Todo instalado correctamente! ✓", window)
label.setGeometry(50, 80, 300, 30)
window.show()
print("\n✓ ¡Si ves una ventana, todo está perfecto!")
sys.exit(app.exec())