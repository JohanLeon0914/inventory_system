"""
Ventana principal de la aplicación
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles import MAIN_STYLESHEET
from ui.views.dashboard_view import DashboardView
from ui.views.products_view import ProductsView
from ui.views.raw_materials_view import RawMaterialsView
from ui.views.inventory_view import InventoryView
from ui.views.sales_view import SalesView
from ui.views.customers_view import CustomersView
from ui.views.expenses_view import ExpensesView
from ui.views.reports_view import ReportsView

class MainWindow(QMainWindow):
    """
    Ventana principal con sidebar y vistas intercambiables
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema de Inventario y Ventas")
        self.setGeometry(100, 100, 1200, 700)
        
        # Aplicar estilos
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Crear área de contenido
        self.create_content_area()
        main_layout.addWidget(self.content_area)
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def create_sidebar(self):
        """Crea la barra lateral de navegación"""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)
        
        # Logo/Título de la aplicación
        title_label = QLabel("📦 Inventario")
        title_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
            background-color: transparent;
        """)
        layout.addWidget(title_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #334155; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Botones de navegación
        self.btn_dashboard = self.create_nav_button("🏠  Dashboard")
        self.btn_products = self.create_nav_button("📦  Productos")
        self.btn_raw_materials = self.create_nav_button("🧪  Materias Primas")
        self.btn_inventory = self.create_nav_button("📊  Inventario")
        self.btn_sales = self.create_nav_button("💰  Ventas")
        self.btn_expenses = self.create_nav_button("📤  Egresos")
        self.btn_customers = self.create_nav_button("👥  Clientes")
        self.btn_reports = self.create_nav_button("📈  Reportes")
        
        # Conectar señales
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.btn_products.clicked.connect(self.show_products)
        self.btn_raw_materials.clicked.connect(self.show_raw_materials)
        self.btn_inventory.clicked.connect(self.show_inventory)
        self.btn_sales.clicked.connect(self.show_sales)
        self.btn_expenses.clicked.connect(self.show_expenses)
        self.btn_customers.clicked.connect(self.show_customers)
        self.btn_reports.clicked.connect(self.show_reports)
        
        # Agregar botones al layout
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_products)
        layout.addWidget(self.btn_raw_materials)
        layout.addWidget(self.btn_inventory)
        layout.addWidget(self.btn_sales)
        layout.addWidget(self.btn_expenses)
        layout.addWidget(self.btn_customers)
        layout.addWidget(self.btn_reports)
        
        layout.addStretch()
        
        # Información de licencia al final
        license_info = QLabel("Licencia Activa ✓")
        license_info.setStyleSheet("""
            color: #10b981;
            font-size: 12px;
            padding: 10px 20px;
        """)
        layout.addWidget(license_info)
    
    def create_nav_button(self, text):
        """Crea un botón de navegación"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(45)
        return btn
    
    def create_content_area(self):
        """Crea el área de contenido con vistas intercambiables"""
        self.content_area = QWidget()
        layout = QVBoxLayout(self.content_area)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget para cambiar entre vistas
        self.stacked_widget = QStackedWidget()
        
        # Crear vistas
        self.dashboard_view = DashboardView()
        self.products_view = ProductsView()
        self.raw_materials_view = RawMaterialsView()
        self.inventory_view = InventoryView()
        self.sales_view = SalesView()
        self.expenses_view = ExpensesView()
        self.customers_view = CustomersView()
        self.reports_view = ReportsView()
        
        # Agregar vistas al stack
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.products_view)
        self.stacked_widget.addWidget(self.raw_materials_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.sales_view)
        self.stacked_widget.addWidget(self.expenses_view)
        self.stacked_widget.addWidget(self.customers_view)
        self.stacked_widget.addWidget(self.reports_view)
        
        layout.addWidget(self.stacked_widget)
    
    def uncheck_all_buttons(self):
        """Desmarca todos los botones de navegación"""
        self.btn_dashboard.setChecked(False)
        self.btn_products.setChecked(False)
        self.btn_raw_materials.setChecked(False)
        self.btn_inventory.setChecked(False)
        self.btn_sales.setChecked(False)
        self.btn_expenses.setChecked(False)
        self.btn_customers.setChecked(False)
        self.btn_reports.setChecked(False)
    
    def show_dashboard(self):
        """Muestra el dashboard"""
        self.uncheck_all_buttons()
        self.btn_dashboard.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.dashboard_view)
    
    def show_products(self):
        """Muestra la vista de productos"""
        self.uncheck_all_buttons()
        self.btn_products.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.products_view)
    
    def show_raw_materials(self):
        """Muestra la vista de materias primas"""
        self.uncheck_all_buttons()
        self.btn_raw_materials.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.raw_materials_view)
    
    def show_inventory(self):
        """Muestra la vista de inventario"""
        self.uncheck_all_buttons()
        self.btn_inventory.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.inventory_view)
    
    def show_sales(self):
        """Muestra la vista de ventas"""
        self.uncheck_all_buttons()
        self.btn_sales.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.sales_view)
    
    def show_expenses(self):
        """Muestra la vista de egresos"""
        self.uncheck_all_buttons()
        self.btn_expenses.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.expenses_view)
    
    def show_customers(self):
        """Muestra la vista de clientes"""
        self.uncheck_all_buttons()
        self.btn_customers.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.customers_view)
    
    def show_reports(self):
        """Muestra la vista de reportes"""
        self.uncheck_all_buttons()
        self.btn_reports.setChecked(True)
        self.stacked_widget.setCurrentWidget(self.reports_view)