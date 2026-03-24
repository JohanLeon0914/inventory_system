"""
Migración para inicializar el contador de facturas con el número más alto existente
"""
from config.database import get_session, close_session
from models.invoice_counter import InvoiceCounter
from models.sale import Sale

def migrate_invoice_counter():
    """
    Migración para sistemas existentes:
    - Si no hay ventas: Inicia contador en 0
    - Si hay ventas: Inicia contador con el número más alto existente
    """
    session = get_session()
    try:
        # Verificar si ya existe un contador
        existing_counter = session.query(InvoiceCounter).filter_by(counter_key="default").first()
        if existing_counter:
            print("✓ El contador de facturas ya existe, no se requiere migración")
            return
        
        # Obtener la venta con el número de factura más alto
        last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
        
        if last_sale:
            try:
                # Extraer el número del formato INV-XXXXXX
                last_number = int(last_sale.invoice_number.split('-')[1])
                print(f"✓ Última factura encontrada: {last_sale.invoice_number}")
                
                # Crear contador con el valor actual
                counter = InvoiceCounter(
                    counter_key="default", 
                    prefix="INV", 
                    format_digits=6,
                    current_value=last_number
                )
                session.add(counter)
                session.commit()
                print(f"✓ Contador inicializado en {last_number}. Próxima factura: INV-{last_number + 1:06d}")
                
            except (ValueError, IndexError) as e:
                print(f"⚠ Error al procesar última factura: {last_sale.invoice_number}")
                print(f"⚠ Iniciando contador desde 0. Error: {e}")
                
                # Si hay error, iniciar desde 0
                counter = InvoiceCounter(counter_key="default", prefix="INV", format_digits=6)
                session.add(counter)
                session.commit()
                print("✓ Contador inicializado desde 0 por seguridad")
        else:
            # No hay ventas, iniciar desde 0
            counter = InvoiceCounter(counter_key="default", prefix="INV", format_digits=6)
            session.add(counter)
            session.commit()
            print("✓ No hay ventas existentes. Contador inicializado desde 0")
            
    except Exception as e:
        session.rollback()
        print(f"✗ Error en migración: {e}")
        raise
    finally:
        close_session()

if __name__ == "__main__":
    print("=" * 50)
    print("Migración de Contador de Facturas")
    print("=" * 50)
    
    try:
        migrate_invoice_counter()
        print("\n✅ Migración completada exitosamente")
    except Exception as e:
        print(f"\n❌ Migración fallida: {e}")
    
    print("=" * 50)
