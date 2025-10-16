"""
Modelo de Item de Venta - Productos individuales en una venta
"""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class SaleItem(BaseModel):
    """
    Items individuales de una venta (detalle de productos vendidos)
    """
    __tablename__ = 'sale_items'
    
    # Venta a la que pertenece
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    sale = relationship('Sale', back_populates='items')
    
    # Producto vendido
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship('Product', back_populates='sale_items')
    
    # Cantidad y precios
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)  # Precio al momento de la venta
    subtotal = Column(Float, nullable=False)    # quantity * unit_price
    
    def calculate_subtotal(self):
        """Calcula el subtotal del item"""
        self.subtotal = self.quantity * self.unit_price
    
    def __repr__(self):
        return f"<SaleItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"