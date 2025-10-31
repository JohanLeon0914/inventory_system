"""
Modelo de Movimiento de Inventario - Historial de entradas y salidas
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum

class MovementType(enum.Enum):
    """Tipos de movimiento de inventario"""
    ENTRY = "Entrada"      # Compra, devolución, ajuste positivo
    EXIT = "Salida"        # Venta, pérdida, ajuste negativo
    ADJUSTMENT = "Ajuste"  # Ajuste manual de inventario

class InventoryMovement(BaseModel):
    """
    Registro de movimientos de inventario (entradas/salidas)
    Útil para auditoría y trazabilidad
    """
    __tablename__ = 'inventory_movements'
    
    # Producto afectado
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship('Product', back_populates='inventory_movements')
    
    # Tipo de movimiento
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    
    # Cantidad (positiva para entradas, negativa para salidas)
    quantity = Column(Integer, nullable=False)
    
    # Stock antes y después del movimiento (para auditoría)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Razón del movimiento
    reason = Column(String(200), nullable=True)  # "Venta", "Compra a proveedor X", etc.
    
    # Razón de edición (si el movimiento fue editado)
    edit_reason = Column(String(500), nullable=True)  # Razón de por qué se editó
    
    # Nota adicional (anotación personalizada)
    note = Column(String(500), nullable=True)  # Nota adicional del usuario
    
    # Referencia (ID de venta, egreso, etc.)
    reference = Column(String(100), nullable=True)  # Referencia a otra entidad (venta, etc.)
    
    # Usuario que realizó el movimiento (opcional, para futuro)
    user = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<InventoryMovement(product_id={self.product_id}, type={self.movement_type.value}, qty={self.quantity})>"