# aiphalab/change_detector.py
"""
Detecta cambios en el código automáticamente
"""

import time
from pathlib import Path
from shadow_hybrid import ShadowHybrid
from gemini_integration import GeminiShadow

def watch_for_changes(interval=60):
    """Monitorea cambios cada X segundos"""

    print(f"👀 Iniciando monitoreo de cambios (intervalo: {interval}s)")
    print("Presiona Ctrl+C para detener\n")

    shadow = ShadowHybrid(".")
    last_analysis = None

    try:
        while True:
            # Re-analizar (incremental)
            shadow.analyze_codebase(force=False)

            # Ver si hay cambios
            current = shadow.get_system_overview()

            if last_analysis and current != last_analysis:
                print("🔄 Cambios detectados!")

                # Mostrar resumen de cambios
                old_components = last_analysis.get('total_components', 0)
                new_components = current.get('total_components', 0)
                old_entries = last_analysis.get('total_entries', 0)
                new_entries = current.get('total_entries', 0)

                print(f"   Componentes: {old_components} → {new_components}")
                print(f"   Entradas: {old_entries} → {new_entries}")

                # Análisis de cambios (si Gemini está disponible)
                try:
                    gemini = GeminiShadow(base_path=".")
                    analysis = gemini.ask("¿Qué cambió y por qué es importante?")
                    print("\n=== ANÁLISIS DE CAMBIOS ===")
                    print(analysis)
                except Exception as e:
                    print(f"⚠️  Gemini no disponible para análisis de cambios: {e}")
                    print("Cambios detectados pero sin análisis detallado")

            last_analysis = current
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo detenido por el usuario")
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")
        import traceback
        traceback.print_exc()


def detect_changes_once():
    """Detecta cambios una sola vez (útil para testing)"""

    print("🔍 Detectando cambios una sola vez...")

    shadow = ShadowHybrid(".")
    shadow.analyze_codebase(force=False)

    overview = shadow.get_system_overview()
    print(f"📊 Estado actual: {overview['total_components']} componentes, {overview['total_entries']} entradas")

    return overview