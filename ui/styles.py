"""
Estilos y temas de la aplicación
"""

# Colores principales
PRIMARY_COLOR = "#2563eb"  # Azul
SECONDARY_COLOR = "#64748b"  # Gris azulado
SUCCESS_COLOR = "#10b981"  # Verde
DANGER_COLOR = "#ef4444"  # Rojo
WARNING_COLOR = "#f59e0b"  # Naranja
BACKGROUND_COLOR = "#f8fafc"  # Gris muy claro
SIDEBAR_COLOR = "#1e293b"  # Gris oscuro
TEXT_COLOR = "#0f172a"  # Negro azulado
TEXT_LIGHT = "#64748b"  # Gris para texto secundario

# Stylesheet principal de la aplicación
MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {BACKGROUND_COLOR};
}}

/* Sidebar - Barra lateral de navegación */
#sidebar {{
    background-color: {SIDEBAR_COLOR};
    border-right: 1px solid #334155;
}}

#sidebar QPushButton {{
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    border-radius: 6px;
    margin: 4px 8px;
}}

#sidebar QPushButton:hover {{
    background-color: #334155;
    color: white;
}}

#sidebar QPushButton:checked {{
    background-color: {PRIMARY_COLOR};
    color: white;
    font-weight: bold;
}}

/* Barra superior */
#topbar {{
    background-color: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 10px;
}}

#topbar QLabel {{
    color: {TEXT_COLOR};
    font-size: 18px;
    font-weight: bold;
}}

/* Botones generales */
QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #1d4ed8;
}}

QPushButton:pressed {{
    background-color: #1e40af;
}}

QPushButton:disabled {{
    background-color: #cbd5e1;
    color: #94a3b8;
}}

/* Botones secundarios */
QPushButton[class="secondary"] {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton[class="secondary"]:hover {{
    background-color: #475569;
}}

/* Botón de éxito */
QPushButton.success {{
    background-color: {SUCCESS_COLOR};
}}

QPushButton.success:hover {{
    background-color: #059669;
}}

/* Botón de peligro */
QPushButton[class="danger"] {{
    background-color: {DANGER_COLOR};
}}

QPushButton[class="danger"]:hover {{
    background-color: #dc2626;
}}

/* Inputs y text fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: white;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 2px solid {PRIMARY_COLOR};
}}

/* ComboBox */
QComboBox {{
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: white;
    font-size: 14px;
}}

QComboBox:hover {{
    border: 1px solid {PRIMARY_COLOR};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

/* SpinBox */
QSpinBox, QDoubleSpinBox {{
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: white;
    font-size: 14px;
}}

/* Tables */
QTableWidget {{
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: white;
    gridline-color: #e2e8f0;
    color: {TEXT_COLOR};
}}

QTableWidget::item {{
    padding: 8px;
    color: {TEXT_COLOR};
}}

QTableWidget::item:selected {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}

QHeaderView::section {{
    background-color: #f1f5f9;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: bold;
    color: {TEXT_COLOR};
}}

/* Scrollbar */
QScrollBar:vertical {{
    border: none;
    background-color: #f1f5f9;
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: #cbd5e1;
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #94a3b8;
}}

/* Labels */
QLabel {{
    color: {TEXT_COLOR};
    font-size: 14px;
}}

QLabel.title {{
    font-size: 24px;
    font-weight: bold;
    color: {TEXT_COLOR};
}}

QLabel.subtitle {{
    font-size: 16px;
    font-weight: 600;
    color: {TEXT_COLOR};
}}

QLabel.hint {{
    color: {TEXT_LIGHT};
    font-size: 12px;
}}

/* Dialog - Diálogos */
QDialog {{
    background-color: white;
}}

QDialog QLabel {{
    color: {TEXT_COLOR};
    font-size: 13px;
    background-color: transparent;
}}

QDialog QPushButton {{
    min-width: 80px;
}}

/* Widgets dentro de tablas */
QTableWidget QWidget {{
    background-color: transparent;
}}

QTableWidget QPushButton {{
    min-width: 60px;
    padding: 5px 10px;
}}

/* GroupBox */
QGroupBox {{
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    background-color: white;
}}

QGroupBox::title {{
    color: {TEXT_COLOR};
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}
"""