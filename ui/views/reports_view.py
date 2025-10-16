"""
Vista de Reportes - Estadísticas y reportes del negocio
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
    QHeaderView, QGroupBox, QFormLayout, QScrollArea, QFrame,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from config.database import get_session, close_session
from models import Sale, Product, Customer, SaleItem
from sqlalchemy import func, desc

class ReportsView(QWidget):
    """Vista para reportes y estadísticas"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        # Cargar reportes después de que la UI esté lista
        self.load_reports()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Aplicar estilo general al widget
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
            QLabel {
                color: #0f172a;
            }
        """)
        
        # Header
        title = QLabel("Reportes y Estadísticas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a; background-color: transparent;")
        layout.addWidget(title)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Filtros de fecha
        filters_group = QGroupBox("Período de Reporte")
        filters_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                font-weight: bold;
                color: #0f172a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 5px;
                padding: 0 5px;
                background-color: white;
                color: #0f172a;
            }
            QLabel {
                color: #0f172a;
                background-color: transparent;
            }
        """)
        filters_layout = QHBoxLayout()
        filters_layout.setContentsMargins(10, 25, 10, 10)
        
        filters_layout.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(35)
        self.date_from.setStyleSheet("""
            QDateEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QCalendarWidget QWidget {
                color: #0f172a;
            }
            QCalendarWidget QAbstractItemView {
                color: #0f172a;
                background-color: white;
                selection-background-color: #2563eb;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                color: #0f172a;
                background-color: white;
            }
            QCalendarWidget QMenu {
                color: #0f172a;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                color: #0f172a;
                background-color: white;
            }
        """)
        filters_layout.addWidget(self.date_from)
        
        filters_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(35)
        self.date_to.setStyleSheet("""
            QDateEdit {
                color: #0f172a;
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QCalendarWidget QWidget {
                color: #0f172a;
            }
            QCalendarWidget QAbstractItemView {
                color: #0f172a;
                background-color: white;
                selection-background-color: #2563eb;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                color: #0f172a;
                background-color: white;
            }
            QCalendarWidget QMenu {
                color: #0f172a;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                color: #0f172a;
                background-color: white;
            }
        """)
        filters_layout.addWidget(self.date_to)
        
        btn_export = QPushButton("Exportar a Excel")
        btn_export.setMinimumHeight(35)
        btn_export.setMinimumWidth(140)
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_export.clicked.connect(self.export_to_excel)
        filters_layout.addWidget(btn_export)
        
        filters_layout.addStretch()
        filters_group.setLayout(filters_layout)
        content_layout.addWidget(filters_group)
        
        
        # Productos más vendidos
        top_products_group = QGroupBox("Top 10 Productos Más Vendidos")
        top_products_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                font-weight: bold;
                color: #0f172a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 5px;
                padding: 0 5px;
                background-color: white;
                color: #0f172a;
            }
        """)
        top_products_layout = QVBoxLayout()
        top_products_layout.setContentsMargins(10, 25, 10, 10)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            "Posición", "Producto", "Cantidad Vendida", "Total Vendido"
        ])
        header = self.top_products_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.top_products_table.setColumnWidth(0, 80)
        self.top_products_table.setColumnWidth(2, 150)
        self.top_products_table.setColumnWidth(3, 150)
        self.top_products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.top_products_table.verticalHeader().setVisible(False)
        self.top_products_table.setMinimumHeight(250)  # Altura para mostrar ~5 filas
        
        top_products_layout.addWidget(self.top_products_table)
        top_products_group.setLayout(top_products_layout)
        content_layout.addWidget(top_products_group)
        
        # Top clientes
        top_customers_group = QGroupBox("Top 10 Mejores Clientes")
        top_customers_group.setStyleSheet("""
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
        top_customers_layout = QVBoxLayout()
        
        self.top_customers_table = QTableWidget()
        self.top_customers_table.setColumnCount(4)
        self.top_customers_table.setHorizontalHeaderLabels([
            "Posición", "Cliente", "N° Compras", "Total Comprado"
        ])
        header = self.top_customers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.top_customers_table.setColumnWidth(0, 80)
        self.top_customers_table.setColumnWidth(2, 120)
        self.top_customers_table.setColumnWidth(3, 150)
        self.top_customers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.top_customers_table.verticalHeader().setVisible(False)
        self.top_customers_table.setMinimumHeight(250)  # Altura para mostrar ~5 filas
        
        top_customers_layout.addWidget(self.top_customers_table)
        top_customers_group.setLayout(top_customers_layout)
        content_layout.addWidget(top_customers_group)
        
        # Productos con bajo stock
        low_stock_group = QGroupBox("Alertas de Stock Bajo")
        low_stock_group.setStyleSheet("""
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
        low_stock_layout = QVBoxLayout()
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels([
            "Producto", "Stock Actual", "Stock Mínimo", "Estado"
        ])
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.low_stock_table.setColumnWidth(1, 120)
        self.low_stock_table.setColumnWidth(2, 120)
        self.low_stock_table.setColumnWidth(3, 120)
        self.low_stock_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.low_stock_table.verticalHeader().setVisible(False)
        self.low_stock_table.setMinimumHeight(250)  # Altura para mostrar ~5 filas
        
        low_stock_layout.addWidget(self.low_stock_table)
        low_stock_group.setLayout(low_stock_layout)
        content_layout.addWidget(low_stock_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def load_reports(self):
        """Carga todos los reportes"""
        self.load_top_products()
        self.load_top_customers()
        self.load_low_stock_products()
    
    def load_top_products(self):
        """Carga los productos más vendidos"""
        session = get_session()
        try:
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()
            
            from datetime import datetime
            datetime_from = datetime.combine(date_from, datetime.min.time())
            datetime_to = datetime.combine(date_to, datetime.max.time())
            
            # Consulta de productos más vendidos (sin filtro de status)
            top_products = session.query(
                Product.name,
                func.sum(SaleItem.quantity).label('total_quantity'),
                func.sum(SaleItem.subtotal).label('total_amount')
            ).join(
                SaleItem, Product.id == SaleItem.product_id
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                Sale.created_at.between(datetime_from, datetime_to)
            ).group_by(
                Product.id, Product.name
            ).order_by(
                desc('total_quantity')
            ).limit(10).all()
            
            # Llenar tabla
            self.top_products_table.setRowCount(len(top_products))
            
            for row, (name, quantity, amount) in enumerate(top_products):
                self.top_products_table.setItem(row, 0, QTableWidgetItem(f"#{row + 1}"))
                self.top_products_table.setItem(row, 1, QTableWidgetItem(name))
                self.top_products_table.setItem(row, 2, QTableWidgetItem(f"{int(quantity)} unidades"))
                self.top_products_table.setItem(row, 3, QTableWidgetItem(f"${amount:,.2f}"))
            
        except Exception as e:
            print(f"Error al cargar productos más vendidos: {e}")
            import traceback
            traceback.print_exc()
        finally:
            close_session()
    
    def load_top_customers(self):
        """Carga los mejores clientes"""
        session = get_session()
        try:
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()
            
            from datetime import datetime
            datetime_from = datetime.combine(date_from, datetime.min.time())
            datetime_to = datetime.combine(date_to, datetime.max.time())
            
            # Consulta de mejores clientes (sin filtro de status)
            top_customers = session.query(
                Customer.name,
                func.count(Sale.id).label('purchase_count'),
                func.sum(Sale.total).label('total_amount')
            ).join(
                Sale, Customer.id == Sale.customer_id
            ).filter(
                Sale.created_at.between(datetime_from, datetime_to)
            ).group_by(
                Customer.id, Customer.name
            ).order_by(
                desc('total_amount')
            ).limit(10).all()
            
            # Llenar tabla
            self.top_customers_table.setRowCount(len(top_customers))
            
            for row, (name, count, amount) in enumerate(top_customers):
                self.top_customers_table.setItem(row, 0, QTableWidgetItem(f"#{row + 1}"))
                self.top_customers_table.setItem(row, 1, QTableWidgetItem(name))
                self.top_customers_table.setItem(row, 2, QTableWidgetItem(f"{count} compras"))
                self.top_customers_table.setItem(row, 3, QTableWidgetItem(f"${amount:,.2f}"))
            
        except Exception as e:
            print(f"Error al cargar mejores clientes: {e}")
            import traceback
            traceback.print_exc()
        finally:
            close_session()
    
    def load_low_stock_products(self):
        """Carga productos con stock bajo"""
        session = get_session()
        try:
            # Productos con stock bajo o igual al mínimo
            low_stock_products = session.query(Product).filter(
                Product.stock <= Product.min_stock
            ).all()
            
            # Llenar tabla
            self.low_stock_table.setRowCount(len(low_stock_products))
            
            for row, product in enumerate(low_stock_products):
                self.low_stock_table.setItem(row, 0, QTableWidgetItem(product.name))
                
                stock_item = QTableWidgetItem(str(product.stock))
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.low_stock_table.setItem(row, 1, stock_item)
                
                min_stock_item = QTableWidgetItem(str(product.min_stock))
                min_stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.low_stock_table.setItem(row, 2, min_stock_item)
                
                # Estado
                if product.stock == 0:
                    status = "SIN STOCK"
                    color = Qt.GlobalColor.red
                elif product.stock <= product.min_stock:
                    status = "BAJO"
                    color = Qt.GlobalColor.darkYellow
                else:
                    status = "NORMAL"
                    color = Qt.GlobalColor.darkGreen
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(color)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.low_stock_table.setItem(row, 3, status_item)
            
            if len(low_stock_products) == 0:
                self.low_stock_table.setRowCount(1)
                self.low_stock_table.setItem(0, 0, QTableWidgetItem("No hay productos con stock bajo"))
                self.low_stock_table.setSpan(0, 0, 1, 4)
            
        except Exception as e:
            print(f"Error al cargar productos con stock bajo: {e}")
        finally:
            close_session()
    
    def export_to_excel(self):
        """Exporta el reporte a Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            from datetime import datetime
            from PyQt6.QtWidgets import QFileDialog
            
            # Preguntar dónde guardar
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte",
                f"Reporte_Ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_name:
                return
            
            # Crear workbook
            wb = Workbook()
            
            # Hoja 1: Resumen
            ws1 = wb.active
            ws1.title = "Resumen"
            
            # Título
            ws1['A1'] = "REPORTE DE VENTAS"
            ws1['A1'].font = Font(size=16, bold=True)
            ws1['A2'] = f"Período: {self.date_from.date().toString('dd/MM/yyyy')} - {self.date_to.date().toString('dd/MM/yyyy')}"
            
            # Resumen de ventas (calculado dinámicamente)
            ws1['A4'] = "RESUMEN DE VENTAS"
            ws1['A4'].font = Font(bold=True)
            
            # Calcular resumen dinámicamente
            session = get_session()
            try:
                date_from = self.date_from.date().toPyDate()
                date_to = self.date_to.date().toPyDate()
                from datetime import datetime
                datetime_from = datetime.combine(date_from, datetime.min.time())
                datetime_to = datetime.combine(date_to, datetime.max.time())
                
                total_sales = session.query(func.sum(Sale.total)).filter(
                    Sale.created_at.between(datetime_from, datetime_to)
                ).scalar() or 0
                
                sales_count = session.query(Sale).filter(
                    Sale.created_at.between(datetime_from, datetime_to)
                ).count()
                
                avg_sale = total_sales / sales_count if sales_count > 0 else 0
                
                ws1['A5'] = "Total Ventas:"
                ws1['B5'] = f"${total_sales:,.2f}"
                ws1['A6'] = "Número de Ventas:"
                ws1['B6'] = str(sales_count)
                ws1['A7'] = "Ticket Promedio:"
                ws1['B7'] = f"${avg_sale:,.2f}"
            except Exception as e:
                ws1['A5'] = "Error al calcular resumen"
                ws1['B5'] = str(e)
            finally:
                close_session()
            
            # Hoja 2: Top Productos
            ws2 = wb.create_sheet("Top Productos")
            ws2['A1'] = "TOP 10 PRODUCTOS MÁS VENDIDOS"
            ws2['A1'].font = Font(size=14, bold=True)
            
            headers = ['Posición', 'Producto', 'Cantidad Vendida', 'Total Vendido']
            for col, header in enumerate(headers, 1):
                cell = ws2.cell(3, col)
                cell.value = header
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            for row in range(self.top_products_table.rowCount()):
                for col in range(4):
                    item = self.top_products_table.item(row, col)
                    if item:
                        ws2.cell(row + 4, col + 1).value = item.text()
            
            # Hoja 3: Top Clientes
            ws3 = wb.create_sheet("Top Clientes")
            ws3['A1'] = "TOP 10 MEJORES CLIENTES"
            ws3['A1'].font = Font(size=14, bold=True)
            
            headers = ['Posición', 'Cliente', 'N° Compras', 'Total Comprado']
            for col, header in enumerate(headers, 1):
                cell = ws3.cell(3, col)
                cell.value = header
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            for row in range(self.top_customers_table.rowCount()):
                for col in range(4):
                    item = self.top_customers_table.item(row, col)
                    if item:
                        ws3.cell(row + 4, col + 1).value = item.text()
            
            # Hoja 4: Stock Bajo
            ws4 = wb.create_sheet("Stock Bajo")
            ws4['A1'] = "ALERTAS DE STOCK BAJO"
            ws4['A1'].font = Font(size=14, bold=True)
            
            headers = ['Producto', 'Stock Actual', 'Stock Mínimo', 'Estado']
            for col, header in enumerate(headers, 1):
                cell = ws4.cell(3, col)
                cell.value = header
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            
            for row in range(self.low_stock_table.rowCount()):
                for col in range(4):
                    item = self.low_stock_table.item(row, col)
                    if item:
                        ws4.cell(row + 4, col + 1).value = item.text()
            
            # Ajustar ancho de columnas
            for ws in [ws1, ws2, ws3, ws4]:
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            # Guardar
            wb.save(file_name)
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Reporte exportado correctamente a:\n{file_name}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al exportar a Excel:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()