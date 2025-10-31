"""
Vista de Selección de Productos - Para elegir productos antes de completar la venta
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QGroupBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QFont
from config.database import get_session, close_session
from models import Product, Customer, Category

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
        # Establecer fondo blanco para el widget principal y estilos de tooltips
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QToolTip {
                background-color: #ffffff;
                color: #0f172a;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: normal;
            }
        """)
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
        self.search_input.setPlaceholderText("Buscar productos por nombre o SKU...")
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
        self.products_container.setStyleSheet("background-color: #f8fafc;")
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
            from sqlalchemy.orm import joinedload
            # Cargar productos con sus categorías usando joinedload
            self.products_cache = session.query(Product).options(
                joinedload(Product.category)
            ).filter(Product.stock > 0).all()
            # Acceder a las relaciones ahora para que se carguen antes de cerrar la sesión
            for product in self.products_cache:
                _ = product.category  # Forzar carga de la relación
                _ = product.name  # Acceder a atributos básicos
            
            # Cargar categorías en el filtro
            self.load_categories()
        finally:
            close_session()
    
    def load_categories(self):
        """Carga las categorías de productos en el filtro"""
        session = get_session()
        try:
            # Obtener categorías únicas de los productos cargados
            categories_set = set()
            for product in self.products_cache:
                if product.category:
                    categories_set.add(product.category.name)
            
            # Agregar categorías al combo box
            for category_name in sorted(categories_set):
                self.category_filter.addItem(category_name)
            
            # Conectar señal de cambio de categoría
            self.category_filter.currentTextChanged.connect(self.on_category_changed)
        finally:
            close_session()
    
    def on_category_changed(self, category_name):
        """Filtra productos cuando cambia la categoría"""
        search_text = self.search_input.text().lower()
        
        # Filtrar productos
        for i in range(self.products_grid.count()):
            widget = self.products_grid.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                product = widget.product
                
                # Filtrar por categoría
                if category_name != "Todas las categorías":
                    if not product.category or product.category.name != category_name:
                        widget.setVisible(False)
                        continue
                
                # Filtrar por búsqueda
                matches_search = not search_text or \
                    search_text in product.name.lower() or \
                    search_text in product.sku.lower()
                
                widget.setVisible(matches_search)
    
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
            
            # Cargar imagen del producto
            pix = None
            if product.image_path:
                # Construir ruta absoluta desde la raíz del proyecto
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                image_path = os.path.join(base_dir, product.image_path)
                if os.path.exists(image_path):
                    pix = QPixmap(image_path)
            
            # Si no hay imagen o no se cargó, intentar rutas alternativas (retrocompatibilidad)
            if not pix or pix.isNull():
                # Intentar con SKU o nombre del producto
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                alt_paths = [
                    os.path.join(base_dir, "resources", "images", f"{product.sku}.png"),
                    os.path.join(base_dir, "resources", "images", f"{product.name}.png"),
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        pix = QPixmap(alt_path)
                        if not pix.isNull():
                            break
            
            # Configurar imagen en el botón si existe
            if pix and not pix.isNull():
                # Escalar imagen para que quepa bien en la tarjeta (90x90 para tarjeta de 140x120)
                scaled_pix = pix.scaled(
                    90, 90,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon = QIcon(scaled_pix)
                btn.setIcon(icon)
                btn.setIconSize(scaled_pix.size())
                btn.setText("")  # No mostrar texto cuando hay imagen
                # Configurar estilo del botón con imagen
                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: white; 
                        border: 2px solid #e2e8f0; 
                        border-radius: 8px; 
                    }
                    QPushButton:hover { 
                        background-color: #f1f5f9; 
                        border-color: #3b82f6;
                        border-width: 3px;
                    }
                    QPushButton:pressed {
                        background-color: #dbeafe;
                        border-color: #1d4ed8;
                    }
                """)
            else:
                # Si no hay imagen, mostrar nombre y precio
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
            
            # Crear tooltip con información completa del producto
            category_name = product.category.name if product.category else "Sin categoría"
            if product.sale_price == int(product.sale_price):
                price_text = f"${int(product.sale_price):,}"
            else:
                price_text = f"${product.sale_price:.2f}"
            
            tooltip_text = (
                f"📦 {product.name}\n"
                f"🏷️ SKU: {product.sku}\n"
                f"💰 Precio: {price_text}\n"
                f"📊 Stock: {product.stock}\n"
                f"📁 Categoría: {category_name}\n"
            )
            if product.description:
                tooltip_text += f"\n📝 {product.description[:100]}..."
            tooltip_text += f"\n\n👆 Click para agregar (+1)"
            
            btn.setToolTip(tooltip_text)
            
            # Guardar referencia al producto en el botón para facilitar la búsqueda
            btn.product = product
            
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
        """Filtra productos por texto de búsqueda (nombre o SKU)"""
        search_text = self.search_input.text().lower()
        category_name = self.category_filter.currentText()
        
        # Filtrar productos
        for i in range(self.products_grid.count()):
            widget = self.products_grid.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                # Si el botón tiene referencia al producto, buscar directamente
                if hasattr(widget, 'product'):
                    product = widget.product
                    product_name = product.name.lower()
                    product_sku = product.sku.lower()
                    
                    # Filtrar por categoría
                    matches_category = True
                    if category_name != "Todas las categorías":
                        if not product.category or product.category.name != category_name:
                            matches_category = False
                    
                    # Mostrar si coincide con nombre o SKU y categoría
                    matches_search = not search_text or (search_text in product_name or search_text in product_sku)
                    widget.setVisible(matches_category and matches_search)
                else:
                    # Fallback: buscar en el tooltip como antes
                    tooltip_text = widget.toolTip().lower()
                    widget.setVisible(search_text in tooltip_text)
    
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
