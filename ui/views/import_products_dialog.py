"""
Diálogo para importar productos desde archivo CSV/Excel
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QCheckBox, QSpinBox, QFormLayout,
    QGroupBox, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from utils.product_importer import ProductImporter
import traceback

class ImportWorker(QThread):
    """Worker thread para importar productos sin bloquear la UI"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, file_path, default_stock, update_existing):
        super().__init__()
        self.file_path = file_path
        self.default_stock = default_stock
        self.update_existing = update_existing
    
    def run(self):
        """Ejecuta la importación"""
        importer = ProductImporter()
        
        # Determinar si es CSV o Excel
        if self.file_path.lower().endswith('.csv'):
            result = importer.import_from_csv(
                self.file_path, 
                self.default_stock, 
                self.update_existing
            )
        else:
            result = importer.import_from_excel(
                self.file_path, 
                self.default_stock, 
                self.update_existing
            )
        
        self.finished.emit(result)

class ImportProductsDialog(QDialog):
    """Diálogo para importar productos y materias primas desde CSV/Excel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Importar Productos desde CSV/Excel")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0f172a;
            }
            QGroupBox {
                color: #0f172a;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Importar Productos y Materias Primas")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Información sobre el formato
        info_group = QGroupBox("Formato del Archivo")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "El archivo debe tener las siguientes columnas:\n\n"
            "• CODIGO: Código del producto\n"
            "• PRODUCTO: Nombre del producto\n"
            "• VALOR UNITARIO: Precio de venta (formato: $ 5.000)\n"
            "• Columnas de materias primas con cantidades\n\n"
            "Materias primas soportadas:\n"
            "ACEITE, MAIZ, SAL, CARAMELO, QUESO, LIMON, TOCINETA,\n"
            "COLORES, BOLSA NORMAL, BOLSA AL MAYOR, CAJA POPETA,\n"
            "JUGUETE, GRANIZADO, VASOS, PITILLOS, PERLAS,\n"
            "TOPIN GOMAS, GASEOSA, AGUA, AZUCAR, VASO ALGODÓN, PICANTE\n\n"
            "Formatos soportados: CSV (.csv) y Excel (.xlsx)"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #475569; font-size: 12px; padding: 10px;")
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Selección de archivo
        file_group = QGroupBox("Seleccionar Archivo")
        file_layout = QVBoxLayout()
        
        file_select_layout = QHBoxLayout()
        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setStyleSheet("color: #64748b; font-size: 13px;")
        file_select_layout.addWidget(self.file_label)
        
        btn_select_file = QPushButton("📁 Seleccionar Archivo")
        btn_select_file.setFixedHeight(35)
        btn_select_file.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_select_file.clicked.connect(self.select_file)
        file_select_layout.addWidget(btn_select_file)
        
        file_layout.addLayout(file_select_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Opciones de importación
        options_group = QGroupBox("Opciones de Importación")
        options_layout = QFormLayout()
        
        # Stock inicial
        self.stock_spin = QSpinBox()
        self.stock_spin.setMinimum(0)
        self.stock_spin.setMaximum(10000)
        self.stock_spin.setValue(100)
        self.stock_spin.setSuffix(" unidades")
        self.stock_spin.setStyleSheet("""
            QSpinBox {
                font-size: 13px;
                padding: 5px;
                color: #0f172a;
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
            QSpinBox:focus {
                border-color: #3b82f6;
            }
        """)
        options_layout.addRow("Stock inicial para productos nuevos:", self.stock_spin)
        
        # Actualizar existentes
        self.update_existing_check = QCheckBox("Actualizar productos existentes")
        self.update_existing_check.setStyleSheet("font-size: 13px;")
        self.update_existing_check.setChecked(False)
        options_layout.addRow("", self.update_existing_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Área de resultados
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        self.results_text.setVisible(False)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 12px;
                background-color: #f8fafc;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.setFixedWidth(120)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        self.btn_import = QPushButton("Importar")
        self.btn_import.setFixedHeight(40)
        self.btn_import.setFixedWidth(120)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #6b7280;
            }
        """)
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self.start_import)
        buttons_layout.addWidget(self.btn_import)
        
        layout.addLayout(buttons_layout)
    
    def select_file(self):
        """Abre el diálogo para seleccionar archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo CSV o Excel",
            "",
            "Archivos CSV/Excel (*.csv *.xlsx);;Archivos CSV (*.csv);;Archivos Excel (*.xlsx)"
        )
        
        if file_path:
            self.file_path = file_path
            import os
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
            self.btn_import.setEnabled(True)
    
    def start_import(self):
        """Inicia el proceso de importación"""
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Por favor seleccione un archivo")
            return
        
        # Confirmar importación
        reply = QMessageBox.question(
            self,
            "Confirmar Importación",
            f"¿Está seguro de importar productos desde:\n{self.file_path}?\n\n"
            f"Stock inicial: {self.stock_spin.value()} unidades\n"
            f"Actualizar existentes: {'Sí' if self.update_existing_check.isChecked() else 'No'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Deshabilitar botones durante la importación
        self.btn_import.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.results_text.setVisible(False)
        self.results_text.clear()
        
        # Crear y ejecutar worker
        self.worker = ImportWorker(
            self.file_path,
            self.stock_spin.value(),
            self.update_existing_check.isChecked()
        )
        self.worker.finished.connect(self.on_import_finished)
        self.worker.start()
    
    def on_import_finished(self, result):
        """Maneja el fin de la importación"""
        # Restaurar UI
        self.progress_bar.setVisible(False)
        self.btn_cancel.setEnabled(True)
        self.results_text.setVisible(True)
        
        # Mostrar resultados
        if result['success']:
            results_html = f"""
            <h3 style="color: #10b981;">✅ Importación Exitosa</h3>
            <p><b>Productos creados:</b> {result['created_products']}</p>
            <p><b>Productos actualizados:</b> {result['updated_products']}</p>
            <p><b>Materias primas creadas:</b> {result['created_materials']}</p>
            <p><b>Relaciones producto-materia prima:</b> {result['created_relations']}</p>
            """
            
            if result.get('warnings'):
                results_html += f"<p><b>Advertencias:</b> {len(result['warnings'])}</p>"
            
            if result.get('errors'):
                results_html += f"<p style='color: #ef4444;'><b>Errores:</b> {len(result['errors'])}</p>"
            
            self.results_text.setHtml(results_html)
            
            # Mostrar mensaje de éxito
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Importación Exitosa")
            msg.setText(f"Se importaron {result['created_products']} productos correctamente")
            
            if result.get('warnings') or result.get('errors'):
                details = ""
                if result.get('warnings'):
                    details += "\n".join(result['warnings'][:20])
                    if len(result['warnings']) > 20:
                        details += f"\n... y {len(result['warnings']) - 20} advertencias más"
                
                if result.get('errors'):
                    details += "\n\nERRORES:\n"
                    details += "\n".join(result['errors'][:10])
                    if len(result['errors']) > 10:
                        details += f"\n... y {len(result['errors']) - 10} errores más"
                
                msg.setDetailedText(details)
            
            msg.exec()
            
            # Cerrar diálogo si todo salió bien
            if not result.get('errors'):
                self.accept()
        else:
            # Mostrar error
            error_html = f"""
            <h3 style="color: #ef4444;">❌ Error en la Importación</h3>
            <p><b>Error:</b> {result.get('error', 'Error desconocido')}</p>
            """
            self.results_text.setHtml(error_html)
            
            QMessageBox.critical(
                self,
                "Error",
                f"Error al importar productos:\n\n{result.get('error', 'Error desconocido')}"
            )
            
            self.btn_import.setEnabled(True)
