# Script para compilar la aplicación de inventario
Write-Host "=== Compilando Sistema de Inventario ===" -ForegroundColor Green

# Activar entorno virtual
Write-Host "`nActivando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Limpiar compilaciones anteriores
Write-Host "`nLimpiando compilaciones anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Compilar con PyInstaller
Write-Host "`nCompilando aplicación..." -ForegroundColor Yellow
pyinstaller build_exe.spec --clean

# Verificar si la compilación fue exitosa
if (Test-Path "dist\SistemaInventario.exe") {
    Write-Host "`n=== ¡Compilación exitosa! ===" -ForegroundColor Green
    Write-Host "`nEl ejecutable se encuentra en: dist\SistemaInventario.exe" -ForegroundColor Cyan
    Write-Host "`nTamaño del ejecutable:" -ForegroundColor Yellow
    Get-Item "dist\SistemaInventario.exe" | Select-Object Name, @{Name="Size (MB)";Expression={[math]::Round($_.Length / 1MB, 2)}}
} else {
    Write-Host "`n=== Error en la compilación ===" -ForegroundColor Red
    Write-Host "Revisa los mensajes de error arriba." -ForegroundColor Yellow
}

Write-Host "`nPresiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

