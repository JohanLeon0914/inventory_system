"""
Gestor de Licencias - Maneja la validación y activación de licencias
"""
from datetime import datetime, timedelta
from config.database import get_session, close_session
from models.license import License
from core.hardware_id import get_hardware_id, format_hardware_id

class LicenseManager:
    """
    Gestiona todo lo relacionado con las licencias
    """
    
    @staticmethod
    def get_or_create_license():
        """
        Obtiene la licencia existente o crea una nueva si no existe
        """
        session = get_session()
        try:
            # Buscar licencia existente
            license = session.query(License).first()
            
            if license is None:
                # No existe licencia, crear una nueva
                hardware_id = get_hardware_id()
                license = License(
                    hardware_id=hardware_id,
                    is_active=False,  # Por defecto inactiva
                    last_validated=datetime.now()
                )
                session.add(license)
                session.commit()
                print(f"✓ Nueva licencia creada: {format_hardware_id(hardware_id)}")
            
            return license
            
        except Exception as e:
            session.rollback()
            print(f"Error al obtener/crear licencia: {e}")
            return None
        finally:
            close_session()
    
    @staticmethod
    def is_license_valid():
        """
        Verifica si la licencia es válida
        POR AHORA: Solo verifica localmente
        FUTURO: Validará con Firebase
        """
        session = get_session()
        try:
            license = session.query(License).first()
            
            if license is None:
                return False
            
            # Verificar si está activa
            if not license.is_active:
                return False
            
            # Verificar si no ha expirado
            if license.expiration_date:
                if datetime.now() > license.expiration_date:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error al validar licencia: {e}")
            return False
        finally:
            close_session()
    
    @staticmethod
    def activate_license(days=30):
        """
        Activa la licencia por X días
        POR AHORA: Activación local para desarrollo
        FUTURO: Se activará solo después de validar con Firebase
        """
        session = get_session()
        try:
            license = session.query(License).first()
            
            if license:
                license.is_active = True
                license.expiration_date = datetime.now() + timedelta(days=days)
                license.last_validated = datetime.now()
                session.commit()
                print(f"✓ Licencia activada hasta: {license.expiration_date}")
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            print(f"Error al activar licencia: {e}")
            return False
        finally:
            close_session()
    
    @staticmethod
    def deactivate_license():
        """
        Desactiva la licencia
        """
        session = get_session()
        try:
            license = session.query(License).first()
            
            if license:
                license.is_active = False
                session.commit()
                print("✓ Licencia desactivada")
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            print(f"Error al desactivar licencia: {e}")
            return False
        finally:
            close_session()
    
    @staticmethod
    def get_license_info():
        """
        Obtiene información de la licencia
        """
        session = get_session()
        try:
            license = session.query(License).first()
            
            if license:
                return {
                    'hardware_id': format_hardware_id(license.hardware_id),
                    'is_active': license.is_active,
                    'expiration_date': license.expiration_date,
                    'last_validated': license.last_validated,
                    'user_email': license.user_email
                }
            
            return None
            
        except Exception as e:
            print(f"Error al obtener info de licencia: {e}")
            return None
        finally:
            close_session()
    
    @staticmethod
    def validate_with_firebase():
        """
        FUTURO: Validará la licencia con Firebase
        Verificará si la membresía está activa
        """
        # TODO: Implementar cuando configuremos Firebase
        pass

# Para testing
if __name__ == '__main__':
    # Crear/obtener licencia
    lic = LicenseManager.get_or_create_license()
    
    # Activar por 30 días (solo para desarrollo)
    LicenseManager.activate_license(30)
    
    # Verificar si es válida
    is_valid = LicenseManager.is_license_valid()
    print(f"¿Licencia válida?: {is_valid}")
    
    # Obtener información
    info = LicenseManager.get_license_info()
    print(f"Info de licencia: {info}")