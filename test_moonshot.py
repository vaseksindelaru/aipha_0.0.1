#!/usr/bin/env python3
# test_moonshot.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env si existe
load_dotenv()

# Obtener la key
api_key = os.getenv("MOONSHOT_API_KEY")
print(f"API Key encontrada: {'SÍ' if api_key else 'NO'}")
if api_key:
    print(f"Formato: {api_key[:10]}...{api_key[-4:]}")
    print(f"Prefijo correcto: {'SÍ' if api_key.startswith('mk-') or api_key.startswith('sk-') else 'NO'}")

# Probar conexión
try:
    import openai
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )
    
    print("\nProbando conexión...")
    response = client.chat.completions.create(
        model="kimi-k2-thinking",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ ¡Conexión exitosa!")
    
except openai.AuthenticationError as e:
    print(f"\n❌ Error de autenticación: {e}")
    print("La API key es inválida o no tiene permisos.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")