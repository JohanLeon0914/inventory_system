"""
Vista de Productos - Gestión completa de productos
"""
import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox,
    QTextEdit, QHeaderView, QSizePolicy, QGroupBox, QScrollArea,
    QFileDialog
)
from PyQt6.QtGui import QDoubleValidator, QShowEvent, QPixmap
from PyQt6.QtCore import Qt
from config.database import get_session, close_session
from models import Product, Category, RawMaterial, ProductMaterial, InventoryMovement, MovementType
from ui.views.increase_stock_dialogs import IncreaseStockDialog, IncreaseStockAllDialog

class ProductsView(QWidget):
    """Vista para gestionar productos"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header con título y botón
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestión de Productos")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para importar productos
        btn_import = QPushButton("📥 Importar desde Excel")
        btn_import.setFixedHeight(40)
        btn_import.setFixedWidth(180)
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_import.clicked.connect(self.import_products)
        header_layout.addWidget(btn_import)
        
        # Botón para gestionar categorías
        btn_categories = QPushButton("Gestionar Categorías")
        btn_categories.setFixedHeight(40)
        btn_categories.setProperty("class", "secondary")
        btn_categories.clicked.connect(self.manage_categories)
        header_layout.addWidget(btn_categories)
        
        # Botón para agregar producto
        btn_add = QPushButton("+ Nuevo Producto")
        btn_add.setFixedHeight(40)
        btn_add.clicked.connect(self.add_product)
        header_layout.addWidget(btn_add)
        
        # Botón para aumentar stock a todos los productos
        btn_add_stock_all = QPushButton("📈 Aumentar Stock a Todos")
        btn_add_stock_all.setFixedHeight(40)
        btn_add_stock_all.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_add_stock_all.clicked.connect(self.increase_stock_all_products)
        header_layout.addWidget(btn_add_stock_all)
        
        layout.addLayout(header_layout)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o SKU...")
        self.search_input.textChanged.connect(self.search_products)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("color: #0f172a;")
        search_layout.addWidget(self.search_input)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_products)
        search_layout.addWidget(btn_refresh)
        
        layout.addLayout(search_layout)
        
        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "SKU", "Nombre", "Categoría", "Precio Venta", "Stock", "Acciones"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        # Configurar anchos fijos para columnas específicas
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(5, 80)   # Stock
        self.table.setColumnWidth(6, 220)  # Acciones
        
        # Hacer que varias columnas se expandan proporcionalmente
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # SKU
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Categoría
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Precio Venta
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        # Asegurar que la tabla use todo el espacio disponible
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.table)
    
    def showEvent(self, event: QShowEvent):
        """Se ejecuta cuando la vista se muestra"""
        super().showEvent(event)
        self.load_products()
    
    def load_products(self):
        """Carga todos los productos en la tabla"""
        session = get_session()
        try:
            products = session.query(Product).all()
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                
                # SKU
                self.table.setItem(row, 1, QTableWidgetItem(product.sku))
                
                # Nombre
                self.table.setItem(row, 2, QTableWidgetItem(product.name))
                
                # Categoría
                category_name = product.category.name if product.category else "Sin categoría"
                self.table.setItem(row, 3, QTableWidgetItem(category_name))
                
                # Precio de venta
                price_item = QTableWidgetItem(f"${product.sale_price:,.2f}")
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 4, price_item)
                
                # Stock
                stock_item = QTableWidgetItem(str(product.stock))
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Colorear según stock
                if product.is_low_stock:
                    stock_item.setBackground(Qt.GlobalColor.yellow)
                
                self.table.setItem(row, 5, stock_item)
                
                # Botones de acción
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                actions_layout.setSpacing(0)
                
                # Botón agregar stock (verde, izquierda redondeada)
                btn_add_stock = QPushButton("➕")
                btn_add_stock.setFixedSize(40, 32)
                btn_add_stock.setToolTip("Aumentar stock")
                btn_add_stock.setStyleSheet("""
                    QPushButton {
                        background-color: #10b981;
                        color: white;
                        border: none;
                        border-top-left-radius: 4px;
                        border-bottom-left-radius: 4px;
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                """)
                btn_add_stock.clicked.connect(lambda checked, p=product: self.increase_product_stock(p))
                actions_layout.addWidget(btn_add_stock)
                
                # Botón editar (azul, sin bordes redondeados)
                btn_edit = QPushButton("✏️")
                btn_edit.setFixedSize(40, 32)
                btn_edit.setToolTip("Editar producto")
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 0px;
                        font-size: 14px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #1d4ed8;
                    }
                """)
                btn_edit.clicked.connect(lambda checked, p=product: self.edit_product(p))
                actions_layout.addWidget(btn_edit)
                
                # Botón eliminar (rojo, derecha redondeada)
                btn_delete = QPushButton("🗑️")
                btn_delete.setFixedSize(40, 32)
                btn_delete.setToolTip("Eliminar producto")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #ef4444;
                        color: white;
                        border: none;
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        border-top-right-radius: 4px;
                        border-bottom-right-radius: 4px;
                        font-size: 14px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #dc2626;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, p=product: self.delete_product(p))
                actions_layout.addWidget(btn_delete)
                
                self.table.setCellWidget(row, 6, actions_widget)
                self.table.setRowHeight(row, 50)  # Altura suficiente para los botones
            
            # Eliminar ajuste automático por contenido que encoge columnas y rompe el stretch
            # self.table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos: {str(e)}")
        finally:
            close_session()
    
    def search_products(self, text):
        """Busca productos por nombre o SKU"""
        for row in range(self.table.rowCount()):
            sku = self.table.item(row, 1).text().lower()
            name = self.table.item(row, 2).text().lower()
            
            if text.lower() in sku or text.lower() in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
    
    def add_product(self):
        """Abre diálogo para agregar producto"""
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def import_products(self):
        """Abre diálogo para importar productos desde Excel/CSV"""
        from ui.views.import_products_dialog import ImportProductsDialog
        dialog = ImportProductsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def manage_categories(self):
        """Abre diálogo para gestionar categorías"""
        dialog = CategoriesDialog(self)
        dialog.exec()
    
    def edit_product(self, product):
        """Abre diálogo para editar producto"""
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def increase_product_stock(self, product):
        """Abre diálogo para aumentar stock de un producto específico"""
        dialog = IncreaseStockDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def increase_stock_all_products(self):
        """Abre diálogo para aumentar stock a todos los productos"""
        dialog = IncreaseStockAllDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def delete_product(self, product):
        """Elimina un producto"""
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto '{product.name}'?\n\n"
            "Esto eliminará también:\n"
            "- Todos los movimientos de inventario relacionados\n"
            "- Todas las relaciones con materias primas\n"
            "- Los items de ventas (se pondrán como NULL)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                # Primero eliminar manualmente los movimientos de inventario
                from models import InventoryMovement, ProductMaterial
                
                # Eliminar movimientos de inventario
                session.query(InventoryMovement).filter_by(product_id=product.id).delete()
                
                # Eliminar relaciones con materias primas
                session.query(ProductMaterial).filter_by(product_id=product.id).delete()
                
                # Eliminar el producto
                session.delete(product)
                
                session.commit()
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.load_products()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            finally:
                close_session()


