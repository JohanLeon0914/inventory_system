"""
Script de migracion para agregar la tabla de egresos
"""
from config.database import get_session, engine
from models import Base, Expense

def migrate():
    """Crea la tabla de egresos si no existe"""
    print("Iniciando migracion de egresos...")
    
    try:
        # Crear tabla de egresos
        Base.metadata.create_all(engine, tables=[Expense.__table__])
        print("OK - Tabla 'expenses' creada exitosamente")
        
        print("\nMigracion completada correctamente")
    except Exception as e:
        print(f"\nERROR durante la migracion: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()

