"""
Script de migración para agregar campo amount a la tabla expenses
"""
from config.database import engine
from sqlalchemy import text

def migrate_expense_amount():
    """Agrega la columna amount a la tabla expenses si no existe"""
    print("Iniciando migracion para agregar campo amount...")
    
    try:
        with engine.begin() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                PRAGMA table_info(expenses);
            """))
            columns = [row[1] for row in result]
            
            if 'amount' not in columns:
                # Agregar la columna amount
                conn.execute(text("""
                    ALTER TABLE expenses ADD COLUMN amount REAL;
                """))
                print("[OK] Columna 'amount' agregada exitosamente a la tabla 'expenses'")
            else:
                print("[OK] La columna 'amount' ya existe en la tabla 'expenses'")
            
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_expense_amount()

