#!/usr/bin/env python3
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Ejecuta comando y aborta si falla"""
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        sys.exit(f"❌ Error: {cmd}")
    return result

print("🔨 Building BrokenLinkCrawler GUI...\n")

# 1. Compilar frontend
print("📦 [1/3] Compilando frontend Vue...")
run_command("npm run build", cwd="gui/frontend")

# 2. Copiar dist a backend
print("📦 [2/3] Copiando archivos compilados...")
frontend_dist = Path("gui/frontend/dist")
backend_dist = Path("gui/backend/dist")
shutil.rmtree(backend_dist, ignore_errors=True)
shutil.copytree(frontend_dist, backend_dist)

# 3. Crear .exe con PyInstaller
print("🔨 [3/3] Empaquetando con PyInstaller...")
run_command(
    f'{sys.executable} -m PyInstaller '
    '--onefile '
    '--windowed '
    '--name=BrokenLinkCrawler '
    '--icon=assets/icon.ico '
    '--add-data=gui/backend/dist:dist '
    '--distpath=./dist '
    '--specpath=./build '
    'gui/backend/main.py',
    cwd="."
)

print("\n✅ Listo!")
print("📁 Ejecutable: ./dist/BrokenLinkCrawler.exe")
print(f"💾 Tamaño estimado: ~160MB")