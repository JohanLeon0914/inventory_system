"""
Diálogo para generar factura legal colombiana
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QMessageBox, QFileDialog, QWidget, QFormLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtGui import QTextDocument
from datetime import datetime
from config.database import get_session, close_session
from models import Sale, CompanyInfo

class InvoiceDialog(QDialog):
    """Diálogo para generar y mostrar factura legal colombiana"""
    
    def __init__(self, parent=None, sale=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle("📄 Factura de Venta")
        self.setMinimumSize(560, 520)
        self.resize(600, 650)
        self.setModal(True)
        self.init_ui()
        self.load_sale_data()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.adjust_dialog_height()
    
    def adjust_dialog_height(self):
        """Reduce la altura para que siempre sea menor que la ventana principal."""
        parent_height = self.parent().height() if self.parent() else None
        if parent_height and parent_height > 200:
            target_height = max(480, min(parent_height - 60, int(parent_height * 0.85)))
        else:
            target_height = 650
        self.resize(self.width(), target_height)
    
    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #0f172a; font-size: 13px; }
            QPushButton {
                background-color: #2563eb; color: white; border: none; border-radius: 6px;
                font-size: 14px; font-weight: 500; padding: 8px 15px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton#printButton {
                background-color: #10b981;
            }
            QPushButton#printButton:hover {
                background-color: #059669;
            }
            QPushButton#cancelButton {
                background-color: #64748b;
            }
            QPushButton#cancelButton:hover {
                background-color: #475569;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Área de factura
        self.invoice_area = QTextEdit()
        self.invoice_area.setReadOnly(True)
        self.invoice_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.invoice_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.invoice_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 20px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.invoice_area, stretch=1)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_print = QPushButton("🖨️ Imprimir")
        btn_print.setObjectName("printButton")
        btn_print.clicked.connect(self.print_invoice)
        buttons_layout.addWidget(btn_print)
        
        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("cancelButton")
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_close)
        
        layout.addLayout(buttons_layout)
    
    def load_sale_data(self):
        """Carga los datos de la venta y genera el HTML de la factura"""
        session = get_session()
        try:
            sale = session.query(Sale).filter_by(id=self.sale.id).first()
            if not sale:
                QMessageBox.critical(self, "Error", "Venta no encontrada.")
                return
            
            # Cargar información de la empresa
            company_info = session.query(CompanyInfo).first()
            if not company_info:
                company_info = CompanyInfo()  # Valores por defecto
            
            # Generar HTML de la factura
            invoice_html = self.generate_invoice_html(sale, company_info)
            self.invoice_area.setHtml(invoice_html)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
        finally:
            close_session()
    
    def generate_invoice_html(self, sale, company_info):
        """Genera el HTML de la factura legal colombiana"""
        # Información de la empresa desde la base de datos
        company_name = company_info.company_name
        company_nit = company_info.company_nit
        company_address = company_info.company_address or "N/A"
        company_city = company_info.company_city or "N/A"
        company_phone = company_info.company_phone or "N/A"
        company_email = company_info.company_email or "N/A"
        company_regimen = company_info.company_regimen or "N/A"
        
        # Cliente
        customer_name = sale.customer.name if sale.customer else "Cliente General"
        customer_doc = "N/A"
        customer_address = "N/A"
        
        if sale.customer:
            if sale.customer.document_number:
                customer_doc = f"{sale.customer.document_type or 'CC'}: {sale.customer.document_number}"
            if sale.customer.address:
                customer_address = sale.customer.address
        
        # Items
        items_html = ""
        for item in sale.items:
            items_html += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 8px; text-align: left;">{item.product.name}</td>
                <td style="padding: 8px; text-align: center;">{item.quantity}</td>
                <td style="padding: 8px; text-align: right;">${item.unit_price:,.0f}</td>
                <td style="padding: 8px; text-align: right;">${item.subtotal:,.0f}</td>
            </tr>
            """
        
        # Totales
        subtotal = sale.subtotal
        tax = sale.tax
        total = sale.total
        
        # Formatear fecha
        sale_date = sale.created_at.strftime("%d/%m/%Y %I:%M %p")
        invoice_date = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        
        # Método de pago
        payment_method = sale.payment_method.value
        if sale.payment_method.value == "Transferencia" and sale.transfer_type:
            payment_method += f" ({sale.transfer_type})"
        
        # Generar HTML completo
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                * {{ color: #000000 !important; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px;
                    color: #000000;
                }}
                .invoice-container {{ 
                    max-width: 80mm; 
                    margin: 0 auto; 
                    background: white;
                    color: #000000;
                }}
                .header {{ 
                    text-align: center; 
                    border-bottom: 2px solid #000; 
                    padding-bottom: 15px; 
                    margin-bottom: 20px;
                    color: #000000;
                }}
                .header h1 {{ 
                    margin: 0; 
                    font-size: 22px; 
                    font-weight: bold;
                    color: #000000;
                }}
                .header h2 {{ 
                    margin: 5px 0; 
                    font-size: 14px; 
                    color: #000000;
                    font-weight: bold;
                }}
                .info-section {{ 
                    margin-bottom: 15px;
                    color: #000000;
                }}
                .info-row {{ 
                    display: flex; 
                    justify-content: space-between; 
                    margin-bottom: 5px; 
                    font-size: 11px;
                    color: #000000;
                }}
                .info-row strong {{ 
                    min-width: 80px;
                    color: #000000;
                    font-weight: bold;
                }}
                .items-table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-bottom: 15px; 
                    font-size: 10px;
                }}
                .items-table th {{ 
                    background-color: #e5e7eb; 
                    padding: 8px; 
                    text-align: left; 
                    border-bottom: 1px solid #000;
                    color: #000000;
                    font-weight: bold;
                }}
                .items-table td {{ 
                    padding: 6px;
                    color: #000000;
                }}
                .totals {{ 
                    border-top: 2px solid #000; 
                    padding-top: 10px;
                    color: #000000;
                }}
                .total-row {{ 
                    display: flex; 
                    justify-content: space-between; 
                    margin-bottom: 5px; 
                    font-size: 12px;
                    color: #000000;
                }}
                .total-row.final {{ 
                    font-weight: bold; 
                    font-size: 16px; 
                    border-top: 1px solid #000; 
                    padding-top: 10px; 
                    margin-top: 10px;
                    color: #000000;
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 20px; 
                    padding-top: 15px; 
                    border-top: 1px solid #ccc; 
                    font-size: 10px; 
                    color: #000000;
                }}
                .footer p {{
                    margin: 5px 0;
                    color: #000000;
                }}
                @media print {{
                    body {{ margin: 0; padding: 0; }}
                    .invoice-container {{ max-width: 100%; }}
                }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <!-- Encabezado -->
                <div class="header">
                    <h1>FACTURA DE VENTA</h1>
                    <h2>{company_name}</h2>
                    <div style="font-size: 11px; margin-top: 5px; color: #000000; font-weight: bold;">
                        NIT: {company_nit}<br>
                        {company_regimen}
                    </div>
                </div>
                
                <!-- Información de la factura -->
                <div class="info-section">
                    <div class="info-row">
                        <strong>No. Factura:</strong>
                        <span>{sale.invoice_number}</span>
                    </div>
                    <div class="info-row">
                        <strong>Fecha y Hora:</strong>
                        <span>{invoice_date}</span>
                    </div>
                    <div class="info-row">
                        <strong>Fecha de Venta:</strong>
                        <span>{sale_date}</span>
                    </div>
                </div>
                
                <!-- Cliente -->
                <div class="info-section">
                    <strong style="font-size: 12px; text-decoration: underline; color: #000000; font-weight: bold;">CLIENTE:</strong>
                    <div class="info-row">
                        <strong>Nombre:</strong>
                        <span>{customer_name}</span>
                    </div>
                    <div class="info-row">
                        <strong>Documento:</strong>
                        <span>{customer_doc}</span>
                    </div>
                    <div class="info-row">
                        <strong>Dirección:</strong>
                        <span>{customer_address}</span>
                    </div>
                </div>
                
                <!-- Items -->
                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="width: 50%;">Producto</th>
                            <th style="width: 15%;">Cant.</th>
                            <th style="width: 20%;">Precio</th>
                            <th style="width: 15%;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <!-- Totales -->
                <div class="totals">
                    <div class="total-row">
                        <span>Subtotal:</span>
                        <span>${subtotal:,.0f}</span>
                    </div>
                    {f'<div class="total-row"><span>IVA (19%):</span><span>${tax:,.0f}</span></div>' if tax > 0 else ''}
                    <div class="total-row final">
                        <span>TOTAL A PAGAR:</span>
                        <span>${total:,.0f}</span>
                    </div>
                </div>
                
                <!-- Método de pago -->
                <div class="info-section">
                    <div class="info-row">
                        <strong>Método de Pago:</strong>
                        <span>{payment_method}</span>
                    </div>
                </div>
                
                <!-- Pie de página -->
                <div class="footer">
                    <p style="margin: 5px 0;"><strong>¡GRACIAS POR SU COMPRA!</strong></p>
                    <p style="margin: 5px 0;">Esta factura cumple con la normativa<br>contable colombiana (DIAN)</p>
                    <p style="margin: 5px 0; font-size: 9px;">
                        {company_address}<br>
                        {company_city}<br>
                        Tel: {company_phone} | Email: {company_email}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def print_invoice(self):
        """Imprime la factura"""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPrinter.PageSize.Custom)
        printer.setPaperSize(QSize(80, 297), QPrinter.Unit.Millimeter)  # 80mm x rollo
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            document = QTextDocument()
            document.setHtml(self.invoice_area.toHtml())
            document.print(printer)
            
            QMessageBox.information(self, "Éxito", "Factura enviada a impresión.")
