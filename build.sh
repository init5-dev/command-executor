#!/bin/bash

# Script para ejecutar PyInstaller con las opciones especificadas

# Verificar si pyinstaller está instalado
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller no está instalado. Por favor, instálalo usando: pip install pyinstaller"
    exit 1
fi

# Ejecutar el comando pyinstaller
pyinstaller --onefile --windowed --add-data "icons:icons" tex.py

# Verificar si el comando se ejecutó correctamente
if [ $? -eq 0 ]; then
    echo "El archivo ejecutable ha sido creado exitosamente."
else
    echo "Ocurrió un error al crear el archivo ejecutable."
    exit 1
fi
