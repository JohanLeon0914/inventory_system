"""
Vista de Egresos - Gestión de salidas de productos y materias primas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox, QHeaderView, QGroupBox,
    QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from config.database import get_session, close_session
from models import (
    Expense, ExpenseType, ExpenseReason, Product, RawMaterial,
    InventoryMovement, MovementType, RawMaterialMovement, RawMaterialMovementType,
    ProductMaterial
)
from datetime import datetime

class ExpensesView(QWidget):
    """Vista principal de egresos"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_expenses()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        title = QLabel("📤 Egresos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón nuevo egreso
        btn_new_expense = QPushButton("➕ Nuevo Egreso")
        btn_new_expense.setFixedHeight(40)
        btn_new_expense.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        btn_new_expense.clicked.connect(self.new_expense)
        header_layout.addWidget(btn_new_expense)
        
        layout.addLayout(header_layout)
        
        # Tabla de egresos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Producto/Materia Prima", "Cantidad", "Razón", "Notas", "Acciones"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 100)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #0f172a;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_expenses(self):
        """Carga los egresos desde la base de datos"""
        session = get_session()
        try:
            expenses = session.query(Expense).order_by(Expense.created_at.desc()).all()
            
            self.table.setRowCount(len(expenses))
            
            for row, expense in enumerate(expenses):
                # Fecha
                date_str = expense.created_at.strftime("%Y-%m-%d %H:%M")
                self.table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Tipo
                self.table.setItem(row, 1, QTableWidgetItem(expense.expense_type.value))
                
                # Producto/Materia Prima
                item_name = expense.product.name if expense.product else expense.raw_material.name
                self.table.setItem(row, 2, QTableWidgetItem(item_name))
                
                # Cantidad
                qty_item = QTableWidgetItem(f"{expense.quantity}")
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, qty_item)
                
                # Razón
                self.table.setItem(row, 4, QTableWidgetItem(expense.reason.value))
                
                # Notas
                notes = expense.notes if expense.notes else "-"
                self.table.setItem(row, 5, QTableWidgetItem(notes))
                
                # Botón eliminar
                btn_delete = QPushButton("🗑️ Eliminar")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #ef4444;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #dc2626;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, e=expense: self.delete_expense(e))
                self.table.setCellWidget(row, 6, btn_delete)
                
                self.table.setRowHeight(row, 50)
        
        finally:
            close_session()
    
    def new_expense(self):
        """Abre el diálogo para crear un nuevo egreso"""
        dialog = NewExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_expenses()
    
    def delete_expense(self, expense):
        """Elimina un egreso (NO devuelve inventario, es solo registro)"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar este registro de egreso?\n\n"
            f"NOTA: Esto NO devolverá el inventario, solo eliminará el registro.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                expense_to_delete = session.query(Expense).filter_by(id=expense.id).first()
                session.delete(expense_to_delete)
                session.commit()
                QMessageBox.information(self, "Éxito", "Registro de egreso eliminado")
                self.load_expenses()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            finally:
                close_session()


class NewExpenseDialog(QDialog):
    """Diálogo para registrar un nuevo egreso"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Egreso")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        # Establecer estilos para el diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-weight: bold;
            }
            QComboBox, QDoubleSpinBox, QTextEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6b7280;
                margin-right: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form = QFormLayout()
        
        # Tipo de egreso
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(35)
        self.type_combo.addItem("Producto", ExpenseType.PRODUCT)
        self.type_combo.addItem("Materia Prima", ExpenseType.RAW_MATERIAL)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form.addRow("Tipo:", self.type_combo)
        
        # Item (producto o materia prima)
        self.item_combo = QComboBox()
        self.item_combo.setMinimumHeight(35)
        form.addRow("Item:", self.item_combo)
        
        # Cantidad
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.01)
        self.quantity_spin.setMaximum(999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setMinimumHeight(35)
        form.addRow("Cantidad:", self.quantity_spin)
        
        # Razón
        self.reason_combo = QComboBox()
        self.reason_combo.setMinimumHeight(35)
        for reason in ExpenseReason:
            self.reason_combo.addItem(reason.value, reason)
        form.addRow("Razón:", self.reason_combo)
        
        # Notas
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        self.notes_text.setPlaceholderText("Descripción adicional (opcional)...")
        form.addRow("Notas:", self.notes_text)
        
        layout.addLayout(form)
        
        # Stock actual
        self.stock_label = QLabel("")
        self.stock_label.setStyleSheet("font-weight: bold; color: #0f172a; padding: 10px; background-color: #f1f5f9; border-radius: 4px;")
        layout.addWidget(self.stock_label)
        
        # Conectar señal para actualizar stock
        self.item_combo.currentIndexChanged.connect(self.update_stock_label)
        
        # Botones
        buttons = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Registrar Egreso")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        btn_save.clicked.connect(self.save_expense)
        
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)
        
        layout.addLayout(buttons)
        
        # Cargar productos inicialmente
        self.on_type_changed()
    
    def on_type_changed(self):
        """Actualiza la lista de items según el tipo seleccionado"""
        self.item_combo.clear()
        expense_type = self.type_combo.currentData()
        
        session = get_session()
        try:
            if expense_type == ExpenseType.PRODUCT:
                products = session.query(Product).all()
                for product in products:
                    self.item_combo.addItem(f"{product.name} (Stock: {product.stock})", product.id)
            else:  # RAW_MATERIAL
                raw_materials = session.query(RawMaterial).all()
                for material in raw_materials:
                    self.item_combo.addItem(f"{material.name} (Stock: {material.stock})", material.id)
        finally:
            close_session()
        
        self.update_stock_label()
    
    def update_stock_label(self):
        """Actualiza la etiqueta de stock actual"""
        if self.item_combo.count() == 0:
            self.stock_label.setText("")
            return
        
        item_id = self.item_combo.currentData()
        expense_type = self.type_combo.currentData()
        
        session = get_session()
        try:
            if expense_type == ExpenseType.PRODUCT:
                item = session.query(Product).filter_by(id=item_id).first()
            else:
                item = session.query(RawMaterial).filter_by(id=item_id).first()
            
            if item:
                self.stock_label.setText(f"📦 Stock actual: {item.stock}")
        finally:
            close_session()
    
    def save_expense(self):
        """Guarda el egreso y actualiza el inventario"""
        if self.item_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No hay items disponibles")
            return
        
        item_id = self.item_combo.currentData()
        expense_type = self.type_combo.currentData()
        quantity = self.quantity_spin.value()
        reason = self.reason_combo.currentData()
        notes = self.notes_text.toPlainText().strip()
        
        session = get_session()
        try:
            # Verificar stock disponible
            if expense_type == ExpenseType.PRODUCT:
                item = session.query(Product).filter_by(id=item_id).first()
            else:
                item = session.query(RawMaterial).filter_by(id=item_id).first()
            
            if not item:
                QMessageBox.warning(self, "Error", "Item no encontrado")
                return
            
            if item.stock < quantity:
                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f"Stock actual: {item.stock}\nCantidad solicitada: {quantity}\n\n"
                    f"No hay suficiente stock disponible."
                )
                return
            
            # Crear egreso
            expense = Expense()
            expense.expense_type = expense_type
            expense.reason = reason
            expense.quantity = quantity
            expense.notes = notes if notes else None
            
            if expense_type == ExpenseType.PRODUCT:
                expense.product_id = item_id
                
                # Descontar del inventario de productos
                previous_stock = item.stock
                item.stock -= quantity
                
                # Registrar movimiento de inventario
                movement = InventoryMovement(
                    product_id=item_id,
                    movement_type=MovementType.EXIT,
                    quantity=-quantity,
                    previous_stock=previous_stock,
                    new_stock=item.stock,
                    reason=f"Egreso: {reason.value}"
                )
                session.add(movement)
                
                # Descontar materia prima utilizada en el producto
                product_materials = session.query(ProductMaterial).filter_by(product_id=item_id).all()
                for product_material in product_materials:
                    raw_material = product_material.raw_material
                    # Calcular cantidad de materia prima a descontar
                    material_quantity = product_material.quantity_needed * quantity
                    
                    # Verificar que hay suficiente materia prima
                    if raw_material.stock < material_quantity:
                        QMessageBox.warning(
                            self,
                            "Stock insuficiente de materia prima",
                            f"No hay suficiente stock de '{raw_material.name}'\n"
                            f"Stock disponible: {raw_material.stock}\n"
                            f"Cantidad necesaria: {material_quantity}"
                        )
                        return
                    
                    # Descontar materia prima
                    previous_material_stock = raw_material.stock
                    raw_material.stock -= material_quantity
                    
                    # Registrar movimiento de materia prima
                    material_movement = RawMaterialMovement(
                        raw_material_id=raw_material.id,
                        movement_type=RawMaterialMovementType.WASTE,
                        quantity=-material_quantity,
                        reference=f"Egreso-Producto-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        reason=f"Egreso de producto '{item.name}': {reason.value}"
                    )
                    session.add(material_movement)
            else:
                expense.raw_material_id = item_id
                
                # Descontar del inventario de materias primas
                item.stock -= quantity
                
                # Registrar movimiento de materia prima
                movement = RawMaterialMovement(
                    raw_material_id=item_id,
                    movement_type=RawMaterialMovementType.WASTE,
                    quantity=-quantity,
                    reference=f"Egreso-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    reason=f"Egreso: {reason.value}"
                )
                session.add(movement)
            
            session.add(expense)
            session.commit()
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Egreso registrado correctamente\n\n"
                f"Item: {item.name}\n"
                f"Cantidad: {quantity}\n"
                f"Stock restante: {item.stock}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar egreso: {str(e)}")
        finally:
            close_session()

