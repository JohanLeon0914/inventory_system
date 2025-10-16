"""
Vista del Dashboard - Resumen general del sistema
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent

class DashboardView(QWidget):
    """
    Dashboard con estadísticas y resumen del negocio
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Título
        title = QLabel("Dashboard")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a; background-color: transparent;")
        main_layout.addWidget(title)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Sección de acciones rápidas
        quick_actions_label = QLabel("Acciones Rápidas")
        quick_actions_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: white;
            background-color: transparent;
            padding: 10px 0;
        """)
        content_layout.addWidget(quick_actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        # Botones de acciones rápidas (TODO: conectar con funcionalidades)
        from PyQt6.QtWidgets import QPushButton
        
        btn_new_sale = QPushButton("+ Nueva Venta")
        btn_new_sale.setFixedHeight(50)
        btn_new_sale.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_new_sale.clicked.connect(self.open_new_sale)
        
        btn_new_product = QPushButton("+ Nuevo Producto")
        btn_new_product.setFixedHeight(50)
        btn_new_product.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_new_product.clicked.connect(self.open_new_product)
        
        btn_new_customer = QPushButton("+ Nuevo Cliente")
        btn_new_customer.setFixedHeight(50)
        btn_new_customer.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_new_customer.clicked.connect(self.open_new_customer)
        
        actions_layout.addWidget(btn_new_sale)
        actions_layout.addWidget(btn_new_product)
        actions_layout.addWidget(btn_new_customer)
        
        content_layout.addLayout(actions_layout)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def open_new_sale(self):
        """Abre el diálogo de nueva venta"""
        # Cambiar a la vista de ventas
        main_window = self.window()
        if hasattr(main_window, 'show_sales'):
            main_window.show_sales()
    
    def open_new_product(self):
        """Abre el diálogo de nuevo producto"""
        # Cambiar a la vista de productos
        main_window = self.window()
        if hasattr(main_window, 'show_products'):
            main_window.show_products()
    
    def open_new_customer(self):
        """Abre el diálogo de nuevo cliente"""
        # Cambiar a la vista de clientes
        main_window = self.window()
        if hasattr(main_window, 'show_customers'):
            main_window.show_customers()