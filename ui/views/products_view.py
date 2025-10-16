"""
Vista de Productos - Gestión completa de productos
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox,
    QTextEdit, QHeaderView, QSizePolicy
)
from PyQt6.QtGui import QDoubleValidator, QShowEvent
from PyQt6.QtCore import Qt
from config.database import get_session, close_session
from models import Product, Category

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
                btn_edit.clicked.connect(lambda checked, p=product: self.edit_product(p))
                
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
                btn_delete.clicked.connect(lambda checked, p=product: self.delete_product(p))
                
                actions_layout.addWidget(btn_edit)
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
    
    def manage_categories(self):
        """Abre diálogo para gestionar categorías"""
        dialog = CategoriesDialog(self)
        dialog.exec()
    
    def edit_product(self, product):
        """Abre diálogo para editar producto"""
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def delete_product(self, product):
        """Elimina un producto"""
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto '{product.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
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
            
            session.commit()
            
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