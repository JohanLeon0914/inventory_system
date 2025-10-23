"""
Vista de Selección de Productos - Para elegir productos antes de completar la venta
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QGroupBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QFont
from config.database import get_session, close_session
from models import Product, Customer

class ProductSelectionView(QWidget):
    """Vista para seleccionar productos antes de completar la venta"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_products = []  # Lista de productos seleccionados
        self.products_cache = []
        self.init_ui()
        self.load_products()
        self.build_products_gallery()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Seleccionar Productos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para limpiar selección
        self.btn_clear = QPushButton("🗑️ Limpiar")
        self.btn_clear.setFixedHeight(45)
        self.btn_clear.setFixedWidth(120)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #6b7280;
            }
        """)
        self.btn_clear.setEnabled(False)
        self.btn_clear.clicked.connect(self.clear_selection)
        header_layout.addWidget(self.btn_clear)
        
        # Botón para continuar
        self.btn_continue = QPushButton("Continuar a Venta")
        self.btn_continue.setFixedHeight(45)
        self.btn_continue.setFixedWidth(180)
        self.btn_continue.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #6b7280;
            }
        """)
        self.btn_continue.setEnabled(False)
        self.btn_continue.clicked.connect(self.continue_to_sale)
        header_layout.addWidget(self.btn_continue)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar productos...")
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
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
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        filter_layout.addWidget(self.search_input)
        
        # Filtro por categoría (si existe)
        self.category_filter = QComboBox()
        self.category_filter.setMinimumHeight(40)
        self.category_filter.addItem("Todas las categorías")
        self.category_filter.setStyleSheet("""
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
        filter_layout.addWidget(self.category_filter)
        
        layout.addLayout(filter_layout)
        
        # Galería de productos
        products_section = QGroupBox("Productos Disponibles")
        products_section.setStyleSheet("""
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
        products_layout = QVBoxLayout()
        
        # Scroll area para productos
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setMinimumHeight(400)
        self.products_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #f8fafc;
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
        """)
        
        # Container para la grilla de productos
        self.products_container = QWidget()
        self.products_grid = QGridLayout(self.products_container)
        self.products_grid.setContentsMargins(15, 15, 15, 15)
        self.products_grid.setHorizontalSpacing(12)
        self.products_grid.setVerticalSpacing(12)
        self.products_scroll.setWidget(self.products_container)
        
        products_layout.addWidget(self.products_scroll)
        products_section.setLayout(products_layout)
        layout.addWidget(products_section)
        
        # Resumen de productos seleccionados
        self.summary_label = QLabel("Ningún producto seleccionado")
        self.summary_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #64748b;
            background-color: #f1f5f9;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        """)
        layout.addWidget(self.summary_label)
    
    def load_products(self):
        """Carga los productos disponibles"""
        session = get_session()
        try:
            self.products_cache = session.query(Product).filter(Product.stock > 0).all()
        finally:
            close_session()
    
    def build_products_gallery(self):
        """Construye la galería de productos"""
        # Limpiar grilla
        while self.products_grid.count():
            item = self.products_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        max_cols = 6
        row = 0
        col = 0
        
        for product in self.products_cache:
            # Crear botón del producto
            btn = QPushButton()
            btn.setFixedSize(140, 120)
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: white; 
                    border: 2px solid #e2e8f0; 
                    border-radius: 8px; 
                    color: #0f172a;
                    font-size: 11px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover { 
                    background-color: #f1f5f9; 
                    border-color: #3b82f6;
                }
                QPushButton:pressed {
                    background-color: #dbeafe;
                    border-color: #1d4ed8;
                }
            """)
            
            # Cargar imagen si existe
            pix = QPixmap(f"resources/images/{product.sku}.png")
            if pix.isNull():
                pix = QPixmap(f"resources/images/{product.name}.png")
            if not pix.isNull():
                icon = QIcon(pix.scaled(60, 60, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
                btn.setIcon(icon)
                btn.setIconSize(pix.rect().size().scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
            
            # Formatear precio
            if product.sale_price == int(product.sale_price):
                price_text = f"${int(product.sale_price):,}"
            else:
                price_text = f"${product.sale_price:.2f}"
            
            # Dividir nombre largo en múltiples líneas
            display_name = product.name
            if len(product.name) > 15:
                words = product.name.split()
                if len(words) > 1:
                    mid_point = len(words) // 2
                    line1 = ' '.join(words[:mid_point])
                    line2 = ' '.join(words[mid_point:])
                    display_name = f"{line1}\n{line2}"
                else:
                    mid_point = len(product.name) // 2
                    display_name = f"{product.name[:mid_point]}\n{product.name[mid_point:]}"
            
            btn.setText(f"{display_name}\n{price_text}\nStock: {product.stock}")
            btn.setToolTip(f"Producto: {product.name}\nPrecio: {price_text}\nStock: {product.stock}\n\nClick para agregar (+1)")
            
            # Conectar click
            btn.clicked.connect(lambda checked=False, p=product: self.toggle_product_selection(p))
            
            self.products_grid.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def toggle_product_selection(self, product):
        """Agrega o incrementa la cantidad de un producto"""
        # Verificar si ya está seleccionado
        for item in self.selected_products:
            if item['product_id'] == product.id:
                # Ya está seleccionado, incrementar cantidad
                if item['quantity'] < product.stock:  # Verificar stock disponible
                    item['quantity'] += 1
                    item['subtotal'] = item['quantity'] * item['unit_price']
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Stock insuficiente", 
                        f"No hay suficiente stock para {product.name}. Disponible: {product.stock}")
                self.update_summary()
                return
        
        # Agregar producto seleccionado por primera vez
        item_data = {
            'product_id': product.id,
            'product_name': product.name,
            'unit_price': product.sale_price,
            'quantity': 1,
            'subtotal': product.sale_price,
            'stock': product.stock
        }
        self.selected_products.append(item_data)
        self.update_summary()
    
    def update_summary(self):
        """Actualiza el resumen de productos seleccionados"""
        if not self.selected_products:
            self.summary_label.setText("Ningún producto seleccionado")
            self.btn_continue.setEnabled(False)
            self.btn_clear.setEnabled(False)
        else:
            total_items = sum(item['quantity'] for item in self.selected_products)
            total_value = sum(item['subtotal'] for item in self.selected_products)
            
            if total_value == int(total_value):
                formatted_total = f"${int(total_value):,}"
            else:
                formatted_total = f"${total_value:,.2f}"
            
            self.summary_label.setText(
                f"Productos seleccionados: {len(self.selected_products)} | "
                f"Total items: {total_items} | "
                f"Valor total: {formatted_total}"
            )
            self.btn_continue.setEnabled(True)
            self.btn_clear.setEnabled(True)
    
    def filter_products(self):
        """Filtra productos por texto de búsqueda"""
        search_text = self.search_input.text().lower()
        
        for i in range(self.products_grid.count()):
            widget = self.products_grid.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                product_name = widget.toolTip().split('\n')[0].replace('Producto: ', '').lower()
                widget.setVisible(search_text in product_name)
    
    def continue_to_sale(self):
        """Continúa a la vista de completar venta"""
        if self.selected_products:
            # Emitir señal o llamar callback para cambiar a la vista de completar venta
            if hasattr(self.parent(), 'show_complete_sale_view'):
                self.parent().show_complete_sale_view(self.selected_products)
            elif hasattr(self, 'on_continue_to_sale'):
                self.on_continue_to_sale(self.selected_products)
    
    def get_selected_products(self):
        """Retorna los productos seleccionados"""
        return self.selected_products.copy()
    
    def clear_selection(self):
        """Limpia la selección de productos"""
        self.selected_products.clear()
        self.update_summary()
