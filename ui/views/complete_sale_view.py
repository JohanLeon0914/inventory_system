"""
Vista de Completar Venta - Para finalizar la venta con los productos seleccionados
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QFormLayout, QGroupBox, QHeaderView, QMessageBox, QDoubleSpinBox, QScrollArea,
    QDialog
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
        # Estilos generales para asegurar que el texto sea visible y fondo blanco
        self.setStyleSheet("""
            QWidget {
                color: #0f172a;
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                background-color: transparent;
            }
            QDoubleSpinBox {
                color: #0f172a;
                background-color: white;
            }
            QLineEdit {
                color: #0f172a;
                background-color: white;
            }
        """)
        
        # Layout principal del widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setAutoFillBackground(True)
        
        # Crear un scroll area para todo el contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setAutoFillBackground(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar:horizontal {
                background-color: #f1f5f9;
                height: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #94a3b8;
            }
        """)
        
        # Widget contenedor para el scroll
        scroll_widget = QWidget()
        scroll_widget.setAutoFillBackground(True)
        scroll_widget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Completar Venta")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para volver a selección
        self.btn_back = QPushButton("← Volver a Productos")
        self.btn_back.setFixedHeight(36)
        self.btn_back.setFixedWidth(170)
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
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
                background-color: white;
            }
        """)
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        
        # Cliente
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(32)
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
        info_layout.addRow("Cliente:", self.customer_combo)
        
        # Método de pago
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(32)
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
        self.payment_method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        info_layout.addRow("Método de Pago:", self.payment_method_combo)
        
        # Tipo de transferencia (oculto inicialmente)
        self.transfer_type_label = QLabel("Tipo de Transferencia:")
        self.transfer_type_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        self.transfer_type_label.setVisible(False)
        
        self.transfer_type_combo = QComboBox()
        self.transfer_type_combo.setMinimumHeight(32)
        self.transfer_type_combo.addItems(["Nequi", "Daviplata", "Bancolombia", "Otro"])
        self.transfer_type_combo.setVisible(False)
        self.transfer_type_combo.setStyleSheet("""
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
        info_layout.addRow(self.transfer_type_label, self.transfer_type_combo)
        
        # Campo para "Otro" tipo de transferencia
        self.other_transfer_label = QLabel("Especifique:")
        self.other_transfer_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        self.other_transfer_label.setVisible(False)
        
        self.other_transfer_input = QLineEdit()
        self.other_transfer_input.setMinimumHeight(32)
        self.other_transfer_input.setPlaceholderText("Ej: Paypal, Bitcoin, etc.")
        self.other_transfer_input.setVisible(False)
        self.other_transfer_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        info_layout.addRow(self.other_transfer_label, self.other_transfer_input)
        
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
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
                background-color: white;
            }
        """)
        items_layout = QVBoxLayout()
        
        header_items_layout = QHBoxLayout()
        header_items_layout.setContentsMargins(0, 0, 0, 4)
        
        items_title = QLabel("Lista de productos agregados")
        items_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #0f172a;")
        header_items_layout.addWidget(items_title)
        header_items_layout.addStretch()
        
        self.items_full_view_btn = QPushButton("Ver en ventana dedicada")
        self.items_full_view_btn.setMinimumHeight(30)
        self.items_full_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.items_full_view_btn.clicked.connect(self.open_items_full_view)
        header_items_layout.addWidget(self.items_full_view_btn)
        
        items_layout.addLayout(header_items_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal", "Acciones"])
        # Ajustar ancho de columna de acciones para dos botones
        self.items_table.horizontalHeader().setStretchLastSection(False)
        self.items_table.setMinimumHeight(150)
        self.items_table.setMaximumHeight(300)
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
                color: #0f172a;
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
                color: #0f172a;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar:horizontal {
                background-color: #f1f5f9;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #94a3b8;
            }
        """)
        
        # Configurar anchos de columnas
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Producto
        self.items_table.setColumnWidth(1, 100)  # Precio
        self.items_table.setColumnWidth(2, 80)  # Cantidad
        self.items_table.setColumnWidth(3, 100)  # Subtotal
        self.items_table.setColumnWidth(4, 80)   # Acciones compactas
        
        # Configurar scroll
        self.items_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.items_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.items_table.setAlternatingRowColors(True)
        
        items_layout.addWidget(self.items_table)
        items_section.setLayout(items_layout)
        layout.addWidget(items_section)
        
        # Totales y pago
        totals_section = QGroupBox("Totales y Pago")
        totals_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0f172a;
                background-color: white;
            }
        """)
        totals_layout = QFormLayout()
        totals_layout.setSpacing(8)
        totals_layout.setContentsMargins(15, 10, 15, 10)
        
        # Subtotal
        subtotal_label_title = QLabel("Subtotal:")
        subtotal_label_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        
        self.subtotal_label = QLabel("$0")
        self.subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #64748b; background-color: #f8fafc; padding: 6px; border-radius: 4px;")
        totals_layout.addRow(subtotal_label_title, self.subtotal_label)
        
        # Impuesto
        tax_label = QLabel("Impuesto:")
        tax_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setMinimum(0)
        self.tax_input.setMaximum(999999.99)
        self.tax_input.setDecimals(2)
        self.tax_input.setPrefix("$ ")
        self.tax_input.setMinimumHeight(30)
        self.tax_input.setMinimumWidth(120)
        self.tax_input.setValue(0.0)
        self.tax_input.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 14px;
                padding: 4px;
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
            }
            QDoubleSpinBox:focus {
                border-color: #3b82f6;
            }
        """)
        self.tax_input.valueChanged.connect(self.calculate_total)
        totals_layout.addRow(tax_label, self.tax_input)
        
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
        self.cash_given_edit.setMinimumHeight(32)
        self.cash_given_edit.setMinimumWidth(120)
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
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setMinimumWidth(130)
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
        btn_complete.setMinimumHeight(38)
        btn_complete.setMinimumWidth(150)
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
        
        # Agregar el widget al scroll area
        scroll_area.setWidget(scroll_widget)
        
        # Agregar el scroll area al layout principal
        main_layout.addWidget(scroll_area)
    
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
            
            # Botones de acciones: sumar y restar
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            button_style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #0f172a;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 0;
                    min-width: 0;
                }
                QPushButton:hover {
                    color: #2563eb;
                }
            """
            
            # Botón sumar cantidad
            btn_increase = QPushButton("+")
            btn_increase.setFixedSize(24, 24)
            btn_increase.setStyleSheet(button_style)
            btn_increase.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_increase.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_increase.clicked.connect(lambda checked, r=row: self.increase_item_quantity(r))
            actions_layout.addWidget(btn_increase)
            
            # Botón reducir cantidad
            btn_reduce = QPushButton("-")
            btn_reduce.setFixedSize(24, 24)
            btn_reduce.setStyleSheet(button_style)
            btn_reduce.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_reduce.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_reduce.clicked.connect(lambda checked, r=row: self.reduce_item_quantity(r))
            actions_layout.addWidget(btn_reduce)
            
            self.items_table.setCellWidget(row, 4, actions_widget)
            
            # Aumentar altura de fila para íconos visibles
            self.items_table.setRowHeight(row, 50)
        
        # Conectar señal para detectar cambios en cantidad
        self.items_table.itemChanged.connect(self.on_quantity_changed)
    
    def increase_item_quantity(self, row):
        """Aumenta la cantidad de un item en 1"""
        if row < len(self.sale_items):
            # Verificar stock disponible
            if self.sale_items[row]['quantity'] >= self.sale_items[row]['stock']:
                QMessageBox.warning(self, "Stock insuficiente", 
                    f"Solo hay {self.sale_items[row]['stock']} unidades disponibles")
                return
            
            self.sale_items[row]['quantity'] += 1
            self.sale_items[row]['subtotal'] = self.sale_items[row]['quantity'] * self.sale_items[row]['unit_price']
            self.update_items_table()
            self.calculate_total()
    
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
        """Calcula los totales incluyendo impuesto"""
        subtotal = sum(item['subtotal'] for item in self.sale_items)
        tax = self.tax_input.value() if hasattr(self, 'tax_input') else 0.0
        total = subtotal + tax
        
        # Actualizar subtotal
        if subtotal == int(subtotal):
            formatted_subtotal = f"${int(subtotal):,}"
        else:
            formatted_subtotal = f"${subtotal:,.2f}"
        self.subtotal_label.setText(formatted_subtotal)
        
        # Actualizar total
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
            subtotal = sum(item['subtotal'] for item in self.sale_items)
            tax = self.tax_input.value() if hasattr(self, 'tax_input') else 0.0
            total = subtotal + tax
            
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
    
    def open_items_full_view(self):
        """Abre una ventana dedicada con todo el detalle de los productos."""
        if not self.sale_items:
            QMessageBox.information(self, "Sin productos", "Agregue productos antes de abrir la vista completa.")
            return
        dialog = ItemsFullViewDialog(self.sale_items, parent_view=self, parent=self)
        dialog.exec()
    
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
        
        # Obtener el impuesto
        tax_amount = self.tax_input.value() if hasattr(self, 'tax_input') else 0.0
        
        # Obtener tipo de transferencia si aplica
        transfer_type = self.get_transfer_type()
        
        # Emitir señal o llamar callback para completar la venta
        if hasattr(self.parent(), 'complete_sale'):
            self.parent().complete_sale(self.sale_items, self.customer_combo.currentData(), self.payment_method_combo.currentData(), tax_amount, transfer_type)
        elif hasattr(self, 'on_complete_sale'):
            self.on_complete_sale(self.sale_items, self.customer_combo.currentData(), self.payment_method_combo.currentData(), tax_amount, transfer_type)
    
    def get_sale_items(self):
        """Retorna los items de la venta"""
        return self.sale_items.copy()


class ItemsFullViewDialog(QDialog):
    """Dialogo dedicado para visualizar y ajustar los items de la venta."""
    def __init__(self, sale_items, parent_view=None, parent=None):
        super().__init__(parent)
        self.sale_items = sale_items or []
        self.parent_view = parent_view
        self._updating_table = False
        self.setWindowTitle("Productos de la Venta")
        self.setModal(True)
        self.resize(800, 500)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #0f172a; font-size: 14px; }
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                font-size: 13px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                font-weight: bold;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Vista completa de productos")
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: #0f172a;")
        layout.addWidget(title)
        
        subtitle = QLabel("Revise con comodidad todos los items antes de completar la venta.")
        subtitle.setStyleSheet("color: #475569; margin-bottom: 8px;")
        layout.addWidget(subtitle)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal", "Acciones"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 80)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked |
            QTableWidget.EditTrigger.EditKeyPressed |
            QTableWidget.EditTrigger.SelectedClicked
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)
        
        self.populate_items()
        self.table.itemChanged.connect(self.on_quantity_changed)
        
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)
    
    def populate_items(self):
        self._updating_table = True
        self.table.setRowCount(len(self.sale_items))
        for row, item in enumerate(self.sale_items):
            product_item = QTableWidgetItem(item.get('product_name', ''))
            product_item.setFont(QFont("Arial", 12, QFont.Weight.Medium))
            self.table.setItem(row, 0, product_item)
            
            unit_price = float(item.get('unit_price', 0))
            unit_text = f"${unit_price:,.2f}" if unit_price % 1 else f"${int(unit_price):,}"
            unit_item = QTableWidgetItem(unit_text)
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 1, unit_item)
            
            qty_item = QTableWidgetItem(str(int(item.get('quantity', 0))))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setFlags(qty_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, qty_item)
            
            subtotal = float(item.get('subtotal', 0))
            subtotal_text = f"${subtotal:,.2f}" if subtotal % 1 else f"${int(subtotal):,}"
            subtotal_item = QTableWidgetItem(subtotal_text)
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.table.setItem(row, 3, subtotal_item)
            
            # Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            button_style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #0f172a;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 0;
                    min-width: 0;
                }
                QPushButton:hover {
                    color: #2563eb;
                }
            """
            
            btn_increase = QPushButton("+")
            btn_increase.setFixedSize(24, 24)
            btn_increase.setStyleSheet(button_style)
            btn_increase.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_increase.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_increase.clicked.connect(lambda checked, r=row: self.change_quantity(r, +1))
            actions_layout.addWidget(btn_increase)
            
            btn_decrease = QPushButton("-")
            btn_decrease.setFixedSize(24, 24)
            btn_decrease.setStyleSheet(button_style)
            btn_decrease.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_decrease.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_decrease.clicked.connect(lambda checked, r=row: self.change_quantity(r, -1))
            actions_layout.addWidget(btn_decrease)
            
            self.table.setCellWidget(row, 4, actions_widget)
            self.table.setRowHeight(row, 48)
        self._updating_table = False
    
    def on_quantity_changed(self, item):
        if self._updating_table or item.column() != 2:
            return
        row = item.row()
        if row >= len(self.sale_items):
            return
        current_item = self.sale_items[row]
        try:
            new_quantity = int(item.text())
        except ValueError:
            self._restore_quantity(item, current_item['quantity'])
            return
        
        if new_quantity < 0:
            QMessageBox.warning(self, "Cantidad inválida", "La cantidad debe ser mayor o igual a 0.")
            self._restore_quantity(item, current_item['quantity'])
            return
        
        max_stock = current_item.get('stock', new_quantity)
        if new_quantity > max_stock:
            QMessageBox.warning(
                self,
                "Stock insuficiente",
                f"Solo hay {max_stock} unidades disponibles para {current_item.get('product_name', 'el producto')}."
            )
            self._restore_quantity(item, current_item['quantity'])
            return
        
        if new_quantity == 0:
            self.sale_items.pop(row)
            self.populate_items()
        else:
            current_item['quantity'] = new_quantity
            current_item['subtotal'] = new_quantity * float(current_item['unit_price'])
            self._updating_table = True
            subtotal = current_item['subtotal']
            subtotal_text = f"${subtotal:,.2f}" if subtotal % 1 else f"${int(subtotal):,}"
            self.table.item(row, 3).setText(subtotal_text)
            self._updating_table = False
        
        self._notify_parent_view()
    
    def _restore_quantity(self, table_item, quantity):
        self._updating_table = True
        table_item.setText(str(quantity))
        self._updating_table = False
    
    def _notify_parent_view(self):
        if self.parent_view:
            self.parent_view.update_items_table()
            self.parent_view.calculate_total()
    
    def change_quantity(self, row, delta):
        if self._updating_table or row >= len(self.sale_items):
            return
        current_item = self.sale_items[row]
        new_quantity = current_item['quantity'] + delta
        if new_quantity < 0:
            return
        if new_quantity == 0:
            self.sale_items.pop(row)
        else:
            max_stock = current_item.get('stock', new_quantity)
            if new_quantity > max_stock:
                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f"Solo hay {max_stock} unidades disponibles para {current_item.get('product_name', 'el producto')}."
                )
                return
            current_item['quantity'] = new_quantity
            current_item['subtotal'] = new_quantity * float(current_item['unit_price'])
        self.populate_items()
        self._notify_parent_view()