class CategoriesDialog(QDialog):
    """Diálogo para gestionar categorías"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        self.setWindowTitle("Gestionar Categorías")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Categorías de Productos")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        btn_add_category = QPushButton("+ Nueva Categoría")
        btn_add_category.clicked.connect(self.add_category)
        header_layout.addWidget(btn_add_category)
        
        layout.addLayout(header_layout)
        
        # Tabla de categorías
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nombre", "Descripción", "Acciones"])
        
        # Estilos para la tabla de categorías
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
                color: #0f172a;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
                color: #0f172a;
            }
            QTableWidget::item:selected {
                background-color: #e0f2f7;
                color: #00796b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
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
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 150)  # Nombre
        self.table.setColumnWidth(2, 220)  # Acciones
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
        
        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_close.setFixedWidth(100)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(btn_close)
        layout.addLayout(close_layout)
    
    def load_categories(self):
        """Carga todas las categorías"""
        session = get_session()
        try:
            categories = session.query(Category).all()
            
            self.table.setRowCount(len(categories))
            
            for row, category in enumerate(categories):
                # Nombre
                self.table.setItem(row, 0, QTableWidgetItem(category.name))
                
                # Descripción
                desc = category.description or ""
                self.table.setItem(row, 1, QTableWidgetItem(desc))
                
                # Botones de acción
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(8, 5, 8, 5)
                actions_layout.setSpacing(8)
                
                btn_edit = QPushButton("Editar")
                btn_edit.setMinimumWidth(80)
                btn_edit.setFixedHeight(32)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 500;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #1d4ed8;
                    }
                """)
                btn_edit.clicked.connect(lambda checked, c=category: self.edit_category(c))
                
                btn_delete = QPushButton("Eliminar")
                btn_delete.setMinimumWidth(80)
                btn_delete.setFixedHeight(32)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #ef4444;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 500;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #dc2626;
                    }
                """)
                btn_delete.clicked.connect(lambda checked, c=category: self.delete_category(c))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                
                self.table.setCellWidget(row, 2, actions_widget)
                self.table.setRowHeight(row, 50)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar categorías: {str(e)}")
        finally:
            close_session()
    
    def add_category(self):
        """Agrega una nueva categoría"""
        dialog = CategoryFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
    
    def edit_category(self, category):
        """Edita una categoría"""
        dialog = CategoryFormDialog(self, category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
    
    def delete_category(self, category):
        """Elimina una categoría"""
        session = get_session()
        try:
            # Verificar si tiene productos
            product_count = session.query(Product).filter_by(category_id=category.id).count()
            
            if product_count > 0:
                reply = QMessageBox.question(
                    self,
                    "Categoría en uso",
                    f"Esta categoría tiene {product_count} producto(s) asociado(s).\n"
                    "Los productos quedarán sin categoría. ¿Desea continuar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            session.delete(category)
            session.commit()
            QMessageBox.information(self, "Éxito", "Categoría eliminada correctamente")
            self.load_categories()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
        finally:
            close_session()


class CategoryFormDialog(QDialog):
    """Formulario para crear/editar categorías"""
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.is_editing = category is not None
        self.init_ui()
        
        if self.is_editing:
            self.load_category_data()
    
    def init_ui(self):
        self.setWindowTitle("Editar Categoría" if self.is_editing else "Nueva Categoría")
        self.setMinimumWidth(400)
        
        # Estilos para el diálogo de formulario
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre de la categoría")
        form_layout.addRow("Nombre*:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Descripción opcional")
        form_layout.addRow("Descripción:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_category)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
    
    def load_category_data(self):
        """Carga los datos de la categoría a editar"""
        self.name_input.setText(self.category.name)
        self.description_input.setText(self.category.description or "")
    
    def save_category(self):
        """Guarda la categoría"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Campo requerido", "El nombre es obligatorio")
            return
        
        session = get_session()
        try:
            if self.is_editing:
                category = session.query(Category).filter_by(id=self.category.id).first()
            else:
                category = Category()
            
            category.name = name
            category.description = self.description_input.toPlainText().strip()
            
            if not self.is_editing:
                session.add(category)
            
            session.commit()
            
            QMessageBox.information(self, "Éxito", "Categoría guardada correctamente")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
        finally:
            close_session()


