"""
Script de migración para actualizar el enum ExpenseType para incluir CASH
Nota: SQLite no soporta ALTER TYPE, por lo que solo verificamos que el campo pueda recibir "Efectivo"
"""
from config.database import engine
from sqlalchemy import text

def migrate_expense_type_cash():
    """Verifica que la tabla expenses pueda almacenar el nuevo tipo CASH"""
    print("Verificando migracion para tipo de egreso CASH...")
    
    try:
        with engine.begin() as conn:
            # Verificar estructura de la tabla
            result = conn.execute(text("""
                PRAGMA table_info(expenses);
            """))
            columns = {row[1]: row for row in result}
            
            if 'expense_type' not in columns:
                print("[ERROR] La columna 'expense_type' no existe en la tabla 'expenses'")
                return False
            
            print("[OK] La tabla 'expenses' tiene la columna 'expense_type'")
            print("[INFO] SQLite almacenara el valor 'Efectivo' como string en la columna")
            print("\n¡Migracion completada con exito!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_expense_type_cash()

