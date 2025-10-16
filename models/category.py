"""
Modelo de Categoría - Para organizar productos
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Category(BaseModel):
    """
    Categorías de productos (ej: Electrónica, Ropa, Alimentos)
    """
    __tablename__ = 'categories'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relación con productos
    products = relationship('Product', back_populates='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"