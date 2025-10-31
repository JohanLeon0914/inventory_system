"""
Modelo de Información de la Empresa
"""
from sqlalchemy import Column, String, Text
from models.base import BaseModel

class CompanyInfo(BaseModel):
    """
    Información legal de la empresa para facturación
    """
    __tablename__ = 'company_info'
    
    # Información legal
    company_name = Column(String(200), nullable=False, default="MI EMPRESA SAS")
    company_nit = Column(String(50), nullable=False, default="900.123.456-7")
    company_address = Column(String(200), nullable=True, default="Calle 123 #45-67")
    company_city = Column(String(100), nullable=True, default="Bogotá D.C., Colombia")
    company_phone = Column(String(50), nullable=True, default="+57 1 123 4567")
    company_email = Column(String(150), nullable=True, default="contacto@miempresa.com")
    company_regimen = Column(String(200), nullable=True, default="Régimen Simplificado")
    
    def __repr__(self):
        return f"<CompanyInfo(company_name={self.company_name})>"
