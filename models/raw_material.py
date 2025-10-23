"""
Modelo de Materia Prima - Materias primas del inventario
"""
from sqlalchemy import Column, String, Float, Integer, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel

class RawMaterial(BaseModel):
    """
    Materias primas para la fabricación de productos
    """
    __tablename__ = 'raw_materials'
    
    # Información básica
    name = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)  # Código único
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=False)  # Unidad de medida (kg, litros, unidades, etc.)
    
    # Precio e inventario
    cost_per_unit = Column(Float, default=0.0, nullable=False)  # Precio por unidad
    stock = Column(Float, default=0.0, nullable=False)  # Stock actual
    min_stock = Column(Float, default=5.0, nullable=False)  # Alerta de stock mínimo
    
    # Relaciones
    product_materials = relationship('ProductMaterial', back_populates='raw_material', cascade='all, delete-orphan')
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return self.stock <= self.min_stock
    
    def __repr__(self):
        return f"<RawMaterial(id={self.id}, sku={self.sku}, name={self.name}, stock={self.stock} {self.unit})>"

