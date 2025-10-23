"""
Vista de Materias Primas - Gestión de inventario de materias primas
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QTextEdit, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent
from config.database import get_session, close_session
from models import RawMaterial

class RawMaterialsView(QWidget):
    """Vista para gestionar materias primas"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_raw_materials()
    
    def showEvent(self, event: QShowEvent):
        """Evento que se ejecuta cuando la vista se muestra"""
        super().showEvent(event)
        # Auto-refrescar datos cuando se accede a la vista
        if event.spontaneous():
            return
        self.load_raw_materials()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestión de Materias Primas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        btn_new = QPushButton("+ Nueva Materia Prima")
        btn_new.setFixedHeight(40)
        btn_new.clicked.connect(self.create_new_material)
        header_layout.addWidget(btn_new)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o SKU...")
        self.search_input.textChanged.connect(self.search_materials)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("color: #0f172a;")
        filter_layout.addWidget(self.search_input)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_raw_materials)
        filter_layout.addWidget(btn_refresh)
        
        layout.addLayout(filter_layout)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "SKU", "Nombre", "Unidad", "Costo/Unidad", "Stock", "Acciones"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(3, 80)   # Unidad
        self.table.setColumnWidth(4, 120)  # Costo
        self.table.setColumnWidth(5, 100)  # Stock
        self.table.setColumnWidth(6, 220)  # Acciones
        
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # SKU
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nombre
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        
        layout.addWidget(self.table)
    
    def load_raw_materials(self):
        """Carga todas las materias primas"""
        session = get_session()
        try:
            materials = session.query(RawMaterial).all()
            
            self.table.setRowCount(len(materials))
            
            for row, material in enumerate(materials):
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(material.id)))
                
                # SKU
                self.table.setItem(row, 1, QTableWidgetItem(material.sku))
                
                # Nombre
                name_item = QTableWidgetItem(material.name)
                if material.is_low_stock:
                    name_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 2, name_item)
                
                # Unidad
                self.table.setItem(row, 3, QTableWidgetItem(material.unit))
                
                # Costo por unidad
                self.table.setItem(row, 4, QTableWidgetItem(f"${material.cost_per_unit:.2f}"))
                
                # Stock
                stock_item = QTableWidgetItem(f"{material.stock:.2f}")
                if material.is_low_stock:
                    stock_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 5, stock_item)
                
                # Botones de acción
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(8, 5, 8, 5)
                actions_layout.setSpacing(8)
                
                btn_edit = QPushButton("Editar")
                btn_edit.setFixedHeight(32)
                btn_edit.setMinimumWidth(80)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 500;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
                btn_edit.clicked.connect(lambda checked, m=material: self.edit_material(m))
                
                btn_delete = QPushButton("Eliminar")
                btn_delete.setFixedHeight(32)
                btn_delete.setMinimumWidth(80)
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
                btn_delete.clicked.connect(lambda checked, m=material: self.delete_material(m))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                
                self.table.setCellWidget(row, 6, actions_widget)
                self.table.setRowHeight(row, 50)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar materias primas: {str(e)}")
        finally:
            close_session()
    
    def search_materials(self, text):
        """Busca materias primas por nombre o SKU"""
        for row in range(self.table.rowCount()):
            sku = self.table.item(row, 1).text().lower()
            name = self.table.item(row, 2).text().lower()
            if text.lower() in sku or text.lower() in name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
    
    def create_new_material(self):
        """Crea una nueva materia prima"""
        dialog = MaterialDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_raw_materials()
    
    def edit_material(self, material):
        """Edita una materia prima existente"""
        dialog = MaterialDialog(self, material)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_raw_materials()
    
    def delete_material(self, material):
        """Elimina una materia prima"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la materia prima '{material.name}'?\n\n"
            "Esto eliminará también:\n"
            "- Todos los movimientos de materia prima relacionados\n"
            "- Todas las relaciones con productos\n"
            "- Los egresos relacionados (se pondrán como NULL)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                # Primero eliminar manualmente los movimientos y relaciones
                from models import RawMaterialMovement, ProductMaterial
                
                # Eliminar movimientos de materia prima
                session.query(RawMaterialMovement).filter_by(raw_material_id=material.id).delete()
                
                # Eliminar relaciones con productos
                session.query(ProductMaterial).filter_by(raw_material_id=material.id).delete()
                
                # Eliminar la materia prima
                material_to_delete = session.query(RawMaterial).filter_by(id=material.id).first()
                session.delete(material_to_delete)
                
                session.commit()
                QMessageBox.information(self, "Éxito", "Materia prima eliminada correctamente")
                self.load_raw_materials()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar materia prima: {str(e)}")
            finally:
                close_session()


class MaterialDialog(QDialog):
    """Diálogo para crear/editar una materia prima"""
    def __init__(self, parent=None, material=None):
        super().__init__(parent)
        self.material = material
        self.is_edit = material is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_material_data()
    
    def init_ui(self):
        title = "Editar Materia Prima" if self.is_edit else "Nueva Materia Prima"
        self.setWindowTitle(title)
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
        form = QFormLayout()
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Ej: MP-001")
        form.addRow("SKU*:", self.sku_input)
        
        # Nombre
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Harina de trigo")
        form.addRow("Nombre*:", self.name_input)
        
        # Descripción
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Descripción opcional...")
        form.addRow("Descripción:", self.description_input)
        
        # Unidad de medida
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "kg", "gramos", "litros", "ml", "unidades", "metros", "cm", "cajas", "paquetes"
        ])
        self.unit_combo.setEditable(True)
        form.addRow("Unidad de medida*:", self.unit_combo)
        
        # Costo por unidad
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setPrefix("$ ")
        self.cost_input.setMaximum(999999.99)
        self.cost_input.setDecimals(2)
        form.addRow("Costo por unidad*:", self.cost_input)
        
        # Stock
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setMaximum(999999.99)
        self.stock_input.setDecimals(2)
        form.addRow("Stock actual:", self.stock_input)
        
        # Stock mínimo
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(999999.99)
        self.min_stock_input.setDecimals(2)
        self.min_stock_input.setValue(5.0)
        form.addRow("Stock mínimo:", self.min_stock_input)
        
        layout.addLayout(form)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_material)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
    
    def load_material_data(self):
        """Carga los datos de la materia prima en el formulario"""
        self.sku_input.setText(self.material.sku)
        self.name_input.setText(self.material.name)
        if self.material.description:
            self.description_input.setPlainText(self.material.description)
        
        # Buscar la unidad en el combo o agregarla
        index = self.unit_combo.findText(self.material.unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        else:
            self.unit_combo.setCurrentText(self.material.unit)
        
        self.cost_input.setValue(float(self.material.cost_per_unit))
        self.stock_input.setValue(float(self.material.stock))
        self.min_stock_input.setValue(float(self.material.min_stock))
    
    def save_material(self):
        """Guarda la materia prima"""
        # Validaciones
        sku = self.sku_input.text().strip()
        name = self.name_input.text().strip()
        unit = self.unit_combo.currentText().strip()
        
        if not sku or not name or not unit:
            QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios (*).")
            return
        
        session = get_session()
        try:
            if self.is_edit:
                # Editar existente
                material = session.query(RawMaterial).filter_by(id=self.material.id).first()
                
                # Verificar SKU único (excepto el actual)
                existing = session.query(RawMaterial).filter(
                    RawMaterial.sku == sku,
                    RawMaterial.id != material.id
                ).first()
                if existing:
                    QMessageBox.warning(self, "Error", f"El SKU '{sku}' ya está en uso.")
                    return
            else:
                # Crear nuevo
                existing = session.query(RawMaterial).filter_by(sku=sku).first()
                if existing:
                    QMessageBox.warning(self, "Error", f"El SKU '{sku}' ya está en uso.")
                    return
                
                material = RawMaterial()
            
            # Asignar valores
            material.sku = sku
            material.name = name
            material.description = self.description_input.toPlainText().strip() or None
            material.unit = unit
            material.cost_per_unit = self.cost_input.value()
            material.stock = self.stock_input.value()
            material.min_stock = self.min_stock_input.value()
            
            if not self.is_edit:
                session.add(material)
            
            session.commit()
            
            action = "actualizada" if self.is_edit else "creada"
            QMessageBox.information(self, "Éxito", f"Materia prima {action} correctamente.")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar materia prima: {str(e)}")
        finally:
            close_session()

