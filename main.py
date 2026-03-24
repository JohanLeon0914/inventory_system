"""
Sistema de Inventario y Ventas
Punto de entrada principal de la aplicación
"""
import sys
from PyQt6.QtWidgets import QApplication
from config.database import init_db
from core.license_manager import LicenseManager

def main():
    """
    Función principal que inicia la aplicación
    """
    print("=" * 50)
    print("Sistema de Inventario y Ventas")
    print("=" * 50)
    
    # 1. Inicializar base de datos
    print("\n[1/4] Inicializando base de datos...")
    try:
        init_db()
        from config.database import init_invoice_counter
        init_invoice_counter()
    except Exception as e:
        print(f"✗ Error al inicializar BD: {e}")
        return
    
    # 2. Verificar/crear licencia
    print("\n[2/4] Verificando licencia...")
    try:
        license = LicenseManager.get_or_create_license()
        if license is None:
            print("✗ Error al crear/obtener licencia")
            return
    except Exception as e:
        print(f"✗ Error con la licencia: {e}")
        return
    
    # 3. Validar licencia
    print("\n[3/4] Validando licencia...")
    is_valid = LicenseManager.is_license_valid()
    
    if not is_valid:
        print("⚠ Licencia inactiva o expirada")
        print("ℹ Por ahora activando automáticamente para desarrollo...")
        LicenseManager.activate_license(365)  # 1 año para desarrollo
        is_valid = True
    else:
        print("✓ Licencia válida")
    
    # Mostrar info de la licencia
    license_info = LicenseManager.get_license_info()
    if license_info:
        print(f"\n📋 Información de Licencia:")
        print(f"   Hardware ID: {license_info['hardware_id']}")
        print(f"   Estado: {'✓ Activa' if license_info['is_active'] else '✗ Inactiva'}")
        if license_info['expiration_date']:
            print(f"   Expira: {license_info['expiration_date'].strftime('%d/%m/%Y')}")

    # 4. Iniciar aplicación GUI
    print("\n[4/4] Iniciando interfaz gráfica...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Inventario")
    app.setOrganizationName("MiEmpresa")
    
    # Importar y mostrar ventana principal
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    print("\n" + "=" * 50)
    print("✓ Aplicación iniciada correctamente")
    print("=" * 50)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()