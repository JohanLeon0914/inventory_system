"""
Script para crear la tabla de información de empresa
"""
from config.database import engine
from sqlalchemy import text

def migrate_company_info():
    print("Iniciando migración para crear tabla company_info...")
    try:
        with engine.begin() as conn:
            # Crear tabla company_info si no existe
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS company_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name VARCHAR(200) NOT NULL DEFAULT 'MI EMPRESA SAS',
                    company_nit VARCHAR(50) NOT NULL DEFAULT '900.123.456-7',
                    company_address VARCHAR(200),
                    company_city VARCHAR(100),
                    company_phone VARCHAR(50),
                    company_email VARCHAR(150),
                    company_regimen VARCHAR(200),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                );
            """))
            print("[OK] Tabla 'company_info' creada o ya existe")
            
            # Verificar si ya hay datos
            result = conn.execute(text("SELECT COUNT(*) FROM company_info;"))
            count = result.fetchone()[0]
            
            if count == 0:
                # Insertar registro por defecto
                conn.execute(text("""
                    INSERT INTO company_info (
                        company_name, company_nit, company_address, company_city,
                        company_phone, company_email, company_regimen
                    ) VALUES (
                        'MI EMPRESA SAS',
                        '900.123.456-7',
                        'Calle 123 #45-67',
                        'Bogotá D.C., Colombia',
                        '+57 1 123 4567',
                        'contacto@miempresa.com',
                        'Régimen Simplificado'
                    );
                """))
                print("[OK] Registro por defecto insertado en 'company_info'")
            else:
                print("[OK] Tabla 'company_info' ya contiene datos")
            
            print("\n¡Migración completada con éxito!")
            return True
    except Exception as e:
        print(f"[ERROR] Error durante la migración: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_company_info()
