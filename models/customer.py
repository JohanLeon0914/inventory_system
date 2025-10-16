"""
Modelo de Cliente - Clientes de la empresa
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Customer(BaseModel):
    """
    Clientes que realizan compras
    """
    __tablename__ = 'customers'
    
    # Información personal
    name = Column(String(200), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Documento de identidad
    document_type = Column(String(20), nullable=True)  # DNI, RUC, Pasaporte, etc
    document_number = Column(String(50), unique=True, nullable=True)
    
    # Dirección
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    
    # Relación con ventas
    sales = relationship('Sale', back_populates='customer')
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, document={self.document_number})>"