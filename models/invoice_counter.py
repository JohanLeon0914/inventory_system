"""
Modelo para mantener el contador consecutivo de facturas
"""
from sqlalchemy import Column, Integer, String
from models.base import BaseModel

class InvoiceCounter(BaseModel):
    """
    Contador secuencial para números de factura
    """
    __tablename__ = 'invoice_counter'
    
    # Identificador único del contador (usando el ID heredado como clave primaria)
    counter_key = Column(String(50), unique=True, nullable=False)
    
    # Valor actual del contador
    current_value = Column(Integer, default=0, nullable=False)
    
    # Prefijo para las facturas
    prefix = Column(String(10), default="INV", nullable=False)
    
    # Formato del número (dígitos)
    format_digits = Column(Integer, default=6, nullable=False)
    
    def __init__(self, counter_key="default", prefix="INV", format_digits=6):
        self.counter_key = counter_key
        self.prefix = prefix
        self.format_digits = format_digits
        self.current_value = 0
    
    def get_next_number(self):
        """Obtiene el siguiente número de factura en formato completo"""
        self.current_value += 1
        return f"{self.prefix}-{self.current_value:0{self.format_digits}d}"
    
    def __repr__(self):
        return f"<InvoiceCounter(key={self.counter_key}, current={self.current_value})>"
