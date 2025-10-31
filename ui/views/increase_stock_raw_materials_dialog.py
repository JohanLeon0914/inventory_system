"""
Diálogo para aumentar stock a todas las materias primas
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QLineEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from config.database import get_session, close_session
from models import RawMaterial, RawMaterialMovement, RawMaterialMovementType

class IncreaseStockAllRawMaterialsDialog(QDialog):
    """Diálogo para aumentar el stock de todas las materias primas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aumentar Stock a Todas las Materias Primas")
        self.setMinimumWidth(500)
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
            QDoubleSpinBox, QLineEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Advertencia
        warning_label = QLabel("⚠️ Esta acción aumentará el stock de TODAS las materias primas")
        warning_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f59e0b; padding: 10px; background-color: #fef3c7; border-radius: 6px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        form = QFormLayout()
        
        # Cantidad a agregar (usar QDoubleSpinBox para materias primas que pueden tener decimales)
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.01)
        self.quantity_spin.setMaximum(999999.99)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setMinimumHeight(35)
        form.addRow("Cantidad a agregar a cada materia prima:", self.quantity_spin)
        
        # Razón
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Razón del aumento masivo de stock...")
        self.reason_input.setMinimumHeight(35)
        form.addRow("Razón:", self.reason_input)
        
        layout.addLayout(form)
        
        # Botones
        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Aumentar Stock a Todas")
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_save.clicked.connect(self.save_increase_all)
        
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)
        layout.addLayout(buttons)
    
    def save_increase_all(self):
        """Aumenta el stock de todas las materias primas"""
        quantity = self.quantity_spin.value()
        reason = self.reason_input.text().strip() or "Aumento masivo de stock"
        
        if quantity <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a cero.")
            return
        
        # Confirmar acción
        reply = QMessageBox.question(
            self,
            "Confirmar Acción",
            f"¿Está seguro de aumentar el stock de TODAS las materias primas en {quantity:.2f} unidades?\n\n"
            f"Esta acción afectará a todas las materias primas del sistema.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        session = get_session()
        try:
            materials = session.query(RawMaterial).all()
            
            if not materials:
                QMessageBox.information(self, "Info", "No hay materias primas en el sistema")
                return
            
            updated_count = 0
            for material in materials:
                previous_stock = material.stock
                material.stock += quantity
                
                # Registrar movimiento de materia prima
                movement = RawMaterialMovement(
                    raw_material_id=material.id,
                    movement_type=RawMaterialMovementType.PURCHASE,
                    quantity=quantity,
                    reason=f"{reason} - Aumento masivo"
                )
                session.add(movement)
                updated_count += 1
            
            session.commit()
            
            QMessageBox.information(
                self,
                "✅ Éxito",
                f"Stock aumentado correctamente.\n\n"
                f"Materias primas afectadas: {updated_count}\n"
                f"Cantidad agregada a cada una: {quantity:.2f}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al aumentar stock: {str(e)}")
        finally:
            close_session()

