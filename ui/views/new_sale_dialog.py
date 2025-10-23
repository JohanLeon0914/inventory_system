"""
Nuevo Diálogo de Venta - Usa las vistas separadas para selección y completar venta
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent
from ui.views.product_selection_view import ProductSelectionView
from ui.views.complete_sale_view import CompleteSaleView
from config.database import get_session, close_session
from models import Sale, SaleItem, Product, PaymentMethod, SaleStatus, InventoryMovement, MovementType, ProductMaterial, RawMaterial, RawMaterialMovement, RawMaterialMovementType
import time
import traceback

class NewSaleDialog(QDialog):
    """Diálogo para crear una nueva venta usando vistas separadas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        self.setWindowTitle("Nueva Venta")
        # Hacer la ventana de pantalla completa
        self.setWindowState(Qt.WindowState.WindowMaximized)
        # También establecer tamaño mínimo para casos donde no se maximice
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget para cambiar entre vistas
        self.stacked_widget = QStackedWidget()
        
        # Vista de selección de productos
        self.product_selection_view = ProductSelectionView()
        self.stacked_widget.addWidget(self.product_selection_view)
        
        # Vista de completar venta
        self.complete_sale_view = CompleteSaleView()
        self.stacked_widget.addWidget(self.complete_sale_view)
        
        layout.addWidget(self.stacked_widget)
        
        # Mostrar vista de selección por defecto
        self.show_product_selection_view()
    
    def setup_connections(self):
        """Configura las conexiones entre las vistas"""
        # Conectar la vista de selección con la de completar venta
        self.product_selection_view.on_continue_to_sale = self.show_complete_sale_view
        
        # Conectar la vista de completar venta con la de selección
        self.complete_sale_view.on_go_back = self.show_product_selection_view
        self.complete_sale_view.on_complete_sale = self.complete_sale
    
    def show_product_selection_view(self):
        """Muestra la vista de selección de productos"""
        self.stacked_widget.setCurrentWidget(self.product_selection_view)
        self.setWindowTitle("Nueva Venta - Seleccionar Productos")
    
    def show_complete_sale_view(self, selected_products):
        """Muestra la vista de completar venta con los productos seleccionados"""
        if not selected_products:
            return
        
        # Establecer los productos seleccionados en la vista de completar venta
        self.complete_sale_view.set_sale_items(selected_products)
        self.stacked_widget.setCurrentWidget(self.complete_sale_view)
        self.setWindowTitle("Nueva Venta - Completar Venta")
    
    def complete_sale(self, sale_items, customer_id, payment_method):
        """Completa la venta guardándola en la base de datos"""
        if not sale_items:
            return
        
        session = get_session()
        try:
            # Crear venta
            sale = Sale()
            
            # Generar número de factura único
            max_attempts = 10
            for attempt in range(max_attempts):
                if attempt == 0:
                    # Intentar con el siguiente número secuencial
                    last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
                    if last_sale:
                        try:
                            last_number = int(last_sale.invoice_number.split('-')[1])
                            invoice_number = f"INV-{last_number + 1:06d}"
                        except (ValueError, IndexError):
                            invoice_number = f"INV-{int(time.time()):06d}"
                    else:
                        invoice_number = "INV-000001"
                else:
                    # Si hay conflicto, usar timestamp
                    invoice_number = f"INV-{int(time.time() * 1000):06d}"
                
                # Verificar si el número ya existe
                existing = session.query(Sale).filter_by(invoice_number=invoice_number).first()
                if not existing:
                    sale.invoice_number = invoice_number
                    break
            else:
                raise Exception("No se pudo generar un número de factura único después de varios intentos")
            
            sale.customer_id = customer_id
            sale.payment_method = payment_method
            sale.tax = 0
            sale.discount = 0
            sale.status = SaleStatus.COMPLETED
            
            # Agregar items
            for item_data in sale_items:
                item = SaleItem()
                item.product_id = item_data['product_id']
                item.quantity = item_data['quantity']
                item.unit_price = item_data['unit_price']
                item.subtotal = item_data['subtotal']
                sale.items.append(item)
                
                # Actualizar stock del producto
                product = session.query(Product).filter_by(id=item_data['product_id']).first()
                previous_stock = product.stock
                product.stock -= item_data['quantity']
                
                # Registrar movimiento de inventario
                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type=MovementType.EXIT,
                    quantity=-item_data['quantity'],
                    previous_stock=previous_stock,
                    new_stock=product.stock,
                    reason=f"Venta {sale.invoice_number}"
                )
                session.add(movement)
                
                # Descontar materias primas asociadas al producto
                product_materials = session.query(ProductMaterial).filter_by(product_id=product.id).all()
                for pm in product_materials:
                    raw_material = session.query(RawMaterial).filter_by(id=pm.raw_material_id).first()
                    if raw_material:
                        # Calcular cantidad a descontar
                        quantity_to_deduct = pm.quantity_needed * item_data['quantity']
                        previous_material_stock = raw_material.stock
                        raw_material.stock -= quantity_to_deduct
                        
                        # Registrar movimiento de materia prima
                        material_movement = RawMaterialMovement(
                            raw_material_id=raw_material.id,
                            movement_type=RawMaterialMovementType.PRODUCTION,
                            quantity=-quantity_to_deduct,
                            reference=sale.invoice_number,
                            reason=f"Producción de {item_data['quantity']} unidades de {product.name}"
                        )
                        session.add(material_movement)
            
            # Calcular total
            sale.calculate_total()
            
            session.add(sale)
            session.commit()
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Venta registrada correctamente\nFactura: {sale.invoice_number}\nTotal: ${sale.total:,.2f}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al guardar venta: {str(e)}")
        finally:
            close_session()
