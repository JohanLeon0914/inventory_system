#!/usr/bin/env python3
"""
Script para eliminar la tabla invoice_counter y permitir su recreación
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.database import get_session, close_session
    from sqlalchemy import text
    
    session = get_session()
    try:
        # Eliminar la tabla invoice_counter si existe
        session.execute(text('DROP TABLE IF EXISTS invoice_counter'))
        session.commit()
        print('✅ Tabla invoice_counter eliminada correctamente')
        print('La tabla se creará automáticamente al iniciar la aplicación')
    except Exception as e:
        print(f'❌ Error: {e}')
        session.rollback()
    finally:
        close_session()
        
except ImportError as e:
    print(f'❌ Error de importación: {e}')
    print('Asegúrate de estar en el entorno virtual con las dependencias instaladas')
