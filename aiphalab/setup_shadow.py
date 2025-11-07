# aiphalab/setup_shadow.py
"""
Script de configuración para Shadow (Fase 1)
Analiza Aipha_0.0.1 y prepara el sistema para consultas con Gemini
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("[Setup] Verificando dependencias...")
    
    dependencies = {
        'google.generativeai': 'google-generativeai',
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package} instalado")
        except ImportError:
            print(f"  ✗ {package} no instalado")
            missing.append(package)
    
    if missing:
        print("\n[Setup] Dependencias faltantes:")
        for package in missing:
            print(f"  pip install {package}")
        return False
    
    print("[Setup] Todas las dependencias están instaladas\n")
    return True

def check_api_key():
    """Verificar configuración de API key"""
    print("[Setup] Verificando API key de Gemini...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("  ✗ GEMINI_API_KEY no configurada")
        print("\n[Setup] Configurar API key:")
        print("  export GEMINI_API_KEY='tu_api_key'")
        print("  O crear archivo .env con: GEMINI_API_KEY=tu_api_key")
        return False
    
    print(f"  ✓ GEMINI_API_KEY configurada (***{api_key[-4:]})\n")
    return True

def analyze_codebase(repo_path: str = "../Aipha_0.0.1"):
    """Analizar el código de Aipha_0.0.1"""
    print(f"[Setup] Analizando código en: {repo_path}")
    
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        print(f"  ✗ Repositorio no encontrado: {repo_path}")
        print("\n[Setup] Ubicaciones posibles:")
        print("  - ../Aipha_0.0.1")
        print("  - ./Aipha_0.0.1")
        print("  - Especificar ruta manualmente")
        return False
    
    try:
        from memory_system import AiphaLabMemory
        
        memory = AiphaLabMemory()
        memory.analyze_codebase(repo_path)
        
        summary = memory.get_memory_summary()
        print(f"  ✓ Análisis completado:")
        print(f"    - {summary['total_entries']} entradas registradas")
        print(f"    - {len(summary['components'])} componentes analizados")
        print(f"    - Componentes: {', '.join(summary['components'].keys())}\n")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error al analizar: {str(e)}")
        return False

def test_shadow_query():
    """Probar consultas básicas a Shadow"""
    print("[Setup] Probando consultas a Shadow...")
    
    try:
        from shadow_query import ShadowQuery
        
        shadow = ShadowQuery()
        
        # Test 1: Componentes
        components = shadow.get_all_components()
        print(f"  ✓ Consulta de componentes: {len(components)} encontrados")
        
        # Test 2: Clases
        classes = shadow.get_all_classes()
        print(f"  ✓ Consulta de clases: {sum(len(c) for c in classes.values())} encontradas")
        
        # Test 3: Funciones
        functions = shadow.get_all_functions()
        print(f"  ✓ Consulta de funciones: {sum(len(f) for f in functions.values())} encontradas")
        
        # Test 4: Contexto
        context = shadow.get_context_for_gemini()
        print(f"  ✓ Generación de contexto: {len(context)} caracteres\n")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error en consultas: {str(e)}")
        return False

def test_gemini_integration():
    """Probar integración con Gemini"""
    print("[Setup] Probando integración con Gemini...")
    
    try:
        from gemini_integration import GeminiShadow
        
        gemini_shadow = GeminiShadow()
        
        # Test simple
        test_question = "¿Cuáles son los componentes principales del sistema?"
        response = gemini_shadow.ask(test_question)
        
        print(f"  ✓ Consulta a Gemini exitosa")
        print(f"  ✓ Respuesta recibida: {len(response)} caracteres\n")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error en integración: {str(e)}")
        return False

def main():
    """Ejecutar configuración completa"""
    print("=" * 60)
    print("SHADOW SETUP - FASE 1")
    print("Configuración de Autoconocimiento para Aipha_0.0.1")
    print("=" * 60)
    print()
    
    # Paso 1: Dependencias
    if not check_dependencies():
        print("\n[Setup] ❌ FALLÓ: Instalar dependencias primero")
        return False
    
    # Paso 2: API Key
    if not check_api_key():
        print("\n[Setup] ❌ FALLÓ: Configurar GEMINI_API_KEY")
        return False
    
    # Paso 3: Analizar código
    repo_path = input("[Setup] Ruta a Aipha_0.0.1 (Enter para '../Aipha_0.0.1'): ").strip()
    if not repo_path:
        repo_path = "../Aipha_0.0.1"
    
    if not analyze_codebase(repo_path):
        print("\n[Setup] ❌ FALLÓ: Analizar código")
        return False
    
    # Paso 4: Probar consultas
    if not test_shadow_query():
        print("\n[Setup] ❌ FALLÓ: Consultas a Shadow")
        return False
    
    # Paso 5: Probar Gemini
    if not test_gemini_integration():
        print("\n[Setup] ⚠️  ADVERTENCIA: Integración con Gemini falló")
        print("[Setup] Puedes usar Shadow sin Gemini")
    
    # Resumen final
    print("=" * 60)
    print("✅ SHADOW CONFIGURADO CORRECTAMENTE")
    print("=" * 60)
    print("\n[Setup] Próximos pasos:")
    print("  1. Probar consultas manuales:")
    print("     python shadow_query.py")
    print("  2. Modo interactivo con Gemini:")
    print("     python gemini_integration.py")
    print("  3. Integrar en tu aplicación:")
    print("     from shadow_query import ShadowQuery")
    print("     shadow = ShadowQuery()")
    print("     context = shadow.get_context_for_gemini()")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[Setup] Cancelado por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Setup] ❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)