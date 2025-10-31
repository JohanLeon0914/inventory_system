"""
Script de migración para agregar el campo transfer_type a la tabla sales
"""
from config.database import engine
from sqlalchemy import text

def migrate_transfer_type():
    """Agrega la columna transfer_type a la tabla sales si no existe"""
    print("Iniciando migracion para agregar campo transfer_type...")
    
    try:
        with engine.begin() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                PRAGMA table_info(sales);
            """))
            columns = [row[1] for row in result]
            
            if 'transfer_type' not in columns:
                # Agregar la columna transfer_type
                conn.execute(text("""
                    ALTER TABLE sales ADD COLUMN transfer_type VARCHAR(100);
                """))
                print("[OK] Columna 'transfer_type' agregada exitosamente a la tabla 'sales'")
            else:
                print("[OK] La columna 'transfer_type' ya existe en la tabla 'sales'")
            
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_transfer_type()

