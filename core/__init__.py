"""
Paquete core - Funcionalidades centrales
"""
from core.hardware_id import get_hardware_id, format_hardware_id
from core.license_manager import LicenseManager

__all__ = ['get_hardware_id', 'format_hardware_id', 'LicenseManager']