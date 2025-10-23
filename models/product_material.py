"""
Modelo ProductMaterial - Relación entre productos y materias primas
Define qué materias primas y en qué cantidad necesita cada producto
"""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class ProductMaterial(BaseModel):
    """
    Tabla de relación entre productos y materias primas
    Define la receta/composición de cada producto
    """
    __tablename__ = 'product_materials'
    
    # Relaciones
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    raw_material_id = Column(Integer, ForeignKey('raw_materials.id'), nullable=False)
    
    # Cantidad de materia prima que necesita el producto
    quantity_needed = Column(Float, nullable=False, default=1.0)
    
    # Relaciones bidireccionales
    product = relationship('Product', back_populates='product_materials')
    raw_material = relationship('RawMaterial', back_populates='product_materials')
    
    def __repr__(self):
        return f"<ProductMaterial(product_id={self.product_id}, raw_material_id={self.raw_material_id}, qty={self.quantity_needed})>"

