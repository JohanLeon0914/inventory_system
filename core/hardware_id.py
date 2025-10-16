"""
Generador de ID único basado en el hardware del equipo
"""
import hashlib
import platform
import subprocess
import uuid

def get_hardware_id():
    """
    Genera un ID único basado en características del hardware del equipo.
    Este ID será siempre el mismo para el mismo equipo.
    """
    hardware_info = []
    
    try:
        # 1. UUID del sistema (más confiable en Windows)
        if platform.system() == 'Windows':
            # Obtener el UUID de Windows usando WMIC
            result = subprocess.check_output(
                'wmic csproduct get uuid', 
                shell=True
            ).decode()
            uuid_value = result.split('\n')[1].strip()
            hardware_info.append(uuid_value)
        else:
            # Para otros sistemas
            hardware_info.append(str(uuid.getnode()))
        
        # 2. Nombre del equipo
        hardware_info.append(platform.node())
        
        # 3. Procesador
        hardware_info.append(platform.processor())
        
        # 4. Sistema operativo
        hardware_info.append(platform.system())
        hardware_info.append(platform.release())
        
    except Exception as e:
        # Fallback: usar MAC address
        print(f"Advertencia al generar hardware ID: {e}")
        hardware_info.append(str(uuid.getnode()))
        hardware_info.append(platform.node())
    
    # Concatenar toda la información
    hardware_string = '|'.join(hardware_info)
    
    # Generar hash SHA-256
    hardware_hash = hashlib.sha256(hardware_string.encode()).hexdigest()
    
    return hardware_hash

def format_hardware_id(hardware_id):
    """
    Formatea el hardware ID para que sea más legible
    Ejemplo: XXXX-XXXX-XXXX-XXXX
    """
    formatted = '-'.join([
        hardware_id[i:i+4] 
        for i in range(0, min(16, len(hardware_id)), 4)
    ])
    return formatted.upper()

# Para debug/testing
if __name__ == '__main__':
    hw_id = get_hardware_id()
    formatted_id = format_hardware_id(hw_id)
    print(f"Hardware ID completo: {hw_id}")
    print(f"Hardware ID formateado: {formatted_id}")