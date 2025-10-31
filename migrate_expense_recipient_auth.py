"""
Script de migración para agregar campos recipient e is_authorized a la tabla expenses
"""
from config.database import engine
from sqlalchemy import text

def migrate_expense_recipient_auth():
    """Agrega las columnas recipient e is_authorized a la tabla expenses si no existen"""
    print("Iniciando migracion para agregar campos recipient e is_authorized...")
    
    try:
        with engine.begin() as conn:
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                PRAGMA table_info(expenses);
            """))
            columns = [row[1] for row in result]
            
            if 'recipient' not in columns:
                # Agregar la columna recipient
                conn.execute(text("""
                    ALTER TABLE expenses ADD COLUMN recipient VARCHAR(200);
                """))
                print("[OK] Columna 'recipient' agregada exitosamente a la tabla 'expenses'")
            else:
                print("[OK] La columna 'recipient' ya existe en la tabla 'expenses'")
            
            if 'is_authorized' not in columns:
                # Agregar la columna is_authorized
                conn.execute(text("""
                    ALTER TABLE expenses ADD COLUMN is_authorized INTEGER DEFAULT 0;
                """))
                print("[OK] Columna 'is_authorized' agregada exitosamente a la tabla 'expenses'")
            else:
                print("[OK] La columna 'is_authorized' ya existe en la tabla 'expenses'")
            
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_expense_recipient_auth()

