"""
Script para agregar campos de facturación a la tabla sales
"""
from config.database import engine
from sqlalchemy import text

def migrate_invoice_fields():
    print("Iniciando migración para agregar campos de facturación...")
    try:
        with engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(sales);"))
            columns = [row[1] for row in result]
            
            if 'has_invoice' not in columns:
                conn.execute(text("ALTER TABLE sales ADD COLUMN has_invoice INTEGER DEFAULT 0 NOT NULL;"))
                print("[OK] Columna 'has_invoice' agregada exitosamente a la tabla 'sales'")
            else:
                print("[OK] La columna 'has_invoice' ya existe en la tabla 'sales'")
            
            if 'invoice_generated_at' not in columns:
                conn.execute(text("ALTER TABLE sales ADD COLUMN invoice_generated_at DATETIME;"))
                print("[OK] Columna 'invoice_generated_at' agregada exitosamente a la tabla 'sales'")
            else:
                print("[OK] La columna 'invoice_generated_at' ya existe en la tabla 'sales'")
            
            print("\n¡Migración completada con éxito!")
            return True
    except Exception as e:
        print(f"[ERROR] Error durante la migración: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_invoice_fields()
