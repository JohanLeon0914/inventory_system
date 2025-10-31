"""
Diálogos para aumentar stock de productos
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QSpinBox, QLineEdit, QMessageBox
)
from config.database import get_session, close_session
from models import Product, InventoryMovement, MovementType


class IncreaseStockDialog(QDialog):
    """Diálogo para aumentar stock de un producto específico"""
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Aumentar Stock - {product.name}")
        self.setMinimumWidth(400)
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
            QSpinBox, QLineEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Información del producto
        product_label = QLabel(f"Producto: {self.product.name}")
        product_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        form.addRow(product_label)
        
        # Stock actual
        current_stock_label = QLabel(f"Stock actual: {self.product.stock}")
        current_stock_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
        form.addRow(current_stock_label)
        
        # Cantidad a agregar
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(35)
        form.addRow("Cantidad a agregar:", self.quantity_spin)
        
        # Razón
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Razón del aumento de stock...")
        self.reason_input.setMinimumHeight(35)
        form.addRow("Razón:", self.reason_input)
        
        # Preview del nuevo stock
        self.new_stock_label = QLabel()
        self.new_stock_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")
        self.quantity_spin.valueChanged.connect(self.update_preview)
        self.update_preview()
        form.addRow("Nuevo stock:", self.new_stock_label)
        
        layout.addLayout(form)
        
        # Botones
        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Aumentar Stock")
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
        btn_save.clicked.connect(self.save_increase)
        
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)
        layout.addLayout(buttons)
    
    def update_preview(self):
        """Actualiza la vista previa del nuevo stock"""
        new_stock = self.product.stock + self.quantity_spin.value()
        self.new_stock_label.setText(str(new_stock))
    
    def save_increase(self):
        """Guarda el aumento de stock"""
        quantity = self.quantity_spin.value()
        reason = self.reason_input.text().strip() or "Aumento de stock manual"
        
        session = get_session()
        try:
            product = session.query(Product).filter_by(id=self.product.id).first()
            if not product:
                QMessageBox.warning(self, "Error", "Producto no encontrado")
                return
            
            previous_stock = product.stock
            product.stock += quantity
            
            # Registrar movimiento de inventario
            movement = InventoryMovement(
                product_id=product.id,
                movement_type=MovementType.ENTRY,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=product.stock,
                reason=reason
            )
            session.add(movement)
            session.commit()
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Stock aumentado correctamente\n\n"
                f"Stock anterior: {previous_stock}\n"
                f"Cantidad agregada: {quantity}\n"
                f"Nuevo stock: {product.stock}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al aumentar stock: {str(e)}")
        finally:
            close_session()


class IncreaseStockAllDialog(QDialog):
    """Diálogo para aumentar stock a todos los productos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aumentar Stock a Todos los Productos")
        self.setMinimumWidth(450)
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
            QSpinBox, QLineEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Advertencia
        warning_label = QLabel("⚠️ Esta acción aumentará el stock de TODOS los productos")
        warning_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f59e0b; padding: 10px; background-color: #fef3c7; border-radius: 6px;")
        layout.addWidget(warning_label)
        
        form = QFormLayout()
        
        # Cantidad a agregar
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(35)
        form.addRow("Cantidad a agregar a cada producto:", self.quantity_spin)
        
        # Razón
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Razón del aumento masivo de stock...")
        self.reason_input.setMinimumHeight(35)
        form.addRow("Razón:", self.reason_input)
        
        layout.addLayout(form)
        
        # Botones
        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Aumentar Stock a Todos")
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
        """Aumenta el stock de todos los productos"""
        quantity = self.quantity_spin.value()
        reason = self.reason_input.text().strip() or "Aumento masivo de stock"
        
        # Confirmar acción
        reply = QMessageBox.question(
            self,
            "Confirmar Acción",
            f"¿Está seguro de aumentar el stock de TODOS los productos en {quantity} unidades?\n\n"
            f"Esta acción afectará a todos los productos del sistema.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        session = get_session()
        try:
            products = session.query(Product).all()
            
            if not products:
                QMessageBox.information(self, "Info", "No hay productos en el sistema")
                return
            
            updated_count = 0
            for product in products:
                previous_stock = product.stock
                product.stock += quantity
                
                # Registrar movimiento de inventario
                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type=MovementType.ENTRY,
                    quantity=quantity,
                    previous_stock=previous_stock,
                    new_stock=product.stock,
                    reason=f"{reason} - Aumento masivo"
                )
                session.add(movement)
                updated_count += 1
            
            session.commit()
            
            QMessageBox.information(
                self,
                "✅ Éxito",
                f"Stock aumentado correctamente.\n\n"
                f"Productos afectados: {updated_count}\n"
                f"Cantidad agregada a cada uno: {quantity}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al aumentar stock: {str(e)}")
        finally:
            close_session()

