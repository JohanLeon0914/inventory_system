"""
Vista de Completar Venta - Para finalizar la venta con los productos seleccionados
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QFormLayout, QGroupBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config.database import get_session, close_session
from models import Customer, PaymentMethod, SaleStatus

class CompleteSaleView(QWidget):
    """Vista para completar la venta con los productos seleccionados"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sale_items = []  # Items de la venta
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Completar Venta")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para volver a selección
        self.btn_back = QPushButton("← Volver a Productos")
        self.btn_back.setFixedHeight(45)
        self.btn_back.setFixedWidth(180)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.btn_back.clicked.connect(self.go_back_to_selection)
        header_layout.addWidget(self.btn_back)
        
        layout.addLayout(header_layout)
        
        # Información de la venta
        info_section = QGroupBox("Información de la Venta")
        info_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
            }
        """)
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        
        # Cliente
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(40)
        self.customer_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        info_layout.addRow("Cliente:", self.customer_combo)
        
        # Método de pago
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(40)
        for method in PaymentMethod:
            self.payment_method_combo.addItem(method.value, method)
        self.payment_method_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        info_layout.addRow("Método de Pago:", self.payment_method_combo)
        
        info_section.setLayout(info_layout)
        layout.addWidget(info_section)
        
        # Tabla de items de la venta
        items_section = QGroupBox("Items de la Venta")
        items_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
            }
        """)
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal", "Acciones"])
        self.items_table.horizontalHeader().setStretchLastSection(False)
        self.items_table.setMinimumHeight(300)
        self.items_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                font-size: 13px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
            }
        """)
        
        # Configurar anchos de columnas
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Producto
        self.items_table.setColumnWidth(1, 120)  # Precio
        self.items_table.setColumnWidth(2, 100)  # Cantidad
        self.items_table.setColumnWidth(3, 120)  # Subtotal
        self.items_table.setColumnWidth(4, 100)  # Acciones
        
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.items_table.setAlternatingRowColors(True)
        
        items_layout.addWidget(self.items_table)
        items_section.setLayout(items_layout)
        layout.addWidget(items_section)
        
        # Totales y pago
        totals_section = QGroupBox("Totales y Pago")
        totals_section.setMaximumHeight(200)
        totals_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
            }
        """)
        totals_layout = QFormLayout()
        totals_layout.setSpacing(8)
        totals_layout.setContentsMargins(15, 10, 15, 10)
        
        # Total
        total_label_title = QLabel("TOTAL:")
        total_label_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        
        self.total_label = QLabel("$0")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981; background-color: #f0fdf4; padding: 8px; border-radius: 6px;")
        totals_layout.addRow(total_label_title, self.total_label)
        
        # Pago con
        pago_label = QLabel("Pago con:")
        pago_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        
        self.cash_given_edit = QLineEdit()
        self.cash_given_edit.setPlaceholderText("Ingrese el monto recibido")
        self.cash_given_edit.setMinimumHeight(40)
        self.cash_given_edit.setMinimumWidth(150)
        self.cash_given_edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px; 
                padding: 8px; 
                background-color: #fef3c7; 
                border: 2px solid #fbbf24; 
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #d97706;
                background-color: #fef9c3;
            }
        """)
        self.cash_given_edit.textChanged.connect(self.on_payment_changed)
        totals_layout.addRow(pago_label, self.cash_given_edit)
        
        # Cambio
        cambio_label = QLabel("Cambio:")
        cambio_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        
        self.change_label = QLabel("")
        self.change_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #64748b; background-color: #eff6ff; padding: 8px; border-radius: 6px; min-height: 40px;")
        totals_layout.addRow(cambio_label, self.change_label)
        
        totals_section.setLayout(totals_layout)
        layout.addWidget(totals_section)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        
        btn_cancel = QPushButton("Cancelar Venta")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setMinimumWidth(140)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_cancel.clicked.connect(self.cancel_sale)
        
        btn_complete = QPushButton("Completar Venta")
        btn_complete.setMinimumHeight(45)
        btn_complete.setMinimumWidth(160)
        btn_complete.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_complete.clicked.connect(self.complete_sale)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_complete)
        
        layout.addLayout(buttons_layout)
    
    def load_customers(self):
        """Carga los clientes disponibles"""
        session = get_session()
        try:
            self.customer_combo.addItem("Cliente General", None)
            customers = session.query(Customer).all()
            for customer in customers:
                self.customer_combo.addItem(customer.name, customer.id)
        finally:
            close_session()
    
    def set_sale_items(self, selected_products):
        """Establece los productos seleccionados como items de la venta"""
        self.sale_items = []
        for product_data in selected_products:
            item_data = {
                'product_id': product_data['product_id'],
                'product_name': product_data['product_name'],
                'unit_price': product_data['unit_price'],
                'quantity': product_data['quantity'],
                'subtotal': product_data['subtotal'],
                'stock': product_data['stock']
            }
            self.sale_items.append(item_data)
        
        self.update_items_table()
        self.calculate_total()
    
    def update_items_table(self):
        """Actualiza la tabla de items"""
        self.items_table.setRowCount(len(self.sale_items))
        
        for row, item in enumerate(self.sale_items):
            # Producto
            product_item = QTableWidgetItem(item['product_name'])
            product_item.setFont(QFont("Arial", 12, QFont.Weight.Medium))
            self.items_table.setItem(row, 0, product_item)
            
            # Precio unitario
            unit_price = item['unit_price']
            if unit_price == int(unit_price):
                price_text = f"${int(unit_price):,}"
            else:
                price_text = f"${unit_price:.2f}"
            price_item = QTableWidgetItem(price_text)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFont(QFont("Arial", 11))
            self.items_table.setItem(row, 1, price_item)
            
            # Cantidad (editable)
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            qty_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            qty_item.setFlags(qty_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.items_table.setItem(row, 2, qty_item)
            
            # Subtotal
            subtotal = item['subtotal']
            if subtotal == int(subtotal):
                subtotal_text = f"${int(subtotal):,}"
            else:
                subtotal_text = f"${subtotal:.2f}"
            subtotal_item = QTableWidgetItem(subtotal_text)
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.items_table.setItem(row, 3, subtotal_item)
            
            # Botón reducir cantidad
            btn_reduce = QPushButton("➖ -1")
            btn_reduce.setFixedHeight(35)
            btn_reduce.setFixedWidth(90)
            btn_reduce.setStyleSheet("""
                QPushButton {
                    background-color: #f59e0b;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d97706;
                }
            """)
            btn_reduce.clicked.connect(lambda checked, r=row: self.reduce_item_quantity(r))
            self.items_table.setCellWidget(row, 4, btn_reduce)
            
            self.items_table.setRowHeight(row, 50)
        
        # Conectar señal para detectar cambios en cantidad
        self.items_table.itemChanged.connect(self.on_quantity_changed)
    
    def reduce_item_quantity(self, row):
        """Reduce la cantidad de un item en 1, o lo elimina si llega a 0"""
        if row < len(self.sale_items):
            if self.sale_items[row]['quantity'] > 1:
                self.sale_items[row]['quantity'] -= 1
                self.sale_items[row]['subtotal'] = self.sale_items[row]['quantity'] * self.sale_items[row]['unit_price']
            else:
                self.sale_items.pop(row)
            self.update_items_table()
            self.calculate_total()
    
    def on_quantity_changed(self, item):
        """Maneja el cambio manual de cantidad en la tabla"""
        if item.column() == 2:  # Columna de cantidad
            row = item.row()
            if row < len(self.sale_items):
                try:
                    new_quantity = int(item.text())
                    if new_quantity > 0:
                        # Verificar stock disponible
                        if new_quantity > self.sale_items[row]['stock']:
                            QMessageBox.warning(self, "Stock insuficiente", 
                                f"Solo hay {self.sale_items[row]['stock']} unidades disponibles")
                            item.setText(str(self.sale_items[row]['quantity']))
                            return
                        
                        self.sale_items[row]['quantity'] = new_quantity
                        self.sale_items[row]['subtotal'] = new_quantity * self.sale_items[row]['unit_price']
                        self.calculate_total()
                        # Actualizar subtotal en la tabla
                        subtotal = self.sale_items[row]['subtotal']
                        if subtotal == int(subtotal):
                            subtotal_text = f"${int(subtotal):,}"
                        else:
                            subtotal_text = f"${subtotal:.2f}"
                        
                        subtotal_item = QTableWidgetItem(subtotal_text)
                        subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        subtotal_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                        self.items_table.setItem(row, 3, subtotal_item)
                    elif new_quantity == 0:
                        # Eliminar el item si cantidad es 0
                        self.sale_items.pop(row)
                        self.update_items_table()
                        self.calculate_total()
                    else:
                        # Restaurar valor anterior si es negativo
                        item.setText(str(self.sale_items[row]['quantity']))
                except ValueError:
                    # Restaurar valor anterior si no es un número válido
                    item.setText(str(self.sale_items[row]['quantity']))
    
    def calculate_total(self):
        """Calcula los totales"""
        total = sum(item['subtotal'] for item in self.sale_items)
        
        if total == int(total):
            formatted_total = f"${int(total):,}"
        else:
            formatted_total = f"${total:,.2f}"
        
        self.total_label.setText(formatted_total)
        self.update_change()
    
    def on_payment_changed(self):
        """Maneja el cambio en el campo de pago"""
        # Auto-formatear el número mientras se escribe
        text = self.cash_given_edit.text()
        if text:
            # Limpiar caracteres no numéricos excepto punto
            clean_text = ''.join(c for c in text if c.isdigit() or c == '.')
            if clean_text:
                try:
                    # Convertir a float y formatear
                    value = float(clean_text)
                    if value == int(value):
                        formatted = f"{int(value):,}"
                    else:
                        formatted = f"{value:,.2f}"
                    if self.cash_given_edit.text() != formatted:
                        cursor_pos = self.cash_given_edit.cursorPosition()
                        self.cash_given_edit.setText(formatted)
                        self.cash_given_edit.setCursorPosition(min(cursor_pos, len(formatted)))
                except ValueError:
                    pass
        self.update_change()
    
    def update_change(self):
        """Actualiza el cambio"""
        try:
            total = sum(item['subtotal'] for item in self.sale_items)
            
            payment_text = self.cash_given_edit.text().strip()
            if not payment_text:
                cash_given = 0
            else:
                clean_text = payment_text.replace('$', '').replace(',', '').strip()
                try:
                    cash_given = float(clean_text) if clean_text else 0
                except ValueError:
                    cash_given = 0
            
            if cash_given == 0:
                self.change_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #64748b; background-color: #eff6ff; padding: 8px; border-radius: 6px; min-height: 40px;")
                self.change_label.setText("")
            else:
                change = cash_given - total
                color = "#10b981" if change >= 0 else "#ef4444"
                bg_color = "#f0fdf4" if change >= 0 else "#fee2e2"
                
                if change == int(change):
                    formatted_change = f"${int(change):,}"
                else:
                    formatted_change = f"${change:,.2f}"
                
                self.change_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; background-color: {bg_color}; padding: 8px; border-radius: 6px; min-height: 40px;")
                self.change_label.setText(formatted_change)
        except Exception:
            pass
    
    def go_back_to_selection(self):
        """Regresa a la vista de selección de productos"""
        if hasattr(self.parent(), 'show_product_selection_view'):
            self.parent().show_product_selection_view()
        elif hasattr(self, 'on_go_back'):
            self.on_go_back()
    
    def cancel_sale(self):
        """Cancela la venta"""
        reply = QMessageBox.question(
            self,
            "Cancelar Venta",
            "¿Está seguro de cancelar esta venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.go_back_to_selection()
    
    def complete_sale(self):
        """Completa la venta"""
        if not self.sale_items:
            QMessageBox.warning(self, "Error", "No hay productos en la venta")
            return
        
        # Verificar que todos los items tengan cantidad > 0
        for item in self.sale_items:
            if item['quantity'] <= 0:
                QMessageBox.warning(self, "Error", "Todos los productos deben tener cantidad mayor a 0")
                return
        
        # Emitir señal o llamar callback para completar la venta
        if hasattr(self.parent(), 'complete_sale'):
            self.parent().complete_sale(self.sale_items, self.customer_combo.currentData(), self.payment_method_combo.currentData())
        elif hasattr(self, 'on_complete_sale'):
            self.on_complete_sale(self.sale_items, self.customer_combo.currentData(), self.payment_method_combo.currentData())
    
    def get_sale_items(self):
        """Retorna los items de la venta"""
        return self.sale_items.copy()
