# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# -----------------------------------------------
# Configuración específica para Linux/Ubuntu
# -----------------------------------------------

# Añade TODOS los archivos de la carpeta icons (incluyendo subdirectorios)
added_files = [
    ('icons/', 'icons')  # Formato correcto para Linux
]

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Directorio actual como raíz
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'tkinter',
        'PIL'  # Si usas Pillow para imágenes
    ],  # Módulos que PyInstaller no detecta automáticamente
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# -----------------------------------------------
# Configuración del ejecutable para Linux
# -----------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='tex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,  # Habilita la consola TEMPORALMENTE para ver errores
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='icons/my-icon.xpm'  # Usa formato .xpm para Linux
)