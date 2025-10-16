# Guía para Compilar el Sistema de Inventario

## Método 1: Usando el Script Automatizado (Recomendado)

### Paso 1: Ejecutar el script de compilación

Haz doble clic en `build.ps1` o ejecuta en PowerShell:

```powershell
.\build.ps1
```

El script automáticamente:
- Activa el entorno virtual
- Limpia compilaciones anteriores
- Compila la aplicación
- Muestra el resultado

### Paso 2: Encontrar el ejecutable

El ejecutable estará en: `dist\SistemaInventario.exe`

---

## Método 2: Compilación Manual

### Paso 1: Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### Paso 2: Instalar PyInstaller (si no está instalado)

```powershell
pip install pyinstaller
```

### Paso 3: Compilar con PyInstaller

**Opción A - Usando el archivo .spec (Recomendado):**

```powershell
pyinstaller build_exe.spec --clean
```

**Opción B - Comando directo:**

```powershell
pyinstaller --name="SistemaInventario" `
    --onefile `
    --windowed `
    --add-data="data;data" `
    --hidden-import=PyQt6.QtCore `
    --hidden-import=PyQt6.QtGui `
    --hidden-import=PyQt6.QtWidgets `
    --hidden-import=sqlalchemy `
    --hidden-import=openpyxl `
    main.py
```

---

## Opciones de Compilación

### Archivo Único (OneFIle)
El ejecutable incluye todo en un solo archivo `.exe`:

```powershell
pyinstaller build_exe.spec --clean
```

**Ventajas:**
- ✅ Un solo archivo
- ✅ Fácil de distribuir
- ✅ No necesita carpetas adicionales

**Desventajas:**
- ⚠️ Más lento al iniciar (descomprime archivos en temp)
- ⚠️ Archivo más grande

### Carpeta con Dependencias (OneDir)
Genera una carpeta con el ejecutable y sus dependencias:

Modifica en `build_exe.spec`, cambia `EXE()` a:

```python
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaInventario',
    # ... resto de opciones
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaInventario',
)
```

**Ventajas:**
- ✅ Inicia más rápido
- ✅ Más fácil de actualizar componentes individuales

**Desventajas:**
- ⚠️ Múltiples archivos y carpetas
- ⚠️ Más difícil de distribuir

---

## Agregar un Ícono

### Paso 1: Crear o conseguir un ícono

Coloca tu archivo `.ico` en: `resources/icons/app.ico`

### Paso 2: Modificar build_exe.spec

Cambia la línea `icon=None` a:

```python
icon='resources/icons/app.ico'
```

---

## Distribución del Ejecutable

### Contenido para distribuir:

1. **SistemaInventario.exe** - El ejecutable principal
2. **data/** (opcional) - Base de datos inicial
3. **LICENSE.txt** (opcional) - Licencia del software
4. **README.txt** (opcional) - Instrucciones para el usuario

### Crear un instalador (Opcional)

Puedes usar herramientas como:
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **NSIS**: https://nsis.sourceforge.io/

---

## Solución de Problemas

### Error: "No se encuentra el módulo X"

Agrega el módulo a `hiddenimports` en `build_exe.spec`:

```python
hiddenimports=[
    'nombre_del_modulo',
    # ... otros módulos
],
```

### Error: "Failed to execute script"

1. Compila con modo debug para ver errores:
   ```powershell
   pyinstaller build_exe.spec --clean --debug all
   ```

2. O cambia `console=False` a `console=True` en `build_exe.spec`

### La base de datos no se crea

Asegúrate de que la carpeta `data` existe y tiene permisos de escritura.

### El ejecutable es muy grande

1. Usa UPX para comprimir:
   ```powershell
   # Descarga UPX de: https://upx.github.io/
   # Coloca upx.exe en la carpeta del proyecto
   ```

2. Excluye módulos no necesarios en `build_exe.spec`:
   ```python
   excludes=['tkinter', 'matplotlib', 'numpy'],
   ```

---

## Notas Importantes

1. **Antivirus**: Algunos antivirus pueden marcar el ejecutable como sospechoso. Esto es normal con PyInstaller.

2. **Tamaño**: El ejecutable será grande (50-150 MB) porque incluye Python y todas las dependencias.

3. **Licencia**: Revisa que tu aplicación cumple con las licencias de PyQt6 y otras bibliotecas.

4. **Base de datos**: La primera vez que se ejecute, creará automáticamente la base de datos SQLite.

5. **Actualización**: Para actualizar la aplicación, simplemente recompila y distribuye el nuevo ejecutable.

---

## Archivo .env

Si usas variables de entorno, crea un archivo `.env` junto al ejecutable:

```env
DATABASE_URL=sqlite:///data/inventory.db
DEBUG=False
```

---

## Testing del Ejecutable

Antes de distribuir:

1. ✅ Ejecuta en una máquina sin Python instalado
2. ✅ Verifica que todas las funciones funcionan
3. ✅ Prueba en diferentes versiones de Windows
4. ✅ Verifica que la base de datos se crea correctamente
5. ✅ Prueba exportar reportes a Excel
6. ✅ Verifica que las licencias funcionan correctamente

---

## Estructura de Archivos Resultante

```
dist/
└── SistemaInventario.exe    (archivo único con todo incluido)

O si usas OneDir:

dist/
└── SistemaInventario/
    ├── SistemaInventario.exe
    ├── _internal/
    │   ├── (librerías y dependencias)
    │   └── data/
    └── (otros archivos necesarios)
```

