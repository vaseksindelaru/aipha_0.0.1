#!/bin/bash
# install_aiphalab.sh

echo "🚀 Instalando AiphaLab CLI..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install google-generativeai

# Verificar API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY no configurada"
    read -p "Ingresa tu API key: " api_key
    echo "export GEMINI_API_KEY='$api_key'" >> ~/.bashrc
    export GEMINI_API_KEY="$api_key"
fi

# Hacer ejecutable
chmod +x aiphalab/aiphalab_cli.py

echo "✅ Instalación completada!"
echo "Ejecutar con: python aiphalab/aiphalab_cli.py"