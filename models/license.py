"""
Modelo de Licencia - Almacena la llave única del hardware y estado de membresía
"""
from sqlalchemy import Column, String, Boolean, DateTime
from models.base import BaseModel

class License(BaseModel):
    """
    Tabla para almacenar la licencia única del equipo
    Solo habrá UN registro en esta tabla
    """
    __tablename__ = 'licenses'
    
    # Llave única generada del hardware del equipo
    hardware_id = Column(String(255), unique=True, nullable=False)
    
    # Estado de la membresía
    is_active = Column(Boolean, default=False, nullable=False)
    
    # Última vez que se validó con Firebase
    last_validated = Column(DateTime, nullable=True)
    
    # Fecha de expiración de la membresía
    expiration_date = Column(DateTime, nullable=True)
    
    # Email asociado (opcional, para identificar al usuario)
    user_email = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<License(hardware_id={self.hardware_id[:10]}..., active={self.is_active})>"