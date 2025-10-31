"""
Diálogo de autenticación para acceder a la sección de inventario
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import hashlib
from config.database import get_session, close_session
from models.inventory_password import InventoryPassword

class InventoryAuthDialog(QDialog):
    """Diálogo para autenticación de inventario"""
    def __init__(self, parent=None, is_password_set=False):
        super().__init__(parent)
        self.is_password_set = is_password_set
        self.setWindowTitle("🔒 Acceso a Inventario")
        self.setMinimumWidth(450)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-size: 13px;
            }
            QLineEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
            QTextEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🔒 Acceso Protegido")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Mensaje
        message = QLabel(
            "La sección de inventario está protegida.\n"
            "Ingrese la contraseña para continuar." if self.is_password_set else
            "Establezca una contraseña para proteger esta sección."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("color: #64748b; margin: 10px 0;")
        layout.addWidget(message)
        
        # Mostrar pista si hay contraseña
        if self.is_password_set:
            session = get_session()
            try:
                password_record = session.query(InventoryPassword).first()
                if password_record and password_record.hint:
                    hint_label = QLabel(f"💡 Pista: {password_record.hint}")
                    hint_label.setStyleSheet("""
                        font-size: 13px;
                        color: #3b82f6;
                        background-color: #eff6ff;
                        border: 1px solid #bfdbfe;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    """)
                    hint_label.setWordWrap(True)
                    layout.addWidget(hint_label)
            finally:
                close_session()
        
        # Campo de contraseña
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Ingrese la contraseña")
        self.password_input.setMinimumHeight(45)
        if not self.is_password_set:
            self.password_input.setPlaceholderText("Nueva contraseña")
        layout.addWidget(self.password_input)
        
        # Campo de confirmación si no hay contraseña
        if not self.is_password_set:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("Confirme la contraseña")
            self.confirm_input.setMinimumHeight(45)
            layout.addWidget(self.confirm_input)
            
            # Campo de pista
            self.hint_input = QTextEdit()
            self.hint_input.setPlaceholderText("Ingrese una pista para recordar su contraseña (opcional)")
            self.hint_input.setMaximumHeight(80)
            layout.addWidget(self.hint_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        if self.is_password_set:
            btn_cancel = QPushButton("❌ Cancelar")
            btn_cancel.setMinimumHeight(45)
            btn_cancel.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            btn_cancel.clicked.connect(self.reject)
            buttons_layout.addWidget(btn_cancel)
            
            btn_enter = QPushButton("🔓 Acceder")
            btn_enter.setMinimumHeight(45)
            btn_enter.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            btn_enter.clicked.connect(self.verify_password)
            buttons_layout.addWidget(btn_enter)
        else:
            btn_skip = QPushButton("⏭️ Omitir")
            btn_skip.setMinimumHeight(45)
            btn_skip.setStyleSheet("""
                QPushButton {
                    background-color: #64748b;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #475569;
                }
            """)
            btn_skip.clicked.connect(self.skip_password)
            buttons_layout.addWidget(btn_skip)
            
            btn_set = QPushButton("🔒 Establecer Contraseña")
            btn_set.setMinimumHeight(45)
            btn_set.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            btn_set.clicked.connect(self.set_password)
            buttons_layout.addWidget(btn_set)
        
        layout.addLayout(buttons_layout)
        
        # Ajustar título y mensaje si no hay contraseña
        if not self.is_password_set:
            title.setText("🔒 Proteger Inventario")
            message.setText("La sección de inventario permite realizar ajustes críticos.\nEstablezca una contraseña para protegerla (opcional).")
        
        # Enfocar en el primer campo
        self.password_input.setFocus()
    
    def hash_password(self, password):
        """Convierte la contraseña en un hash"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self):
        """Verifica la contraseña ingresada"""
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese la contraseña")
            return
        
        # Verificar en la base de datos
        session = get_session()
        try:
            password_record = session.query(InventoryPassword).first()
            if not password_record or not password_record.password_hash:
                QMessageBox.warning(self, "Error", "No hay contraseña configurada")
                self.reject()
                return
            
            # Comparar hashes
            password_hash = self.hash_password(password)
            if password_hash == password_record.password_hash:
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Contraseña incorrecta")
                self.password_input.clear()
                self.password_input.setFocus()
        finally:
            close_session()
    
    def set_password(self):
        """Establece una nueva contraseña"""
        password = self.password_input.text()
        confirm = self.confirm_input.text() if not self.is_password_set else ""
        hint = self.hint_input.toPlainText().strip() if not self.is_password_set else ""
        
        if not password:
            QMessageBox.warning(self, "Error", "La contraseña no puede estar vacía")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        
        # Guardar contraseña
        session = get_session()
        try:
            password_record = session.query(InventoryPassword).first()
            if not password_record:
                password_record = InventoryPassword()
                session.add(password_record)
            
            password_record.password_hash = self.hash_password(password)
            password_record.hint = hint
            
            session.commit()
            
            QMessageBox.information(
                self,
                "✅ Contraseña Establecida",
                "La sección de inventario ahora está protegida.\n\n"
                f"{'Pista guardada: ' + hint if hint else 'Sin pista configurada.'}"
            )
            
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al establecer contraseña: {str(e)}")
        finally:
            close_session()
    
    def skip_password(self):
        """Omite establecer contraseña"""
        self.reject()


class ChangeInventoryPasswordDialog(QDialog):
    """Diálogo para cambiar la contraseña de inventario"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Cambiar Contraseña de Inventario")
        self.setMinimumWidth(450)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-size: 13px;
            }
            QLineEdit, QTextEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🔐 Cambiar Contraseña")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Mostrar pista actual si existe
        session = get_session()
        try:
            password_record = session.query(InventoryPassword).first()
            if password_record and password_record.hint:
                hint_label = QLabel(f"💡 Pista actual: {password_record.hint}")
                hint_label.setStyleSheet("""
                    font-size: 13px;
                    color: #f59e0b;
                    background-color: #fef3c7;
                    border: 1px solid #fde68a;
                    border-radius: 6px;
                    padding: 10px;
                    font-weight: bold;
                """)
                hint_label.setWordWrap(True)
                layout.addWidget(hint_label)
        finally:
            close_session()
        
        # Campo de contraseña actual
        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_input.setPlaceholderText("Contraseña actual")
        self.current_input.setMinimumHeight(45)
        layout.addWidget(QLabel("Contraseña actual:"))
        layout.addWidget(self.current_input)
        
        # Campo de nueva contraseña
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input.setPlaceholderText("Nueva contraseña")
        self.new_input.setMinimumHeight(45)
        layout.addWidget(QLabel("Nueva contraseña:"))
        layout.addWidget(self.new_input)
        
        # Campo de confirmación
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirme la nueva contraseña")
        self.confirm_input.setMinimumHeight(45)
        layout.addWidget(QLabel("Confirmar nueva contraseña:"))
        layout.addWidget(self.confirm_input)
        
        # Campo de pista
        self.hint_input = QTextEdit()
        self.hint_input.setPlaceholderText("Nueva pista (opcional, dejar vacío para mantener la actual)")
        self.hint_input.setMaximumHeight(80)
        layout.addWidget(QLabel("Nueva pista:"))
        layout.addWidget(self.hint_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("❌ Cancelar")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        btn_change = QPushButton("💾 Cambiar Contraseña")
        btn_change.setMinimumHeight(45)
        btn_change.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_change.clicked.connect(self.change_password)
        buttons_layout.addWidget(btn_change)
        
        layout.addLayout(buttons_layout)
        
        # Enfocar en el primer campo
        self.current_input.setFocus()
    
    def hash_password(self, password):
        """Convierte la contraseña en un hash"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def change_password(self):
        """Cambia la contraseña"""
        current_password = self.current_input.text()
        new_password = self.new_input.text()
        confirm_password = self.confirm_input.text()
        new_hint = self.hint_input.toPlainText().strip()
        
        if not current_password:
            QMessageBox.warning(self, "Error", "Debe ingresar la contraseña actual")
            return
        
        if not new_password:
            QMessageBox.warning(self, "Error", "La nueva contraseña no puede estar vacía")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        
        # Verificar contraseña actual y cambiar
        session = get_session()
        try:
            password_record = session.query(InventoryPassword).first()
            if not password_record or not password_record.password_hash:
                QMessageBox.warning(self, "Error", "No hay contraseña configurada")
                return
            
            # Verificar contraseña actual
            current_hash = self.hash_password(current_password)
            if current_hash != password_record.password_hash:
                QMessageBox.warning(self, "Error", "Contraseña actual incorrecta")
                self.current_input.clear()
                self.current_input.setFocus()
                return
            
            # Actualizar contraseña
            password_record.password_hash = self.hash_password(new_password)
            
            # Actualizar pista solo si se proporciona una nueva
            if new_hint:
                password_record.hint = new_hint
            
            session.commit()
            
            QMessageBox.information(
                self,
                "✅ Contraseña Cambiada",
                "La contraseña ha sido cambiada exitosamente."
            )
            
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al cambiar contraseña: {str(e)}")
        finally:
            close_session()

