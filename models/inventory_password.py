"""
Modelo para almacenar la contraseña de acceso al inventario
"""
from sqlalchemy import Column, String, Integer
from models.base import BaseModel

class InventoryPassword(BaseModel):
    """
    Almacena la contraseña y pista para acceder a la sección de inventario
    """
    __tablename__ = 'inventory_password'
    
    # Solo habrá un registro
    id = Column(Integer, primary_key=True, default=1)
    
    # Contraseña encriptada (hash simple)
    password_hash = Column(String(500), nullable=True)
    
    # Pista para recordar la contraseña
    hint = Column(String(200), nullable=True)
    
    def __repr__(self):
        return f"<InventoryPassword(id={self.id})>"

