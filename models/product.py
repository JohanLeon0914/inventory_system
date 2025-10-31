"""
Modelo de Producto - Productos del inventario
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Product(BaseModel):
    """
    Productos en el inventario
    """
    __tablename__ = 'products'
    
    # Información básica
    name = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)  # Código único del producto
    description = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)  # Ruta de la imagen del producto
    
    # Categoría
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    category = relationship('Category', back_populates='products')
    
    # Precios
    cost_price = Column(Float, default=0.0, nullable=False)  # Precio de costo
    sale_price = Column(Float, default=0.0, nullable=False)  # Precio de venta
    
    # Inventario
    stock = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=5, nullable=False)  # Alerta de stock mínimo
    
    # Relaciones
    sale_items = relationship('SaleItem', back_populates='product')
    inventory_movements = relationship('InventoryMovement', back_populates='product')
    product_materials = relationship('ProductMaterial', back_populates='product', cascade='all, delete-orphan')
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return self.stock <= self.min_stock
    
    @property
    def profit_margin(self):
        """Calcula el margen de ganancia"""
        if self.cost_price == 0:
            return 0
        return ((self.sale_price - self.cost_price) / self.cost_price) * 100
    
    @property
    def real_cost_from_materials(self):
        """Calcula el costo real basado en las materias primas"""
        total_cost = 0.0
        for pm in self.product_materials:
            if pm.raw_material:
                total_cost += pm.quantity_needed * pm.raw_material.cost_per_unit
        return total_cost
    
    @property
    def max_producible_units(self):
        """Calcula cuántas unidades se pueden producir con el stock actual de materias primas"""
        if not self.product_materials:
            return float('inf')  # Sin materias primas definidas = producción ilimitada
        
        min_units = float('inf')
        for pm in self.product_materials:
            if pm.raw_material and pm.quantity_needed > 0:
                units_possible = pm.raw_material.stock / pm.quantity_needed
                min_units = min(min_units, units_possible)
        
        return int(min_units) if min_units != float('inf') else 0
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name}, stock={self.stock})>"