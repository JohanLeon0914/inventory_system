"""
Vista de Egresos - Gestión de salidas de productos y materias primas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox, QHeaderView, QGroupBox,
    QDateEdit, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from config.database import get_session, close_session
from models import (
    Expense, ExpenseType, ExpenseReason, Product, RawMaterial,
    InventoryMovement, MovementType, RawMaterialMovement, RawMaterialMovementType,
    ProductMaterial, PaymentMethod
)
from PyQt6.QtWidgets import QLineEdit
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
        
        # Crear tabs para separar tipos de egresos
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                color: #0f172a;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
            }
        """)
        
        # Tab 1: Efectivo/Transferencias (primero)
        self.cash_tab = QWidget()
        cash_layout = QVBoxLayout(self.cash_tab)
        self.cash_table = self.create_table(["Fecha", "Monto", "Método Pago", "Razón", "Destinatario", "Autorizado", "Notas", "Acciones"])
        cash_layout.addWidget(self.cash_table)
        self.tabs.addTab(self.cash_tab, "💵 Efectivo/Transferencias")
        
        # Tab 2: Productos y Materias Primas
        self.inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(self.inventory_tab)
        self.inventory_table = self.create_table(["Fecha", "Tipo", "Producto/Materia Prima", "Cantidad", "Monto", "Razón", "Destinatario", "Autorizado", "Notas", "Acciones"])
        inventory_layout.addWidget(self.inventory_table)
        self.tabs.addTab(self.inventory_tab, "📦 Inventario")
        
        layout.addWidget(self.tabs)
    
    def create_table(self, headers):
        """Crea y configura una tabla con los headers especificados"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        header = table.horizontalHeader()
        for i in range(len(headers)):
            if headers[i] == "Acciones":
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                table.setColumnWidth(i, 100)
            elif headers[i] in ["Fecha", "Cantidad", "Monto", "Tipo", "Autorizado"]:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #0f172a;
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
        
        return table
    
    def load_expenses(self):
        """Carga los egresos desde la base de datos y los separa por tipo"""
        session = get_session()
        try:
            expenses = session.query(Expense).order_by(Expense.created_at.desc()).all()
            
            # Separar egresos
            inventory_expenses = [e for e in expenses if e.expense_type != ExpenseType.CASH]
            cash_expenses = [e for e in expenses if e.expense_type == ExpenseType.CASH]
            
            # Cargar tabla de inventario
            self.load_inventory_table(inventory_expenses)
            
            # Cargar tabla de efectivo
            self.load_cash_table(cash_expenses)
        
        finally:
            close_session()
    
    def load_inventory_table(self, expenses):
        """Carga egresos de inventario en la tabla correspondiente"""
        self.inventory_table.setRowCount(len(expenses))
        
        for row, expense in enumerate(expenses):
            col = 0
            # Fecha
            date_str = expense.created_at.strftime("%Y-%m-%d %H:%M")
            self.inventory_table.setItem(row, col, QTableWidgetItem(date_str))
            col += 1
            
            # Tipo
            self.inventory_table.setItem(row, col, QTableWidgetItem(expense.expense_type.value))
            col += 1
            
            # Producto/Materia Prima
            item_name = expense.product.name if expense.product else expense.raw_material.name
            self.inventory_table.setItem(row, col, QTableWidgetItem(item_name))
            col += 1
            
            # Cantidad
            qty_item = QTableWidgetItem(f"{expense.quantity}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inventory_table.setItem(row, col, qty_item)
            col += 1
            
            # Monto
            amount_text = f"${expense.amount:,.2f}" if expense.amount else "-"
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.inventory_table.setItem(row, col, amount_item)
            col += 1
            
            # Razón
            self.inventory_table.setItem(row, col, QTableWidgetItem(expense.reason.value))
            col += 1
            
            # Destinatario
            recipient = expense.recipient if expense.recipient else "-"
            self.inventory_table.setItem(row, col, QTableWidgetItem(recipient))
            col += 1
            
            # Autorizado
            authorized_text = "✓ Sí" if expense.is_authorized else "✗ No"
            authorized_item = QTableWidgetItem(authorized_text)
            if expense.is_authorized:
                authorized_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                authorized_item.setForeground(Qt.GlobalColor.red)
            authorized_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inventory_table.setItem(row, col, authorized_item)
            col += 1
            
            # Notas
            notes = expense.notes if expense.notes else "-"
            self.inventory_table.setItem(row, col, QTableWidgetItem(notes))
            col += 1
            
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
            self.inventory_table.setCellWidget(row, col, btn_delete)
            
            self.inventory_table.setRowHeight(row, 50)
    
    def load_cash_table(self, expenses):
        """Carga egresos de efectivo en la tabla correspondiente"""
        self.cash_table.setRowCount(len(expenses))
        
        for row, expense in enumerate(expenses):
            col = 0
            # Fecha
            date_str = expense.created_at.strftime("%Y-%m-%d %H:%M")
            self.cash_table.setItem(row, col, QTableWidgetItem(date_str))
            col += 1
            
            # Monto
            amount_text = f"${expense.amount:,.2f}" if expense.amount else "-"
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            amount_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.cash_table.setItem(row, col, amount_item)
            col += 1
            
            # Método de pago
            payment_method = expense.payment_method.value if expense.payment_method else "-"
            if expense.transfer_type:
                payment_method += f" ({expense.transfer_type})"
            self.cash_table.setItem(row, col, QTableWidgetItem(payment_method))
            col += 1
            
            # Razón
            self.cash_table.setItem(row, col, QTableWidgetItem(expense.reason.value))
            col += 1
            
            # Destinatario
            recipient = expense.recipient if expense.recipient else "-"
            self.cash_table.setItem(row, col, QTableWidgetItem(recipient))
            col += 1
            
            # Autorizado
            authorized_text = "✓ Sí" if expense.is_authorized else "✗ No"
            authorized_item = QTableWidgetItem(authorized_text)
            if expense.is_authorized:
                authorized_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                authorized_item.setForeground(Qt.GlobalColor.red)
            authorized_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cash_table.setItem(row, col, authorized_item)
            col += 1
            
            # Notas
            notes = expense.notes if expense.notes else "-"
            self.cash_table.setItem(row, col, QTableWidgetItem(notes))
            col += 1
            
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
            self.cash_table.setCellWidget(row, col, btn_delete)
            
            self.cash_table.setRowHeight(row, 50)
    
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
            QComboBox QAbstractItemView {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                selection-background-color: #3b82f6;
                selection-color: white;
                outline: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form = QFormLayout()
        
        # Tipo de egreso
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(35)
        self.type_combo.addItem("Efectivo", ExpenseType.CASH)
        self.type_combo.addItem("Producto", ExpenseType.PRODUCT)
        self.type_combo.addItem("Materia Prima", ExpenseType.RAW_MATERIAL)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form.addRow("Tipo:", self.type_combo)
        
        # Item (producto o materia prima) - solo visible para Producto y Materia Prima
        self.item_label = QLabel("Item:")
        self.item_label.setStyleSheet("color: #0f172a; font-weight: bold;")
        self.item_combo = QComboBox()
        self.item_combo.setMinimumHeight(35)
        form.addRow(self.item_label, self.item_combo)
        
        # Cantidad
        self.quantity_label = QLabel("Cantidad:")
        self.quantity_label.setStyleSheet("color: #0f172a; font-weight: bold;")
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.01)
        self.quantity_spin.setMaximum(999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setMinimumHeight(35)
        form.addRow(self.quantity_label, self.quantity_spin)
        
        # Razón
        self.reason_combo = QComboBox()
        self.reason_combo.setMinimumHeight(35)
        for reason in ExpenseReason:
            self.reason_combo.addItem(reason.value, reason)
        form.addRow("Razón:", self.reason_combo)
        
        # Método de pago
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(35)
        self.payment_method_combo.addItem("No aplica", None)
        for method in PaymentMethod:
            self.payment_method_combo.addItem(method.value, method)
        self.payment_method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        self.payment_method_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #64748b;
                margin-right: 5px;
            }
        """)
        form.addRow("Método de Pago:", self.payment_method_combo)
        
        # Tipo de transferencia (oculto inicialmente)
        self.transfer_type_label = QLabel("Tipo de Transferencia:")
        self.transfer_type_label.setStyleSheet("color: #0f172a; font-weight: bold;")
        self.transfer_type_label.setVisible(False)
        
        self.transfer_type_combo = QComboBox()
        self.transfer_type_combo.setMinimumHeight(35)
        self.transfer_type_combo.addItems(["Nequi", "Daviplata", "Bancolombia", "Otro"])
        self.transfer_type_combo.setVisible(False)
        self.transfer_type_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #64748b;
                margin-right: 5px;
            }
        """)
        self.transfer_type_combo.currentIndexChanged.connect(self.on_transfer_type_changed)
        form.addRow(self.transfer_type_label, self.transfer_type_combo)
        
        # Campo para "Otro" tipo de transferencia
        self.other_transfer_label = QLabel("Especifique:")
        self.other_transfer_label.setStyleSheet("color: #0f172a; font-weight: bold;")
        self.other_transfer_label.setVisible(False)
        
        self.other_transfer_input = QLineEdit()
        self.other_transfer_input.setMinimumHeight(35)
        self.other_transfer_input.setPlaceholderText("Ej: Paypal, Bitcoin, etc.")
        self.other_transfer_input.setVisible(False)
        self.other_transfer_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form.addRow(self.other_transfer_label, self.other_transfer_input)
        
        # Destinatario
        self.recipient_input = QLineEdit()
        self.recipient_input.setMinimumHeight(35)
        self.recipient_input.setPlaceholderText("Nombre del destinatario o descripción")
        self.recipient_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form.addRow("Destinatario:", self.recipient_input)
        
        # Autorizado
        self.authorized_checkbox = QCheckBox("¿Está autorizado?")
        self.authorized_checkbox.setStyleSheet("""
            QCheckBox {
                color: #0f172a;
                font-weight: bold;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #10b981;
                border-color: #10b981;
            }
        """)
        form.addRow("", self.authorized_checkbox)
        
        # Monto/Valor del egreso (para todos los tipos)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMinimum(0.00)
        self.amount_spin.setMaximum(999999999.99)
        self.amount_spin.setValue(0.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$ ")
        self.amount_spin.setMinimumHeight(35)
        self.amount_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                color: #0f172a;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QDoubleSpinBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form.addRow("Monto del Egreso:", self.amount_spin)
        
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
        expense_type = self.type_combo.currentData()
        
        # Si es efectivo, ocultar campos relacionados con inventario
        is_cash = expense_type == ExpenseType.CASH
        
        self.item_label.setVisible(not is_cash)
        self.item_combo.setVisible(not is_cash)
        self.quantity_label.setVisible(not is_cash)
        self.quantity_spin.setVisible(not is_cash)
        self.stock_label.setVisible(not is_cash)
        
        # Si es efectivo, ocultar también las notas temporariamente
        # (las notas estarán visibles pero no el stock)
        
        if is_cash:
            # Limpiar el combo si es efectivo
            self.item_combo.clear()
            return
        
        # Si no es efectivo, cargar items normalmente
        self.item_combo.clear()
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
    
    def on_payment_method_changed(self):
        """Maneja el cambio en el método de pago"""
        current_method = self.payment_method_combo.currentData()
        
        # Mostrar campos de transferencia solo si se selecciona Transferencia
        is_transfer = current_method == PaymentMethod.TRANSFER
        
        self.transfer_type_label.setVisible(is_transfer)
        self.transfer_type_combo.setVisible(is_transfer)
        
        # Si no es transferencia, ocultar también el campo "Otro"
        if not is_transfer:
            self.other_transfer_label.setVisible(False)
            self.other_transfer_input.setVisible(False)
        else:
            # Si es transferencia, verificar si seleccionaron "Otro"
            self.on_transfer_type_changed()
    
    def on_transfer_type_changed(self):
        """Maneja el cambio en el tipo de transferencia"""
        # Mostrar campo "Otro" solo si se selecciona "Otro"
        show_other = self.transfer_type_combo.currentText() == "Otro"
        self.other_transfer_label.setVisible(show_other)
        self.other_transfer_input.setVisible(show_other)
        
        # Limpiar el campo si se cambia a otra opción
        if not show_other:
            self.other_transfer_input.clear()
    
    def get_transfer_type(self):
        """Obtiene el tipo de transferencia según la selección"""
        current_method = self.payment_method_combo.currentData()
        
        if current_method != PaymentMethod.TRANSFER:
            return None
        
        transfer_type = self.transfer_type_combo.currentText()
        if transfer_type == "Otro":
            # Usar el valor del campo de texto si está especificado
            other_text = self.other_transfer_input.text().strip()
            return other_text if other_text else "Otro"
        
        return transfer_type
    
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
        expense_type = self.type_combo.currentData()
        reason = self.reason_combo.currentData()
        notes = self.notes_text.toPlainText().strip()
        
        # Si es efectivo, no necesita item ni cantidad
        if expense_type == ExpenseType.CASH:
            # Validar que haya método de pago seleccionado
            payment_method = self.payment_method_combo.currentData()
            if not payment_method:
                QMessageBox.warning(self, "Error", "Debe seleccionar un método de pago para egreso en efectivo")
                return
            
            session = get_session()
            try:
                # Crear egreso de efectivo
                expense = Expense()
                expense.expense_type = expense_type
                expense.reason = reason
                expense.quantity = 0  # No aplica cantidad para efectivo
                expense.notes = notes if notes else None
                expense.payment_method = payment_method
                expense.transfer_type = self.get_transfer_type()
                expense.recipient = self.recipient_input.text().strip() if self.recipient_input.text().strip() else None
                expense.is_authorized = 1 if self.authorized_checkbox.isChecked() else 0
                expense.amount = self.amount_spin.value() if self.amount_spin.value() > 0 else None
                
                session.add(expense)
                session.commit()
                
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Egreso en efectivo registrado correctamente\n\n"
                    f"Método de pago: {payment_method.value}"
                )
                self.accept()
                return
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al guardar egreso: {str(e)}")
            finally:
                close_session()
            return
        
        # Para Producto y Materia Prima, validar items y stock
        if self.item_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No hay items disponibles")
            return
        
        item_id = self.item_combo.currentData()
        quantity = self.quantity_spin.value()
        
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
            expense.payment_method = self.payment_method_combo.currentData()  # Guardar método de pago
            expense.transfer_type = self.get_transfer_type()  # Guardar tipo de transferencia si aplica
            expense.recipient = self.recipient_input.text().strip() if self.recipient_input.text().strip() else None
            expense.is_authorized = 1 if self.authorized_checkbox.isChecked() else 0
            expense.amount = self.amount_spin.value() if self.amount_spin.value() > 0 else None
            
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

