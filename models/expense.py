"""
Modelo de Egreso - Registro de salidas de productos/materias primas sin venta
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum

# Importar PaymentMethod desde sale (o definir aquí si es necesario)
try:
    from models.sale import PaymentMethod
except ImportError:
    # Si no se puede importar, definir aquí
    class PaymentMethod(enum.Enum):
        """Métodos de pago disponibles"""
        CASH = "Efectivo"
        CARD = "Tarjeta"
        TRANSFER = "Transferencia"
        OTHER = "Otro"

class ExpenseType(enum.Enum):
    """Tipos de egreso"""
    PRODUCT = "Producto"
    RAW_MATERIAL = "Materia Prima"
    CASH = "Efectivo"

class ExpenseReason(enum.Enum):
    """Razones de egreso"""
    DAMAGED = "Dañado/Vencido"
    LOST = "Pérdida/Robo"
    SAMPLE = "Muestra"
    DONATION = "Donación"
    PERSONAL_USE = "Uso Personal"
    WASTE = "Merma/Desperdicio"
    OTHER = "Otro"

class Expense(BaseModel):
    """
    Registro de salidas de productos o materias primas que no son ventas
    """
    __tablename__ = 'expenses'
    
    # Tipo de egreso
    expense_type = Column(SQLEnum(ExpenseType), nullable=False)
    
    # Razón del egreso
    reason = Column(SQLEnum(ExpenseReason), nullable=False)
    
    # Puede ser producto o materia prima (solo uno será no nulo)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    raw_material_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=True)
    
    # Relaciones
    product = relationship('Product', foreign_keys=[product_id])
    raw_material = relationship('RawMaterial', foreign_keys=[raw_material_id])
    
    # Cantidad que salió
    quantity = Column(Float, nullable=False)
    
    # Monto/Valor del egreso (para todos los tipos)
    amount = Column(Float, nullable=True)  # Monto en dinero del egreso
    
    # Método de pago (cuando el egreso es salida de efectivo)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    
    # Tipo de transferencia (cuando payment_method es TRANSFER)
    transfer_type = Column(String(100), nullable=True)  # Nequi, Daviplata, Bancolombia, Otro, etc.
    
    # Destinatario del egreso
    recipient = Column(String(200), nullable=True)
    
    # Si el egreso está autorizado
    is_authorized = Column(Integer, default=0, nullable=False)  # 0 = No autorizado, 1 = Autorizado
    
    # Descripción adicional
    notes = Column(String(500), nullable=True)
    
    def __repr__(self):
        item_name = ""
        if self.product:
            item_name = self.product.name
        elif self.raw_material:
            item_name = self.raw_material.name
        return f"<Expense(tipo={self.expense_type.value}, item={item_name}, qty={self.quantity})>"

