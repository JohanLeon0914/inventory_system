"""
Script para agregar columna edit_reason a inventory_movements
"""
from config.database import engine
from sqlalchemy import text

def migrate_edit_reason():
    print("Iniciando migración para agregar campo edit_reason...")
    try:
        with engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(inventory_movements);"))
            columns = [row[1] for row in result]
            
            if 'edit_reason' not in columns:
                conn.execute(text("ALTER TABLE inventory_movements ADD COLUMN edit_reason VARCHAR(500);"))
                print("[OK] Columna 'edit_reason' agregada exitosamente a la tabla 'inventory_movements'")
            else:
                print("[OK] La columna 'edit_reason' ya existe en la tabla 'inventory_movements'")
            
            print("\n¡Migración completada con éxito!")
            return True
    except Exception as e:
        print(f"[ERROR] Error durante la migración: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_edit_reason()

