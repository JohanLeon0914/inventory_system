"""
Script para migrar la base de datos y crear las nuevas tablas de materias primas
"""
from config.database import engine
from models import Base

def migrate_database():
    """Crea todas las tablas que no existan en la base de datos"""
    print("Iniciando migración de base de datos...")
    
    try:
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(engine)
        print("✓ Tablas creadas exitosamente")
        print("✓ Se han creado las siguientes tablas nuevas:")
        print("  - raw_materials (materias primas)")
        print("  - product_materials (relación producto-materia prima)")
        print("  - raw_material_movements (movimientos de materias primas)")
        print("\n¡Migración completada con éxito!")
        print("\nNOTA: Los datos existentes se han preservado.")
        
    except Exception as e:
        print(f"✗ Error durante la migración: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_database()

