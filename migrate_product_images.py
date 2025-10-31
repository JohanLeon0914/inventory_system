"""
Script de migración para agregar el campo image_path a la tabla products
"""
from config.database import engine
from sqlalchemy import text

def migrate_product_images():
    """Agrega la columna image_path a la tabla products si no existe"""
    print("Iniciando migración para agregar campo image_path...")
    
    try:
        with engine.begin() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                PRAGMA table_info(products);
            """))
            columns = [row[1] for row in result]
            
            if 'image_path' not in columns:
                # Agregar la columna image_path
                conn.execute(text("""
                    ALTER TABLE products ADD COLUMN image_path VARCHAR(500);
                """))
                print("[OK] Columna 'image_path' agregada exitosamente a la tabla 'products'")
            else:
                print("[OK] La columna 'image_path' ya existe en la tabla 'products'")
            
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_product_images()

