"""
Vista de Inventario - Control y movimientos de inventario
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QComboBox, QHeaderView,
    QTextEdit, QDateEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QShowEvent
from datetime import datetime
from config.database import get_session, close_session
from models import Product, InventoryMovement, MovementType

class InventoryView(QWidget):
    """Vista para control de inventario"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Control de Inventario")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para ajustar inventario
        btn_adjust = QPushButton("Ajustar Inventario")
        btn_adjust.setFixedHeight(40)
        btn_adjust.clicked.connect(self.adjust_inventory)
        header_layout.addWidget(btn_adjust)
        
        layout.addLayout(header_layout)
        
        # Tabs / Secciones
        # Stock Actual
        stock_group = QGroupBox("Stock Actual de Productos")
        stock_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #0f172a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #0f172a;
            }
        """)
        stock_layout = QVBoxLayout()
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.search_products)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("color: #0f172a;")
        search_layout.addWidget(self.search_input)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_inventory)
        search_layout.addWidget(btn_refresh)
        
        stock_layout.addLayout(search_layout)
        
        # Tabla de stock
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "SKU", "Producto", "Categoría", "Stock", "Stock Mín.", "Estado"
        ])
        
        header = self.stock_table.horizontalHeader()
        # Configurar anchos fijos para columnas específicas
        self.stock_table.setColumnWidth(3, 80)   # Stock
        self.stock_table.setColumnWidth(4, 100)  # Stock Mín.
        self.stock_table.setColumnWidth(5, 100)  # Estado
        
        # Hacer que varias columnas se expandan proporcionalmente
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # SKU
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Producto
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Categoría
        
        self.stock_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.stock_table.verticalHeader().setVisible(False)
        
        # Asegurar que la tabla use todo el espacio disponible
        self.stock_table.horizontalHeader().setStretchLastSection(False)
        
        stock_layout.addWidget(self.stock_table)
        stock_group.setLayout(stock_layout)
        layout.addWidget(stock_group)
        
        # Historial de movimientos
        movements_group = QGroupBox("Historial de Movimientos (Últimos 50)")
        movements_layout = QVBoxLayout()
        
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(6)
        self.movements_table.setHorizontalHeaderLabels([
            "Fecha", "Producto", "Tipo", "Cantidad", "Razón", "Stock Resultante"
        ])
        
        header = self.movements_table.horizontalHeader()
        # Configurar anchos fijos para columnas específicas
        self.movements_table.setColumnWidth(3, 80)   # Cantidad
        self.movements_table.setColumnWidth(5, 130)  # Stock Resultante
        
        # Hacer que varias columnas se expandan proporcionalmente
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Fecha
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Producto
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Tipo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Razón
        
        self.movements_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.movements_table.verticalHeader().setVisible(False)
        self.movements_table.setMaximumHeight(300)
        
        # Asegurar que la tabla use todo el espacio disponible
        self.movements_table.horizontalHeader().setStretchLastSection(False)
        
        movements_layout.addWidget(self.movements_table)
        movements_group.setLayout(movements_layout)
        layout.addWidget(movements_group)
    
    def showEvent(self, event: QShowEvent):
        """Se ejecuta cuando la vista se muestra"""
        super().showEvent(event)
        # Recargar inventario cada vez que se muestra la vista
        self.load_inventory()
    
    def load_inventory(self):
        """Carga el inventario actual"""
        session = get_session()
        try:
            products = session.query(Product).all()
            
            self.stock_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # SKU
                self.stock_table.setItem(row, 0, QTableWidgetItem(product.sku))
                
                # Nombre
                self.stock_table.setItem(row, 1, QTableWidgetItem(product.name))
                
                # Categoría
                category = product.category.name if product.category else "-"
                self.stock_table.setItem(row, 2, QTableWidgetItem(category))
                
                # Stock
                stock_item = QTableWidgetItem(str(product.stock))
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stock_table.setItem(row, 3, stock_item)
                
                # Stock mínimo
                min_stock_item = QTableWidgetItem(str(product.min_stock))
                min_stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stock_table.setItem(row, 4, min_stock_item)
                
                # Estado
                if product.stock == 0:
                    status = "SIN STOCK"
                    color = Qt.GlobalColor.red
                elif product.is_low_stock:
                    status = "BAJO"
                    color = Qt.GlobalColor.darkYellow
                else:
                    status = "NORMAL"
                    color = Qt.GlobalColor.darkGreen
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(color)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stock_table.setItem(row, 5, status_item)
            
            # Cargar movimientos
            self.load_movements()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar inventario: {str(e)}")
        finally:
            close_session()
    
    def load_movements(self):
        """Carga el historial de movimientos"""
        session = get_session()
        try:
            movements = session.query(InventoryMovement).order_by(
                InventoryMovement.created_at.desc()
            ).limit(50).all()
            
            self.movements_table.setRowCount(len(movements))
            
            for row, movement in enumerate(movements):
                # Fecha
                date_str = movement.created_at.strftime("%d/%m/%Y %H:%M")
                self.movements_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Producto
                product_name = movement.product.name if movement.product else "Producto eliminado"
                self.movements_table.setItem(row, 1, QTableWidgetItem(product_name))
                
                # Tipo
                type_item = QTableWidgetItem(movement.movement_type.value)
                if movement.movement_type == MovementType.ENTRY:
                    type_item.setForeground(Qt.GlobalColor.darkGreen)
                elif movement.movement_type == MovementType.EXIT:
                    type_item.setForeground(Qt.GlobalColor.red)
                self.movements_table.setItem(row, 2, type_item)
                
                # Cantidad
                quantity_item = QTableWidgetItem(str(abs(movement.quantity)))
                quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.movements_table.setItem(row, 3, quantity_item)
                
                # Razón
                reason = movement.reason or "-"
                self.movements_table.setItem(row, 4, QTableWidgetItem(reason))
                
                # Stock resultante
                stock_item = QTableWidgetItem(str(movement.new_stock))
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.movements_table.setItem(row, 5, stock_item)
            
        except Exception as e:
            print(f"Error al cargar movimientos: {e}")
        finally:
            close_session()
    
    def search_products(self, text):
        """Busca productos en la tabla"""
        for row in range(self.stock_table.rowCount()):
            sku = self.stock_table.item(row, 0).text().lower()
            name = self.stock_table.item(row, 1).text().lower()
            
            if text.lower() in sku or text.lower() in name:
                self.stock_table.setRowHidden(row, False)
            else:
                self.stock_table.setRowHidden(row, True)
    
    def adjust_inventory(self):
        """Abre diálogo para ajustar inventario"""
        dialog = InventoryAdjustmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()


class InventoryAdjustmentDialog(QDialog):
    """Diálogo para ajustar inventario"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Ajustar Inventario")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-size: 13px;
                background-color: transparent;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                color: #0f172a;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Producto
        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(35)
        self.load_products()
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        form_layout.addRow("Producto*:", self.product_combo)
        
        # Stock actual
        self.current_stock_label = QLabel("0")
        self.current_stock_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563eb;")
        form_layout.addRow("Stock Actual:", self.current_stock_label)
        
        # Tipo de movimiento
        self.movement_type_combo = QComboBox()
        self.movement_type_combo.setMinimumHeight(35)
        self.movement_type_combo.addItem("Entrada (+)", MovementType.ENTRY)
        self.movement_type_combo.addItem("Salida (-)", MovementType.EXIT)
        self.movement_type_combo.addItem("Ajuste", MovementType.ADJUSTMENT)
        self.movement_type_combo.currentIndexChanged.connect(self.update_preview)
        form_layout.addRow("Tipo de Movimiento*:", self.movement_type_combo)
        
        # Cantidad
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99999)
        self.quantity_spin.setMinimumHeight(35)
        self.quantity_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.quantity_spin.valueChanged.connect(self.update_preview)
        form_layout.addRow("Cantidad*:", self.quantity_spin)
        
        # Stock resultante (preview)
        self.new_stock_label = QLabel("0")
        self.new_stock_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        form_layout.addRow("Nuevo Stock:", self.new_stock_label)
        
        # Razón
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(80)
        self.reason_input.setPlaceholderText("Motivo del ajuste (ej: Compra a proveedor, Inventario físico, etc.)")
        form_layout.addRow("Razón:", self.reason_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Guardar Ajuste")
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(self.save_adjustment)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
        
        # Inicializar
        self.on_product_changed()
    
    def load_products(self):
        """Carga los productos disponibles"""
        session = get_session()
        try:
            products = session.query(Product).all()
            for product in products:
                display_text = f"{product.name} (Stock: {product.stock})"
                self.product_combo.addItem(display_text, product.id)
        finally:
            close_session()
    
    def on_product_changed(self):
        """Actualiza el stock actual cuando cambia el producto"""
        product_id = self.product_combo.currentData()
        if not product_id:
            return
        
        session = get_session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                self.current_stock_label.setText(str(product.stock))
                self.update_preview()
        finally:
            close_session()
    
    def update_preview(self):
        """Actualiza la vista previa del nuevo stock"""
        try:
            current_stock = int(self.current_stock_label.text())
            quantity = self.quantity_spin.value()
            movement_type = self.movement_type_combo.currentData()
            
            if movement_type == MovementType.ENTRY:
                new_stock = current_stock + quantity
            elif movement_type == MovementType.EXIT:
                new_stock = current_stock - quantity
            else:  # ADJUSTMENT
                new_stock = quantity  # Para ajustes, la cantidad es el nuevo stock
            
            # Validar que no sea negativo
            if new_stock < 0:
                self.new_stock_label.setText("ERROR: Stock negativo")
                self.new_stock_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
            else:
                self.new_stock_label.setText(str(new_stock))
                self.new_stock_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        except:
            pass
    
    def save_adjustment(self):
        """Guarda el ajuste de inventario"""
        product_id = self.product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        
        reason = self.reason_input.toPlainText().strip()
        if not reason:
            reason = "Ajuste de inventario"  # Razón por defecto si está vacío
        
        # Validar stock negativo
        if "ERROR" in self.new_stock_label.text():
            QMessageBox.warning(self, "Error", "El ajuste resultaría en stock negativo")
            return
        
        session = get_session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            
            previous_stock = product.stock
            quantity = self.quantity_spin.value()
            movement_type = self.movement_type_combo.currentData()
            
            # Calcular nuevo stock
            if movement_type == MovementType.ENTRY:
                product.stock += quantity
                quantity_for_movement = quantity
            elif movement_type == MovementType.EXIT:
                product.stock -= quantity
                quantity_for_movement = -quantity
            else:  # ADJUSTMENT
                product.stock = quantity
                quantity_for_movement = quantity - previous_stock
            
            # Registrar movimiento
            movement = InventoryMovement(
                product_id=product.id,
                movement_type=movement_type,
                quantity=quantity_for_movement,
                previous_stock=previous_stock,
                new_stock=product.stock,
                reason=reason
            )
            
            session.add(movement)
            session.commit()
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Inventario ajustado correctamente\n"
                f"Stock anterior: {previous_stock}\n"
                f"Nuevo stock: {product.stock}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar ajuste: {str(e)}")
        finally:
            close_session()