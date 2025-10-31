"""
Modelo de Venta - Registro de ventas realizadas
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum
from datetime import datetime

class PaymentMethod(enum.Enum):
    """Métodos de pago disponibles"""
    CASH = "Efectivo"
    CARD = "Tarjeta"
    TRANSFER = "Transferencia"
    OTHER = "Otro"

class SaleStatus(enum.Enum):
    """Estados de la venta"""
    PENDING = "Pendiente"
    COMPLETED = "Completada"
    CANCELLED = "Cancelada"
    EDITED = "Editada"

class Sale(BaseModel):
    """
    Ventas realizadas a clientes
    """
    __tablename__ = 'sales'
    
    # Número de factura/ticket
    invoice_number = Column(String(50), unique=True, nullable=False)
    
    # Cliente (opcional para ventas sin cliente registrado)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    customer = relationship('Customer', back_populates='sales')
    
    # Totales
    subtotal = Column(Float, default=0.0, nullable=False)
    tax = Column(Float, default=0.0, nullable=False)  # IVA u otros impuestos
    discount = Column(Float, default=0.0, nullable=False)
    total = Column(Float, default=0.0, nullable=False)
    
    # Método de pago y estado
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    status = Column(SQLEnum(SaleStatus), default=SaleStatus.COMPLETED, nullable=False)
    
    # Tipo de transferencia (cuando payment_method es TRANSFER)
    transfer_type = Column(String(100), nullable=True)  # Nequi, Daviplata, Bancolombia, Otro, etc.
    
    # Notas adicionales
    notes = Column(String(500), nullable=True)
    
    # Facturación
    has_invoice = Column(Integer, default=0, nullable=False)  # 0 = No, 1 = Sí
    invoice_generated_at = Column(DateTime, nullable=True)  # Fecha de generación de factura
    
    # Relación con los items de la venta
    items = relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')
    
    def calculate_total(self):
        """Calcula el total de la venta basado en los items"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.total = self.subtotal + self.tax - self.discount
    
    def __repr__(self):
        return f"<Sale(id={self.id}, invoice={self.invoice_number}, total=${self.total})>"