"""
Vista de Ventas - Sistema completo de registro de ventas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
    QHeaderView, QTextEdit, QDateEdit, QGroupBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QShowEvent
from datetime import datetime
from config.database import get_session, close_session
from models import Sale, SaleItem, Product, Customer, PaymentMethod, SaleStatus, InventoryMovement, MovementType
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
import traceback

class SalesView(QWidget):
    """Vista para gestionar ventas"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_sales()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Registro de Ventas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para limpiar tabla
        btn_clear = QPushButton("🗑️ Limpiar Tabla")
        btn_clear.setFixedHeight(40)
        btn_clear.setFixedWidth(140)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_clear.clicked.connect(self.clear_sales_table)
        header_layout.addWidget(btn_clear)
        
        # Botón para importar Excel
        btn_import = QPushButton("📥 Importar Excel")
        btn_import.setFixedHeight(40)
        btn_import.setFixedWidth(150)
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
        btn_import.clicked.connect(self.import_from_excel)
        header_layout.addWidget(btn_import)
        
        # Botón para exportar Excel
        btn_export = QPushButton("📤 Exportar Excel")
        btn_export.setFixedHeight(40)
        btn_export.setFixedWidth(150)
        btn_export.setStyleSheet("""
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
        btn_export.clicked.connect(self.export_to_excel)
        header_layout.addWidget(btn_export)
        
        # Botón para nueva venta
        btn_new_sale = QPushButton("+ Nueva Venta")
        btn_new_sale.setFixedHeight(40)
        btn_new_sale.clicked.connect(self.create_new_sale)
        header_layout.addWidget(btn_new_sale)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por número de factura...")
        self.search_input.textChanged.connect(self.search_sales)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("color: #0f172a;")
        filter_layout.addWidget(self.search_input)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_sales)
        filter_layout.addWidget(btn_refresh)
        
        layout.addLayout(filter_layout)
        
        # Tabla de ventas
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Factura", "Fecha", "Cliente", "Total", "Método Pago", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        # Configurar anchos fijos para columnas específicas
        self.table.setColumnWidth(0, 120)  # N° Factura
        self.table.setColumnWidth(3, 120)  # Total
        self.table.setColumnWidth(6, 170)  # Acciones
        
        # Hacer que varias columnas se expandan proporcionalmente
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Fecha
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Cliente
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Método Pago
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Estado
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        # Asegurar que la tabla use todo el espacio disponible
        self.table.horizontalHeader().setStretchLastSection(False)
        
        layout.addWidget(self.table)
    
    def showEvent(self, event: QShowEvent):
        """Se ejecuta cuando la vista se muestra"""
        super().showEvent(event)
        self.load_sales()
    
    def load_sales(self):
        """Carga todas las ventas"""
        session = get_session()
        try:
            sales = session.query(Sale).order_by(Sale.created_at.desc()).all()
            
            self.table.setRowCount(len(sales))
            
            for row, sale in enumerate(sales):
                # N° Factura
                self.table.setItem(row, 0, QTableWidgetItem(sale.invoice_number))
                
                # Fecha
                date_str = sale.created_at.strftime("%d/%m/%Y %H:%M")
                self.table.setItem(row, 1, QTableWidgetItem(date_str))
                
                # Cliente
                customer_name = sale.customer.name if sale.customer else "Cliente General"
                self.table.setItem(row, 2, QTableWidgetItem(customer_name))
                
                # Total
                total_item = QTableWidgetItem(f"${sale.total:,.2f}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 3, total_item)
                
                # Método de pago
                self.table.setItem(row, 4, QTableWidgetItem(sale.payment_method.value))
                
                # Estado
                status_item = QTableWidgetItem(sale.status.value)
                if sale.status == SaleStatus.COMPLETED:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif sale.status == SaleStatus.CANCELLED:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 5, status_item)
                
                # Botones de acción
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(8, 5, 8, 5)
                actions_layout.setSpacing(8)
                
                btn_view = QPushButton("Ver Detalle")
                btn_view.setFixedHeight(32)
                btn_view.setMinimumWidth(100)
                btn_view.setStyleSheet("""
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
                btn_view.clicked.connect(lambda checked, s=sale: self.view_sale_detail(s))
                
                actions_layout.addWidget(btn_view)
                
                self.table.setCellWidget(row, 6, actions_widget)
                self.table.setRowHeight(row, 50)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar ventas: {str(e)}")
        finally:
            close_session()
    
    def search_sales(self, text):
        """Busca ventas por número de factura"""
        for row in range(self.table.rowCount()):
            invoice = self.table.item(row, 0).text().lower()
            if text.lower() in invoice:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
    
    def create_new_sale(self):
        """Abre el diálogo para crear una nueva venta"""
        dialog = NewSaleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_sales()
    
    def view_sale_detail(self, sale):
        """Muestra el detalle de una venta"""
        dialog = SaleDetailDialog(self, sale.id)
        dialog.exec()
    
    def export_to_excel(self):
        """Exporta todas las ventas a un archivo Excel"""
        try:
            # Seleccionar ubicación del archivo
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Ventas como Excel",
                f"Ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            session = get_session()
            try:
                # Obtener todas las ventas con sus items
                from sqlalchemy.orm import joinedload
                sales = session.query(Sale).options(joinedload(Sale.items)).order_by(Sale.created_at.desc()).all()
                
                if not sales:
                    QMessageBox.warning(self, "Advertencia", "No hay ventas para exportar")
                    return
                
                # Crear libro de Excel
                wb = Workbook()
                
                # Hoja 1: Resumen de Ventas
                ws_summary = wb.active
                ws_summary.title = "Resumen de Ventas"
                
                # Encabezados con estilo
                headers = ["N° Factura", "Fecha", "Cliente", "Método Pago", "Estado", "Subtotal", "Impuesto", "Descuento", "Total"]
                for col, header in enumerate(headers, 1):
                    cell = ws_summary.cell(row=1, column=col, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="2563eb", end_color="2563eb", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                
                # Datos
                for row, sale in enumerate(sales, 2):
                    ws_summary.cell(row=row, column=1, value=sale.invoice_number)
                    ws_summary.cell(row=row, column=2, value=sale.created_at.strftime("%d/%m/%Y %H:%M"))
                    ws_summary.cell(row=row, column=3, value=sale.customer.name if sale.customer else "Cliente General")
                    ws_summary.cell(row=row, column=4, value=sale.payment_method.value)
                    ws_summary.cell(row=row, column=5, value=sale.status.value)
                    ws_summary.cell(row=row, column=6, value=sale.subtotal)
                    ws_summary.cell(row=row, column=7, value=sale.tax)
                    ws_summary.cell(row=row, column=8, value=sale.discount)
                    ws_summary.cell(row=row, column=9, value=sale.total)
                
                # Ajustar anchos de columna
                ws_summary.column_dimensions['A'].width = 15
                ws_summary.column_dimensions['B'].width = 18
                ws_summary.column_dimensions['C'].width = 25
                ws_summary.column_dimensions['D'].width = 15
                ws_summary.column_dimensions['E'].width = 12
                ws_summary.column_dimensions['F'].width = 12
                ws_summary.column_dimensions['G'].width = 12
                ws_summary.column_dimensions['H'].width = 12
                ws_summary.column_dimensions['I'].width = 12
                
                # Hoja 2: Detalle de Items
                ws_detail = wb.create_sheet(title="Detalle de Items")
                
                detail_headers = ["N° Factura", "Fecha", "Cliente", "Producto", "Cantidad", "Precio Unit.", "Subtotal"]
                for col, header in enumerate(detail_headers, 1):
                    cell = ws_detail.cell(row=1, column=col, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="10b981", end_color="10b981", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                
                detail_row = 2
                for sale in sales:
                    for item in sale.items:
                        ws_detail.cell(row=detail_row, column=1, value=sale.invoice_number)
                        ws_detail.cell(row=detail_row, column=2, value=sale.created_at.strftime("%d/%m/%Y %H:%M"))
                        ws_detail.cell(row=detail_row, column=3, value=sale.customer.name if sale.customer else "Cliente General")
                        ws_detail.cell(row=detail_row, column=4, value=item.product.name)
                        ws_detail.cell(row=detail_row, column=5, value=item.quantity)
                        ws_detail.cell(row=detail_row, column=6, value=item.unit_price)
                        ws_detail.cell(row=detail_row, column=7, value=item.subtotal)
                        detail_row += 1
                
                # Ajustar anchos de columna
                ws_detail.column_dimensions['A'].width = 15
                ws_detail.column_dimensions['B'].width = 18
                ws_detail.column_dimensions['C'].width = 25
                ws_detail.column_dimensions['D'].width = 30
                ws_detail.column_dimensions['E'].width = 10
                ws_detail.column_dimensions['F'].width = 12
                ws_detail.column_dimensions['G'].width = 12
                
                # Guardar archivo
                wb.save(file_path)
                
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Ventas exportadas correctamente\n\nArchivo: {file_path}\nTotal ventas: {len(sales)}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}\n\n{traceback.format_exc()}")
            finally:
                close_session()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def import_from_excel(self):
        """Importa ventas desde un archivo Excel"""
        try:
            # Seleccionar archivo
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo Excel",
                "",
                "Excel Files (*.xlsx *.xls)"
            )
            
            if not file_path:
                return
            
            # Mostrar mensaje de información sobre el formato esperado
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Formato de Excel para Importación")
            msg.setText("El archivo Excel debe tener las siguientes columnas en la primera hoja:")
            msg.setInformativeText(
                "Columnas requeridas:\n"
                "• N° Factura (único, no debe existir)\n"
                "• Fecha (DD/MM/YYYY o DD/MM/YYYY HH:MM)\n"
                "• Cliente\n"
                "• Método Pago (Efectivo/Tarjeta/Transferencia)\n"
                "• Estado (Completada/Pendiente/Cancelada)\n"
                "• Subtotal (número)\n"
                "• Impuesto (número)\n"
                "• Descuento (número)\n"
                "• Total (número)\n\n"
                "NOTA: Las facturas duplicadas serán omitidas.\n\n"
                "¿Desea continuar con la importación?"
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if msg.exec() != QMessageBox.StandardButton.Yes:
                return
            
            session = get_session()
            try:
                # Cargar archivo Excel
                wb = load_workbook(file_path)
                ws = wb.active
                
                # Validar encabezados para asegurarse de que es un archivo de ventas
                headers = [cell.value for cell in ws[1]]
                
                # Verificar que tenga encabezados relacionados con ventas
                expected_headers_keywords = ['factura', 'fecha', 'cliente', 'método pago', 'metodo pago', 'estado', 'subtotal', 'total']
                has_valid_headers = any(
                    any(keyword in str(header).lower() for keyword in expected_headers_keywords)
                    for header in headers if header
                )
                
                # Verificar que NO tenga encabezados de clientes o productos
                invalid_headers_keywords = ['teléfono', 'telefono', 'dirección', 'direccion', 'stock', 'precio venta', 'precio costo']
                has_invalid_headers = any(
                    any(keyword in str(header).lower() for keyword in invalid_headers_keywords)
                    for header in headers if header
                )
                
                if has_invalid_headers or not has_valid_headers:
                    QMessageBox.critical(
                        self,
                        "Formato Incorrecto",
                        "El archivo Excel no tiene el formato correcto para importar ventas.\n\n"
                        "Parece ser un archivo de clientes, productos u otro tipo de datos.\n\n"
                        "Por favor, seleccione un archivo Excel con el formato de ventas:\n"
                        "• N° Factura\n"
                        "• Fecha\n"
                        "• Cliente\n"
                        "• Método Pago\n"
                        "• Estado\n"
                        "• Subtotal\n"
                        "• Impuesto\n"
                        "• Descuento\n"
                        "• Total"
                    )
                    return
                
                imported_count = 0
                errors = []
                
                # Leer datos (empezando desde la fila 2, asumiendo que la 1 son encabezados)
                for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                    try:
                        if not row[0]:  # Si no hay número de factura, saltar
                            continue
                        
                        invoice_number = str(row[0])
                        
                        # Verificar si ya existe la factura
                        existing = session.query(Sale).filter_by(invoice_number=invoice_number).first()
                        if existing:
                            errors.append(f"Fila {row_idx}: Factura {invoice_number} ya existe")
                            continue
                        
                        # Parsear fecha
                        try:
                            from datetime import date
                            if isinstance(row[1], datetime):
                                sale_date = row[1]
                            elif isinstance(row[1], date):
                                # Convertir date a datetime
                                sale_date = datetime.combine(row[1], datetime.min.time())
                            elif row[1]:
                                date_str = str(row[1]).strip()
                                # Intentar varios formatos de fecha
                                for date_format in ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        sale_date = datetime.strptime(date_str, date_format)
                                        break
                                    except:
                                        continue
                                else:
                                    raise ValueError("Formato no reconocido")
                            else:
                                raise ValueError("Fecha vacía")
                        except Exception as e:
                            errors.append(f"Fila {row_idx}: Formato de fecha inválido '{row[1]}' - {str(e)}")
                            continue
                        
                        # Buscar o crear cliente
                        customer_name = str(row[2]) if row[2] else "Cliente General"
                        customer = session.query(Customer).filter_by(name=customer_name).first()
                        if not customer and customer_name != "Cliente General":
                            customer = Customer(
                                name=customer_name,
                                email="",
                                phone="",
                                address=""
                            )
                            session.add(customer)
                            session.flush()
                        
                        # Método de pago
                        payment_method_str = str(row[3]) if row[3] else "Efectivo"
                        try:
                            payment_method = PaymentMethod(payment_method_str)
                        except:
                            payment_method = PaymentMethod.CASH
                        
                        # Estado
                        status_str = str(row[4]) if row[4] else "Completada"
                        try:
                            status = SaleStatus(status_str)
                        except:
                            status = SaleStatus.COMPLETED
                        
                        # Valores numéricos
                        try:
                            subtotal = float(row[5]) if row[5] else 0.0
                            tax = float(row[6]) if row[6] else 0.0
                            discount = float(row[7]) if row[7] else 0.0
                            total = float(row[8]) if row[8] else 0.0
                        except:
                            errors.append(f"Fila {row_idx}: Valores numéricos inválidos")
                            continue
                        
                        # Crear venta
                        sale = Sale(
                            invoice_number=invoice_number,
                            customer_id=customer.id if customer else None,
                            payment_method=payment_method,
                            status=status,
                            subtotal=subtotal,
                            tax=tax,
                            discount=discount,
                            total=total,
                            created_at=sale_date
                        )
                        
                        session.add(sale)
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Fila {row_idx}: {str(e)}")
                        continue
                
                session.commit()
                
                # Mostrar resultado
                result_msg = f"Importación completada\n\nVentas importadas: {imported_count}"
                if errors:
                    result_msg += f"\n\nErrores encontrados:\n" + "\n".join(errors[:10])
                    if len(errors) > 10:
                        result_msg += f"\n... y {len(errors) - 10} errores más"
                
                QMessageBox.information(self, "Resultado de Importación", result_msg)
                self.load_sales()
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al importar: {str(e)}\n\n{traceback.format_exc()}")
            finally:
                close_session()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def clear_sales_table(self):
        """Limpia toda la tabla de ventas con confirmación"""
        try:
            # Primera confirmación
            reply = QMessageBox.question(
                self,
                "⚠️ Confirmar Limpieza",
                "¿Está seguro de que desea eliminar TODAS las ventas?\n\n"
                "Esta acción NO se puede deshacer y eliminará:\n"
                "• Todas las ventas registradas\n"
                "• Todos los items de ventas\n"
                "• Los movimientos de inventario NO se eliminarán\n\n"
                "¿Desea continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Segunda confirmación (seguridad adicional)
            reply2 = QMessageBox.warning(
                self,
                "⚠️ ÚLTIMA CONFIRMACIÓN",
                "Esta es su ÚLTIMA oportunidad para cancelar.\n\n"
                "¿Realmente desea eliminar TODAS las ventas de forma permanente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply2 != QMessageBox.StandardButton.Yes:
                return
            
            session = get_session()
            try:
                # Contar ventas antes de eliminar
                total_sales = session.query(Sale).count()
                total_items = session.query(SaleItem).count()
                
                if total_sales == 0:
                    QMessageBox.information(self, "Información", "No hay ventas para eliminar")
                    return
                
                # Eliminar todos los items de ventas primero (por la relación)
                session.query(SaleItem).delete()
                
                # Eliminar todas las ventas
                session.query(Sale).delete()
                
                session.commit()
                
                QMessageBox.information(
                    self,
                    "✅ Limpieza Completada",
                    f"Se han eliminado correctamente:\n\n"
                    f"• {total_sales} ventas\n"
                    f"• {total_items} items de ventas"
                )
                
                self.load_sales()
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al limpiar tabla: {str(e)}\n\n{traceback.format_exc()}")
            finally:
                close_session()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class NewSaleDialog(QDialog):
    """Diálogo para crear una nueva venta"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sale_items = []  # Lista de items de la venta
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Nueva Venta")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                background-color: transparent;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                color: #0f172a;
                background-color: white;
            }
            QTableWidget {
                color: #0f172a;
            }
            QTableWidget::item {
                color: #0f172a;
            }
            QGroupBox {
                color: #0f172a;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Sección superior - Info de la venta
        top_section = QGroupBox("Información de la Venta")
        top_layout = QFormLayout()
        
        # Cliente
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(35)
        self.load_customers()
        top_layout.addRow("Cliente:", self.customer_combo)
        
        # Método de pago
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(35)
        for method in PaymentMethod:
            self.payment_method_combo.addItem(method.value, method)
        top_layout.addRow("Método de Pago:", self.payment_method_combo)
        
        top_section.setLayout(top_layout)
        layout.addWidget(top_section)
        
        # Sección de productos
        products_section = QGroupBox("Productos")
        products_layout = QVBoxLayout()
        
        # Selector de producto
        add_product_layout = QHBoxLayout()
        
        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(35)
        self.load_products()
        add_product_layout.addWidget(QLabel("Producto:"))
        add_product_layout.addWidget(self.product_combo, 1)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(35)
        self.quantity_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        add_product_layout.addWidget(QLabel("Cantidad:"))
        add_product_layout.addWidget(self.quantity_spin)
        
        btn_add_product = QPushButton("Agregar")
        btn_add_product.setMinimumHeight(35)
        btn_add_product.clicked.connect(self.add_product_to_sale)
        add_product_layout.addWidget(btn_add_product)
        
        products_layout.addLayout(add_product_layout)
        
        # Tabla de productos agregados
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Producto", "Precio Unit.", "Cantidad", "Subtotal", "Acción"
        ])
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.items_table.setColumnWidth(4, 80)
        products_layout.addWidget(self.items_table)
        
        products_section.setLayout(products_layout)
        layout.addWidget(products_section)
        
        # Totales
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        totals_group = QGroupBox("Totales")
        totals_form = QFormLayout()
        
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        totals_form.addRow("Subtotal:", self.subtotal_label)
        
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setPrefix("$ ")
        self.tax_spin.setMaximum(999999)
        self.tax_spin.setMinimumHeight(35)
        self.tax_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.tax_spin.valueChanged.connect(self.calculate_total)
        totals_form.addRow("Impuesto:", self.tax_spin)
        
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setPrefix("$ ")
        self.discount_spin.setMaximum(999999)
        self.discount_spin.setMinimumHeight(35)
        self.discount_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.discount_spin.valueChanged.connect(self.calculate_total)
        totals_form.addRow("Descuento:", self.discount_spin)
        
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        totals_form.addRow("TOTAL:", self.total_label)
        
        totals_group.setLayout(totals_form)
        totals_layout.addWidget(totals_group)
        
        layout.addLayout(totals_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Completar Venta")
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(self.save_sale)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
    
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
    
    def load_products(self):
        """Carga los productos disponibles"""
        session = get_session()
        try:
            products = session.query(Product).filter(Product.stock > 0).all()
            for product in products:
                display_text = f"{product.name} - ${product.sale_price:.2f} (Stock: {product.stock})"
                self.product_combo.addItem(display_text, product.id)
        finally:
            close_session()
    
    def add_product_to_sale(self):
        """Agrega un producto a la venta"""
        product_id = self.product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        
        quantity = self.quantity_spin.value()
        
        session = get_session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            
            if not product:
                QMessageBox.warning(self, "Error", "Producto no encontrado")
                return
            
            if product.stock < quantity:
                QMessageBox.warning(
                    self, 
                    "Stock insuficiente", 
                    f"Solo hay {product.stock} unidades disponibles"
                )
                return
            
            # Agregar a la lista
            item_data = {
                'product_id': product.id,
                'product_name': product.name,
                'unit_price': product.sale_price,
                'quantity': quantity,
                'subtotal': product.sale_price * quantity
            }
            self.sale_items.append(item_data)
            
            # Actualizar tabla
            self.update_items_table()
            self.calculate_total()
            
        finally:
            close_session()
    
    def update_items_table(self):
        """Actualiza la tabla de items"""
        self.items_table.setRowCount(len(self.sale_items))
        
        for row, item in enumerate(self.sale_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"${item['subtotal']:.2f}"))
            
            # Botón eliminar
            btn_remove = QPushButton("Quitar")
            btn_remove.setFixedHeight(28)
            btn_remove.setStyleSheet("background-color: #ef4444; color: white;")
            btn_remove.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 4, btn_remove)
    
    def remove_item(self, row):
        """Elimina un item de la venta"""
        if row < len(self.sale_items):
            self.sale_items.pop(row)
            self.update_items_table()
            self.calculate_total()
    
    def calculate_total(self):
        """Calcula los totales"""
        subtotal = sum(item['subtotal'] for item in self.sale_items)
        tax = self.tax_spin.value()
        discount = self.discount_spin.value()
        total = subtotal + tax - discount
        
        self.subtotal_label.setText(f"${subtotal:,.2f}")
        self.total_label.setText(f"${total:,.2f}")
    
    def save_sale(self):
        """Guarda la venta"""
        if not self.sale_items:
            QMessageBox.warning(self, "Error", "Agregue al menos un producto")
            return
        
        session = get_session()
        try:
            # Crear venta
            sale = Sale()
            
            # Generar número de factura
            last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
            if last_sale:
                last_number = int(last_sale.invoice_number.split('-')[1])
                sale.invoice_number = f"INV-{last_number + 1:06d}"
            else:
                sale.invoice_number = "INV-000001"
            
            sale.customer_id = self.customer_combo.currentData()
            sale.payment_method = self.payment_method_combo.currentData()
            sale.tax = self.tax_spin.value()
            sale.discount = self.discount_spin.value()
            sale.status = SaleStatus.COMPLETED
            
            # Agregar items
            for item_data in self.sale_items:
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
            
            # Calcular total
            sale.calculate_total()
            
            session.add(sale)
            session.commit()
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Venta registrada correctamente\nFactura: {sale.invoice_number}\nTotal: ${sale.total:,.2f}"
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar venta: {str(e)}")
        finally:
            close_session()


class SaleDetailDialog(QDialog):
    """Diálogo para ver el detalle de una venta"""
    def __init__(self, parent=None, sale_id=None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.sale_data = None
        self.items_data = []
        self.load_sale()
        self.init_ui()
    
    def load_sale(self):
        """Carga la venta desde la base de datos"""
        session = get_session()
        try:
            from sqlalchemy.orm import joinedload
            sale = session.query(Sale).options(joinedload(Sale.items)).filter_by(id=self.sale_id).first()
            if not sale:
                QMessageBox.warning(self, "Error", "Venta no encontrada")
                return
            
            # Extraer datos de la venta
            self.sale_data = {
                'invoice_number': sale.invoice_number,
                'created_at': sale.created_at,
                'customer_name': sale.customer.name if sale.customer else "Cliente General",
                'payment_method': sale.payment_method.value,
                'status': sale.status.value,
                'subtotal': sale.subtotal,
                'tax': sale.tax,
                'discount': sale.discount,
                'total': sale.total
            }
            
            # Extraer datos de los items
            self.items_data = []
            for item in sale.items:
                self.items_data.append({
                    'product_name': item.product.name,
                    'unit_price': item.unit_price,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal
                })
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar venta: {str(e)}")
        finally:
            close_session()
    
    def init_ui(self):
        if not self.sale_data:
            self.reject()
            return
            
        self.setWindowTitle(f"Detalle de Venta - {self.sale_data['invoice_number']}")
        self.setMinimumSize(700, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
                background-color: transparent;
            }
            QTableWidget {
                color: #0f172a;
            }
            QTableWidget::item {
                color: #0f172a;
            }
            QGroupBox {
                color: #0f172a;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Información de la venta
        info_group = QGroupBox("Información General")
        info_layout = QFormLayout()
        
        info_layout.addRow("Factura:", QLabel(self.sale_data['invoice_number']))
        info_layout.addRow("Fecha:", QLabel(self.sale_data['created_at'].strftime("%d/%m/%Y %H:%M")))
        info_layout.addRow("Cliente:", QLabel(self.sale_data['customer_name']))
        info_layout.addRow("Método de Pago:", QLabel(self.sale_data['payment_method']))
        info_layout.addRow("Estado:", QLabel(self.sale_data['status']))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Tabla de productos
        products_group = QGroupBox("Productos")
        products_layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Producto", "Precio Unit.", "Cantidad", "Subtotal"])
        table.setRowCount(len(self.items_data))
        
        for row, item in enumerate(self.items_data):
            table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            table.setItem(row, 1, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            table.setItem(row, 3, QTableWidgetItem(f"${item['subtotal']:.2f}"))
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        products_layout.addWidget(table)
        products_group.setLayout(products_layout)
        layout.addWidget(products_group)
        
        # Totales
        totals_layout = QFormLayout()
        totals_layout.addRow("Subtotal:", QLabel(f"${self.sale_data['subtotal']:,.2f}"))
        totals_layout.addRow("Impuesto:", QLabel(f"${self.sale_data['tax']:,.2f}"))
        totals_layout.addRow("Descuento:", QLabel(f"${self.sale_data['discount']:,.2f}"))
        
        total_label = QLabel(f"${self.sale_data['total']:,.2f}")
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #10b981;")
        totals_layout.addRow("TOTAL:", total_label)
        
        layout.addLayout(totals_layout)
        
        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)