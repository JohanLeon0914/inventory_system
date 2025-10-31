"""
Modelo de Movimiento de Materia Prima - Historial de entradas/salidas de materias primas
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum

class RawMaterialMovementType(enum.Enum):
    """Tipos de movimientos de materias primas"""
    PURCHASE = "Compra"  # Entrada por compra
    ADJUSTMENT = "Ajuste"  # Ajuste manual
    PRODUCTION = "Producción"  # Salida por producción/venta
    RETURN = "Devolución"  # Entrada por devolución
    WASTE = "Merma"  # Salida por desperdicio

class RawMaterialMovement(BaseModel):
    """
    Registro de movimientos de materias primas
    """
    __tablename__ = 'raw_material_movements'
    
    # Relación con materia prima
    raw_material_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
    raw_material = relationship('RawMaterial', backref='movements')
    
    # Tipo de movimiento
    movement_type = Column(SQLEnum(RawMaterialMovementType), nullable=False)
    
    # Cantidad (positivo = entrada, negativo = salida)
    quantity = Column(Float, nullable=False)
    
    # Costo del movimiento (para compras)
    cost = Column(Float, default=0.0)
    
    # Referencia (ID de venta, orden de compra, etc.)
    reference = Column(String(100), nullable=True)
    
    # Razón del movimiento
    reason = Column(String(500), nullable=True)
    
    # Nota adicional (anotación personalizada)
    note = Column(String(500), nullable=True)  # Nota adicional del usuario
    
    # Usuario que realizó el movimiento (opcional)
    user = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<RawMaterialMovement(id={self.id}, material_id={self.raw_material_id}, qty={self.quantity})>"