class ProductDialog(QDialog):
    """Diálogo para crear/editar productos"""
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.is_editing = product is not None
        self.materials_data = []  # Lista de materias primas asociadas
        self.current_image_path = None  # Ruta de la imagen seleccionada
        self.original_image_path = None  # Ruta original de la imagen (para edición)
        self.image_changed = False  # Indica si la imagen fue modificada
        self.init_ui()
        
        if self.is_editing:
            self.load_product_data()
    
    def init_ui(self):
        self.setWindowTitle("Editar Producto" if self.is_editing else "Nuevo Producto")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-size: 13px;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                color: #0f172a;
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
        form_layout = QFormLayout()
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Ej: PROD-001")
        form_layout.addRow("SKU*:", self.sku_input)
        
        # Nombre
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        form_layout.addRow("Nombre*:", self.name_input)
        
        # Descripción
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Descripción opcional")
        form_layout.addRow("Descripción:", self.description_input)
        
        # Categoría
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Categoría:", self.category_combo)
        
        # Precio de costo
        self.cost_price_input = QLineEdit()
        self.cost_price_input.setPlaceholderText("0.00")
        self.cost_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        form_layout.addRow("Precio Costo:", self.cost_price_input)
        
        # Precio de venta
        self.sale_price_input = QLineEdit()
        self.sale_price_input.setPlaceholderText("0.00")
        self.sale_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        form_layout.addRow("Precio Venta*:", self.sale_price_input)
        
        # Stock
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(999999)
        self.stock_input.setMinimumHeight(35)
        self.stock_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        form_layout.addRow("Stock:", self.stock_input)
        
        # Stock mínimo
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(999)
        self.min_stock_input.setValue(5)
        self.min_stock_input.setMinimumHeight(35)
        self.min_stock_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        form_layout.addRow("Stock Mínimo:", self.min_stock_input)
        
        layout.addLayout(form_layout)
        
        # Sección de Imagen
        image_group = QGroupBox("Imagen del Producto")
        image_layout = QVBoxLayout()
        
        image_control_layout = QHBoxLayout()
        
        btn_select_image = QPushButton("📁 Seleccionar Imagen")
        btn_select_image.setMinimumHeight(35)
        btn_select_image.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_select_image.clicked.connect(self.select_image)
        image_control_layout.addWidget(btn_select_image)
        
        btn_remove_image = QPushButton("🗑️ Eliminar Imagen")
        btn_remove_image.setMinimumHeight(35)
        btn_remove_image.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_remove_image.clicked.connect(self.remove_image)
        image_control_layout.addWidget(btn_remove_image)
        
        image_control_layout.addStretch()
        image_layout.addLayout(image_control_layout)
        
        # Vista previa de imagen
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(200)
        self.image_label.setMaximumHeight(300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                background-color: #f8fafc;
            }
        """)
        self.image_label.setText("No hay imagen seleccionada")
        self.current_image_path = None
        image_layout.addWidget(self.image_label)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Botón para ver/editar materias primas
        btn_materials = QPushButton("🔧 Configurar Materia Prima")
        btn_materials.setMinimumHeight(40)
        btn_materials.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        btn_materials.clicked.connect(self.open_materials_dialog)
        layout.addWidget(btn_materials)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_product)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
    
    def load_categories(self):
        """Carga las categorías disponibles"""
        session = get_session()
        try:
            self.category_combo.addItem("Sin categoría", None)
            categories = session.query(Category).all()
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
        finally:
            close_session()
    
    def open_materials_dialog(self):
        """Abre el diálogo para gestionar las materias primas del producto"""
        if self.is_editing and self.product:
            # Obtener el producto actualizado de la base de datos
            session = get_session()
            try:
                product = session.query(Product).filter_by(id=self.product.id).first()
                if product:
                    # Mantener la referencia actualizada
                    self.product = product
                    dialog = ProductMaterialsDialog(self, self.materials_data, product)
                    dialog.exec()
            finally:
                close_session()
        else:
            dialog = ProductMaterialsDialog(self, self.materials_data, None)
            dialog.exec()
    
    def select_image(self):
        """Abre el diálogo para seleccionar una imagen"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif);;Todos los archivos (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.image_changed = True
            self.display_image(file_path)
    
    def remove_image(self):
        """Elimina la imagen seleccionada"""
        self.current_image_path = None
        self.image_changed = True
        self.image_label.clear()
        self.image_label.setText("No hay imagen seleccionada")
    
    def display_image(self, image_path):
        """Muestra una vista previa de la imagen"""
        if not image_path or not os.path.exists(image_path):
            self.image_label.setText("Imagen no encontrada")
            return
        
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText("Error al cargar imagen")
            return
        
        # Escalar la imagen para que quepa en el área de vista previa
        # Usar un tamaño máximo de 250x250 para la vista previa
        max_size = 250
        if pixmap.width() > max_size or pixmap.height() > max_size:
            scaled_pixmap = pixmap.scaled(
                max_size, max_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            scaled_pixmap = pixmap
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def get_image_directory(self):
        """Obtiene el directorio donde se guardarán las imágenes de productos"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        image_dir = os.path.join(base_dir, 'resources', 'images', 'products')
        os.makedirs(image_dir, exist_ok=True)
        return image_dir
    
    def save_image_to_resources(self, source_path, product_id):
        """Copia la imagen a la carpeta de recursos y retorna la ruta relativa"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        try:
            image_dir = self.get_image_directory()
            _, ext = os.path.splitext(source_path)
            filename = f"product_{product_id}{ext}"
            dest_path = os.path.join(image_dir, filename)
            
            # Si ya existe una imagen para este producto, eliminarla
            if os.path.exists(dest_path):
                os.remove(dest_path)
            
            # Copiar la nueva imagen
            shutil.copy2(source_path, dest_path)
            
            # Retornar ruta relativa desde la raíz del proyecto
            return os.path.join('resources', 'images', 'products', filename)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar imagen: {str(e)}")
            return None
    
    def delete_old_image(self, image_path):
        """Elimina una imagen antigua de la carpeta de recursos"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            absolute_image_path = os.path.join(base_dir, image_path)
            if os.path.exists(absolute_image_path):
                os.remove(absolute_image_path)
        except Exception as e:
            # No es crítico si falla la eliminación
            print(f"Warning: No se pudo eliminar la imagen antigua: {str(e)}")
    
    def load_product_data(self):
        """Carga los datos del producto a editar"""
        self.sku_input.setText(self.product.sku)
        self.name_input.setText(self.product.name)
        self.description_input.setText(self.product.description or "")
        self.cost_price_input.setText(str(self.product.cost_price))
        self.sale_price_input.setText(str(self.product.sale_price))
        self.stock_input.setValue(self.product.stock)
        self.min_stock_input.setValue(self.product.min_stock)
        
        # Seleccionar categoría
        if self.product.category_id:
            index = self.category_combo.findData(self.product.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        # Cargar imagen si existe
        if self.product.image_path:
            # Construir ruta absoluta
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            absolute_image_path = os.path.join(base_dir, self.product.image_path)
            if os.path.exists(absolute_image_path):
                self.current_image_path = absolute_image_path
                self.original_image_path = self.product.image_path
                self.display_image(absolute_image_path)
            else:
                self.current_image_path = None
                self.original_image_path = None
        
        # Cargar materias primas asociadas
        self.materials_data.clear()
        session = get_session()
        try:
            product_materials = session.query(ProductMaterial).filter_by(product_id=self.product.id).all()
            for pm in product_materials:
                material = session.query(RawMaterial).filter_by(id=pm.raw_material_id).first()
                if material:
                    self.materials_data.append({
                        'id': material.id,
                        'name': material.name,
                        'quantity': pm.quantity_needed,
                        'unit': material.unit
                    })
        finally:
            close_session()
    
    def save_product(self):
        """Guarda el producto (crear o actualizar)"""
        # Validar campos requeridos
        if not self.sku_input.text() or not self.name_input.text():
            QMessageBox.warning(self, "Campos requeridos", "SKU y Nombre son obligatorios")
            return
        
        session = get_session()
        try:
            if self.is_editing:
                # Actualizar producto existente
                product = session.query(Product).filter_by(id=self.product.id).first()
            else:
                # Crear nuevo producto
                product = Product()
            
            # Asignar valores
            product.sku = self.sku_input.text()
            product.name = self.name_input.text()
            product.description = self.description_input.toPlainText()
            product.category_id = self.category_combo.currentData()
            # Convertir precios de texto a float
            try:
                product.cost_price = float(self.cost_price_input.text() or 0)
            except ValueError:
                product.cost_price = 0.0
            
            try:
                product.sale_price = float(self.sale_price_input.text() or 0)
            except ValueError:
                product.sale_price = 0.0
            product.stock = self.stock_input.value()
            product.min_stock = self.min_stock_input.value()
            
            if not self.is_editing:
                session.add(product)
                session.flush()  # Asegurar que product.id esté disponible
            
            # Manejar imagen del producto (si fue modificada o es un producto nuevo con imagen)
            if self.image_changed or (not self.is_editing and self.current_image_path):
                if self.current_image_path:
                    # Guardar la imagen en resources/images/products
                    saved_image_path = self.save_image_to_resources(self.current_image_path, product.id)
                    if saved_image_path:
                        product.image_path = saved_image_path
                        # Eliminar imagen anterior si existe y es diferente
                        if self.is_editing and self.original_image_path and self.original_image_path != saved_image_path:
                            self.delete_old_image(self.original_image_path)
                else:
                    # Si se eliminó la imagen, limpiar el campo y eliminar archivo
                    if self.is_editing and self.original_image_path:
                        self.delete_old_image(self.original_image_path)
                    product.image_path = None

            # Actualizar materias primas asociadas
            session.query(ProductMaterial).filter_by(product_id=product.id).delete()
            for mat_data in self.materials_data:
                product_material = ProductMaterial(
                    product_id=product.id,
                    raw_material_id=mat_data['id'],
                    quantity_needed=mat_data['quantity']
                )
                session.add(product_material)
            
            session.commit()
            self.product = product
            
            QMessageBox.information(
                self, 
                "Éxito", 
                "Producto guardado correctamente"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
        finally:
            close_session()


class ProductMaterialsDialog(QDialog):
    """Diálogo para gestionar las materias primas de un producto"""

    def __init__(self, parent=None, materials_data=None, product=None):
        super().__init__(parent)
        self.product = product
        # Usar la lista compartida con el diálogo principal
        self.materials_data = materials_data if materials_data is not None else []
        self.init_ui()
        self.load_raw_materials()
        self.populate_materials_table()

    def init_ui(self):
        product_name = self.product.name if self.product else "Nuevo producto"
        product_sku = f" ({self.product.sku})" if self.product and self.product.sku else ""
        self.setWindowTitle(f"Materias Primas - {product_name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                font-size: 13px;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                color: #0f172a;
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
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Información del producto
        info_label = QLabel(f"<b>Producto:</b> {product_name}{product_sku}")
        info_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f8fafc; border-radius: 6px;")
        layout.addWidget(info_label)

        # Sección de Materias Primas
        materials_group = QGroupBox("Materias Primas Requeridas")
        materials_layout = QVBoxLayout()

        # Selector para agregar materia prima
        add_material_layout = QHBoxLayout()

        self.material_combo = QComboBox()
        self.material_combo.setMinimumHeight(35)
        add_material_layout.addWidget(QLabel("Materia Prima:"))
        add_material_layout.addWidget(self.material_combo, 1)

        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.01)
        self.quantity_spin.setMaximum(9999.99)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setMinimumHeight(35)
        add_material_layout.addWidget(QLabel("Cantidad:"))
        add_material_layout.addWidget(self.quantity_spin)

        btn_add_material = QPushButton("Agregar")
        btn_add_material.setMinimumHeight(35)
        btn_add_material.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_add_material.clicked.connect(self.add_material_to_list)
        add_material_layout.addWidget(btn_add_material)

        materials_layout.addLayout(add_material_layout)

        # Tabla de materias primas asociadas
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(4)
        self.materials_table.setHorizontalHeaderLabels(["Materia Prima", "Cantidad", "Unidad", "Acciones"])
        self.materials_table.setMinimumHeight(250)

        materials_header = self.materials_table.horizontalHeader()
        materials_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.materials_table.setColumnWidth(1, 120)
        self.materials_table.setColumnWidth(2, 100)
        self.materials_table.setColumnWidth(3, 100)

        # Estilos para la tabla
        self.materials_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
            }
        """)

        materials_layout.addWidget(self.materials_table)
        materials_group.setLayout(materials_layout)
        layout.addWidget(materials_group)

        # Botones
        buttons_layout = QHBoxLayout()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar")
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_save.clicked.connect(self.save_materials)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)

        layout.addLayout(buttons_layout)

    def load_raw_materials(self):
        """Carga las materias primas disponibles"""
        session = get_session()
        try:
            self.material_combo.clear()
            materials = session.query(RawMaterial).all()
            for material in materials:
                display_text = f"{material.name} ({material.unit})"
                self.material_combo.addItem(display_text, material.id)
        finally:
            close_session()

    def populate_materials_table(self):
        """Muestra los datos actuales en la tabla"""
        self.materials_table.setRowCount(len(self.materials_data))
        for row, mat_data in enumerate(self.materials_data):
            self.materials_table.setItem(row, 0, QTableWidgetItem(mat_data['name']))

            quantity_item = QTableWidgetItem(f"{mat_data['quantity']:.2f}")
            quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.materials_table.setItem(row, 1, quantity_item)

            unit_item = QTableWidgetItem(mat_data['unit'])
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.materials_table.setItem(row, 2, unit_item)

            btn_remove = QPushButton("Eliminar")
            btn_remove.setMinimumHeight(30)
            btn_remove.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            btn_remove.clicked.connect(lambda checked, mid=mat_data['id']: self.remove_material_from_list(mid))
            self.materials_table.setCellWidget(row, 3, btn_remove)
            self.materials_table.setRowHeight(row, 40)

    def add_material_to_list(self):
        """Agrega una materia prima a la lista del producto"""
        material_id = self.material_combo.currentData()
        if not material_id:
            QMessageBox.warning(self, "Error", "Seleccione una materia prima")
            return

        quantity = self.quantity_spin.value()

        for mat_data in self.materials_data:
            if mat_data['id'] == material_id:
                QMessageBox.warning(self, "Error", "Esta materia prima ya está en la lista")
                return

        session = get_session()
        try:
            material = session.query(RawMaterial).filter_by(id=material_id).first()
            if material:
                self.materials_data.append({
                    'id': material.id,
                    'name': material.name,
                    'quantity': quantity,
                    'unit': material.unit
                })
                self.populate_materials_table()
                self.quantity_spin.setValue(1.0)
        finally:
            close_session()

    def remove_material_from_list(self, material_id):
        """Elimina una materia prima de la lista"""
        self.materials_data[:] = [m for m in self.materials_data if m['id'] != material_id]
        self.populate_materials_table()

    def save_materials(self):
        """Persistir los cambios si el producto ya existe"""
        if not self.product:
            QMessageBox.information(
                self,
                "Información",
                "Las materias primas se guardarán cuando guardes el producto."
            )
            self.accept()
            return

        session = get_session()
        try:
            session.query(ProductMaterial).filter_by(product_id=self.product.id).delete()
            for mat_data in self.materials_data:
                product_material = ProductMaterial(
                    product_id=self.product.id,
                    raw_material_id=mat_data['id'],
                    quantity_needed=mat_data['quantity']
                )
                session.add(product_material)

            session.commit()

            QMessageBox.information(
                self,
                "Éxito",
                "Materias primas guardadas correctamente"
            )
            self.accept()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
        finally:
            close_session()