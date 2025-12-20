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