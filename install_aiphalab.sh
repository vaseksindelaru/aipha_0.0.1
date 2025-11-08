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
pip install python-dotenv google-generativeai

# Verificar API key
if [ -z "$GEMINI_API_KEY" ]; then
    # Verificar si existe archivo .env
    if [ -f ".env" ]; then
        echo "📄 Cargando configuración desde .env..."
        export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2)
        if [ -n "$GEMINI_API_KEY" ]; then
            echo "✅ GEMINI_API_KEY cargada desde .env"
        else
            echo "⚠️  .env existe pero no contiene GEMINI_API_KEY"
            read -p "Ingresa tu API key: " api_key
            echo "GEMINI_API_KEY=$api_key" >> .env
            export GEMINI_API_KEY="$api_key"
        fi
    else
        echo "⚠️  GEMINI_API_KEY no configurada"
        read -p "Ingresa tu API key: " api_key
        echo "GEMINI_API_KEY=$api_key" > .env
        export GEMINI_API_KEY="$api_key"
    fi
fi

# Hacer ejecutable
chmod +x aiphalab/aiphalab_cli.py

echo "✅ Instalación completada!"
echo "Ejecutar con: python aiphalab/aiphalab_cli.py"