"""
Configuración de la base de datos SQLite
"""
import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base import Base

def _get_default_db_dir() -> str:
    override = os.environ.get('INVENTORY_DB_PATH')
    if override:
        return os.path.dirname(override)

    appdata = os.environ.get('APPDATA') or os.environ.get('LOCALAPPDATA')
    if appdata:
        return os.path.join(appdata, 'inventory_system')

    return os.path.join(os.path.expanduser('~'), '.inventory_system')


# Ruta de la base de datos (por defecto en una carpeta escribible por usuario)
_override_db_path = os.environ.get('INVENTORY_DB_PATH')
DB_DIR = _get_default_db_dir()
DB_PATH = _override_db_path if _override_db_path else os.path.join(DB_DIR, 'inventory.db')

# Crear directorio si no existe
os.makedirs(DB_DIR, exist_ok=True)

# Migración simple desde ruta antigua (proyecto/data/inventory.db) si aplica
_legacy_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
_legacy_path = os.path.join(_legacy_dir, 'inventory.db')
try:
    if os.path.exists(_legacy_path) and not os.path.exists(DB_PATH):
        shutil.copy2(_legacy_path, DB_PATH)
except Exception:
    pass

# Crear engine de SQLAlchemy
DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver las queries SQL en consola (debug)
    connect_args={'check_same_thread': False}  
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    """
    # Importar todos los modelos para que SQLAlchemy los registre
    from models import (
        License, Category, Product, Customer, 
        Sale, SaleItem, InventoryMovement
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente")

def get_session():
    """
    Obtiene una sesión de base de datos
    """
    return Session()

def close_session():
    """
    Cierra la sesión de base de datos
    """
    Session.remove()

def init_invoice_counter():
    """
    Inicializa el contador de facturas si no existe.
    Para sistemas existentes, busca el número más alto y lo usa como base.
    """
    session = get_session()
    try:
        from models.invoice_counter import InvoiceCounter
        from models.sale import Sale
        
        # Verificar si ya existe un contador
        counter = session.query(InvoiceCounter).filter_by(counter_key="default").first()
        if not counter:
            # Buscar la última venta para determinar el número base
            last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
            
            if last_sale:
                try:
                    # Extraer el número del formato INV-XXXXXX
                    last_number = int(last_sale.invoice_number.split('-')[1])
                    print(f"Última factura existente: {last_sale.invoice_number}")
                    
                    # Crear contador con el valor actual
                    counter = InvoiceCounter(
                        counter_key="default", 
                        prefix="INV", 
                        format_digits=6,
                        current_value=last_number
                    )
                    session.add(counter)
                    session.commit()
                    print(f"Contador de facturas inicializado en {last_number}")
                    print(f"Próxima factura: INV-{last_number + 1:06d}")
                    
                except (ValueError, IndexError):
                    print(f"Error al procesar última factura: {last_sale.invoice_number}")
                    print("Iniciando contador desde 0 por seguridad")
                    
                    # Si hay error, iniciar desde 0
                    counter = InvoiceCounter(counter_key="default", prefix="INV", format_digits=6)
                    session.add(counter)
                    session.commit()
                    print("Contador de facturas inicializado desde 0")
            else:
                # No hay ventas, iniciar desde 0
                counter = InvoiceCounter(counter_key="default", prefix="INV", format_digits=6)
                session.add(counter)
                session.commit()
                print("No hay ventas existentes. Contador inicializado desde 0")
        else:
            print("Contador de facturas ya existe")
            
    except Exception as e:
        print(f"Error al inicializar contador de facturas: {e}")
        session.rollback()
    finally:
        close_session()