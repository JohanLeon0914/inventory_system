"""
Script de migración para agregar campos payment_method y transfer_type a la tabla expenses
"""
from config.database import engine
from sqlalchemy import text

def migrate_expense_payment():
    """Agrega las columnas payment_method y transfer_type a la tabla expenses si no existen"""
    print("Iniciando migracion para agregar campos payment_method y transfer_type...")
    
    try:
        with engine.begin() as conn:
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                PRAGMA table_info(expenses);
            """))
            columns = [row[1] for row in result]
            
            if 'payment_method' not in columns:
                # Agregar la columna payment_method
                conn.execute(text("""
                    ALTER TABLE expenses ADD COLUMN payment_method VARCHAR(50);
                """))
                print("[OK] Columna 'payment_method' agregada exitosamente a la tabla 'expenses'")
            else:
                print("[OK] La columna 'payment_method' ya existe en la tabla 'expenses'")
            
            if 'transfer_type' not in columns:
                # Agregar la columna transfer_type
                conn.execute(text("""
                    ALTER TABLE expenses ADD COLUMN transfer_type VARCHAR(100);
                """))
                print("[OK] Columna 'transfer_type' agregada exitosamente a la tabla 'expenses'")
            else:
                print("[OK] La columna 'transfer_type' ya existe en la tabla 'expenses'")
            
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_expense_payment()

