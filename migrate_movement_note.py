"""
Migración para agregar campo 'note' a las tablas de movimientos
"""
from config.database import engine
from sqlalchemy import text

def migrate_movement_note():
    print("Iniciando migración para agregar campo 'note'...")
    try:
        with engine.begin() as conn:
            # Agregar campo note a inventory_movements
            result = conn.execute(text("PRAGMA table_info(inventory_movements);"))
            columns = [row[1] for row in result]
            if 'note' not in columns:
                conn.execute(text("ALTER TABLE inventory_movements ADD COLUMN note VARCHAR(500);"))
                print("[OK] Columna 'note' agregada exitosamente a la tabla 'inventory_movements'")
            else:
                print("[OK] La columna 'note' ya existe en la tabla 'inventory_movements'")
            
            # Agregar campo note a raw_material_movements
            result = conn.execute(text("PRAGMA table_info(raw_material_movements);"))
            columns = [row[1] for row in result]
            if 'note' not in columns:
                conn.execute(text("ALTER TABLE raw_material_movements ADD COLUMN note VARCHAR(500);"))
                print("[OK] Columna 'note' agregada exitosamente a la tabla 'raw_material_movements'")
            else:
                print("[OK] La columna 'note' ya existe en la tabla 'raw_material_movements'")
            
            print("\n¡Migración completada con éxito!")
            return True
    except Exception as e:
        print(f"[ERROR] Error durante la migración: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_movement_note()

