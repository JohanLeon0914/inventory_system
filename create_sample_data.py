"""
Script para crear datos de ejemplo
"""
from config.database import init_db, get_session, close_session
from models import Category

def create_sample_categories():
    """Crea categorías de ejemplo"""
    session = get_session()
    try:
        # Verificar si ya existen categorías
        if session.query(Category).count() > 0:
            print("Ya existen categorías")
            return
        
        categories = [
            Category(name="Electrónica", description="Dispositivos electrónicos"),
            Category(name="Ropa", description="Prendas de vestir"),
            Category(name="Alimentos", description="Productos alimenticios"),
            Category(name="Hogar", description="Artículos para el hogar"),
            Category(name="Deportes", description="Equipamiento deportivo"),
        ]
        
        for cat in categories:
            session.add(cat)
        
        session.commit()
        print("✓ Categorías creadas correctamente")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        close_session()

if __name__ == '__main__':
    init_db()
    create_sample_categories()