"""
Configuración de la base de datos SQLite
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base import Base

# Ruta de la base de datos
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'inventory.db')

# Crear directorio data si no existe
os.makedirs(DB_DIR, exist_ok=True)

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