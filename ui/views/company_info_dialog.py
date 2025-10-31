"""
Diálogo para editar información de la empresa
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from config.database import get_session, close_session
from models import CompanyInfo

class CompanyInfoDialog(QDialog):
    """Diálogo para editar información de la empresa"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Información de la Empresa")
        self.setMinimumWidth(500)
        self.setModal(True)
        self.init_ui()
        self.load_company_info()
    
    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { 
                color: #0f172a; 
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLineEdit { 
                color: #0f172a; 
                background-color: white; 
                border: 1px solid #d1d5db; 
                border-radius: 6px; 
                padding: 10px; 
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
            QPushButton {
                background-color: #2563eb; 
                color: white; 
                border: none; 
                border-radius: 6px;
                font-size: 14px; 
                font-weight: 500; 
                padding: 10px 20px;
                min-height: 40px;
            }
            QPushButton:hover { 
                background-color: #1d4ed8; 
            }
            QPushButton#cancelButton { 
                background-color: #64748b;
            }
            QPushButton#cancelButton:hover { 
                background-color: #475569;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Información de la Empresa")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Esta información aparecerá en las facturas generadas")
        subtitle.setStyleSheet("color: #64748b; font-size: 13px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: MI EMPRESA SAS")
        form_layout.addRow("Nombre de la Empresa*:", self.name_input)
        
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("Ej: 900.123.456-7")
        form_layout.addRow("NIT*:", self.nit_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Ej: Calle 123 #45-67")
        form_layout.addRow("Dirección:", self.address_input)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Ej: Bogotá D.C., Colombia")
        form_layout.addRow("Ciudad:", self.city_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Ej: +57 1 123 4567")
        form_layout.addRow("Teléfono:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: contacto@miempresa.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.regimen_input = QLineEdit()
        self.regimen_input.setPlaceholderText("Ej: Régimen Simplificado")
        form_layout.addRow("Régimen Tributario:", self.regimen_input)
        
        layout.addLayout(form_layout)
        
        # Nota
        note = QLabel("* Campos obligatorios")
        note.setStyleSheet("color: #64748b; font-size: 12px; font-style: italic;")
        layout.addWidget(note)
        
        layout.addStretch()
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("cancelButton")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_company_info)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
    
    def load_company_info(self):
        """Carga la información de la empresa desde la base de datos"""
        session = get_session()
        try:
            company_info = session.query(CompanyInfo).first()
            if company_info:
                self.name_input.setText(company_info.company_name)
                self.nit_input.setText(company_info.company_nit)
                self.address_input.setText(company_info.company_address or "")
                self.city_input.setText(company_info.company_city or "")
                self.phone_input.setText(company_info.company_phone or "")
                self.email_input.setText(company_info.company_email or "")
                self.regimen_input.setText(company_info.company_regimen or "")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
        finally:
            close_session()
    
    def save_company_info(self):
        """Guarda la información de la empresa"""
        name = self.name_input.text().strip()
        nit = self.nit_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre de la empresa es obligatorio.")
            return
        if not nit:
            QMessageBox.warning(self, "Error", "El NIT es obligatorio.")
            return
        
        session = get_session()
        try:
            company_info = session.query(CompanyInfo).first()
            
            if not company_info:
                company_info = CompanyInfo()
                session.add(company_info)
            
            company_info.company_name = name
            company_info.company_nit = nit
            company_info.company_address = self.address_input.text().strip() or None
            company_info.company_city = self.city_input.text().strip() or None
            company_info.company_phone = self.phone_input.text().strip() or None
            company_info.company_email = self.email_input.text().strip() or None
            company_info.company_regimen = self.regimen_input.text().strip() or None
            
            session.commit()
            QMessageBox.information(self, "Éxito", "Información de la empresa actualizada correctamente.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
        finally:
            close_session()
