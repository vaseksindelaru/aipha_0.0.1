# aiphalab/analyze_aipha_1.py
"""
Analiza el sistema completo Aipha_1.0
"""

from shadow_hybrid import ShadowHybrid
from gemini_integration import GeminiShadow

def analyze_aipha_1():
    """Analiza Aipha_1 completo"""

    print("🔍 Iniciando análisis completo de Aipha_1...")
    print(f"📂 Directorio objetivo: ../aipha_1")

    # Verificar que el directorio existe
    import os
    target_path = "../aipha_1"
    if not os.path.exists(target_path):
        print(f"❌ Error: Directorio {target_path} no existe")
        return

    if not os.path.isdir(target_path):
        print(f"❌ Error: {target_path} no es un directorio")
        return

    try:
        # Shadow Híbrido con cache
        print("\n🏗️  Inicializando Shadow Hybrid...")
        shadow = ShadowHybrid(target_path)

        print("📊 Ejecutando análisis incremental...")
        shadow.analyze_codebase(force=False)  # Incremental

        overview = shadow.get_system_overview()

        print(f"\n✅ Análisis completado exitosamente:")
        print(f"   📦 Componentes analizados: {overview['total_components']}")
        print(f"   📝 Entradas en memoria: {overview['total_entries']}")
        print(f"   🔄 Última actualización: {overview.get('last_update', 'desconocida')}")

        # Mostrar estado de MCPs
        mcp_status = overview.get('mcp_status', {})
        print(f"\n🔧 Estado de MCPs:")
        for mcp, status in mcp_status.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {mcp}: {'Activo' if status else 'Deshabilitado'}")

        # Análisis con Gemini (si está disponible)
        print(f"\n🤖 Intentando análisis con Gemini...")
        try:
            gemini = GeminiShadow(base_path=target_path)
            analysis = gemini.get_architecture_explanation()

            # Mostrar análisis
            print("\n" + "="*50)
            print("🎯 ANÁLISIS DETALLADO DE AIPHA_1")
            print("="*50)
            print(analysis[:2000] + "..." if len(analysis) > 2000 else analysis)

            # Guardar reporte
            try:
                report_file = "aipha_1_analysis.md"
                with open(report_file, "w", encoding='utf-8') as f:
                    f.write("# 📊 Análisis Completo de Aipha_1\n\n")
                    f.write(f"**Fecha de análisis:** {overview.get('last_update', 'desconocida')}\n")
                    f.write(f"**Componentes analizados:** {overview['total_components']}\n")
                    f.write(f"**Entradas en memoria:** {overview['total_entries']}\n\n")
                    f.write("---\n\n")
                    f.write(analysis)

                print(f"\n📄 Reporte guardado exitosamente en: {report_file}")
                print(f"   📏 Tamaño: {len(analysis)} caracteres")

            except Exception as e:
                print(f"⚠️  Error guardando reporte: {e}")
                print("El análisis se mostró arriba pero no se guardó en archivo.")

        except Exception as e:
            print(f"⚠️  Gemini no disponible: {e}")
            print("   💡 Para análisis avanzado, configura GEMINI_API_KEY")
            print("   🔄 Análisis completado solo con Shadow Core (funcional básico)")

        print(f"\n🎉 Análisis de Aipha_1 completado exitosamente!")

    except Exception as e:
        print(f"\n❌ Error crítico en análisis: {e}")
        print("\n🔍 Detalles del error:")
        import traceback
        traceback.print_exc()

        print(f"\n💡 Sugerencias:")
        print("   - Verifica que el directorio ../aipha_1 existe y es accesible")
        print("   - Asegúrate de que hay archivos Python para analizar")
        print("   - Revisa permisos de lectura en el directorio")


def quick_analysis():
    """Análisis rápido de Aipha_1 (solo estadísticas básicas)"""

    print("⚡ Análisis rápido de Aipha_1...")

    try:
        shadow = ShadowHybrid("../aipha_1")
        overview = shadow.get_system_overview()

        print("📊 Estadísticas rápidas:")
        print(f"   📦 Componentes: {overview['total_components']}")
        print(f"   📝 Entradas: {overview['total_entries']}")
        print(f"   🔄 Actualización: {overview.get('last_update', 'N/A')[:19]}")

        return overview

    except Exception as e:
        print(f"❌ Error en análisis rápido: {e}")
        return None